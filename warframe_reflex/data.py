from __future__ import annotations

import copy
import json
import sys
from functools import lru_cache
from pathlib import Path

import warframe_damage_calculator
from warframe_damage_calculator import Enemy, Upgrade, arsenal
from warframe_damage_calculator.utils.constants import HEAVY_ATTACK_CATEGORIES, SLIDE_ATTACK_CATEGORIES

from .constants import WEAPON_CATEGORY_TYPES, WEAPON_COMPATIBILITY_FAMILIES, WEAPON_TYPES

ATTACK_BOUND_STANCE_COMBOS = frozenset({"heavy", "slide", "slam"})
FREE_STANCE_COMBO_OPTIONS = (
    "neutral",
    "forward",
    "forward_block",
    "block",
    "aerial",
    "wall",
    "finisher",
)

AUTOMATIC_CONDITIONS = {
    "primary", "rifle", "bow", "shotgun", "sniper", "secondary", "pistol",
    "melee", "sacrificial set",
}

FACTION_DAMAGE_STATS = {"corpus damage", "corrupted damage", "grineer damage", "infested damage", "murmur damage", "narmer damage", "orokin damage", "sentient damage"}

EXTERNAL_ACTIVATION_UPGRADES_WITHOUT_DATABASE_CONDITIONS = {"Melee Careen", "Melee Retaliation", "Secondary Kinship", "Secondary Surge"}

WEAPON_ACTIVATED_CONDITIONS = {
    "cold proc", "cold status effect", "consecutive throw", "downed enemy", "each tendril active", "health drain", "hit", "kill", "no enemies within 10m",
    "on 2 hits within 0 02s", "on 2 hits within 0 2s", "on 4 hits within 0 05s", "on 5 pellet headshot", "on alt fire", "on cold status effect",
    "on combined status at 10 stacks", "on critical hit", "on damaging enemies with heat", "on direct hit", "on electricity status effect", "on full charge",
    "on headshot", "on headshot kill", "on headshot kill on eximus", "on heat status effect", "on hit", "on kill", "on orb strike", "on proc", "on pull",
    "on status effect", "on toxin status effect", "on weak point hits with primary fire", "stacks", "status type", "target 15m", "weak point hit",
    "weak point kill",
}


def type_query_for_weapon_type(weapon_type_name: str) -> str:
    return {"Primary": "primary", "Secondary": "secondary", "Melee": "melee"}[weapon_type_name]


def normalized_database_key(value: object) -> str:
    return " ".join(str(value or "").casefold().replace("_", " ").replace("-", " ").split())


def is_faction_damage_stat(stat_name: str) -> bool:
    return normalized_database_key(stat_name) in FACTION_DAMAGE_STATS


@lru_cache(maxsize=1)
def raw_database() -> dict:
    """Load the v0.8 canonical database without constructing calculator objects."""
    project_root = Path(__file__).resolve().parents[1]
    package_root = Path(warframe_damage_calculator.__file__).resolve().parent
    candidates = (
        project_root / "database" / "database.json",
        package_root / "database" / "database.json",
        package_root.parent / "database" / "database.json",
        Path(sys.prefix) / "database" / "database.json",
    )
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
    return {}


def raw_weapons_database() -> dict:
    return raw_database().get("weapons", {}) or {}


def raw_upgrades_database() -> dict:
    return raw_database().get("upgrades", {}) or {}


def raw_enemies_database() -> dict:
    return raw_database().get("enemies", {}) or {}


def raw_riven_stats_database() -> dict:
    return raw_database().get("riven_stats", {}) or {}


def raw_weapon_metadata(_weapon_type_name: str, weapon_name: str | None) -> dict:
    if not weapon_name or normalized_database_key(weapon_name) in {"custom", "none"}:
        return {}
    return raw_weapons_database().get(weapon_name, {}) or {}


def raw_upgrade_metadata(upgrade_name: str, *, kind: str | None = None) -> dict:
    metadata = raw_upgrades_database().get(upgrade_name, {}) or {}
    return metadata if not kind or metadata.get("type") == kind else {}


def raw_enemy_metadata(enemy_name: str | None) -> dict:
    if not enemy_name or normalized_database_key(enemy_name) in {"custom", "none"}:
        return {}
    return raw_enemies_database().get(enemy_name, {}) or {}


def iter_upgrade_effects(metadata: dict):
    """Yield v0.8 effects as ``(stat, value, condition, stacking)``."""
    stats = metadata.get("stats") or {}
    for stat, effects in (stats.items() if isinstance(stats, dict) else ()):
        for effect in effects if isinstance(effects, list) else [effects]:
            if isinstance(effect, dict) and "value" in effect:
                stack = effect.get("stacks")
                stacking = isinstance(stack, dict)
                condition = stack.get("when") if stacking else effect.get("when")
                yield stat, effect["value"], condition, stacking
            else:
                yield stat, effect, None, False


