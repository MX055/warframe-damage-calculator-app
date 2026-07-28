from __future__ import annotations

import itertools
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Iterable

from warframe_damage_calculator import Build, Upgrade

from .constants import (
    BALANCED_MAXIMIZE_TARGETS,
    DEFAULT_OPTIMIZE_MAXIMIZE,
    DEFAULT_OPTIMIZE_SEARCH,
    INITIAL_COMBO_RUNTIME,
    NO_EFFECT,
    OPTIMIZE_MAXIMIZE_TARGETS,
    OPTIMIZE_SEARCH_BALANCED,
    OPTIMIZE_SEARCH_EVALUATION_BUDGETS,
    OPTIMIZE_SEARCH_FAST,
    OPTIMIZE_SEARCH_OPTIONS,
    OPTIMIZE_SEARCH_THOROUGH,
    RIVEN_NON_NEGATIVE_STATS,
    RIVEN_ROLL_CONFIGS,
    RIVEN_ROLL_OPTIONS,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP,
    SLOT_POLICY_KEEP_IN_SLOT,
)
from .data import (
    _upgrade_names_for_ui,
    database_max_stacks,
    database_rank_bounds,
    database_upgrade,
    raw_upgrade_metadata,
    upgrade_conflicts_with_selected,
    upgrade_names_for_ui,
    weapon_evolution_perk_choices,
)
from .engine import build_upgrade, combo_multiplier_from_initial_combo, configured_enemy, configured_weapon, custom_upgrade_from_entry, is_non_empty_upgrade, parse_database_entry, progenitor_upgrade

NONE = "None"
CUSTOM = "Custom"
RIVEN = "Riven"

DAMAGE_RELATED_STATS = {
    "damage_bonus", "crit_chance", "crit_damage", "multishot", "status_chance", "status_damage",
    "fire_rate", "attack_speed", "weakpoint_damage", "weakpoint_crit_chance", "reload_speed",
    "magazine_capacity", "ammo_efficiency", "flat_crit_chance", "multiplicative_crit_chance",
    "flat_crit_damage", "multiplicative_base_damage", "multiplicative_fire_rate", "slash_proc",
    "random_proc", "crit_reset_charges", "duplicated_hit", "impact", "puncture", "slash", "cold",
    "electricity", "heat", "toxin", "blast", "corrosive", "gas", "magnetic", "radiation",
    "viral", "void", "corpus_damage", "grineer_damage", "infested_damage", "orokin_damage",
    "murmur_damage", "sentient_damage",
    # Legacy database aliases retained for custom and older database entries.
    "hunter_munitions", "internal_bleeding", "primed_chamber", "vigilante_bonus",
    "secondary_enervate", "secondary_encumber", "melee_duplicate", "melee_doughty",
}

DAMAGE_RELATED_BEHAVIORS = {
    "WEAPON_COMBO", "FIRST_SHOT", "LAST_SHOT", "DOUBLE_FOR_BOWS", "UNIQUE_STATUS",
    "ON_NON_CRIT", "ON_IMPACT_DOUBLE_BELOW_2_5_FR", "ON_CRIT", "ON_HIT", "ON_ANY_PROC",
    "NEAR_YELLOW", "FROM_PUNCTURE_X_STATUS", "STACK_RESET_CRIT_2_PLUS",
    "STATUS_EFFECT_STACKS", "STATUS_PROC_STACKS", "MULTISHOT_CONSUMES_AMMO",
}
CANDIDATE_SOFT_CAP = 72
CANDIDATE_SHORTLIST_LIMIT = 24
CANDIDATE_SHORTLIST_HARD_CAP = 36
CANDIDATE_PER_STAT_LIMIT = 2
CANDIDATE_RAW_STAT_LIMIT = 2
EVOLUTION_EXHAUSTIVE_LIMIT = 36
EVOLUTION_DESCENT_PASSES = 2
BALANCED_BEAM_WIDTH = 2
THOROUGH_BEAM_WIDTH = 8
THOROUGH_REBUILD_VARIANTS = 4
HILL_CLIMB_SWAP_LIMIT = 40  # Backward-compatible profile-script export; the optimizer now uses quality budgets.

ProgressCallback = Callable[[str, float, int, float | None], None]  # phase, fraction 0-1, evaluations, best_score
MAXIMIZE_TARGET_ATTRS = frozenset(OPTIMIZE_MAXIMIZE_TARGETS.values())
MAXIMIZE_TARGET_LABELS = {attr: label for label, attr in OPTIMIZE_MAXIMIZE_TARGETS.items()}


def score_maximize_target(final, maximize_target: str, weakpoint_weight: float = 0.5, flat_dot_weight: float = 0.5) -> float:
    """Return a numeric optimizer score, including for unavailable bodypart metrics.

    The library represents weakpoint/resistant results as ``None`` when the
    selected enemy has no matching bodypart. Those values must not escape into
    candidate comparisons such as ``dps > best_dps``.
    """
    pair = BALANCED_MAXIMIZE_TARGETS.get(maximize_target)
    if pair is not None:
        normal_dps = max(float(getattr(final, pair[0], 0) or 0), 0.0)
        normal_dph = max(float(getattr(final, pair[1], 0) or 0), 0.0)
        weakpoint_dps = max(float(getattr(final, "total_weakpoint_dps", 0) or 0), 0.0)
        weakpoint_dph = max(float(getattr(final, "total_weakpoint_dph", 0) or 0), 0.0)
        normal_score = (normal_dps * normal_dph) ** 0.5
        weakpoint_score = (weakpoint_dps * weakpoint_dph) ** 0.5
        weakpoint_weight = min(max(float(weakpoint_weight), 0.0), 1.0)

        normal_dotps = max(float(getattr(final, "flat_dotps", 0) or 0), 0.0)
        normal_dotph = max(float(getattr(final, "flat_dotph", 0) or 0), 0.0)
        weakpoint_dotps = max(float(getattr(final, "flat_weakpoint_dotps", 0) or 0), 0.0)
        weakpoint_dotph = max(float(getattr(final, "flat_weakpoint_dotph", 0) or 0), 0.0)
        normal_dot_score = (normal_dotps * normal_dotph) ** 0.5
        weakpoint_dot_score = (weakpoint_dotps * weakpoint_dotph) ** 0.5

        def blend(normal: float, weakpoint: float) -> float:
            if weakpoint_weight <= 0:
                return normal
            if weakpoint_weight >= 1:
                return weakpoint
            if normal <= 0 or weakpoint <= 0:
                return 0.0
            return normal ** (1.0 - weakpoint_weight) * weakpoint ** weakpoint_weight

        direct_score = blend(normal_score, weakpoint_score)
        dot_score = blend(normal_dot_score, weakpoint_dot_score)
        flat_dot_weight = min(max(float(flat_dot_weight), 0.0), 1.0)
        if flat_dot_weight <= 0:
            return direct_score
        if flat_dot_weight >= 1:
            return dot_score
        if direct_score <= 0 or dot_score <= 0:
            return 0.0
        return direct_score ** (1.0 - flat_dot_weight) * dot_score ** flat_dot_weight
    return float(getattr(final, maximize_target, 0) or 0)


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
    custom_entry: str = ""
    riven_roll: str = "2 Positive + 1 Negative"
    riven_fields: dict[str, float] = field(default_factory=dict)


