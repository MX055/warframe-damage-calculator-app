from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Iterable

from warframe_damage_calculator import Build, Upgrade

from .constants import (
    NO_EFFECT,
    RIVEN_NON_NEGATIVE_STATS,
    RIVEN_ROLL_CONFIGS,
    RIVEN_ROLL_OPTIONS,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP,
    SLOT_POLICY_KEEP_IN_SLOT,
)
from .data import (
    database_max_stacks,
    database_rank_bounds,
    database_upgrade,
    raw_upgrade_metadata,
    upgrade_conflicts_with_selected,
    upgrade_names_for_ui,
)
from .engine import build_upgrade, configured_weapon, custom_upgrade_from_entry, is_non_empty_upgrade, progenitor_upgrade

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
CANDIDATE_SOFT_CAP = 150
CANDIDATE_SHORTLIST_LIMIT = 24
CANDIDATE_PER_STAT_LIMIT = 2
CANDIDATE_RAW_STAT_LIMIT = 2
HILL_CLIMB_SWAP_LIMIT = 60

ProgressCallback = Callable[[str, float, int, float | None], None]  # phase, fraction 0-1, evaluations, best_dps


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
    progenitor_element: str
    progenitor_value: float
    external_fields: dict[str, float]
    slots: list[SlotSpec]
    find_optimal_riven: bool
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
    return Upgrade({"name": NONE, "type": kind, "stats": {}})


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

    evaluations = 0

    def report(phase: str, fraction: float, best: float | None = None):
        if progress:
            progress(phase, max(0.0, min(1.0, fraction)), evaluations, best)

    report("Preparing…", 0.0)

    weapon_filter_name = None if request.custom_weapon else request.weapon_name
    excluded_upgrades = set(request.excluded_upgrades)
    mod_pool = [name for name in _cap_candidates(upgrade_names_for_ui(request.weapon_category, weapon_filter_name, request.attack_mode, True, False, False)) if name not in excluded_upgrades]
    exilus_pool = [name for name in _cap_candidates(upgrade_names_for_ui(request.weapon_category, weapon_filter_name, request.attack_mode, True, False, True)) if name not in excluded_upgrades]
    arcane_pool = [name for name in _cap_candidates(upgrade_names_for_ui(request.weapon_category, weapon_filter_name, request.attack_mode, False, True, False)) if name not in excluded_upgrades]

    n = len(slots)
    names = [NONE for _ in range(n)]
    ranks = [0 for _ in range(n)]
    stacks_list = [0 for _ in range(n)]
    policies = [SLOT_POLICY_DISCARD for _ in range(n)]
    rolls = [slot.riven_roll for slot in slots]
    riven_fields = [{} for _ in range(n)]
    customs = [slot.custom_entry for slot in slots]

    progenitor = progenitor_upgrade(request.progenitor_element, request.progenitor_value, NO_EFFECT)
    external = build_upgrade("External Buffs", dict(request.external_fields))
    optimizer_weapon = configured_weapon(
        request.weapon_type, request.weapon_name, custom_weapon=request.custom_weapon, base_stats={}, upgrades=[],
        custom_entry=request.custom_weapon_entry if request.custom_weapon else None,
        selected_mode=request.attack_mode or None, evolutions=request.evolutions or None,
    )
    optimizer_build = Build()
    optimizer_weapon.build = optimizer_build
    empty_upgrades = {kind: _empty_upgrade(kind) for kind in {slot.kind for slot in slots}}
    upgrade_cache: dict[tuple[str, str, int, int, bool], Upgrade] = {}
    runtime_cache: dict[tuple[str, str], tuple[int, int]] = {}
    score_cache: dict[tuple, float] = {}

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

    def score() -> float:
        nonlocal evaluations
        key = (
            tuple(names), tuple(ranks), tuple(stacks_list), tuple(rolls),
            tuple(tuple(sorted(fields.items())) for fields in riven_fields), tuple(customs),
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
        optimizer_weapon.results.resolve(validate_cycles=False)
        result = float(optimizer_weapon.results.main.final.total_dps)
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

    # Open slots: not keep / keep-in-slot (includes None and discard).
    open_slots = [i for i in range(n) if policies[i] not in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT}]
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
        (mod_pool, [i for i in open_slots if slots[i].kind == "mod" and not slots[i].exilus]),
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
        return retained

    mod_pool = shortlist(mod_pool, pool_groups[0][1])
    exilus_pool = shortlist(exilus_pool, pool_groups[1][1])
    arcane_pool = shortlist(arcane_pool, pool_groups[2][1])
    report("Candidates ready", 0.15, baseline)

    # 3) Greedy fill open slots by best ΔDPS.
    n_open = max(len(open_slots), 1)
    for fill_i, index in enumerate(open_slots):
        best_name, best_dps, best_rank, best_stacks = names[index], baseline, ranks[index], stacks_list[index]
        prev = names[index], ranks[index], stacks_list[index], dict(riven_fields[index]), rolls[index], customs[index]
        # Also try leaving empty / keeping current.
        for candidate in pool_for(index):
            if not legal(candidate, index):
                continue
            max_rank, max_stacks = max_runtime(candidate, slots[index].kind)
            place(index, candidate, policy=SLOT_POLICY_DISCARD, rank=max_rank, stacks=max_stacks, fields={}, custom=customs[index])
            dps = score()
            if dps > best_dps:
                best_name, best_dps, best_rank, best_stacks = candidate, dps, max_rank, max_stacks
        place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2], fields=prev[3], roll=prev[4], custom=prev[5])
        if best_dps > baseline:
            place(index, best_name, policy=SLOT_POLICY_DISCARD, rank=best_rank, stacks=best_stacks, fields={})
            baseline = best_dps
        report(f"Greedy fill ({fill_i + 1}/{len(open_slots)})", 0.15 + 0.50 * (fill_i + 1) / n_open, baseline)

    # 4) Local 1-swap hill climb.
    swaps, improved, last_report_swaps = 0, True, -20
    while improved and swaps < HILL_CLIMB_SWAP_LIMIT:
        improved = False
        for index in open_slots:
            if swaps >= HILL_CLIMB_SWAP_LIMIT:
                break
            current = names[index]
            for candidate in pool_for(index):
                if swaps >= HILL_CLIMB_SWAP_LIMIT:
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
                    report("Hill climb…", 0.65 + 0.15 * swaps / HILL_CLIMB_SWAP_LIMIT, baseline)
                    last_report_swaps = swaps
                    break
                if swaps - last_report_swaps >= 20:
                    report("Hill climb…", 0.65 + 0.15 * swaps / HILL_CLIMB_SWAP_LIMIT, baseline)
                    last_report_swaps = swaps
                place(index, prev[0], policy=SLOT_POLICY_DISCARD, rank=prev[1], stacks=prev[2])
            if improved:
                break

    riven_note = ""
    if request.find_optimal_riven:
        targets = [i for i in open_slots if slots[i].kind == "mod" and not slots[i].exilus]
        preferred = [i for i in targets if names[i] == RIVEN] or [i for i in targets if names[i] == NONE] or targets
        if not preferred:
            riven_note = " No open mod slot for Riven search."
        elif not request.riven_base_stats:
            riven_note = " Missing Riven base stats."
        else:
            target = preferred[0]
            for i in open_slots:
                if i != target and names[i] == RIVEN:
                    place(i, NONE, policy=SLOT_POLICY_DISCARD, fields={})
            best_dps, best_roll, best_fields = baseline, rolls[target], {}
            saved = names[target], ranks[target], stacks_list[target], dict(riven_fields[target]), rolls[target]
            n_rolls = max(len(RIVEN_ROLL_OPTIONS), 1)
            for roll_i, roll_name in enumerate(RIVEN_ROLL_OPTIONS):
                report(f"Riven search ({roll_i + 1}/{n_rolls})", 0.80 + 0.18 * (roll_i + 1) / n_rolls, best_dps)
                pos_count, neg_count, _b, _m = RIVEN_ROLL_CONFIGS[roll_name]
                chosen: list[tuple[str, float]] = []
                used: set[str] = set()
                for _ in range(pos_count):
                    pick, pick_dps = None, -1.0
                    for stat in request.riven_base_stats:
                        if stat in used or stat in request.excluded_riven_stats:
                            continue
                        limits = riven_field_limits(request.riven_base_stats, request.riven_disposition, roll_name, stat, False, request.riven_non_negative)
                        if limits is None:
                            continue
                        for value in (limits[1], limits[0]):
                            trial = {**dict(chosen), stat: value}
                            place(target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=roll_name, fields=trial)
                            dps = score()
                            if dps > pick_dps:
                                pick, pick_dps = (stat, value), dps
                    if pick is None:
                        break
                    chosen.append(pick)
                    used.add(pick[0])
                for _ in range(neg_count):
                    pick, pick_dps = None, -1.0
                    for stat in request.riven_base_stats:
                        if stat in used or stat in request.riven_non_negative or stat in request.excluded_riven_stats:
                            continue
                        limits = riven_field_limits(request.riven_base_stats, request.riven_disposition, roll_name, stat, True, request.riven_non_negative)
                        if limits is None:
                            continue
                        for value in (limits[0], limits[1]):
                            trial = {**dict(chosen), stat: value}
                            place(target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=roll_name, fields=trial)
                            dps = score()
                            if dps > pick_dps:
                                pick, pick_dps = (stat, value), dps
                    if pick is None:
                        break
                    chosen.append(pick)
                    used.add(pick[0])
                fields = dict(chosen)
                place(target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=roll_name, fields=fields)
                dps = score()
                if dps > best_dps:
                    best_dps, best_roll, best_fields = dps, roll_name, fields
            if best_fields:
                place(target, RIVEN, policy=SLOT_POLICY_DISCARD, roll=best_roll, fields=best_fields)
                baseline = best_dps
                riven_note = f" Optimal Riven on slot {target + 1} ({best_roll})."
            else:
                place(target, saved[0], policy=SLOT_POLICY_DISCARD, rank=saved[1], stacks=saved[2], fields=saved[3], roll=saved[4])
                riven_note = " Riven search found no improvement."

    final_dps = score()
    report("Finishing…", 0.99, final_dps)
    filled = sum(1 for name in names if name != NONE)
    return OptimizeResult(
        slot_names=names, slot_ranks=ranks, slot_stacks=stacks_list, slot_policies=policies,
        riven_rolls=rolls, riven_fields=riven_fields, custom_entries=customs,
        total_dps=final_dps, evaluations=evaluations,
        message=f"Optimized {filled} slots | {evaluations} evaluations | {final_dps:,.1f} DPS.{riven_note}",
    )
