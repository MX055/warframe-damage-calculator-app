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
        return upgrades.get("mods", {}).get(upgrade_name, {}) or {}
    if kind == "arcane":
        return upgrades.get("arcanes", {}).get(upgrade_name, {}) or {}
    return (
        upgrades.get("mods", {}).get(upgrade_name)
        or upgrades.get("arcanes", {}).get(upgrade_name)
        or {}
    )


def _condition_text_values(value: object) -> list[str]:
    """Flatten condition metadata into readable labels."""
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        values: list[str] = []
        for nested_value in value.values():
            values.extend(_condition_text_values(nested_value))
        return values
    if isinstance(value, (list, tuple, set)):
        values: list[str] = []
        for nested_value in value:
            values.extend(_condition_text_values(nested_value))
        return values
    text = str(value).strip()
    return [text] if text else []


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
    conditionals = metadata.get("conditionals") or {}
    if not isinstance(conditionals, dict) or not conditionals:
        return False, ""

    conditions = metadata.get("conditions") or {}
    raw_labels: list[str] = []
    for field_name in conditionals:
        if isinstance(conditions, dict):
            raw_labels.extend(_condition_text_values(conditions.get(field_name)))

    unique_labels: list[str] = []
    for label in raw_labels:
        normalized = normalized_database_key(label)
        if normalized in {"bow", "sacrificial set"}:
            continue
        if normalized and normalized not in {
            normalized_database_key(existing) for existing in unique_labels
        }:
            unique_labels.append(label)

    # Bow and set-bonus conditions are derived from the configured weapon/build.
    if raw_labels and not unique_labels:
        return False, ""

    if unique_labels:
        readable = " / ".join(
            label.replace("_", " ").strip().title() for label in unique_labels
        )
        return True, readable

    return True, "Conditional Bonus"


def database_upgrade_condition_labels(
    upgrade_name: str | None,
    *,
    is_arcane_slot: bool,
) -> set[str]:
    """Return normalized condition labels used by an upgrade's bonus fields."""
    if not upgrade_name:
        return set()
    kind = "arcane" if is_arcane_slot else "mod"
    metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
    conditions = metadata.get("conditions") or {}
    conditionals = metadata.get("conditionals") or {}
    labels: set[str] = set()
    if isinstance(conditions, dict) and isinstance(conditionals, dict):
        for field_name in conditionals:
            labels.update(
                normalized_database_key(label)
                for label in _condition_text_values(conditions.get(field_name))
                if label
            )
    return labels


def weapon_compatibility_terms(
    weapon_category: str,
    selected_weapon_name: str | None = None,
) -> set[str]:
    terms = set(WEAPON_COMPATIBILITY_FAMILIES[weapon_category])
    weapon_type_name = WEAPON_CATEGORY_TYPES[weapon_category]
    if selected_weapon_name and selected_weapon_name != "custom":
        metadata = raw_weapon_metadata(weapon_type_name, selected_weapon_name)
        terms.add(normalized_database_key(selected_weapon_name))
        weapon_subtype = metadata.get("type")
        if weapon_subtype:
            terms.add(normalized_database_key(weapon_subtype))
    return terms


def upgrade_matches_weapon_type(
    metadata: dict,
    weapon_category: str,
    *,
    selected_weapon_name: str | None = None,
) -> bool:
    raw_compatibility = metadata.get("compatibility", [])
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

    requirements = metadata.get("requirements") or {}
    if not requirements or not selected_weapon_name or selected_weapon_name == "custom":
        return True

    weapon_type_name = WEAPON_CATEGORY_TYPES[weapon_category]
    weapon_metadata = raw_weapon_metadata(weapon_type_name, selected_weapon_name)
    for key, expected in requirements.items():
        actual = weapon_metadata.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


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
                    or normalized_database_key(metadata.get("type"))
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
        (include_mods and "mods" in upgrades)
        or (include_arcanes and "arcanes" in upgrades)
    )

    if include_mods:
        for name, metadata in upgrades.get("mods", {}).items():
            is_exilus = bool(metadata.get("is_exilus", False))
            if exilus_only != is_exilus:
                continue
            if upgrade_matches_weapon_type(
                metadata,
                weapon_category,
                selected_weapon_name=selected_weapon_name,
            ):
                names.append(name)

    if include_arcanes:
        for name, metadata in upgrades.get("arcanes", {}).items():
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
        category = str(getattr(item, "category", "") or "").casefold()
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
    return arsenal.get(
        upgrade_name,
        type=kind,
        rank=rank,
    )