@dataclass
class OptimizeRequest:
    weapon_type: str
    weapon_category: str
    weapon_name: str
    custom_weapon: bool
    custom_weapon_entry: str
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
    custom_enemy_entry: str = ""
    enemy_level: int = 1
    enemy_steel_path: bool = False
    enemy_empowered: bool = False
    find_optimal_evolutions: bool = False
    maximize_target: str = OPTIMIZE_MAXIMIZE_TARGETS[DEFAULT_OPTIMIZE_MAXIMIZE]
    weakpoint_weight: float = 0.5
    flat_dot_weight: float = 0.5
    cancel_event: threading.Event | None = None
    stance_combo: str = "neutral"
    ability_strength: float | None = None
    excluded_upgrades: set[str] = field(default_factory=set)
    excluded_riven_stats: set[str] = field(default_factory=set)
    riven_disposition: float = 1.0
    riven_base_stats: dict[str, float] = field(default_factory=dict)
    riven_non_negative: set[str] = field(default_factory=lambda: set(RIVEN_NON_NEGATIVE_STATS))
    search_quality: str = DEFAULT_OPTIMIZE_SEARCH


@dataclass
class OptimizeResult:
    slot_names: list[str]
    slot_ranks: list[int]
    slot_stacks: list[int]
    slot_policies: list[str]
    riven_rolls: list[str]
    riven_fields: list[dict[str, float]]
    custom_entries: list[str]
    total_dps: float
    evaluations: int
    message: str
    evolutions: dict[int, int] = field(default_factory=dict)
    evolutions_optimized: bool = False
    search_quality: str = DEFAULT_OPTIMIZE_SEARCH
    termination_reason: str = "local optimum"


@dataclass(frozen=True)
class _SearchState:
    names: tuple[str, ...]
    ranks: tuple[int, ...]
    stacks: tuple[int, ...]
    rolls: tuple[str, ...]
    riven_fields: tuple[tuple[tuple[str, float], ...], ...]
    customs: tuple[str, ...]
    evolutions: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class _ScoredState:
    score: float
    state: _SearchState
    changed_slot: int = -1


def riven_field_limits(base_stats: dict[str, float], disposition: float, roll_name: str, field_name: str, negative: bool, non_negative: Iterable[str]) -> tuple[float, float] | None:
    base_value = base_stats.get(field_name)
    if base_value is None:
        return None
    _pos, neg_count, bonus_factor, malus_factor = RIVEN_ROLL_CONFIGS.get(roll_name, RIVEN_ROLL_CONFIGS["2 Positive + 1 Negative"])
    if negative:
        if not neg_count or field_name in set(non_negative):
            return None
        center = base_value * disposition * malus_factor
        return center * 1.1, center * 0.9
    center = base_value * disposition * bonus_factor
    return center * 0.9, center * 1.1


def _empty_upgrade(kind: str) -> Upgrade:
    return Upgrade({"name": NONE, "type": kind, "stats": {}, "runtime": {"rank": 0}})


def _upgrade_effects(name: str):
    stats = raw_upgrade_metadata(name).get("stats") or {}
    for stat, effects in (stats.items() if isinstance(stats, dict) else ()):
        for effect in effects if isinstance(effects, list) else [effects]:
            yield stat, effect


def _has_damage_stats(name: str) -> bool:
    for stat, effect in _upgrade_effects(name):
        if stat in DAMAGE_RELATED_STATS:
            return True
        if isinstance(effect, dict) and str(effect.get("behavior") or "") in DAMAGE_RELATED_BEHAVIORS:
            return True
    return False


def _has_special_optimizer_behavior(name: str) -> bool:
    return any(isinstance(effect, dict) and str(effect.get("behavior") or "") in DAMAGE_RELATED_BEHAVIORS for _stat, effect in _upgrade_effects(name))


def _has_trigger_compatibility(name: str) -> bool:
    return bool((raw_upgrade_metadata(name).get("compatibility") or {}).get("triggers"))


def _matches_optimizer_stat(name: str, stat: str) -> bool:
    for effect_stat, effect in _upgrade_effects(name):
        if effect_stat == stat:
            return True
        if isinstance(effect, dict) and str(effect.get("behavior") or "") == stat:
            return True
    return False


def _raw_optimizer_strength(name: str, stat: str) -> float:
    values: list[float] = []
    for effect_stat, effect in _upgrade_effects(name):
        behavior = str(effect.get("behavior") or "") if isinstance(effect, dict) else ""
        if effect_stat != stat and behavior != stat:
            continue
        value = effect.get("value", 0) if isinstance(effect, dict) else effect
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            values.append(abs(float(value)))
    return max(values, default=0.0)


def _cap_candidates(names: tuple[str, ...] | list[str]) -> list[str]:
    names = list(names)
    if len(names) < CANDIDATE_SOFT_CAP:
        return names
    preferred = [name for name in names if _has_damage_stats(name)]
    return preferred or names


def _max_runtime(name: str, *, kind: str) -> tuple[int, int]:
    is_arcane = kind == "arcane"
    _, max_rank = database_rank_bounds(name, is_arcane_slot=is_arcane)
    return max_rank, database_max_stacks(name, is_arcane_slot=is_arcane) or 0


def _db_upgrade(name: str, kind: str, rank: int, stacks: int, condition: bool = True) -> Upgrade:
    loaded = database_upgrade(name, kind=kind, rank=rank, stacks=stacks if stacks > 0 else None, condition=condition)
    return loaded or _empty_upgrade(kind)


