from __future__ import annotations

import json
import time
import uuid
from copy import deepcopy
from typing import Any

from .constants import (
    DEFAULT_OPTIMIZE_DPH_WEIGHT,
    DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT,
    DEFAULT_OPTIMIZE_MAXIMIZE,
    DEFAULT_OPTIMIZE_SEARCH,
    DEFAULT_OPTIMIZE_SPATIAL,
    INITIAL_COMBO_OPTION,
    NO_EFFECT,
    OPTIMIZE_SPATIAL_AOE,
    OPTIMIZE_SPATIAL_AUTO,
    OPTIMIZE_SPATIAL_OPTIONS,
    OPTIMIZE_SPATIAL_SINGLE,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
)
from .models import EditorField, RuntimeStackField, RuntimeToggleField

NONE = "None"
SETTINGS_VERSION = 1
BUILDS_VERSION = 1


def default_settings() -> dict[str, Any]:
    return {
        "version": SETTINGS_VERSION,
        "enemy": {
            "faction": "",
            "name": NONE,
            "level": 100,
            "steel_path": False,
            "empowered": False,
            "body_part": "",
        },
        "optimizer": {
            "maximize_target": DEFAULT_OPTIMIZE_MAXIMIZE,
            "search_quality": DEFAULT_OPTIMIZE_SEARCH,
            "dph_weight": DEFAULT_OPTIMIZE_DPH_WEIGHT,
            "flat_dot_weight": DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT,
            "spatial": DEFAULT_OPTIMIZE_SPATIAL,
            "find_riven": False,
            "find_evolutions": False,
            "find_progenitor": False,
            "excluded_upgrades": [],
            "default_exclusion_overrides": [],
            "excluded_riven_stats": [],
            "default_riven_exclusion_overrides": [],
        },
    }


def _editor_field_to_dict(field: EditorField) -> dict[str, Any]:
    return {
        "name": field.name,
        "label": field.label,
        "value": field.value,
        "min_value": field.min_value,
        "max_value": field.max_value,
        "integer": field.integer,
    }


def _editor_field_from_dict(data: dict[str, Any]) -> EditorField:
    return EditorField(
        str(data.get("name", "")),
        str(data.get("label", "")),
        float(data.get("value", 0.0)),
        float(data.get("min_value", -1_000_000_000.0)),
        float(data.get("max_value", 1_000_000_000.0)),
        bool(data.get("integer", False)),
    )


def _toggle_to_dict(field: RuntimeToggleField) -> dict[str, Any]:
    return {"name": field.name, "label": field.label, "value": bool(field.value)}


def _toggle_from_dict(data: dict[str, Any]) -> RuntimeToggleField:
    return RuntimeToggleField(str(data.get("name", "")), str(data.get("label", "")), bool(data.get("value", True)))


def _stack_to_dict(field: RuntimeStackField) -> dict[str, Any]:
    return {"name": field.name, "label": field.label, "value": str(field.value), "options": list(field.options)}


def _stack_from_dict(data: dict[str, Any]) -> RuntimeStackField:
    return RuntimeStackField(str(data.get("name", "")), str(data.get("label", "")), str(data.get("value", "0")), list(data.get("options") or []))


def encode_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True)


def decode_json(raw: str | None, fallback: Any) -> Any:
    if not raw:
        return deepcopy(fallback)
    try:
        return json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return deepcopy(fallback)


def resolve_optimize_spatial(optimizer: dict[str, Any]) -> str:
    spatial = str(optimizer.get("spatial") or "")
    if spatial in OPTIMIZE_SPATIAL_OPTIONS:
        return spatial
    weight = optimizer.get("aoe_weight")
    if weight is None:
        return DEFAULT_OPTIMIZE_SPATIAL
    try:
        value = int(weight)
    except (TypeError, ValueError):
        return DEFAULT_OPTIMIZE_SPATIAL
    if value <= 0:
        return OPTIMIZE_SPATIAL_SINGLE
    if value >= 100:
        return OPTIMIZE_SPATIAL_AOE
    return OPTIMIZE_SPATIAL_AUTO


def parse_settings(raw: str | None) -> dict[str, Any]:
    data = decode_json(raw, default_settings())
    if not isinstance(data, dict):
        return default_settings()
    base = default_settings()
    enemy = data.get("enemy") if isinstance(data.get("enemy"), dict) else {}
    optimizer = data.get("optimizer") if isinstance(data.get("optimizer"), dict) else {}
    base["enemy"].update({key: enemy[key] for key in base["enemy"] if key in enemy})
    base["optimizer"].update({key: optimizer[key] for key in base["optimizer"] if key in optimizer})
    base["optimizer"]["spatial"] = resolve_optimize_spatial({**optimizer, "spatial": base["optimizer"].get("spatial")})
    base["optimizer"].pop("aoe_weight", None)
    base["version"] = SETTINGS_VERSION
    return base


