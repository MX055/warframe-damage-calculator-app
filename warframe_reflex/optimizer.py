from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial

from warframe_damage_calculator import Arcane, Build, Calculator, Effect, Mod, OptimizationProgress, Optimizer, Progenitor, UpgradeStats, arsenal, balanced_damage_metric
from warframe_damage_calculator.engine.metrics import balanced_damage

from .constants import DEFAULT_OPTIMIZE_SEARCH, DEFAULT_OPTIMIZE_SPATIAL, INITIAL_COMBO_RUNTIME, NO_EFFECT, OPTIMIZE_SEARCH_EVALUATION_BUDGETS, OPTIMIZE_SPATIAL_MODES, RIVEN_ROLL_CONFIGS, RIVEN_STAT_ALIASES, SLOT_CONFIGS, SLOT_POLICY_DISCARD, SLOT_POLICY_KEEP
from .engine import apply_loadout_runtime, build_calculation_state

NONE = "None"
RIVEN = "Riven"

ProgressCallback = Callable[[OptimizationProgress], None]


@dataclass
class SlotSpec:
    index: int
    kind: str
    exilus: bool
    selected: str
    policy: str
    rank: int
    stacks: int
    condition: bool
    stance: bool = False
    riven_roll: str = "2 Positive + 1 Negative"
    riven_fields: dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizeRequest:
    weapon_type: str
    weapon_category: str
    weapon_name: str
    attack_mode: str
    evolutions: dict[int, int]
    combo_count: int | str
    evolution_runtime: dict[str, bool | int]
    progenitor_element: str
    progenitor_value: float
    external_fields: dict[str, float]
    slots: list[SlotSpec]
    find_optimal_riven: bool
    enemy_name: str = NONE
    enemy_level: int = 1
    enemy_steel_path: bool = False
    enemy_empowered: bool = False
    find_optimal_evolutions: bool = False
    find_optimal_progenitor: bool = False
    maximize_target: str = "balanced_total_dps_dph"
    body_part: str | None = None
    flat_dot_weight: float = 0.5
    dph_weight: float = 0.5
    spatial: str = DEFAULT_OPTIMIZE_SPATIAL
    cancel_event: threading.Event | None = None
    stance_combo: str = "neutral"
    ability_strength: float | None = None
    excluded_upgrades: set[str] = field(default_factory=set)
    excluded_riven_stats: set[str] = field(default_factory=set)
    riven_disposition: float = 1.0
    riven_base_stats: dict[str, float] = field(default_factory=dict)
    riven_non_negative: set[str] = field(default_factory=set)
    search_quality: str = DEFAULT_OPTIMIZE_SEARCH


@dataclass
class OptimizeResult:
    slot_names: list[str]
    slot_ranks: list[int]
    slot_stacks: list[int]
    slot_conditions: list[bool]
    slot_policies: list[str]
    riven_rolls: list[str]
    riven_fields: list[dict[str, float]]
    total_dps: float
    evaluations: int
    message: str
    evolutions: dict[int, int] = field(default_factory=dict)
    evolutions_optimized: bool = False
    progenitor_element: str = NO_EFFECT
    progenitor_optimized: bool = False
    progenitor_value: float = 0.0
    search_quality: str = DEFAULT_OPTIMIZE_SEARCH
    termination_reason: str = "budget exhausted"
    elapsed_seconds: float = 0.0


def _repository(weapon_type: str):
    return {"Primary": arsenal.primary, "Secondary": arsenal.secondary, "Melee": arsenal.melee, "Archgun": arsenal.archgun}.get(weapon_type, arsenal.primary)


def _load_weapon(request: OptimizeRequest):
    return _repository(request.weapon_type).get(request.weapon_name)


def _calculation_state(request: OptimizeRequest):
    combo = None if request.combo_count == INITIAL_COMBO_RUNTIME else int(request.combo_count) if str(request.combo_count).isdigit() else None
    return build_calculation_state(combo=combo, stance_combo=request.stance_combo, ability_strength=request.ability_strength)