def upgrade_conditions(metadata: dict, *, include_stacking: bool = True) -> list[str]:
    return [
        condition
        for _stat, _value, condition, stacking in iter_upgrade_effects(metadata)
        if isinstance(condition, str) and (include_stacking or not stacking)
    ]


@lru_cache(maxsize=None)
def optimizer_excludes_upgrade_by_default(upgrade_name: str) -> bool:
    if upgrade_name in EXTERNAL_ACTIVATION_UPGRADES_WITHOUT_DATABASE_CONDITIONS:
        return True
    metadata = raw_upgrade_metadata(upgrade_name)
    stats = {normalized_database_key(stat) for stat in (metadata.get("stats") or {})}
    if stats and stats <= FACTION_DAMAGE_STATS:
        return True
    conditions = {normalized_database_key(condition) for condition in upgrade_conditions(metadata) if normalized_database_key(condition) not in AUTOMATIC_CONDITIONS}
    return any(condition not in WEAPON_ACTIVATED_CONDITIONS for condition in conditions)


def database_conditional_info(upgrade_name: str | None, *, is_arcane_slot: bool) -> tuple[bool, str]:
    if not upgrade_name:
        return False, ""
    kind = "arcane" if is_arcane_slot else "mod"
    labels = dict.fromkeys(
        label
        for label in upgrade_conditions(raw_upgrade_metadata(upgrade_name, kind=kind), include_stacking=False)
        if normalized_database_key(label) not in AUTOMATIC_CONDITIONS
    )
    readable = " / ".join(label.replace("_", " ").strip().title() for label in labels)
    return bool(readable), readable


def weapon_attack_modes(weapon_name: str | None) -> tuple[str, ...]:
    metadata = raw_weapon_metadata("", weapon_name)
    attacks = metadata.get("attacks") or {}
    child_names = {
        child
        for attack in attacks.values()
        for child in (attack.get("children", []) if isinstance(attack, dict) else [])
    }
    selectable = [name for name in attacks if name not in child_names] or list(attacks)
    return tuple(name.replace("_", " ").title() for name in selectable)


def weapon_evolution_options(weapon_name: str | None) -> list[dict]:
    evolutions = raw_weapon_metadata("", weapon_name).get("evolutions") or {}
    tiers: list[dict] = []
    for tier, perks in evolutions.items():
        options = ["None"]
        for perk, data in perks.items():
            description = str((data or {}).get("description", "")).strip()
            options.append(f"Perk {perk}" + (f" — {description}" if description else ""))
        tiers.append({"tier": str(tier), "label": f"Evolution {tier}", "options": options})
    return tiers


def weapon_evolution_perk_choices(weapon_name: str | None, *, custom_metadata: dict | None = None) -> dict[int, tuple[int, ...]]:
    """Map evolution tier -> perk ids available for search. Every tier with perks must be filled."""
    metadata = custom_metadata if custom_metadata is not None else raw_weapon_metadata("", weapon_name)
    evolutions = (metadata or {}).get("evolutions") or {}
    choices: dict[int, tuple[int, ...]] = {}
    for tier, perks in evolutions.items():
        try:
            tier_id = int(tier)
        except (TypeError, ValueError):
            continue
        perk_ids: list[int] = []
        for perk in perks or {}:
            try:
                perk_ids.append(int(perk))
            except (TypeError, ValueError):
                continue
        if perk_ids:
            choices[tier_id] = tuple(sorted(perk_ids))
    return choices


def _selected_attack(metadata: dict, selected_mode: str | None) -> dict:
    attacks = metadata.get("attacks") or {}
    wanted = normalized_database_key(selected_mode)
    for name, attack in attacks.items():
        if normalized_database_key(name) == wanted:
            return attack or {}
    return next(iter(attacks.values()), {})


def selected_attack_trigger(selected_weapon_name: str | None, selected_mode: str | None, *, custom_metadata: dict | None = None) -> str | None:
    metadata = custom_metadata if custom_metadata is not None else raw_weapon_metadata("", selected_weapon_name)
    trigger = _selected_attack(metadata, selected_mode).get("trigger")
    return normalized_database_key(trigger) if trigger else None


