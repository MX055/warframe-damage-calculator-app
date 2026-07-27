from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Iterable

from warframe_damage_calculator import Build, Upgrade

from .constants import (
    BALANCED_MAXIMIZE_TARGETS,
    DEFAULT_OPTIMIZE_MAXIMIZE,
    INITIAL_COMBO_RUNTIME,
    NO_EFFECT,
    OPTIMIZE_MAXIMIZE_TARGETS,
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
    "fire_rate", "attack_speed", "weakpoint_damage", "reload_speed", "magazine_capacity",
    "ammo_efficiency", "flat_crit_chance", "multiplicative_crit_chance", "flat_crit_damage",
    "multiplicative_base_damage", "multiplicative_fire_rate", "hunter_munitions", "internal_bleeding",
    "primed_chamber", "vigilante_bonus", "impact", "puncture", "slash", "cold", "electricity",
    "heat", "toxin", "blast", "corrosive", "gas", "magnetic", "radiation", "viral", "void",
    "corpus_damage", "grineer_damage", "infested_damage", "orokin_damage", "murmur_damage",
    "sentient_damage", "secondary_enervate", "secondary_encumber", "melee_duplicate", "melee_doughty",
}
CANDIDATE_SOFT_CAP = 72
CANDIDATE_SHORTLIST_LIMIT = 24
CANDIDATE_SHORTLIST_HARD_CAP = 36
CANDIDATE_PER_STAT_LIMIT = 2
CANDIDATE_RAW_STAT_LIMIT = 2
HILL_CLIMB_SWAP_LIMIT = 40
EVOLUTION_REFINE_HILL_LIMIT = 20
EVOLUTION_EXHAUSTIVE_LIMIT = 36
EVOLUTION_DESCENT_PASSES = 2

ProgressCallback = Callable[[str, float, int, float | None], None]  # phase, fraction 0-1, evaluations, best_score
MAXIMIZE_TARGET_ATTRS = frozenset(OPTIMIZE_MAXIMIZE_TARGETS.values())
MAXIMIZE_TARGET_LABELS = {attr: label for label, attr in OPTIMIZE_MAXIMIZE_TARGETS.items()}


def score_maximize_target(final, maximize_target: str, weakpoint_weight: float = 0.5) -> float:
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
        weight = min(max(float(weakpoint_weight), 0.0), 1.0)
        if weight <= 0:
            return normal_score
        if weight >= 1:
            return weakpoint_score
        if normal_score <= 0 or weakpoint_score <= 0:
            return 0.0
        return normal_score ** (1.0 - weight) * weakpoint_score ** weight
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
    stance_combo: str = "neutral"
    ability_strength: float | None = None
    excluded_upgrades: set[str] = field(default_factory=set)
    excluded_riven_stats: set[str] = field(default_factory=set)
    riven_disposition: float = 1.0
    riven_base_stats: dict[str, float] = field(default_factory=dict)
    riven_non_negative: set[str] = field(default_factory=lambda: set(RIVEN_NON_NEGATIVE_STATS))


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