def _load_enemy(request: OptimizeRequest):
    return arsenal.enemy.get(request.enemy_name).set(level=request.enemy_level, steel_path=request.enemy_steel_path, empowered=request.enemy_empowered)


def _riven_ranked(spec: SlotSpec):
    slot = "stance_mod" if spec.stance else "exilus_mod" if spec.exilus else "regular_arcane" if spec.kind == "arcane" else "regular_mod"
    library_stats = {alias: name for name, alias in RIVEN_STAT_ALIASES.items()}
    stats: dict[str, object] = {}
    for stat, raw in spec.riven_fields.items():
        if isinstance(raw, (int, float, bool, str)) and raw != 0:
            stats[library_stats.get(stat, stat)] = raw
    cls = Arcane if spec.kind == "arcane" else Mod
    return cls(name=RIVEN, slot=slot, max_rank=max(spec.rank, 0), stats=UpgradeStats(**stats), runtime={"rank": max(spec.rank, 0)})


def _load_slot(spec: SlotSpec):
    if spec.selected == NONE: return None
    if spec.selected == RIVEN: return _riven_ranked(spec)
    item = (arsenal.arcane if spec.kind == "arcane" else arsenal.mod).get(spec.selected)
    values = {"rank": min(max(spec.rank, 0), item.max_rank)}
    for field_name in item.stats.manual_fields:
        values[field_name] = spec.stacks if spec.stacks > 0 else spec.condition
    item.set(**values)
    return item


def _result_damage_mass(result) -> float:
    damage = result.aggregate.damage
    total_dph = damage.direct_dph + damage.dot_dph
    if total_dph <= 0:
        return 1.0
    weighted = sum((attack.damage.direct_dph + attack.damage.dot_dph) * (attack.spatial.damage_mass if attack.spatial.damage_mass is not None else 1.0) for attack in result.attacks.values())
    return weighted / total_dph


def _compact_balanced(direct_dph: float, dot_dph: float, direct_dps: float, dot_dps: float, damage_mass: float, dph_weight: float = 0.5) -> float:
    dps = balanced_damage(direct_dps, dot_dps)
    dph = balanced_damage(direct_dph, dot_dph)
    if dps <= 0 or dph <= 0 or damage_mass <= 0:
        return 0.0
    return (dps ** (2 * (1 - dph_weight)) * dph ** (2 * dph_weight) * damage_mass) ** (1 / 3)


def _compact_named(direct_dph: float, dot_dph: float, direct_dps: float, dot_dps: float, damage_mass: float, field: str = "total_dps") -> float:
    values = {
        "total_dps": direct_dps + dot_dps,
        "flat_dps": direct_dps,
        "direct_dps": direct_dps,
        "flat_dotps": dot_dps,
        "dot_dps": dot_dps,
        "total_dph": direct_dph + dot_dph,
        "flat_dph": direct_dph,
        "direct_dph": direct_dph,
        "flat_dotph": dot_dph,
        "dot_dph": dot_dph,
    }
    value = float(values.get(field, direct_dps + dot_dps))
    return value * damage_mass if value > 0 and damage_mass > 0 else 0.0


def _normalize_metric_field(target: str) -> str:
    return target.replace("total_weak_point_", "total_").replace("flat_weak_point_", "flat_").replace("total_resistant_", "total_").replace("flat_resistant_", "flat_")