def weapon_has_aoe_attack(selected_weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    metadata = custom_metadata if custom_metadata is not None else raw_weapon_metadata("", selected_weapon_name)
    return any(bool(attack.get("aoe", False)) for attack in (metadata.get("attacks") or {}).values() if isinstance(attack, dict))


def selected_attack_category(selected_weapon_name: str | None, selected_mode: str | None, *, custom_metadata: dict | None = None) -> str:
    metadata = custom_metadata if custom_metadata is not None else raw_weapon_metadata("", selected_weapon_name)
    return str(_selected_attack(metadata, selected_mode).get("category") or "normal")


def stance_combo_key_for_attack_category(category: str) -> str | None:
    if category in HEAVY_ATTACK_CATEGORIES:
        return "heavy"
    if category in SLIDE_ATTACK_CATEGORIES:
        return "slide"
    if category == "slam":
        return "slam"
    return None


def stance_combo_options_for_attack(category: str) -> list[str]:
    """Combo choices for an attack category, independent of the equipped stance."""
    bound = stance_combo_key_for_attack_category(category)
    if bound is not None:
        return [bound]
    return list(FREE_STANCE_COMBO_OPTIONS)


def weapon_compatibility_terms(weapon_category: str, selected_weapon_name: str | None = None, *, custom_metadata: dict | None = None) -> set[str]:
    terms = set(WEAPON_COMPATIBILITY_FAMILIES[weapon_category])
    metadata = custom_metadata
    if metadata is None and selected_weapon_name and normalized_database_key(selected_weapon_name) not in {"custom", "none"}:
        metadata = raw_weapon_metadata(WEAPON_CATEGORY_TYPES[weapon_category], selected_weapon_name)
    if selected_weapon_name and normalized_database_key(selected_weapon_name) not in {"custom", "none"}:
        terms.add(normalized_database_key(selected_weapon_name))
    if metadata:
        for value in (metadata.get("type"), metadata.get("subtype")):
            if value:
                terms.add(normalized_database_key(value))
    return terms


def upgrade_incompatibility_names(metadata: dict) -> set[str]:
    return {str(name) for name in (metadata.get("incompatibility") or []) if name}


def upgrades_are_incompatible(left_name: str, right_name: str) -> bool:
    if not left_name or not right_name or left_name == right_name:
        return False
    left = raw_upgrade_metadata(left_name)
    right = raw_upgrade_metadata(right_name)
    return right_name in upgrade_incompatibility_names(left) or left_name in upgrade_incompatibility_names(right)


def upgrade_conflicts_with_selected(upgrade_name: str, selected_names: set[str]) -> bool:
    return any(upgrades_are_incompatible(upgrade_name, other) for other in selected_names if other != upgrade_name)


def upgrade_matches_weapon_type(metadata: dict, weapon_category: str, *, selected_weapon_name: str | None = None, selected_mode: str | None = None, custom_metadata: dict | None = None) -> bool:
    compatibility = metadata.get("compatibility") or {}
    allowed = {
        normalized_database_key(item)
        for key in ("types", "subtypes", "names")
        for item in compatibility.get(key, [])
    }
    if allowed and not (allowed & weapon_compatibility_terms(weapon_category, selected_weapon_name, custom_metadata=custom_metadata)):
        return False
    has_trigger_rule = bool(compatibility.get("triggers"))
    # The database serializes aoe=false for every upgrade. It is a meaningful
    # restriction only alongside another weapon-mode rule (the Cannonade mods);
    # aoe=true remains meaningful on its own for future database entries.
    has_aoe_rule = compatibility.get("aoe") is True or ("aoe" in compatibility and has_trigger_rule)
    if has_aoe_rule:
        is_aoe = weapon_has_aoe_attack(selected_weapon_name, custom_metadata=custom_metadata)
        if bool(compatibility["aoe"]) != is_aoe:
            return False
    if has_trigger_rule:
        trigger = selected_attack_trigger(selected_weapon_name, selected_mode, custom_metadata=custom_metadata)
        allowed_triggers = {normalized_database_key(item) for item in compatibility.get("triggers", [])}
        if trigger is None or trigger not in allowed_triggers:
            return False
    return bool(allowed or has_aoe_rule or has_trigger_rule)


def arcane_matches_weapon_slot(name: str, weapon_category: str) -> bool:
    """Filter weapon-slot Arcanes without trusting the database's broad primary tag."""
    if weapon_category in {"Rifle", "Shotgun", "Bow", "Sniper"}:
        return name.startswith("Primary ") or name == "Fractalized Reset" or (weapon_category == "Bow" and name == "Longbow Sharpshot") or (weapon_category == "Shotgun" and name == "Shotgun Vendetta")
    if weapon_category == "Pistol":
        return name.startswith(("Secondary ", "Cascadia ")) or name in {"Akimbo Slip Shot", "Conjunction Voltage"}
    if weapon_category == "Melee":
        return name.startswith("Melee ")
    return False


@lru_cache(maxsize=None)
def weapon_names_for_type(weapon_type_name: str, weapon_category: str | None = None) -> tuple[str, ...]:
    category = type_query_for_weapon_type(weapon_type_name)
    return tuple(sorted(
        (
            name for name, metadata in raw_weapons_database().items()
            if metadata.get("type") == category
            and (weapon_category is None or weapon_category == "Melee" or normalized_database_key(metadata.get("subtype")) == normalized_database_key(weapon_category))
        ), key=str.casefold,
    ))


def _weapon_flag_metadata(weapon_name: str | None, *, custom_metadata: dict | None = None) -> dict | None:
    if custom_metadata is not None:
        return custom_metadata
    if not weapon_name or normalized_database_key(weapon_name) in {"custom", "none"}:
        return None
    return raw_weapon_metadata("", weapon_name)


def weapon_is_exalted(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """True for exalted weapons that use a fixed exclusive stance."""
    metadata = _weapon_flag_metadata(weapon_name, custom_metadata=custom_metadata)
    return bool(metadata and metadata.get("exalted"))


def weapon_is_pseudo_exalted(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """True for pseudo-exalted weapons that do not use stance mods."""
    metadata = _weapon_flag_metadata(weapon_name, custom_metadata=custom_metadata)
    return bool(metadata and metadata.get("pseudo_exalted"))


def weapon_uses_ability_strength(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """True for exalted / pseudo-exalted weapons scaled by Ability Strength."""
    metadata = _weapon_flag_metadata(weapon_name, custom_metadata=custom_metadata)
    return bool(metadata and (metadata.get("exalted") or metadata.get("pseudo_exalted")))


def weapon_is_companion(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """True for companion weapons that do not use stance mods or stance combos."""
    metadata = _weapon_flag_metadata(weapon_name, custom_metadata=custom_metadata)
    return bool(metadata and metadata.get("companion"))


def weapon_allows_stance(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """False for pseudo-exalted and companion weapons."""
    return not weapon_is_pseudo_exalted(weapon_name, custom_metadata=custom_metadata) and not weapon_is_companion(weapon_name, custom_metadata=custom_metadata)


def weapon_has_riven_disposition(weapon_name: str | None, *, custom_metadata: dict | None = None) -> bool:
    """True when the weapon has a positive Riven disposition."""
    metadata = _weapon_flag_metadata(weapon_name, custom_metadata=custom_metadata)
    if not metadata:
        return False
    disposition = metadata.get("disposition")
    if disposition is None:
        return False
    try:
        return float(disposition) > 0
    except (TypeError, ValueError):
        return False


@lru_cache(maxsize=None)
def weapon_exclusive_stance_names(weapon_name: str | None) -> tuple[str, ...]:
    """Stances locked to an exalted weapon via compatibility.names."""
    if not weapon_name or normalized_database_key(weapon_name) in {"custom", "none"}:
        return ()
    if not weapon_is_exalted(weapon_name) or not weapon_allows_stance(weapon_name):
        return ()
    wanted = normalized_database_key(weapon_name)
    names = [
        name
        for name, metadata in raw_upgrades_database().items()
        if bool((metadata.get("compatibility") or {}).get("stance"))
        and wanted in {normalized_database_key(item) for item in ((metadata.get("compatibility") or {}).get("names") or [])}
    ]
    return tuple(sorted(names, key=str.casefold))


def preferred_exclusive_stance(weapon_name: str | None, exclusive: tuple[str, ...] | list[str]) -> str:
    if not exclusive:
        return ""
    if weapon_name:
        wanted = normalized_database_key(weapon_name)
        for name in exclusive:
            if normalized_database_key(name) == wanted:
                return name
    return exclusive[0]


def _upgrade_names_for_ui(weapon_category: str, selected_weapon_name: str | None, selected_mode: str | None, include_mods: bool, include_arcanes: bool, exilus_only: bool, stance_only: bool = False, custom_metadata: dict | None = None) -> tuple[str, ...]:
    if stance_only and not weapon_allows_stance(selected_weapon_name, custom_metadata=custom_metadata):
        return ()
    exclusive_stances = weapon_exclusive_stance_names(selected_weapon_name) if stance_only and weapon_is_exalted(selected_weapon_name, custom_metadata=custom_metadata) else ()
    names = []
    for name, metadata in raw_upgrades_database().items():
        kind = metadata.get("type")
        if not ((include_mods and kind == "mod") or (include_arcanes and kind == "arcane")):
            continue
        compatibility = metadata.get("compatibility") or {}
        is_stance = bool(compatibility.get("stance", False))
        is_exilus = bool(compatibility.get("exilus", False))
        if stance_only:
            if not is_stance:
                continue
            if exclusive_stances:
                if name in exclusive_stances:
                    names.append(name)
                continue
        elif is_stance:
            continue
        if kind == "mod" and exilus_only and not is_exilus:
            continue
        matches_weapon = arcane_matches_weapon_slot(name, weapon_category) if kind == "arcane" else upgrade_matches_weapon_type(metadata, weapon_category, selected_weapon_name=selected_weapon_name, selected_mode=selected_mode, custom_metadata=custom_metadata)
        if matches_weapon:
            names.append(name)
    return tuple(sorted(names, key=str.casefold))


@lru_cache(maxsize=None)
def upgrade_names_for_ui(weapon_category: str, selected_weapon_name: str | None, selected_mode: str | None, include_mods: bool, include_arcanes: bool, exilus_only: bool, stance_only: bool = False) -> tuple[str, ...]:
    return _upgrade_names_for_ui(weapon_category, selected_weapon_name, selected_mode, include_mods, include_arcanes, exilus_only, stance_only=stance_only)


@lru_cache(maxsize=None)
def _cached_database_weapon(weapon_name: str, type_filter: str):
    return arsenal.get(weapon_name, type=type_filter)


def database_weapon(weapon_name: str, weapon_type_name: str):
    loaded = _cached_database_weapon(weapon_name, type_query_for_weapon_type(weapon_type_name))
    return copy.deepcopy(loaded) if isinstance(loaded, tuple(WEAPON_TYPES.values())) else None


@lru_cache(maxsize=1)
def enemy_names_for_ui() -> tuple[str, ...]:
    return tuple(sorted(raw_enemies_database(), key=str.casefold))


@lru_cache(maxsize=None)
def _cached_database_enemy(enemy_name: str, level: int, steel_path: bool, empowered: bool):
    return arsenal.get(enemy_name, type="enemy", context={"level": level, "steel_path": steel_path, "empowered": empowered})


def database_enemy(enemy_name: str, *, level: int, steel_path: bool, empowered: bool):
    loaded = _cached_database_enemy(enemy_name, level, steel_path, empowered)
    return loaded.copy() if isinstance(loaded, Enemy) else None


@lru_cache(maxsize=None)
def _cached_database_upgrade(upgrade_name: str, kind: str | None, rank: int | None, stacks: int | None, condition: bool):
    metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
    runtime: dict[str, bool | int] = {}
    if rank is not None:
        runtime["rank"] = rank
    if stacks is not None:
        runtime["stacks"] = stacks
    for _stat, _value, when, stacking in iter_upgrade_effects(metadata):
        if isinstance(when, str) and normalized_database_key(when) not in AUTOMATIC_CONDITIONS:
            runtime[when] = stacks if stacking and stacks is not None else condition
    return arsenal.get(upgrade_name, type=kind, context=runtime)


def database_upgrade(upgrade_name: str, *, kind: str | None = None, rank: int | None = None, stacks: int | None = None, condition: bool = True):
    loaded = _cached_database_upgrade(upgrade_name, kind, rank, stacks, condition)
    return loaded.copy() if isinstance(loaded, Upgrade) else None


def database_rank_bounds(upgrade_name: str | None = None, *, is_arcane_slot: bool) -> tuple[int, int]:
    metadata = raw_upgrade_metadata(upgrade_name or "", kind="arcane" if is_arcane_slot else "mod")
    default = 5 if is_arcane_slot else 10
    raw_max_rank = metadata.get("max_rank")
    if raw_max_rank is None and bool((metadata.get("compatibility") or {}).get("stance", False)):
        return 0, 0
    try:
        return 0, max(0, int(default if raw_max_rank is None else raw_max_rank))
    except (TypeError, ValueError):
        return 0, default


def database_max_stacks(upgrade_name: str | None = None, *, is_arcane_slot: bool) -> int | None:
    metadata = raw_upgrade_metadata(upgrade_name or "", kind="arcane" if is_arcane_slot else "mod")
    maximums = []
    for stat, effects in (metadata.get("stats") or {}).items():
        if stat == "condition_overload":
            continue
        for effect in effects if isinstance(effects, list) else [effects]:
            maximum = effect.get("stacks", {}).get("max") if isinstance(effect, dict) else None
            if isinstance(maximum, int):
                maximums.append(maximum)
    return max(maximums) if maximums else None
