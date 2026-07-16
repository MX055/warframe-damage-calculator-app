from __future__ import annotations

import copy
import json
from functools import lru_cache
from importlib import resources
from pathlib import Path

from warframe_damage_calculator import Upgrade, arsenal

from .constants import (
    WEAPON_CATEGORY_TYPES,
    WEAPON_COMPATIBILITY_FAMILIES,
    WEAPON_DATABASE_SECTIONS,
    WEAPON_TYPES,
)

AUTOMATIC_CONDITIONS = {
    "primary",
    "rifle",
    "bow",
    "shotgun",
    "sniper",
    "secondary",
    "pistol",
    "melee",
    "sacrificial set",
}


def type_query_for_weapon_type(weapon_type_name: str) -> str:
    return {
        "Primary": "primary",
        "Secondary": "secondary",
        "Melee": "melee",
    }[weapon_type_name]


def normalized_database_key(value: object) -> str:
    return " ".join(str(value or "").casefold().split())


@lru_cache(maxsize=None)
def load_json_database(filename: str) -> dict:
    """Load packaged JSON without constructing calculator objects."""
    project_root = Path(__file__).resolve().parents[1]
    local_candidates = (
        project_root / filename,
        project_root / "database" / filename,
        Path(__file__).with_name(filename),
        Path(__file__).parent / "database" / filename,
    )

    for path in local_candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)

    package_candidates = (
        ("warframe_damage_calculator.data.database", filename),
        ("warframe_damage_calculator.data", f"database/{filename}"),
    )

    for package_name, resource_name in package_candidates:
        try:
            resource_path = resources.files(package_name).joinpath(resource_name)
            with resource_path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, ModuleNotFoundError, AttributeError):
            continue

    return {}


@lru_cache(maxsize=1)
def raw_weapons_database() -> dict:
    return load_json_database("weapons.json")


@lru_cache(maxsize=1)
def raw_upgrades_database() -> dict:
    return load_json_database("upgrades.json")


def raw_weapon_metadata(weapon_type_name: str, weapon_name: str | None) -> dict:
    if not weapon_name or weapon_name == "custom":
        return {}
    section = WEAPON_DATABASE_SECTIONS[weapon_type_name]
    return raw_weapons_database().get(section, {}).get(weapon_name, {}) or {}


def raw_upgrade_metadata(upgrade_name: str, *, kind: str | None = None) -> dict:
    upgrades = raw_upgrades_database()
    if kind == "mod":
        return upgrades.get("mod", {}).get(upgrade_name, {}) or {}
    if kind == "arcane":
        return upgrades.get("arcane", {}).get(upgrade_name, {}) or {}
    return (
        upgrades.get("mod", {}).get(upgrade_name)
        or upgrades.get("arcane", {}).get(upgrade_name)
        or {}
    )


def metadata_context(metadata: dict) -> dict:
    context = metadata.get("context") or {}
    return context if isinstance(context, dict) else {}


def iter_upgrade_effects(metadata: dict):
    """Yield v0.6 effects as ``(stat, value, condition, stacking)``."""
    stats = metadata.get("stats") or {}
    for stat, effects in (stats.items() if isinstance(stats, dict) else ()):
        for effect in effects if isinstance(effects, list) else [effects]:
            if isinstance(effect, dict) and "value" in effect:
                yield stat, effect["value"], effect.get("when"), bool(effect.get("stacking"))
            else:
                yield stat, effect, None, False


def upgrade_conditions(metadata: dict, *, include_stacking: bool = True) -> list[str]:
    return [
        condition
        for _stat, _value, condition, stacking in iter_upgrade_effects(metadata)
        if isinstance(condition, str) and (include_stacking or not stacking)
    ]