def _metrics_for(request: OptimizeRequest):
    """Return (full_result_metric, compact_metric_or_None).

    Compact metrics keep the library's parallel interpreter path. None means the
    library default compact scorer for balanced_damage_metric. Spatial mass handling
    is applied by Optimizer.resolve(spatial=...).
    """
    target = request.maximize_target
    if target == "balanced_total_dps_dph":
        if request.dph_weight == 0.5:
            return balanced_damage_metric, None
        compact = partial(_compact_balanced, dph_weight=request.dph_weight)

        def metric(result):
            damage = result.aggregate.damage
            return _compact_balanced(damage.direct_dph, damage.dot_dph, damage.direct_dps, damage.dot_dps, _result_damage_mass(result), dph_weight=request.dph_weight)

        return metric, compact

    field = _normalize_metric_field(target)
    compact = partial(_compact_named, field=field)

    def metric(result):
        damage = result.aggregate.damage
        return _compact_named(damage.direct_dph, damage.dot_dph, damage.direct_dps, damage.dot_dps, _result_damage_mass(result), field=field)

    return metric, compact


def _metric_for(request: OptimizeRequest):
    return _metrics_for(request)[0]


def _body_part(request: OptimizeRequest) -> str | None:
    return request.body_part or None


def _perk_map(weapon, perks) -> dict[int, int]:
    selected = set(perks)
    return {tier: choice for tier, choices in weapon.perk_choices.items() for choice, perk in choices.items() if perk in selected}


def _is_riven(mod: Mod) -> bool:
    name = mod.name.casefold()
    return name == "riven" or name.startswith("riven (")


def _effect_numeric(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    nested = getattr(value, "value", None)
    if isinstance(nested, bool):
        return None
    if isinstance(nested, (int, float)):
        return float(nested)
    return None


def _riven_fields(mod: Mod) -> dict[str, float]:
    fields: dict[str, float] = {}
    for stat, effects in mod.stats.items():
        total = 0.0
        found = False
        for effect in effects:
            numeric = _effect_numeric(getattr(effect, "value", effect))
            if numeric is None:
                continue
            total += numeric
            found = True
        if found and total != 0:
            fields[RIVEN_STAT_ALIASES.get(stat, stat)] = total
    return dict(sorted(fields.items(), key=lambda item: (item[1] < 0, str.casefold(item[0]))))


def _runtime_stacks(upgrade: Mod | Arcane) -> int:
    values = [getattr(upgrade.runtime, field_name) for field_name in upgrade.stats.manual_fields]
    numeric = [int(value) for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)]
    return max(numeric, default=0)


def _runtime_condition(upgrade: Mod | Arcane) -> bool:
    return any(getattr(upgrade.runtime, field_name) is True for field_name in upgrade.stats.manual_fields)


def _riven_roll(mod: Mod) -> str:
    values = _riven_fields(mod).values()
    shape = (sum(value > 0 for value in values), sum(value < 0 for value in values))
    return next((name for name, config in RIVEN_ROLL_CONFIGS.items() if config[:2] == shape), "2 Positive + 1 Negative")