def parse_builds(raw: str | None) -> list[dict[str, Any]]:
    data = decode_json(raw, {"version": BUILDS_VERSION, "builds": []})
    if isinstance(data, list):
        builds = data
    elif isinstance(data, dict):
        builds = data.get("builds") if isinstance(data.get("builds"), list) else []
    else:
        builds = []
    cleaned: list[dict[str, Any]] = []
    for entry in builds:
        if not isinstance(entry, dict):
            continue
        snapshot = entry.get("snapshot")
        if not isinstance(snapshot, dict):
            continue
        cleaned.append({
            "id": str(entry.get("id") or uuid.uuid4()),
            "name": str(entry.get("name") or "Untitled Build"),
            "weapon": str(entry.get("weapon") or snapshot.get("selected_weapon") or NONE),
            "enemy": str(entry.get("enemy") or snapshot.get("selected_enemy") or NONE),
            "updated_at": float(entry.get("updated_at") or time.time()),
            "snapshot": snapshot,
        })
    return cleaned


def encode_builds(builds: list[dict[str, Any]]) -> str:
    return encode_json({"version": BUILDS_VERSION, "builds": builds})


def encode_settings(settings: dict[str, Any]) -> str:
    normalized = parse_settings(encode_json(settings))
    return encode_json(normalized)


def new_build_entry(name: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "name": name.strip() or "Untitled Build",
        "weapon": str(snapshot.get("selected_weapon") or NONE),
        "enemy": str(snapshot.get("selected_enemy") or NONE),
        "updated_at": time.time(),
        "snapshot": snapshot,
    }


def upsert_build(builds: list[dict[str, Any]], entry: dict[str, Any], *, replace_id: str | None = None) -> list[dict[str, Any]]:
    output = list(builds)
    target_id = replace_id or entry["id"]
    for index, existing in enumerate(output):
        if existing.get("id") == target_id:
            updated = dict(entry)
            updated["id"] = target_id
            output[index] = updated
            return output
    output.insert(0, entry)
    return output


def rename_build(builds: list[dict[str, Any]], build_id: str, name: str) -> list[dict[str, Any]]:
    output = []
    for entry in builds:
        if entry.get("id") == build_id:
            updated = dict(entry)
            updated["name"] = name.strip() or updated.get("name") or "Untitled Build"
            updated["updated_at"] = time.time()
            output.append(updated)
        else:
            output.append(entry)
    return output


def delete_build(builds: list[dict[str, Any]], build_id: str) -> list[dict[str, Any]]:
    return [entry for entry in builds if entry.get("id") != build_id]


def find_build(builds: list[dict[str, Any]], build_id: str) -> dict[str, Any] | None:
    for entry in builds:
        if entry.get("id") == build_id:
            return entry
    return None


def empty_slot_fields() -> list[list[dict[str, Any]]]:
    return [[] for _ in SLOT_CONFIGS]