def _condition_labels(value: object) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]
    return {normalized_database_key(item) for item in values if item}


def _database_rank_multiplier(metadata: dict, rank: int | None) -> float:
    if rank is None:
        return 1.0
    try:
        max_rank = int(metadata.get("max_rank"))
    except (TypeError, ValueError):
        return 1.0
    if max_rank <= 0:
        return 1.0
    clamped_rank = max(0, min(int(rank), max_rank))
    return (clamped_rank + 1) / (max_rank + 1)


def _bow_fire_rate_bonus(
    upgrade_name: str,
    *,
    kind: str | None,
    rank: int | None,
) -> float:
    metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
    conditions = metadata.get("conditions") or {}
    if "bow" not in _condition_labels(conditions.get("fire_rate")):
        return 0.0
    try:
        bonus = float((metadata.get("conditionals") or {}).get("fire_rate", 0.0))
    except (TypeError, ValueError):
        return 0.0
    return bonus * _database_rank_multiplier(metadata, rank)


def database_upgrade(
    upgrade_name: str,
    *,
    kind: str | None = None,
    rank: int | None = None,
    stacks: int | None = None,
    condition: bool = True,
    is_bow: bool = False,
):
    loaded_upgrade = _cached_database_upgrade(
        upgrade_name,
        kind,
        rank,
        stacks,
        condition,
    )
    if not isinstance(loaded_upgrade, Upgrade):
        return None

    loaded_upgrade = copy.deepcopy(loaded_upgrade)

    # The database loader may apply the Arcane's stacking multiplier to every
    # numeric field. For Secondary Enervate, ``secondary_enervate`` is not a
    # stackable percentage: it is the number of Big Critical Hits before the
    # Arcane resets (1 at rank 0 through 6 at rank 5). Normalize it here so
    # both the calculator and the UI receive the correct value.
    if normalized_database_key(upgrade_name) == "secondary enervate":
        metadata = raw_upgrade_metadata(upgrade_name, kind=kind)
        try:
            max_rank = max(0, int(metadata.get("max_rank", 5)))
        except (TypeError, ValueError):
            max_rank = 5
        selected_rank = max_rank if rank is None else max(0, min(int(rank), max_rank))
        loaded_upgrade.stats = dict(loaded_upgrade.stats)
        loaded_upgrade.stats["secondary_enervate"] = selected_rank + 1
        loaded_upgrade.stats.pop("flat_crit_chance", None)
        loaded_upgrade.conditional_stats = dict(loaded_upgrade.conditional_stats)
        loaded_upgrade.conditional_stats.pop("flat_crit_chance", None)
        loaded_upgrade.stacking_stats = dict(loaded_upgrade.stacking_stats)
        loaded_upgrade.stacking_stats.pop("flat_crit_chance", None)

    return loaded_upgrade


def database_rank_bounds(
    upgrade_name: str | None = None,
    *,
    is_arcane_slot: bool,
) -> tuple[int, int]:
    kind = "arcane" if is_arcane_slot else "mod"
    metadata = raw_upgrade_metadata(upgrade_name or "", kind=kind)
    max_rank = metadata.get("max_rank")
    if max_rank is None:
        return (0, 5 if is_arcane_slot else 10)
    try:
        return 0, max(0, int(max_rank))
    except (TypeError, ValueError):
        return (0, 5 if is_arcane_slot else 10)


def database_max_stacks(
    upgrade_name: str | None = None,
    *,
    is_arcane_slot: bool,
) -> int | None:
    kind = "arcane" if is_arcane_slot else "mod"
    metadata = raw_upgrade_metadata(upgrade_name or "", kind=kind)
    max_stacks = metadata.get("max_stacks")
    if max_stacks is None:
        return None
    try:
        max_stacks = int(max_stacks)
    except (TypeError, ValueError):
        return None
    return max_stacks if max_stacks > 0 else None