def _has_damage_stats(name: str) -> bool:
    return any(stat in DAMAGE_RELATED_STATS for stat in (raw_upgrade_metadata(name).get("stats") or {}))


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

    evaluations = 0

    def report(phase: str, fraction: float, best: float | None = None):
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
        capped = list(names) if stance_only else _cap_candidates(names)
        return [name for name in capped if name not in excluded_upgrades]

    mod_pool = upgrade_pool(True, False, False)
    stance_pool = upgrade_pool(True, False, False, stance_only=True) if request.weapon_type == "Melee" else []
    exilus_pool = upgrade_pool(True, False, True)
    arcane_pool = upgrade_pool(False, True, False)

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

    def score() -> float:
        nonlocal evaluations
        key = (
            tuple(names), tuple(ranks), tuple(stacks_list), tuple(rolls),
            tuple(tuple(sorted(fields.items())) for fields in riven_fields), tuple(customs),
            tuple(sorted(current_evolutions.items())),
        )
        if key in score_cache:
            return score_cache[key]
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
        result = score_maximize_target(optimizer_weapon.results.main.final, maximize_target, request.weakpoint_weight)
        score_cache[key] = result
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
                ranked.append((score(), candidate))
            screening_done += 1
            if screening_done % 8 == 0:
                report("Screening candidates...", 0.05 + 0.10 * screening_done / max(screening_total, 1), baseline)
        place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2], fields=prev[3], roll=prev[4], custom=prev[5])
        ranked.sort(key=lambda item: (-item[0], item[1].casefold()))
        retained = [name for _dps, name in ranked[:CANDIDATE_SHORTLIST_LIMIT]]
        for stat in DAMAGE_RELATED_STATS:
            matching = [name for _dps, name in ranked if stat in (raw_upgrade_metadata(name).get("stats") or {})]
            for name in matching[:CANDIDATE_PER_STAT_LIMIT]:
                if name not in retained:
                    retained.append(name)
            def raw_strength(name: str) -> float:
                effects = (raw_upgrade_metadata(name).get("stats") or {}).get(stat, [])
                values = [effect.get("value", 0) if isinstance(effect, dict) else effect for effect in (effects if isinstance(effects, list) else [effects])]
                return max((float(value) for value in values if isinstance(value, (int, float)) and not isinstance(value, bool)), default=0.0)
            by_strength = sorted(matching, key=lambda name: (-raw_strength(name), name.casefold()))
            for name in by_strength[:CANDIDATE_RAW_STAT_LIMIT]:
                if name not in retained:
                    retained.append(name)
        for i in indices:
            if names[i] not in {NONE, CUSTOM, RIVEN} and names[i] not in retained:
                retained.append(names[i])
        return retained[:CANDIDATE_SHORTLIST_HARD_CAP]

    mod_pool = shortlist(mod_pool, pool_groups[0][1])
    stance_pool = shortlist(stance_pool, pool_groups[1][1])
    exilus_pool = shortlist(exilus_pool, pool_groups[2][1])
    arcane_pool = shortlist(arcane_pool, pool_groups[3][1])
    report("Candidates ready", 0.12, baseline)

    def hill_climb(*, label: str, swap_limit: int, progress_start: float, progress_span: float) -> None:
        nonlocal baseline
        swaps, improved, last_report_swaps = 0, True, -8
        while improved and swaps < swap_limit:
            improved = False
            for index in open_slots:
                if swaps >= swap_limit:
                    break
                current = names[index]
                for candidate in pool_for(index):
                    if swaps >= swap_limit:
                        break
                    if candidate == current or not legal(candidate, index):
                        continue
                    prev = names[index], ranks[index], stacks_list[index]
                    max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
                    place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks)
                    dps = score()
                    swaps += 1
                    if dps > baseline:
                        baseline, improved = dps, True
                        report(label, progress_start + progress_span * swaps / max(swap_limit, 1), baseline)
                        last_report_swaps = swaps
                        break
                    if swaps - last_report_swaps >= 8:
                        report(label, progress_start + progress_span * swaps / max(swap_limit, 1), baseline)
                        last_report_swaps = swaps
                    place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2])
                if improved:
                    break
        report(label, progress_start + progress_span, baseline)

    def greedy_fill(*, label: str, progress_start: float, progress_span: float) -> None:
        nonlocal baseline
        n_open = max(len(open_slots), 1)
        for fill_i, index in enumerate(open_slots):
            best_name, best_dps, best_rank, best_stacks = names[index], baseline, ranks[index], stacks_list[index]
            prev = names[index], ranks[index], stacks_list[index], dict(riven_fields[index]), rolls[index], customs[index]
            pool = pool_for(index)
            pool_n = max(len(pool), 1)
            for candidate_i, candidate in enumerate(pool, start=1):
                if not legal(candidate, index):
                    continue
                max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
                place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks, fields={}, custom=customs[index])
                dps = score()
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

    evolution_choices: dict[int, tuple[int, ...]] = {}
    if request.find_optimal_evolutions:
        custom_metadata = None
        if request.custom_weapon:
            try:
                custom_metadata = parse_database_entry(request.custom_weapon_entry, default_name="Custom Weapon", default_type=request.weapon_type.casefold())
            except ValueError:
                custom_metadata = None
        evolution_choices = weapon_evolution_perk_choices(None if request.custom_weapon else request.weapon_name, custom_metadata=custom_metadata)

    def search_evolutions(*, label: str, progress_start: float, progress_span: float) -> bool:
        """Pick Incarnon perks for the current build. Small spaces are exhaustive; large ones use coordinate descent."""
        nonlocal baseline, current_evolutions
        if not evolution_choices:
            return False
        tiers = sorted(evolution_choices)
        perk_lists = [evolution_choices[tier] for tier in tiers]
        previous = dict(current_evolutions)
        total = 1
        for options in perk_lists:
            total *= max(len(options), 1)

        if total <= EVOLUTION_EXHAUSTIVE_LIMIT:
            best_evolutions: dict[int, int] = {}
            best_dps = -1.0
            for combo_i, combo in enumerate(itertools.product(*perk_lists), start=1):
                trial = {tier: perk for tier, perk in zip(tiers, combo)}
                current_evolutions = trial
                dps = score()
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
        best_dps = score()
        steps = max(sum(len(evolution_choices[tier]) for tier in tiers) * EVOLUTION_DESCENT_PASSES, 1)
        step_i = 0
        for pass_i in range(EVOLUTION_DESCENT_PASSES):
            improved = False
            for tier in tiers:
                best_perk = current[tier]
                for perk in evolution_choices[tier]:
                    step_i += 1
                    current_evolutions = {**current, tier: perk}
                    dps = score()
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
        search_evolutions(label="Incarnon seed", progress_start=0.12, progress_span=0.05)

    # 3) Greedy fill open slots by best ΔDPS.
    greedy_fill(label="Greedy fill", progress_start=0.17, progress_span=0.38)
    # 4) Local 1-swap hill climb.
    hill_climb(label="Hill climb…", swap_limit=HILL_CLIMB_SWAP_LIMIT, progress_start=0.55, progress_span=0.10)

    # 5) One Incarnon pass after mods settle — avoid stacked refine loops.
    evolution_note = ""
    evolutions_optimized = False
    if request.find_optimal_evolutions:
        if not evolution_choices:
            evolution_note = " No Incarnon evolutions available."
        else:
            changed = search_evolutions(label="Incarnon search", progress_start=0.65, progress_span=0.06)
            if changed:
                hill_climb(label="Refine mods…", swap_limit=EVOLUTION_REFINE_HILL_LIMIT, progress_start=0.71, progress_span=0.05)
            evolutions_optimized = True
            picks = ", ".join(f"E{tier}:P{perk}" for tier, perk in sorted(current_evolutions.items()))
            evolution_note = f" Optimal Incarnon ({picks})."

    riven_note = ""
    if request.find_optimal_riven:
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
            baseline = score()
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
                    cleared = score()
                    place(index, saved[0], policy=SLOT_POLICY_DISCARD, rank=saved[1], stacks=saved[2], fields=saved[3], roll=saved[4])
                    if cleared > best_cleared:
                        weakest, best_cleared = index, cleared
                seat = weakest

            def greedy_riven(roll_name: str, *, progress_start: float, progress_span: float) -> dict[str, float]:
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
                            dps = score()
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
                fields = greedy_riven(roll_name, progress_start=roll_start, progress_span=roll_span)
                if fields:
                    roll_rivens.append((roll_name, fields))
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
                    dps = score()
                    if check_i == 1 or check_i == checks or check_i % 3 == 0:
                        report(f"Riven slot check ({check_i}/{checks})", 0.86 + 0.08 * check_i / checks, best_dps)
                    if dps > best_dps:
                        best_dps, best_target, best_roll, best_fields = dps, target, roll_name, fields
            restore_targets()
            if best_target is not None and best_fields:
                place(best_target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=best_roll, fields=best_fields)
                baseline = best_dps
                riven_note = f" Optimal Riven on {SLOT_CONFIGS[best_target]['label']} ({best_roll})."
            else:
                riven_note = " Riven search found no improvement over the mods it would replace."
            # Riven can change which Incarnon perks are best — one quick pass, no extra hill climb.
            if request.find_optimal_evolutions and evolution_choices:
                if search_evolutions(label="Incarnon after Riven", progress_start=0.94, progress_span=0.04):
                    picks = ", ".join(f"E{tier}:P{perk}" for tier, perk in sorted(current_evolutions.items()))
                    evolution_note = f" Optimal Incarnon ({picks})."
                    evolutions_optimized = True

    final_dps = score()
    report("Finishing…", 0.99, final_dps)
    filled = sum(1 for name in names if name != NONE)
    stance_name = equipped_stance_name()
    stance_note = f" Stance {stance_name}." if request.weapon_type == "Melee" and stance_name not in {NONE, CUSTOM, RIVEN} else ""
    return OptimizeResult(
        slot_names=names, slot_ranks=ranks, slot_stacks=stacks_list, slot_policies=policies,
        riven_rolls=rolls, riven_fields=riven_fields, custom_entries=customs,
        total_dps=final_dps, evaluations=evaluations,
        message=f"Optimized {filled} slots | {evaluations} evaluations | {final_dps:,.1f} {maximize_label}.{riven_note}{evolution_note}{stance_note}",
        evolutions=dict(current_evolutions), evolutions_optimized=evolutions_optimized,
    )