def snapshot_from_state_values(
    *,
    selected_weapon_type: str,
    selected_weapon_category: str,
    selected_weapon: str,
    selected_attack_mode: str,
    evolution_selections: list[str],
    evolution_condition_toggles: list[RuntimeToggleField],
    evolution_stack_fields: list[RuntimeStackField],
    melee_combo_count: str,
    selected_stance_combo: str,
    progenitor_element: str,
    progenitor_value: float,
    ability_strength: float,
    selected_enemy_faction: str,
    selected_enemy: str,
    enemy_level: int,
    enemy_steel_path: bool,
    enemy_empowered: bool,
    optimize_body_part: str,
    slot_selected_upgrades: list[str],
    slot_policies: list[str],
    slot_ranks: list[int],
    slot_stacks: list[int],
    slot_conditions_enabled: list[bool],
    slot_fields: list[list[EditorField]],
    slot_riven_rolls: list[str],
    external_fields: list[EditorField],
    optimize_find_riven: bool,
    optimize_find_evolutions: bool,
    optimize_find_progenitor: bool,
    optimize_maximize_target: str,
    optimize_search_quality: str,
    optimize_dph_weight: int,
    optimize_flat_dot_weight: int,
    optimize_spatial: str,
    optimize_excluded_upgrades: list[str],
    optimize_default_exclusion_overrides: list[str],
    optimize_excluded_riven_stats: list[str],
    optimize_default_riven_exclusion_overrides: list[str],
) -> dict[str, Any]:
    return {
        "selected_weapon_type": selected_weapon_type,
        "selected_weapon_category": selected_weapon_category,
        "selected_weapon": selected_weapon,
        "selected_attack_mode": selected_attack_mode,
        "evolution_selections": list(evolution_selections),
        "evolution_condition_toggles": [_toggle_to_dict(field) for field in evolution_condition_toggles],
        "evolution_stack_fields": [_stack_to_dict(field) for field in evolution_stack_fields],
        "melee_combo_count": melee_combo_count,
        "selected_stance_combo": selected_stance_combo,
        "progenitor_element": progenitor_element,
        "progenitor_value": float(progenitor_value),
        "ability_strength": float(ability_strength),
        "selected_enemy_faction": selected_enemy_faction,
        "selected_enemy": selected_enemy,
        "enemy_level": int(enemy_level),
        "enemy_steel_path": bool(enemy_steel_path),
        "enemy_empowered": bool(enemy_empowered),
        "optimize_body_part": optimize_body_part,
        "slot_selected_upgrades": list(slot_selected_upgrades),
        "slot_policies": list(slot_policies),
        "slot_ranks": list(slot_ranks),
        "slot_stacks": list(slot_stacks),
        "slot_conditions_enabled": list(slot_conditions_enabled),
        "slot_fields": [[_editor_field_to_dict(field) for field in fields] for fields in slot_fields],
        "slot_riven_rolls": list(slot_riven_rolls),
        "external_fields": [_editor_field_to_dict(field) for field in external_fields],
        "optimize_find_riven": bool(optimize_find_riven),
        "optimize_find_evolutions": bool(optimize_find_evolutions),
        "optimize_find_progenitor": bool(optimize_find_progenitor),
        "optimize_maximize_target": optimize_maximize_target,
        "optimize_search_quality": optimize_search_quality,
        "optimize_dph_weight": int(optimize_dph_weight),
        "optimize_flat_dot_weight": int(optimize_flat_dot_weight),
        "optimize_spatial": str(optimize_spatial),
        "optimize_excluded_upgrades": list(optimize_excluded_upgrades),
        "optimize_default_exclusion_overrides": list(optimize_default_exclusion_overrides),
        "optimize_excluded_riven_stats": list(optimize_excluded_riven_stats),
        "optimize_default_riven_exclusion_overrides": list(optimize_default_riven_exclusion_overrides),
    }


def hydrate_editor_fields(raw_fields: list[Any] | None) -> list[EditorField]:
    return [_editor_field_from_dict(item) for item in (raw_fields or []) if isinstance(item, dict)]


def hydrate_slot_fields(raw_slots: list[Any] | None) -> list[list[EditorField]]:
    slots = list(raw_slots or [])
    while len(slots) < len(SLOT_CONFIGS):
        slots.append([])
    return [hydrate_editor_fields(fields if isinstance(fields, list) else []) for fields in slots[: len(SLOT_CONFIGS)]]


def hydrate_toggles(raw: list[Any] | None) -> list[RuntimeToggleField]:
    return [_toggle_from_dict(item) for item in (raw or []) if isinstance(item, dict)]


def hydrate_stacks(raw: list[Any] | None) -> list[RuntimeStackField]:
    return [_stack_from_dict(item) for item in (raw or []) if isinstance(item, dict)]


def pad_list(values: list[Any] | None, length: int, fill: Any) -> list[Any]:
    items = list(values or [])
    if len(items) < length:
        items.extend([deepcopy(fill) for _ in range(length - len(items))])
    return items[:length]


def empty_build_slot_defaults() -> dict[str, Any]:
    return {
        "slot_selected_upgrades": [NONE for _ in SLOT_CONFIGS],
        "slot_policies": [SLOT_POLICY_DISCARD for _ in SLOT_CONFIGS],
        "slot_ranks": [0 for _ in SLOT_CONFIGS],
        "slot_stacks": [0 for _ in SLOT_CONFIGS],
        "slot_conditions_enabled": [True for _ in SLOT_CONFIGS],
        "slot_fields": empty_slot_fields(),
        "slot_riven_rolls": ["2 Positive + 1 Negative" for _ in SLOT_CONFIGS],
        "external_fields": [],
        "evolution_selections": [],
        "evolution_condition_toggles": [],
        "evolution_stack_fields": [],
        "melee_combo_count": INITIAL_COMBO_OPTION,
        "selected_stance_combo": "neutral",
        "progenitor_element": NO_EFFECT,
        "progenitor_value": 0.0,
        "ability_strength": 100.0,
        "selected_attack_mode": "",
    }
