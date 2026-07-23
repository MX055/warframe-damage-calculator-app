from __future__ import annotations

import copy
import json
import sys
from functools import lru_cache
from pathlib import Path

import warframe_damage_calculator
from warframe_damage_calculator import Upgrade, arsenal

from .constants import WEAPON_CATEGORY_TYPES, WEAPON_COMPATIBILITY_FAMILIES, WEAPON_TYPES

AUTOMATIC_CONDITIONS = {
    "primary", "rifle", "bow", "shotgun", "sniper", "secondary", "pistol",
    "melee", "sacrificial set",
}


def type_query_for_weapon_type(weapon_type_name: str) -> str:
    return {"Primary": "primary", "Secondary": "secondary", "Melee": "melee"}[weapon_type_name]


def normalized_database_key(value: object) -> str:
    return " ".join(str(value or "").casefold().replace("_", " ").replace("-", " ").split())


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


def raw_riven_stats_database() -> dict:
    return raw_database().get("riven_stats", {}) or {}


def raw_weapon_metadata(_weapon_type_name: str, weapon_name: str | None) -> dict:
    if not weapon_name or normalized_database_key(weapon_name) == "custom":
        return {}
    return raw_weapons_database().get(weapon_name, {}) or {}


def raw_upgrade_metadata(upgrade_name: str, *, kind: str | None = None) -> dict:
    metadata = raw_upgrades_database().get(upgrade_name, {}) or {}
    return metadata if not kind or metadata.get("type") == kind else {}


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


def _selected_attack(metadata: dict, selected_mode: str | None) -> dict:
    attacks = metadata.get("attacks") or {}
    wanted = normalized_database_key(selected_mode)
    for name, attack in attacks.items():
        if normalized_database_key(name) == wanted:
            return attack or {}
    return next(iter(attacks.values()), {})


def weapon_compatibility_terms(weapon_category: str, selected_weapon_name: str | None = None) -> set[str]:
    terms = set(WEAPON_COMPATIBILITY_FAMILIES[weapon_category])
    if selected_weapon_name and normalized_database_key(selected_weapon_name) != "custom":
        metadata = raw_weapon_metadata(WEAPON_CATEGORY_TYPES[weapon_category], selected_weapon_name)
        terms.add(normalized_database_key(selected_weapon_name))
        for value in (metadata.get("type"), metadata.get("subtype")):
            if value:
                terms.add(normalized_database_key(value))
    return terms


def upgrade_matches_weapon_type(metadata: dict, weapon_category: str, *, selected_weapon_name: str | None = None, selected_mode: str | None = None) -> bool:
    compatibility = metadata.get("compatibility") or {}
    allowed = {
        normalized_database_key(item)
        for key in ("types", "subtypes", "names")
        for item in compatibility.get(key, [])
    }
    if allowed and not (allowed & weapon_compatibility_terms(weapon_category, selected_weapon_name)):
        return False
    if "aoe" in compatibility and selected_weapon_name:
        is_aoe = bool(_selected_attack(raw_weapon_metadata("", selected_weapon_name), selected_mode).get("aoe", False))
        if bool(compatibility["aoe"]) != is_aoe:
            return False
    return bool(allowed or "aoe" in compatibility)


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


@lru_cache(maxsize=None)
def upgrade_names_for_ui(weapon_category: str, selected_weapon_name: str | None, selected_mode: str | None, include_mods: bool, include_arcanes: bool, exilus_only: bool) -> tuple[str, ...]:
    names = []
    for name, metadata in raw_upgrades_database().items():
        kind = metadata.get("type")
        if not ((include_mods and kind == "mod") or (include_arcanes and kind == "arcane")):
            continue
        is_exilus = bool((metadata.get("compatibility") or {}).get("exilus", False))
        if kind == "mod" and exilus_only and not is_exilus:
            continue
        if upgrade_matches_weapon_type(metadata, weapon_category, selected_weapon_name=selected_weapon_name, selected_mode=selected_mode):
            names.append(name)
    return tuple(sorted(names, key=str.casefold))


@lru_cache(maxsize=None)
def _cached_database_weapon(weapon_name: str, type_filter: str):
    return arsenal.get(weapon_name, type=type_filter)


def database_weapon(weapon_name: str, weapon_type_name: str):
    loaded = _cached_database_weapon(weapon_name, type_query_for_weapon_type(weapon_type_name))
    return copy.deepcopy(loaded) if isinstance(loaded, tuple(WEAPON_TYPES.values())) else None


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
    try:
        return 0, max(0, int(metadata.get("max_rank", default)))
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