def optimize_build(request: OptimizeRequest, progress: ProgressCallback | None = None) -> OptimizeResult:
    if not request.weapon_name or request.weapon_name == NONE:
        raise ValueError("Select a weapon before optimizing.")
    slots = sorted(request.slots, key=lambda item: item.index)
    if len(slots) != len(SLOT_CONFIGS):
        raise ValueError("Optimizer expects one SlotSpec per configured slot.")
    maximize_target = request.maximize_target
    if maximize_target not in MAXIMIZE_TARGET_ATTRS:
        raise ValueError(f"unsupported maximize target {maximize_target!r}; expected one of {sorted(MAXIMIZE_TARGET_ATTRS)}")
    maximize_label = MAXIMIZE_TARGET_LABELS.get(maximize_target, maximize_target)
    search_quality = request.search_quality if request.search_quality in OPTIMIZE_SEARCH_OPTIONS else DEFAULT_OPTIMIZE_SEARCH
    evaluation_budget = OPTIMIZE_SEARCH_EVALUATION_BUDGETS[search_quality]
    active_quality = OPTIMIZE_SEARCH_BALANCED if search_quality == OPTIMIZE_SEARCH_THOROUGH else search_quality
    primary_budget = OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_BALANCED] if search_quality == OPTIMIZE_SEARCH_THOROUGH else evaluation_budget

    evaluations = 0
    budget_limited = False

    def check_cancelled() -> None:
        if request.cancel_event is not None and request.cancel_event.is_set():
            raise InterruptedError("Optimization aborted")

    def report(phase: str, fraction: float, best: float | None = None):
        check_cancelled()
        if progress:
            progress(phase, max(0.0, min(1.0, fraction)), evaluations, best)

    report("Preparing…", 0.0)

    weapon_filter_name = None if request.custom_weapon else request.weapon_name
    excluded_upgrades = set(request.excluded_upgrades)
    custom_metadata = None
    if request.custom_weapon and request.custom_weapon_entry.strip():
        try:
            custom_metadata = parse_database_entry(request.custom_weapon_entry, default_name="Custom Weapon", default_type=request.weapon_type.casefold())
        except ValueError:
            custom_metadata = None

    def upgrade_pool(include_mods: bool, include_arcanes: bool, exilus_only: bool, *, stance_only: bool = False) -> list[str]:
        if custom_metadata is not None:
            names = _upgrade_names_for_ui(request.weapon_category, weapon_filter_name, request.attack_mode, include_mods, include_arcanes, exilus_only, stance_only=stance_only, custom_metadata=custom_metadata)
        else:
            names = upgrade_names_for_ui(request.weapon_category, weapon_filter_name, request.attack_mode, include_mods, include_arcanes, exilus_only, stance_only)
        return [name for name in names if name not in excluded_upgrades]

    full_mod_pool = upgrade_pool(True, False, False)
    full_stance_pool = upgrade_pool(True, False, False, stance_only=True) if request.weapon_type == "Melee" else []
    full_exilus_pool = upgrade_pool(True, False, True)
    full_arcane_pool = upgrade_pool(False, True, False)
    mod_pool = _cap_candidates(full_mod_pool)
    stance_pool = list(full_stance_pool)
    exilus_pool = _cap_candidates(full_exilus_pool)
    arcane_pool = _cap_candidates(full_arcane_pool)

    n = len(slots)
    names = [NONE for _ in range(n)]
    ranks = [0 for _ in range(n)]
    stacks_list = [0 for _ in range(n)]
    policies = [SLOT_POLICY_DISCARD for _ in range(n)]
    rolls = [slot.riven_roll for slot in slots]
    riven_fields = [{} for _ in range(n)]
    customs = [slot.custom_entry for slot in slots]
    stance_combo = request.stance_combo if request.weapon_type == "Melee" else "neutral"

    progenitor = progenitor_upgrade(request.progenitor_element, request.progenitor_value, NO_EFFECT)
    external = build_upgrade("External Buffs", dict(request.external_fields))
    target = configured_enemy(request.enemy_name, custom_enemy=request.enemy_name == CUSTOM, custom_entry=request.custom_enemy_entry if request.enemy_name == CUSTOM else None, level=request.enemy_level, steel_path=request.enemy_steel_path, empowered=request.enemy_empowered)
    optimizer_weapon = configured_weapon(
        request.weapon_type, request.weapon_name, custom_weapon=request.custom_weapon, base_stats={}, upgrades=[],
        custom_entry=request.custom_weapon_entry if request.custom_weapon else None,
        selected_mode=request.attack_mode or None, evolutions=request.evolutions or None,
        combo=request.combo_count if request.weapon_type == "Melee" else None,
        runtime_conditions=request.evolution_runtime,
        stance_combo=stance_combo if request.weapon_type == "Melee" else None,
        ability_strength=request.ability_strength,
        target=target,
    )
    optimizer_build = Build()
    optimizer_weapon.build = optimizer_build
    empty_upgrades = {kind: _empty_upgrade(kind) for kind in {slot.kind for slot in slots}}
    upgrade_cache: dict[tuple[str, str, int, int, bool], Upgrade] = {}
    runtime_cache: dict[tuple[str, str], tuple[int, int]] = {}
    score_cache: dict[tuple, float] = {}
    current_evolutions = dict(request.evolutions or {})
    best_seen: _ScoredState | None = None

    def max_runtime(name: str, kind: str) -> tuple[int, int]:
        key = name, kind
        if key not in runtime_cache:
            runtime_cache[key] = _max_runtime(name, kind=kind)
        return runtime_cache[key]

    def cached_db_upgrade(name: str, kind: str, rank: int, stacks: int, condition: bool = True) -> Upgrade:
        key = name, kind, rank, stacks, condition
        if key not in upgrade_cache:
            upgrade_cache[key] = _db_upgrade(name, kind, rank, stacks, condition)
        return upgrade_cache[key]

    def pool_for(index: int) -> list[str]:
        slot = slots[index]
        if slot.kind == "arcane":
            return arcane_pool
        if slot.stance:
            return stance_pool
        return exilus_pool if slot.exilus else mod_pool

    def occupied(exclude: int | None = None) -> set[str]:
        return {names[i] for i in range(n) if i != exclude and names[i] not in {NONE, CUSTOM, RIVEN}}

    def legal(name: str, index: int) -> bool:
        if name in {NONE, CUSTOM, RIVEN}:
            return True
        others = occupied(exclude=index)
        return name not in others and not upgrade_conflicts_with_selected(name, others)

    def build_slot_upgrade(index: int) -> Upgrade:
        name, slot = names[index], slots[index]
        if name == NONE:
            return empty_upgrades[slot.kind]
        if name == CUSTOM:
            return custom_upgrade_from_entry(customs[index] or f'{{"name":"Custom","type":"{slot.kind}","stats":{{}}}}', default_name=slot.kind.title(), default_type=slot.kind)
        if name == RIVEN:
            return build_upgrade(RIVEN, riven_fields[index])
        return cached_db_upgrade(name, slot.kind, ranks[index], stacks_list[index], True)

    def equipped_stance_name() -> str:
        for index, slot in enumerate(slots):
            if slot.stance:
                return names[index]
        return NONE

    def capture_state() -> _SearchState:
        return _SearchState(
            names=tuple(names), ranks=tuple(ranks), stacks=tuple(stacks_list), rolls=tuple(rolls),
            riven_fields=tuple(tuple(sorted(fields.items())) for fields in riven_fields),
            customs=tuple(customs), evolutions=tuple(sorted(current_evolutions.items())),
        )

    def restore_state(state: _SearchState) -> None:
        nonlocal current_evolutions
        names[:] = state.names
        ranks[:] = state.ranks
        stacks_list[:] = state.stacks
        rolls[:] = state.rolls
        riven_fields[:] = [dict(fields) for fields in state.riven_fields]
        customs[:] = state.customs
        current_evolutions = dict(state.evolutions)

    def fresh_score_state(state: _SearchState) -> float:
        fresh_upgrades: list[Upgrade] = []
        fresh_progenitor = progenitor_upgrade(request.progenitor_element, request.progenitor_value, NO_EFFECT)
        if is_non_empty_upgrade(fresh_progenitor):
            fresh_upgrades.append(fresh_progenitor)
        for index, name in enumerate(state.names):
            slot = slots[index]
            if name == NONE:
                continue
            if name == CUSTOM:
                fresh_upgrades.append(custom_upgrade_from_entry(state.customs[index] or f'{{"name":"Custom","type":"{slot.kind}","stats":{{}}}}', default_name=slot.kind.title(), default_type=slot.kind))
            elif name == RIVEN:
                fresh_upgrades.append(build_upgrade(RIVEN, dict(state.riven_fields[index])))
            else:
                fresh_upgrades.append(_db_upgrade(name, slot.kind, state.ranks[index], state.stacks[index], True))
        fresh_external = build_upgrade("External Buffs", dict(request.external_fields))
        if is_non_empty_upgrade(fresh_external):
            fresh_upgrades.append(fresh_external)
        fresh_target = configured_enemy(request.enemy_name, custom_enemy=request.enemy_name == CUSTOM, custom_entry=request.custom_enemy_entry if request.enemy_name == CUSTOM else None, level=request.enemy_level, steel_path=request.enemy_steel_path, empowered=request.enemy_empowered)
        fresh_weapon = configured_weapon(
            request.weapon_type, request.weapon_name, custom_weapon=request.custom_weapon, base_stats={}, upgrades=fresh_upgrades,
            custom_entry=request.custom_weapon_entry if request.custom_weapon else None, selected_mode=request.attack_mode or None,
            evolutions=dict(state.evolutions), combo=request.combo_count if request.weapon_type == "Melee" else None,
            runtime_conditions=request.evolution_runtime, stance_combo=stance_combo if request.weapon_type == "Melee" else None,
            ability_strength=request.ability_strength, target=fresh_target,
        )
        return score_maximize_target(fresh_weapon.results.main.final, maximize_target, request.weakpoint_weight, request.flat_dot_weight)

    def score(*, deadline: int | None = None) -> float | None:
        nonlocal evaluations, best_seen, budget_limited
        check_cancelled()
        slot_keys = []
        for index, name in enumerate(names):
            if name == RIVEN:
                slot_keys.append((name, 0, 0, rolls[index], tuple(sorted(riven_fields[index].items())), ""))
            elif name == CUSTOM:
                slot_keys.append((name, 0, 0, "", (), customs[index]))
            elif name == NONE:
                slot_keys.append((name, 0, 0, "", (), ""))
            else:
                slot_keys.append((name, ranks[index], stacks_list[index], "", (), ""))
        key = (tuple(slot_keys), tuple(sorted(current_evolutions.items())))
        if key in score_cache:
            return score_cache[key]
        limit = min(evaluation_budget, deadline) if deadline is not None else evaluation_budget
        if evaluations >= limit:
            budget_limited = True
            return None
        evaluations += 1
        upgrades: list[Upgrade] = []
        if is_non_empty_upgrade(progenitor):
            upgrades.append(progenitor)
        upgrades.extend(u for u in (build_slot_upgrade(i) for i in range(n)) if is_non_empty_upgrade(u))
        if is_non_empty_upgrade(external):
            upgrades.append(external)
        optimizer_build.upgrades = upgrades
        if request.weapon_type == "Melee":
            optimizer_weapon.data.runtime.stance_combo = stance_combo
            optimizer_weapon.data.runtime.combo = 1 if request.combo_count == INITIAL_COMBO_RUNTIME else int(request.combo_count)
        optimizer_weapon.data.runtime.evolutions = dict(current_evolutions)
        optimizer_weapon.data.runtime.update(request.evolution_runtime)
        optimizer_weapon.results.resolve(validate_cycles=False)
        if request.weapon_type == "Melee" and request.combo_count == INITIAL_COMBO_RUNTIME:
            optimizer_weapon.data.runtime.combo = combo_multiplier_from_initial_combo(optimizer_weapon.results.main.effective.initial_combo, optimizer_weapon)
            optimizer_weapon.results.resolve(validate_cycles=False)
        result = score_maximize_target(optimizer_weapon.results.main.final, maximize_target, request.weakpoint_weight, request.flat_dot_weight)
        candidate_state = capture_state()
        if best_seen is None or result > best_seen.score:
            if evaluations >= limit:
                budget_limited = True
                return best_seen.score if best_seen is not None else result
            evaluations += 1
            result = fresh_score_state(candidate_state)
        score_cache[key] = result
        if best_seen is None or result > best_seen.score:
            best_seen = _ScoredState(result, candidate_state)
        return result

    def place(index: int, name: str, *, policy: str, rank: int = 0, stacks: int = 0, roll: str | None = None, fields: dict[str, float] | None = None, custom: str | None = None):
        names[index] = name
        ranks[index], stacks_list[index], policies[index] = rank, stacks, policy
        if roll is not None:
            rolls[index] = roll
        if fields is not None:
            riven_fields[index] = dict(fields)
        if custom is not None:
            customs[index] = custom

    # 1) Pin keep-in-slot.
    for i, slot in enumerate(slots):
        if slot.selected != NONE and slot.policy == SLOT_POLICY_KEEP_IN_SLOT:
            place(i, slot.selected, policy=SLOT_POLICY_KEEP_IN_SLOT, rank=slot.rank, stacks=slot.stacks, roll=slot.riven_roll, fields=slot.riven_fields, custom=slot.custom_entry)

    # 2) Assign keep items into compatible empty slots (prefer original index).
    for i, slot in enumerate(slots):
        if slot.selected == NONE or slot.policy != SLOT_POLICY_KEEP:
            continue
        candidates = [j for j in range(n) if names[j] == NONE and slots[j].kind == slot.kind and slots[j].exilus == slot.exilus]
        target = i if i in candidates else (candidates[0] if candidates else i)
        place(target, slot.selected, policy=SLOT_POLICY_KEEP, rank=slot.rank, stacks=slot.stacks, roll=slot.riven_roll, fields=slot.riven_fields, custom=slot.custom_entry)

    # Open slots: not keep / keep-in-slot (includes None and discard). Stance first so combo DPS is settled early.
    open_slots = [i for i in range(n) if policies[i] not in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT}]
    open_slots.sort(key=lambda index: (0 if slots[index].stance else 1, index))
    for i in open_slots:
        # Seed discard selections that are still present as starting point, else clear.
        slot = slots[i]
        if slot.selected != NONE and slot.selected not in excluded_upgrades and slot.policy == SLOT_POLICY_DISCARD and legal(slot.selected, i):
            if slot.selected in {CUSTOM, RIVEN}:
                place(i, slot.selected, policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, roll=slot.riven_roll, fields=slot.riven_fields, custom=slot.custom_entry)
            else:
                max_rank, max_stacks = max_runtime(slot.selected, slot.kind)
                place(i, slot.selected, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks)
        else:
            place(i, NONE, policy=SLOT_POLICY_DISCARD)

    baseline = score()
    if baseline is None:
        raise RuntimeError("Optimizer evaluation budget is too small to score the starting build.")
    report("Seeded baseline", 0.05, baseline)

    # Rank large pools once against the seeded build. The full greedy search then
    # evaluates the strongest candidates in every slot without repeatedly scanning
    # hundreds of clearly weaker upgrades.
    pool_groups = [
        (mod_pool, [i for i in open_slots if slots[i].kind == "mod" and not slots[i].exilus and not slots[i].stance]),
        (stance_pool, [i for i in open_slots if slots[i].stance]),
        (exilus_pool, [i for i in open_slots if slots[i].kind == "mod" and slots[i].exilus]),
        (arcane_pool, [i for i in open_slots if slots[i].kind == "arcane"]),
    ]
    screening_total = sum(len(pool) for pool, indices in pool_groups if indices and len(pool) > CANDIDATE_SHORTLIST_LIMIT)
    screening_done = 0

    def shortlist(pool: list[str], indices: list[int]) -> list[str]:
        nonlocal screening_done
        if not indices or len(pool) <= CANDIDATE_SHORTLIST_LIMIT:
            return pool
        index = indices[0]
        prev = names[index], ranks[index], stacks_list[index], dict(riven_fields[index]), rolls[index], customs[index]
        ranked: list[tuple[float, str]] = []
        for candidate in pool:
            if legal(candidate, index):
                max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
                place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks, fields={})
                candidate_score = score()
                if candidate_score is None:
                    break
                ranked.append((candidate_score, candidate))
            screening_done += 1
            if screening_done % 8 == 0:
                report("Screening candidates...", 0.05 + 0.10 * screening_done / max(screening_total, 1), baseline)
        place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2], fields=prev[3], roll=prev[4], custom=prev[5])
        ranked.sort(key=lambda item: (-item[0], item[1].casefold()))
        trigger_limited = [name for name in pool if _has_trigger_compatibility(name)]
        ranked_base = [(dps, name) for dps, name in ranked if name not in trigger_limited]
        mandatory = [name for name in pool if _has_special_optimizer_behavior(name) and name not in trigger_limited]
        for i in indices:
            if names[i] not in {NONE, CUSTOM, RIVEN}:
                mandatory.append(names[i])
        retained = list(dict.fromkeys(mandatory))
        for _dps, name in ranked_base[:CANDIDATE_SHORTLIST_LIMIT]:
            if name not in retained:
                retained.append(name)
        for stat in (*sorted(DAMAGE_RELATED_STATS), *sorted(DAMAGE_RELATED_BEHAVIORS)):
            matching = [name for _dps, name in ranked_base if _matches_optimizer_stat(name, stat)]
            for name in matching[:CANDIDATE_PER_STAT_LIMIT]:
                if name not in retained:
                    retained.append(name)
            by_strength = sorted(matching, key=lambda name: (-_raw_optimizer_strength(name, stat), name.casefold()))
            for name in by_strength[:CANDIDATE_RAW_STAT_LIMIT]:
                if name not in retained:
                    retained.append(name)
        mandatory_count = len(set(mandatory))
        retained = retained[:max(CANDIDATE_SHORTLIST_HARD_CAP, mandatory_count)]
        retained.extend(name for name in trigger_limited if name not in retained)
        return retained

    mod_pool = shortlist(mod_pool, pool_groups[0][1])
    stance_pool = shortlist(stance_pool, pool_groups[1][1])
    exilus_pool = shortlist(exilus_pool, pool_groups[2][1])
    arcane_pool = shortlist(arcane_pool, pool_groups[3][1])
    report("Candidates ready", 0.12, baseline)

    def greedy_fill(*, label: str, progress_start: float, progress_span: float, slot_order: list[int] | None = None, deadline: int | None = None, defer_trigger_limited: bool = False) -> None:
        nonlocal baseline
        ordered_slots = slot_order or open_slots
        n_open = max(len(ordered_slots), 1)
        current_score = score(deadline=deadline)
        if current_score is None:
            return
        baseline = current_score
        for fill_i, index in enumerate(ordered_slots):
            best_name, best_dps, best_rank, best_stacks = names[index], baseline, ranks[index], stacks_list[index]
            prev = names[index], ranks[index], stacks_list[index], dict(riven_fields[index]), rolls[index], customs[index]
            pool = pool_for(index)
            pool_n = max(len(pool), 1)
            for candidate_i, candidate in enumerate(pool, start=1):
                if defer_trigger_limited and _has_trigger_compatibility(candidate) or not legal(candidate, index):
                    continue
                max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
                place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks, fields={}, custom=customs[index])
                dps = score(deadline=deadline)
                if dps is None:
                    break
                if dps > best_dps:
                    best_name, best_dps, best_rank, best_stacks = candidate, dps, max_rank, max_stacks
                if candidate_i == 1 or candidate_i == pool_n or candidate_i % 12 == 0:
                    slot_frac = (fill_i + candidate_i / pool_n) / n_open
                    report(f"{label} ({fill_i + 1}/{len(open_slots)})", progress_start + progress_span * slot_frac, best_dps)
            place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2], fields=prev[3], roll=prev[4], custom=prev[5])
            if best_dps > baseline:
                place(index, best_name, policy=SLOT_POLICY_DISCARD, rank=best_rank, stacks=best_stacks, fields={})
                baseline = best_dps
            report(f"{label} ({fill_i + 1}/{len(open_slots)})", progress_start + progress_span * (fill_i + 1) / n_open, baseline)
            if evaluations >= (deadline or evaluation_budget):
                break

    def replacement_candidates(index: int) -> list[str]:
        return [NONE, *pool_for(index)]

    def place_candidate(index: int, candidate: str) -> None:
        if candidate == NONE:
            place(index, NONE, policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, fields={})
            return
        max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
        place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks, fields={})

    def round_robin_moves() -> Iterable[tuple[int, str]]:
        candidates = {index: replacement_candidates(index) for index in open_slots}
        for candidate_i in range(max((len(values) for values in candidates.values()), default=0)):
            for index in open_slots:
                if candidate_i < len(candidates[index]):
                    yield index, candidates[index][candidate_i]

    def replacement_pass(*, deadline: int, label: str, collect_frontier: bool) -> tuple[bool, list[_ScoredState], bool]:
        """Evaluate a complete one-replacement neighborhood fairly across every mutable slot."""
        nonlocal baseline
        origin = capture_state()
        origin_score = baseline
        best = _ScoredState(origin_score, origin)
        frontier_by_slot: dict[int, _ScoredState] = {}
        completed = True
        for move_i, (index, candidate) in enumerate(round_robin_moves(), start=1):
            restore_state(origin)
            if candidate == names[index] or not legal(candidate, index):
                continue
            place_candidate(index, candidate)
            dps = score(deadline=deadline)
            if dps is None:
                completed = False
                break
            state = capture_state()
            if dps > best.score:
                best = _ScoredState(dps, state, index)
            elif collect_frontier:
                previous = frontier_by_slot.get(index)
                if previous is None or dps > previous.score:
                    frontier_by_slot[index] = _ScoredState(dps, state, index)
            if move_i == 1 or move_i % 16 == 0:
                report(label, 0.50 + 0.32 * evaluations / max(evaluation_budget, 1), max(best.score, baseline))
        restore_state(best.state)
        improved = best.score > origin_score
        baseline = best.score
        frontier = sorted(frontier_by_slot.values(), key=lambda item: (-item.score, item.changed_slot))
        return improved, frontier, completed

    def swap_payload(first: int, second: int) -> None:
        names[first], names[second] = names[second], names[first]
        ranks[first], ranks[second] = ranks[second], ranks[first]
        stacks_list[first], stacks_list[second] = stacks_list[second], stacks_list[first]
        rolls[first], rolls[second] = rolls[second], rolls[first]
        riven_fields[first], riven_fields[second] = riven_fields[second], riven_fields[first]
        customs[first], customs[second] = customs[second], customs[first]

    def ordering_pass(*, deadline: int, label: str) -> tuple[bool, bool]:
        """Optimize slot order separately; elemental combinations depend on mod order."""
        nonlocal baseline
        reorderable = [index for index in open_slots if slots[index].kind == "mod" and not slots[index].exilus and not slots[index].stance and names[index] != NONE]
        origin = capture_state()
        best = _ScoredState(baseline, origin)
        completed = True
        for first, second in itertools.combinations(reorderable, 2):
            restore_state(origin)
            swap_payload(first, second)
            dps = score(deadline=deadline)
            if dps is None:
                completed = False
                break
            if dps > best.score:
                best = _ScoredState(dps, capture_state())
        restore_state(best.state)
        improved = best.score > baseline
        baseline = best.score
        report(label, 0.50 + 0.32 * evaluations / max(evaluation_budget, 1), baseline)
        return improved, completed

    def variable_neighborhood_descent(*, deadline: int, label: str, collect_frontier: bool = True) -> tuple[list[_ScoredState], bool]:
        """Run order and replacement neighborhoods until locally stable or out of budget."""
        frontier: list[_ScoredState] = []
        completed = True
        while evaluations < deadline:
            order_improved, order_completed = ordering_pass(deadline=deadline, label=f"{label}: ordering")
            replace_improved, frontier, replace_completed = replacement_pass(deadline=deadline, label=f"{label}: replacements", collect_frontier=collect_frontier)
            completed = order_completed and replace_completed
            if not completed or not order_improved and not replace_improved:
                break
        return frontier, completed

    def beam_escape(frontier: list[_ScoredState], *, deadline: int, width: int, label: str) -> bool:
        """Expand a second exact move from strong non-improving neighbors to cross two-move valleys."""
        nonlocal baseline
        if width <= 0 or not frontier or evaluations >= deadline:
            return False
        incumbent = best_seen
        if incumbent is None:
            return False
        starts = frontier[:width]
        for start_i, start in enumerate(starts):
            if evaluations >= deadline:
                break
            restore_state(start.state)
            per_start_deadline = min(deadline, evaluations + max((deadline - evaluations) // max(len(starts) - start_i, 1), 1))
            origin = start.state
            for move_i, (index, candidate) in enumerate(round_robin_moves(), start=1):
                restore_state(origin)
                if candidate == names[index] or not legal(candidate, index):
                    continue
                place_candidate(index, candidate)
                if score(deadline=per_start_deadline) is None:
                    break
                if move_i == 1 or move_i % 16 == 0:
                    report(label, 0.72 + 0.12 * evaluations / max(evaluation_budget, 1), best_seen.score if best_seen else baseline)
        if best_seen is None:
            restore_state(incumbent.state)
            baseline = incumbent.score
            return False
        restore_state(best_seen.state)
        improved = best_seen.score > incumbent.score
        baseline = best_seen.score
        return improved

    def diversified_rebuild(frontier: list[_ScoredState], *, deadline: int, variants: int, label: str) -> bool:
        """Deterministically destroy and greedily repair different parts of strong complete builds."""
        nonlocal baseline
        incumbent = best_seen
        if incumbent is None or not frontier or evaluations >= deadline:
            return False
        mutable_mods = [index for index in open_slots if slots[index].kind == "mod" and not slots[index].exilus and not slots[index].stance]
        if len(mutable_mods) < 2:
            return False
        for variant in range(min(variants, len(frontier))):
            if evaluations >= deadline:
                break
            restore_state(frontier[variant].state)
            first = mutable_mods[variant % len(mutable_mods)]
            second = mutable_mods[(variant * 3 + 1) % len(mutable_mods)]
            if second == first:
                second = mutable_mods[(mutable_mods.index(first) + 1) % len(mutable_mods)]
            place_candidate(first, NONE)
            place_candidate(second, NONE)
            local = score(deadline=deadline)
            if local is None:
                break
            baseline = local
            ordered = [second, first]
            greedy_fill(label=f"{label} {variant + 1}/{variants}", progress_start=0.82, progress_span=0.08, slot_order=ordered, deadline=deadline)
        if best_seen is None:
            restore_state(incumbent.state)
            baseline = incumbent.score
            return False
        restore_state(best_seen.state)
        improved = best_seen.score > incumbent.score
        baseline = best_seen.score
        return improved

    def run_quality_search(*, deadline: int, label: str) -> bool:
        """Continue the incumbent through progressively broader deterministic neighborhoods."""
        nonlocal baseline
        if evaluations >= deadline:
            return False
        starting_score = best_seen.score if best_seen else baseline
        remaining = deadline - evaluations
        if active_quality == OPTIMIZE_SEARCH_FAST:
            vnd_deadline = deadline
        elif active_quality == OPTIMIZE_SEARCH_BALANCED:
            vnd_deadline = evaluations + max(int(remaining * 0.68), 1)
        else:
            vnd_deadline = evaluations + max(int(remaining * 0.48), 1)
        frontier, _completed = variable_neighborhood_descent(deadline=vnd_deadline, label=label)
        if active_quality != OPTIMIZE_SEARCH_FAST and evaluations < deadline:
            width = BALANCED_BEAM_WIDTH if active_quality == OPTIMIZE_SEARCH_BALANCED else THOROUGH_BEAM_WIDTH
            beam_deadline = deadline if active_quality == OPTIMIZE_SEARCH_BALANCED else evaluations + max(int((deadline - evaluations) * 0.68), 1)
            beam_escape(frontier, deadline=beam_deadline, width=width, label=f"{label}: two-move beam")
        if active_quality == OPTIMIZE_SEARCH_THOROUGH and evaluations < deadline:
            diversified_rebuild(frontier, deadline=deadline, variants=THOROUGH_REBUILD_VARIANTS, label=f"{label}: rebuild")
        if best_seen is not None:
            restore_state(best_seen.state)
            baseline = best_seen.score
        return baseline > starting_score

    evolution_choices: dict[int, tuple[int, ...]] = {}
    if request.find_optimal_evolutions:
        custom_metadata = None
        if request.custom_weapon:
            try:
                custom_metadata = parse_database_entry(request.custom_weapon_entry, default_name="Custom Weapon", default_type=request.weapon_type.casefold())
            except ValueError:
                custom_metadata = None
        evolution_choices = weapon_evolution_perk_choices(None if request.custom_weapon else request.weapon_name, custom_metadata=custom_metadata)

    def search_evolutions(*, label: str, progress_start: float, progress_span: float, deadline: int) -> bool:
        """Pick Incarnon perks for the current build. Small spaces are exhaustive; large ones use coordinate descent."""
        nonlocal baseline, current_evolutions
        if not evolution_choices or evaluations >= deadline:
            return False
        tiers = sorted(evolution_choices)
        perk_lists = [evolution_choices[tier] for tier in tiers]
        previous = dict(current_evolutions)
        total = 1
        for options in perk_lists:
            total *= max(len(options), 1)

        if total <= EVOLUTION_EXHAUSTIVE_LIMIT:
            best_evolutions = dict(previous)
            previous_score = score(deadline=deadline)
            if previous_score is None:
                return False
            best_dps = previous_score
            for combo_i, combo in enumerate(itertools.product(*perk_lists), start=1):
                trial = {tier: perk for tier, perk in zip(tiers, combo)}
                current_evolutions = trial
                dps = score(deadline=deadline)
                if dps is None:
                    break
                if dps > best_dps:
                    best_dps, best_evolutions = dps, dict(trial)
                if combo_i == 1 or combo_i == total or combo_i % 8 == 0:
                    report(f"{label} ({combo_i}/{total})", progress_start + progress_span * combo_i / max(total, 1), best_dps)
            current_evolutions = best_evolutions
            baseline = best_dps
            return best_evolutions != previous

        # Coordinate descent: optimize one tier at a time. O(passes * sum(choices)) instead of O(product).
        current = {}
        for tier in tiers:
            choices = evolution_choices[tier]
            pick = current_evolutions.get(tier, choices[0])
            current[tier] = pick if pick in choices else choices[0]
        current_evolutions = dict(current)
        best_dps = score(deadline=deadline)
        if best_dps is None:
            current_evolutions = previous
            return False
        steps = max(sum(len(evolution_choices[tier]) for tier in tiers) * EVOLUTION_DESCENT_PASSES, 1)
        step_i = 0
        for pass_i in range(EVOLUTION_DESCENT_PASSES):
            improved = False
            for tier in tiers:
                best_perk = current[tier]
                for perk in evolution_choices[tier]:
                    step_i += 1
                    current_evolutions = {**current, tier: perk}
                    dps = score(deadline=deadline)
                    if dps is None:
                        current_evolutions = dict(current)
                        baseline = best_dps
                        return current != previous
                    if dps > best_dps:
                        best_dps, best_perk, improved = dps, perk, True
                    if step_i == 1 or step_i == steps or step_i % 6 == 0:
                        report(f"{label} ({step_i}/{steps})", progress_start + progress_span * step_i / steps, best_dps)
                if best_perk != current[tier]:
                    current[tier] = best_perk
                    improved = True
                current_evolutions = dict(current)
            if not improved:
                break
        baseline = best_dps
        return current != previous

    # Seed Incarnon perks before greedy fill when requested, so mod choices see the right attack profile.
    if request.find_optimal_evolutions and evolution_choices:
        search_evolutions(label="Incarnon seed", progress_start=0.12, progress_span=0.05, deadline=primary_budget)

    # 3) Greedy fill supplies a fast incumbent shared by every quality profile.
    greedy_fill(label="Greedy fill", progress_start=0.17, progress_span=0.32, deadline=primary_budget, defer_trigger_limited=True)
    optional_phases = int(bool(request.find_optimal_evolutions and evolution_choices)) + int(bool(request.find_optimal_riven))
    initial_search_deadline = primary_budget if not optional_phases else min(primary_budget, evaluations + max(int((primary_budget - evaluations) * 0.55), 1))
    run_quality_search(deadline=initial_search_deadline, label=f"{search_quality} search")

    # 4) Revisit Incarnon perks after the first complete build, then refine mods again later.
    evolution_note = ""
    evolutions_optimized = False
    if request.find_optimal_evolutions:
        if not evolution_choices:
            evolution_note = " No Incarnon evolutions available."
        else:
            remaining_after_core = max(primary_budget - evaluations, 0)
            evolution_deadline = min(primary_budget, evaluations + max(int(remaining_after_core * (0.35 if request.find_optimal_riven else 0.50)), 1))
            search_evolutions(label="Incarnon search", progress_start=0.65, progress_span=0.06, deadline=evolution_deadline)
            evolutions_optimized = True
            picks = ", ".join(f"E{tier}:P{perk}" for tier, perk in sorted(current_evolutions.items()))
            evolution_note = f" Best-found Incarnon ({picks})."

    riven_note = ""
    if request.find_optimal_riven:
        riven_remaining = max(primary_budget - evaluations, 0)
        riven_deadline = min(primary_budget, evaluations + max(int(riven_remaining * 0.78), 1))
        targets = [i for i in open_slots if slots[i].kind == "mod" and not slots[i].exilus and not slots[i].stance]
        ordered_targets = []
        for group in (
            [i for i in targets if names[i] == RIVEN],
            [i for i in targets if names[i] == NONE],
            [i for i in targets if names[i] not in {RIVEN, NONE}],
        ):
            for index in group:
                if index not in ordered_targets:
                    ordered_targets.append(index)
        if not ordered_targets:
            riven_note = " No open mod slot for Riven search."
        elif not request.riven_base_stats:
            riven_note = " Missing Riven base stats."
        else:
            for i in open_slots:
                if names[i] == RIVEN:
                    place(i, NONE, policy=SLOT_POLICY_DISCARD, fields={})
            without_riven_score = score(deadline=riven_deadline)
            if without_riven_score is not None:
                baseline = without_riven_score
            saved_slots = {i: (names[i], ranks[i], stacks_list[i], dict(riven_fields[i]), rolls[i]) for i in ordered_targets}

            def restore_targets() -> None:
                for index, saved in saved_slots.items():
                    place(index, saved[0], policy=SLOT_POLICY_DISCARD, rank=saved[1], stacks=saved[2], fields=saved[3], roll=saved[4])

            # Discover Riven rolls once on the cheapest seat (empty/existing Riven, else weakest mod).
            seat_candidates = [i for i in ordered_targets if saved_slots[i][0] in {NONE, RIVEN}]
            if seat_candidates:
                seat = seat_candidates[0]
            else:
                # Weakest mod = removing it hurts least = highest score with that slot cleared.
                weakest, best_cleared = ordered_targets[0], -1.0
                for index in ordered_targets:
                    saved = saved_slots[index]
                    place(index, NONE, policy=SLOT_POLICY_DISCARD, fields={})
                    cleared = score(deadline=riven_deadline)
                    place(index, saved[0], policy=SLOT_POLICY_DISCARD, rank=saved[1], stacks=saved[2], fields=saved[3], roll=saved[4])
                    if cleared is None:
                        break
                    if cleared > best_cleared:
                        weakest, best_cleared = index, cleared
                seat = weakest

            def greedy_riven(roll_name: str, *, progress_start: float, progress_span: float, deadline: int) -> dict[str, float]:
                pos_count, neg_count, _b, _m = RIVEN_ROLL_CONFIGS[roll_name]
                chosen: list[tuple[str, float]] = []
                used: set[str] = set()
                stats = [stat for stat in request.riven_base_stats if stat not in request.excluded_riven_stats]
                total_picks = max(pos_count + neg_count, 1)
                pick_i = 0
                for negative in (False, True):
                    need = neg_count if negative else pos_count
                    for _ in range(need):
                        pick, pick_dps = None, -1.0
                        for stat in stats:
                            if stat in used:
                                continue
                            if negative and stat in request.riven_non_negative:
                                continue
                            limits = riven_field_limits(request.riven_base_stats, request.riven_disposition, roll_name, stat, negative, request.riven_non_negative)
                            if limits is None:
                                continue
                            # Positives: max roll. Negatives: least harmful roll only.
                            value = limits[1]
                            trial = {**dict(chosen), stat: value}
                            place(seat, RIVEN, policy=SLOT_POLICY_DISCARD, roll=roll_name, fields=trial)
                            dps = score(deadline=deadline)
                            if dps is None:
                                break
                            if dps > pick_dps:
                                pick, pick_dps = (stat, value), dps
                        pick_i += 1
                        report(f"Riven search ({roll_name})", progress_start + progress_span * pick_i / total_picks, pick_dps if pick is not None else baseline)
                        if pick is None:
                            break
                        chosen.append(pick)
                        used.add(pick[0])
                return dict(chosen)

            restore_targets()
            place(seat, NONE, policy=SLOT_POLICY_DISCARD, fields={})
            roll_rivens: list[tuple[str, dict[str, float]]] = []
            n_rolls = max(len(RIVEN_ROLL_OPTIONS), 1)
            for roll_i, roll_name in enumerate(RIVEN_ROLL_OPTIONS):
                roll_start = 0.76 + 0.10 * roll_i / n_rolls
                roll_span = 0.10 / n_rolls
                fields = greedy_riven(roll_name, progress_start=roll_start, progress_span=roll_span, deadline=riven_deadline)
                if fields:
                    roll_rivens.append((roll_name, fields))
                if evaluations >= riven_deadline:
                    break
            restore_targets()

            # Test each discovered Riven in every open mod slot (cheap: one score each).
            best_dps, best_target, best_roll, best_fields = baseline, None, "", {}
            checks = max(len(roll_rivens) * len(ordered_targets), 1)
            check_i = 0
            for roll_name, fields in roll_rivens:
                for target in ordered_targets:
                    check_i += 1
                    restore_targets()
                    place(target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=roll_name, fields=fields)
                    dps = score(deadline=riven_deadline)
                    if dps is None:
                        break
                    if check_i == 1 or check_i == checks or check_i % 3 == 0:
                        report(f"Riven slot check ({check_i}/{checks})", 0.86 + 0.08 * check_i / checks, best_dps)
                    if dps > best_dps:
                        best_dps, best_target, best_roll, best_fields = dps, target, roll_name, fields
                if evaluations >= riven_deadline:
                    break
            restore_targets()
            if best_target is not None and best_fields:
                place(best_target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=best_roll, fields=best_fields)
                baseline = best_dps
                riven_note = f" Best-found Riven on {SLOT_CONFIGS[best_target]['label']} ({best_roll})."
            else:
                riven_note = " Riven search found no improvement over the mods it would replace."
            # Riven can change both Incarnon perks and the best surrounding mods.
            if request.find_optimal_evolutions and evolution_choices:
                if search_evolutions(label="Incarnon after Riven", progress_start=0.94, progress_span=0.02, deadline=primary_budget):
                    picks = ", ".join(f"E{tier}:P{perk}" for tier, perk in sorted(current_evolutions.items()))
                    evolution_note = f" Best-found Incarnon ({picks})."
                    evolutions_optimized = True

    # Spend any reserved budget refining the build around the final Riven/evolution context.
    while evaluations < primary_budget:
        before = best_seen.score if best_seen else baseline
        evolution_changed = False
        if request.find_optimal_evolutions and evolution_choices:
            evolution_refine_deadline = min(primary_budget, evaluations + max(int((primary_budget - evaluations) * 0.25), 1))
            evolution_changed = search_evolutions(label="Final Incarnon refinement", progress_start=0.95, progress_span=0.01, deadline=evolution_refine_deadline)
        build_changed = run_quality_search(deadline=primary_budget, label="Final refinement")
        if not evolution_changed and not build_changed or best_seen is None or best_seen.score <= before:
            break

    # Thorough is a strict continuation of the complete Balanced search. Expanding
    # the pools only after that incumbent exists guarantees it cannot regress.
    if search_quality == OPTIMIZE_SEARCH_THOROUGH and evaluations < evaluation_budget:
        active_quality = OPTIMIZE_SEARCH_THOROUGH
        mod_pool = list(full_mod_pool)
        stance_pool = list(full_stance_pool)
        exilus_pool = list(full_exilus_pool)
        arcane_pool = list(full_arcane_pool)
        run_quality_search(deadline=evaluation_budget, label="Thorough full-pool search")
        if request.find_optimal_evolutions and evolution_choices and evaluations < evaluation_budget:
            search_evolutions(label="Thorough Incarnon refinement", progress_start=0.96, progress_span=0.01, deadline=evaluation_budget)
            run_quality_search(deadline=evaluation_budget, label="Thorough final refinement")

    if best_seen is None:
        raise RuntimeError("Optimizer did not produce a scored build.")
    restore_state(best_seen.state)
    baseline = best_seen.score
    final_dps = best_seen.score
    report("Finishing…", 0.99, final_dps)
    filled = sum(1 for name in names if name != NONE)
    stance_name = equipped_stance_name()
    stance_note = f" Stance {stance_name}." if request.weapon_type == "Melee" and stance_name not in {NONE, CUSTOM, RIVEN} else ""
    termination_reason = "evaluation budget reached" if evaluations >= evaluation_budget or budget_limited else "local optimum reached"
    return OptimizeResult(
        slot_names=names, slot_ranks=ranks, slot_stacks=stacks_list, slot_policies=policies,
        riven_rolls=rolls, riven_fields=riven_fields, custom_entries=customs,
        total_dps=final_dps, evaluations=evaluations,
        message=f"{search_quality} search · {termination_reason} | Best found: {filled} slots | {evaluations} evaluations | {final_dps:,.1f} {maximize_label}.{riven_note}{evolution_note}{stance_note}",
        evolutions=dict(current_evolutions), evolutions_optimized=evolutions_optimized,
        search_quality=search_quality, termination_reason=termination_reason,
    )