def database_conditional_info(
    upgrade_name: str | None,
    *,
    is_arcane_slot: bool,
) -> tuple[bool, str]:
    """Return whether an upgrade needs a user-controlled conditional toggle.

    Bow-only fire-rate bonuses are selected automatically from the weapon type,
    so they do not need a checkbox. Other conditional stats share the loader's
    single ``condition`` flag and are controlled by one checkbox per slot.
    """
    if not upgrade_name:
        return False, ""

    kind = "arcane" if is_arcane_slot else "mod"
    metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
    labels = dict.fromkeys(
        label
        for label in upgrade_conditions(metadata, include_stacking=False)
        if normalized_database_key(label) not in AUTOMATIC_CONDITIONS
    )
    readable = " / ".join(label.replace("_", " ").strip().title() for label in labels)
    return (bool(readable), readable)


def weapon_compatibility_terms(
    weapon_category: str,
    selected_weapon_name: str | None = None,
) -> set[str]:
    terms = set(WEAPON_COMPATIBILITY_FAMILIES[weapon_category])
    weapon_type_name = WEAPON_CATEGORY_TYPES[weapon_category]
    if selected_weapon_name and selected_weapon_name != "custom":
        metadata = raw_weapon_metadata(weapon_type_name, selected_weapon_name)
        terms.add(normalized_database_key(selected_weapon_name))
        weapon_subtype = metadata_context(metadata).get("type")
        if weapon_subtype:
            terms.add(normalized_database_key(weapon_subtype))
    return terms


def upgrade_matches_weapon_type(
    metadata: dict,
    weapon_category: str,
    *,
    selected_weapon_name: str | None = None,
) -> bool:
    context = metadata_context(metadata)
    raw_compatibility = context.get("compatibility", [])
    if isinstance(raw_compatibility, str):
        raw_compatibility = [raw_compatibility]
    compatibility = {
        normalized_database_key(item) for item in raw_compatibility
    }
    if not compatibility:
        return False

    if not (
        compatibility
        & weapon_compatibility_terms(weapon_category, selected_weapon_name)
    ):
        return False

    requirements = context.get("requirements") or {}
    if not requirements or not selected_weapon_name or selected_weapon_name == "custom":
        return True

    weapon_type_name = WEAPON_CATEGORY_TYPES[weapon_category]
    weapon_metadata = metadata_context(
        raw_weapon_metadata(weapon_type_name, selected_weapon_name)
    )
    return all(
        weapon_metadata.get(key) in expected
        if isinstance(expected, list)
        else weapon_metadata.get(key) == expected
        for key, expected in requirements.items()
    )


@lru_cache(maxsize=None)
def database_items(type_filter: str | None = None) -> dict:
    items = arsenal.get(type=type_filter)
    return items if isinstance(items, dict) else {}


@lru_cache(maxsize=None)
def weapon_names_for_type(
    weapon_type_name: str,
    weapon_category: str | None = None,
) -> tuple[str, ...]:
    section = WEAPON_DATABASE_SECTIONS[weapon_type_name]
    names = raw_weapons_database().get(section, {})
    if names:
        return tuple(
            sorted(
                (
                    name
                    for name, metadata in names.items()
                    if weapon_category is None
                    or weapon_category == "Melee"
                    or normalized_database_key(metadata_context(metadata).get("type"))
                    == normalized_database_key(weapon_category)
                ),
                key=str.casefold,
            )
        )

    weapon_class = WEAPON_TYPES[weapon_type_name]
    return tuple(
        sorted(
            (
                name
                for name, item in database_items(
                    type_query_for_weapon_type(weapon_type_name)
                ).items()
                if isinstance(item, weapon_class)
            ),
            key=str.casefold,
        )
    )