def optimize_build(request: OptimizeRequest, progress: ProgressCallback | None = None) -> OptimizeResult:
    weapon = _load_weapon(request)
    enemy = _load_enemy(request)
    fixed_specs = [spec for spec in request.slots if spec.policy == SLOT_POLICY_KEEP and spec.selected != NONE]
    fixed = [_load_slot(spec) for spec in fixed_specs]
    mods = [item for item in fixed if isinstance(item, Mod)]
    arcanes = [item for item in fixed if isinstance(item, Arcane)]
    perks = [weapon.perk_choices[tier][choice] for tier, choice in request.evolutions.items() if tier in weapon.perk_choices and choice in weapon.perk_choices[tier]]
    if request.find_optimal_progenitor or request.progenitor_element in {NO_EFFECT, NONE, ""}:
        progenitor = None
    else:
        progenitor = Progenitor(element=request.progenitor_element, bonus=(request.progenitor_value if request.progenitor_value > 0 else 0.6))
    build = Build(mods=mods, arcanes=arcanes, evolutions=perks, progenitor=progenitor)
    apply_loadout_runtime(build, request.evolution_runtime)
    calculator = Calculator(weapon, enemy, build)
    budget = OPTIMIZE_SEARCH_EVALUATION_BUDGETS.get(request.search_quality, OPTIMIZE_SEARCH_EVALUATION_BUDGETS[DEFAULT_OPTIMIZE_SEARCH])
    upgrade_blacklist = set(request.excluded_upgrades) if request.excluded_upgrades else None
    riven_blacklist = set(request.excluded_riven_stats) if request.excluded_riven_stats else None
    attack = (request.attack_mode or "").strip().lower().replace(" ", "_") or None
    metric, compact_metric = _metrics_for(request)
    spatial = OPTIMIZE_SPATIAL_MODES.get(request.spatial, OPTIMIZE_SPATIAL_MODES[DEFAULT_OPTIMIZE_SPATIAL])
    optimization = Optimizer(calculator).resolve(metric, compact_metric=compact_metric, spatial=spatial, attack=attack, body_part=_body_part(request), state=_calculation_state(request), evaluations=budget, riven=request.find_optimal_riven, evolutions=request.find_optimal_evolutions, upgrade_blacklist=upgrade_blacklist, riven_stat_blacklist=riven_blacklist, progress=progress)

    names = [NONE for _ in SLOT_CONFIGS]
    ranks = [0 for _ in SLOT_CONFIGS]
    stacks = [0 for _ in SLOT_CONFIGS]
    conditions = [False for _ in SLOT_CONFIGS]
    policies = [SLOT_POLICY_DISCARD for _ in SLOT_CONFIGS]
    rolls = ["2 Positive + 1 Negative" for _ in SLOT_CONFIGS]
    riven_fields = [{} for _ in SLOT_CONFIGS]
    used: set[int] = set()

    def place(item, preferred=None):
        candidates = [preferred] if preferred is not None else []
        if isinstance(item, Arcane): candidates += [i for i, c in enumerate(SLOT_CONFIGS) if c["kind"] == "arcane"]
        elif item.slot == "stance_mod": candidates += [i for i, c in enumerate(SLOT_CONFIGS) if c.get("stance")]
        elif item.slot == "exilus_mod": candidates += [i for i, c in enumerate(SLOT_CONFIGS) if c.get("exilus")]
        else: candidates += [i for i, c in enumerate(SLOT_CONFIGS) if c["kind"] == "mod" and not c.get("stance") and not c.get("exilus")]
        index = next((i for i in candidates if i is not None and i not in used), None)
        if index is None: return
        used.add(index)
        if isinstance(item, Mod) and _is_riven(item):
            names[index] = RIVEN
            rolls[index] = _riven_roll(item)
            riven_fields[index] = _riven_fields(item)
        else: names[index] = item.name
        ranks[index] = int(item.runtime.rank)
        stacks[index] = _runtime_stacks(item)
        conditions[index] = _runtime_condition(item)

    for spec in fixed_specs:
        item = _load_slot(spec)
        if item is not None:
            place(item, spec.index)
            policies[spec.index] = SLOT_POLICY_KEEP
    for item in optimization.build.ranked_upgrades:
        if any(item.name == fixed_item.name and type(item) is type(fixed_item) for fixed_item in fixed): continue
        place(item)

    perk_selection = _perk_map(weapon, optimization.build.evolutions)
    progenitor_element = optimization.build.progenitor.element if optimization.build.progenitor else NO_EFFECT
    progenitor_value = float(optimization.build.progenitor.bonus) if optimization.build.progenitor else 0.0
    return OptimizeResult(names, ranks, stacks, conditions, policies, rolls, riven_fields, optimization.score, optimization.evaluations, f"Optimization completed in {optimization.elapsed:.1f}s.", perk_selection, request.find_optimal_evolutions, progenitor_element, request.find_optimal_progenitor, progenitor_value, request.search_quality, "budget exhausted" if optimization.budget_exhausted else "converged", optimization.elapsed)