@lru_cache(maxsize=None)
def upgrade_names_for_ui(
    weapon_category: str,
    selected_weapon_name: str | None,
    include_mods: bool,
    include_arcanes: bool,
    exilus_only: bool,
) -> tuple[str, ...]:
    upgrades = raw_upgrades_database()
    weapon_type_name = WEAPON_CATEGORY_TYPES[weapon_category]
    names: list[str] = []
    database_has_requested_items = bool(
        (include_mods and "mod" in upgrades)
        or (include_arcanes and "arcane" in upgrades)
    )

    if include_mods:
        for name, metadata in upgrades.get("mod", {}).items():
            is_exilus = bool(metadata_context(metadata).get("is_exilus", False))
            if exilus_only != is_exilus:
                continue
            if upgrade_matches_weapon_type(
                metadata,
                weapon_category,
                selected_weapon_name=selected_weapon_name,
            ):
                names.append(name)

    if include_arcanes:
        for name, metadata in upgrades.get("arcane", {}).items():
            if upgrade_matches_weapon_type(
                metadata,
                weapon_category,
                selected_weapon_name=selected_weapon_name,
            ):
                names.append(name)

    if database_has_requested_items:
        return tuple(sorted(names, key=str.casefold))

    type_filter = type_query_for_weapon_type(weapon_type_name)
    fallback_names = []
    for name, item in database_items(type_filter).items():
        if not isinstance(item, Upgrade):
            continue
        category = str(item.data.context.get("category", "") or "").casefold()
        if (include_mods and category == "mod") or (
            include_arcanes and category == "arcane"
        ):
            fallback_names.append(name)
    return tuple(sorted(fallback_names, key=str.casefold))


@lru_cache(maxsize=None)
def _cached_database_weapon(weapon_name: str, type_filter: str | None):
    return arsenal.get(weapon_name, type=type_filter)


def database_weapon(weapon_name: str, weapon_type_name: str):
    loaded_weapon = _cached_database_weapon(
        weapon_name,
        type_query_for_weapon_type(weapon_type_name),
    )
    if not isinstance(loaded_weapon, tuple(WEAPON_TYPES.values())):
        return None
    return copy.deepcopy(loaded_weapon)


@lru_cache(maxsize=None)
def _cached_database_upgrade(
    upgrade_name: str,
    kind: str | None,
    rank: int | None,
    stacks: int | None,
    condition: bool,
):
    metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
    context: dict[str, bool | int] = {}
    if rank is not None:
        context["rank"] = rank
    for _stat, _value, when, stacking in iter_upgrade_effects(metadata):
        if isinstance(when, str) and normalized_database_key(when) not in AUTOMATIC_CONDITIONS:
            context[when] = (stacks or 0) if stacking else condition
    loaded = arsenal.get(upgrade_name, type=kind)
    if isinstance(loaded, Upgrade):
        loaded.data.context.update(context)
    return loaded


def database_upgrade(
    upgrade_name: str,
    *,
    kind: str | None = None,
    rank: int | None = None,
    stacks: int | None = None,
    condition: bool = True,
):
    loaded_upgrade = _cached_database_upgrade(
        upgrade_name,
        kind,
        rank,
        stacks,
        condition,
    )
    return copy.deepcopy(loaded_upgrade) if isinstance(loaded_upgrade, Upgrade) else None


def _upgrade_limit(
    upgrade_name: str | None,
    *,
    is_arcane_slot: bool,
    key: str,
    default: int | None,
) -> int | None:
    kind = "arcane" if is_arcane_slot else "mod"
    value = metadata_context(raw_upgrade_metadata(upgrade_name or "", kind=kind)).get(key)
    try:
        value = default if value is None else max(0, int(value))
    except (TypeError, ValueError):
        return default
    return value if value is None or value > 0 or key == "max_rank" else None


def database_rank_bounds(
    upgrade_name: str | None = None,
    *,
    is_arcane_slot: bool,
) -> tuple[int, int]:
    default = 5 if is_arcane_slot else 10
    return 0, int(_upgrade_limit(
        upgrade_name, is_arcane_slot=is_arcane_slot, key="max_rank", default=default
    ))


def database_max_stacks(
    upgrade_name: str | None = None,
    *,
    is_arcane_slot: bool,
) -> int | None:
    return _upgrade_limit(
        upgrade_name, is_arcane_slot=is_arcane_slot, key="max_stacks", default=None
    )
