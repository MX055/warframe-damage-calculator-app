from __future__ import annotations

import copy
import json
from typing import Any

import reflex as rx
from warframe_damage_calculator import Upgrade
from warframe_damage_calculator.core.dist import Dist

from .constants import (
    ARCANE_FIELD,
    BUFF_FIELD,
    DAMAGE_TYPES,
    DEFAULT_DAMAGE_TYPES,
    DEFAULT_OPTIMIZE_MAXIMIZE,
    FIELD_WEAPON_RULES,
    MOD_FIELD,
    NO_EFFECT,
    OPTIMIZE_MAXIMIZE_OPTIONS,
    OPTIMIZE_MAXIMIZE_TARGETS,
    RIVEN_NON_NEGATIVE_STATS,
    RIVEN_ROLL_CONFIGS,
    RIVEN_ROLL_OPTIONS,
    RIVEN_STAT_ALIASES,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP,
    SLOT_POLICY_KEEP_IN_SLOT,
    SLOT_POLICY_OPTIONS,
    STANCE_SLOT_INDEX,
    WEAPON_CATEGORY_TYPES,
    UPGRADE_BOOL_FIELDS,
    UPGRADE_SCALAR_FIELDS,
)
from .data import (
    database_conditional_info,
    database_max_stacks,
    database_rank_bounds,
    database_upgrade,
    enemy_names_for_ui,
    is_faction_damage_stat,
    optimizer_excludes_upgrade_by_default,
    raw_riven_stats_database,
    raw_upgrade_metadata,
    raw_weapon_metadata,
    upgrade_conflicts_with_selected,
    preferred_exclusive_stance,
    selected_attack_category,
    stance_combo_key_for_attack_category,
    stance_combo_options_for_attack,
    upgrade_names_for_ui,
    _upgrade_names_for_ui,
    weapon_attack_modes,
    weapon_evolution_options,
    weapon_allows_stance,
    weapon_exclusive_stance_names,
    weapon_has_riven_disposition,
    weapon_names_for_type,
    weapon_uses_ability_strength,
)
from .optimizer import OptimizeRequest, SlotSpec, optimize_build as run_optimize_build
from .engine import (
    build_upgrade,
    clamp_number,
    configured_enemy,
    configured_weapon,
    contribution_for_category,
    contribution_lookup_for_weapon,
    contribution_rows,
    stance_combo_rows,
    custom_upgrade_from_entry,
    effective_damage_rows,
    field_label,
    format_contribution,
    format_upgrade_contributions,
    is_field_allowed,
    is_non_empty_upgrade,
    main_metrics,
    parse_float,
    parse_database_entry,
    parse_int,
    progenitor_upgrade,
    ranged_misc_metrics,
    resistant_metrics,
    upgrade_field_input_config,
    upgrade_stat_rows,
    weakpoint_metrics,
)
from .models import (
    ContributionRow,
    DamageResultRow,
    DisplayRow,
    EditorField,
    MetricRow,
)

NONE = "None"
CUSTOM = "Custom"
RIVEN = "Riven"

ALL_UPGRADE_FIELDS = tuple(dict.fromkeys((*MOD_FIELD, *ARCANE_FIELD, *BUFF_FIELD)))
FIELD_LABEL_TO_NAME = {field_label(name): name for name in ALL_UPGRADE_FIELDS}
DAMAGE_LABEL_TO_NAME = {field_label(name): name for name in DAMAGE_TYPES}

RIVEN_FLAT_STAT_UNITS = {
    "combo_duration": "s",
    "initial_combo": "",
    "punch_through": "m",
    "range": "m",
}

BASE_NUMBER_BOUNDS: dict[str, tuple[float, float, bool]] = {
    "base_crit_chance": (0.0, 10.0, False),
    "base_crit_damage": (1.0, 20.0, False),
    "base_status_chance": (0.0, 10.0, False),
    "base_multishot": (1.0, 100.0, False),
    "base_fire_rate": (0.05, 100.0, False),
    "base_reload_speed": (0.0, 20.0, False),
    "base_magazine_capacity": (1.0, 10000.0, True),
    "base_weakpoint_damage": (1.0, 20.0, False),
    "base_attack_speed": (0.0, 20.0, False),
    "base_recharge_rate": (0.0, 1000.0, False),
    "base_charge_time": (0.0, 20.0, False),
    "base_burst_count": (1.0, 100.0, True),
    "base_burst_delay": (0.0, 20.0, False),
    "progenitor_value": (0.0, 10.0, False),
    "ability_strength": (0.0, 1000.0, False),
}


def _default_direct_damage_fields() -> list[EditorField]:
    return [
        EditorField(name, field_label(name), 0.0, 0.0, 1_000_000_000.0, False)
        for name in DEFAULT_DAMAGE_TYPES
    ]


def _default_slot_max_ranks() -> list[int]:
    return [5 if config["kind"] == "arcane" else 10 for config in SLOT_CONFIGS]


def _empty_nested_list() -> list[list[Any]]:
    return [[] for _ in SLOT_CONFIGS]


def _custom_weapon_template(
    weapon_type_name: str = "Primary",
    weapon_category: str = "Rifle",
) -> str:
    melee = weapon_type_name == "Melee"
    stats = {
        "damage": {"impact": 30, "puncture": 45, "slash": 25},
        "forced_procs": {"slash": 1},
        "crit_chance": 0.24,
        "crit_damage": 2.2,
        "status_chance": 0.3,
    }
    if melee:
        stats["attack_speed"] = 1.0
    else:
        stats.update(
            {
                "multishot": 1,
                "fire_rate": 3.5,
                "ammo_cost": 1,
                "weakpoint_damage": 3,
            }
        )
    entry: dict[str, Any] = {
        "name": "Custom Weapon",
        "type": weapon_type_name.casefold(),
        "subtype": weapon_category.casefold(),
        "progenitor": True,
        "attacks": {
            "normal_attack": {
                "trigger": "melee" if melee else "semi",
                "delivery": "melee" if melee else "hitscan",
                "form": "normal",
                "stats": stats,
            }
        },
        "disposition": 1.0,
    }
    if not melee:
        entry["attacks"]["normal_attack"]["children"] = ["radial_attack"]
        entry["attacks"]["radial_attack"] = {
            "trigger": "semi",
            "delivery": "projectile",
            "aoe": True,
            "form": "normal",
            "stats": {
                "damage": {"blast": 50},
                "forced_procs": {"impact": 1},
                "crit_chance": 0.24,
                "crit_damage": 2.2,
                "status_chance": 0.3,
                "multishot": 1,
                "fire_rate": 3.5,
                "falloff": {
                    "start_range": 0,
                    "end_range": 5,
                    "final_multiplier": 0.5,
                },
            },
        }
        entry["ammo"] = {
            "reload_time": 2.0,
            "magazine_size": 30,
            "recharge_rate": 10.0,
        }
    return json.dumps(entry, indent=2)


def _custom_enemy_template() -> str:
    return json.dumps(
        {
            "name": "Custom Enemy",
            "faction": "Grineer",
            "base_level": 1,
            "runtime": {"level": 100, "steel_path": False, "empowered": False},
            "stats": {"health": 300, "shields": 0, "armor": 500, "overguard": 0},
            "bodyparts": {
                "body": {"type": "normal", "multiplier": 1.0},
                "head": {"type": "weakpoint", "multiplier": 3.0},
            },
            "modifiers": {"corrosive": 1.5, "impact": 1.5},
        },
        indent=2,
    )


def _custom_upgrade_templates(
    weapon_type_name: str = "Primary",
    weapon_category: str = "Rifle",
) -> list[str]:
    entries = []
    for config in SLOT_CONFIGS:
        entry = {
            "name": f"Custom {config['label']}",
            "type": config["kind"],
            "max_rank": 10 if config["kind"] == "mod" else 5,
            "stats": {
                "damage_bonus": [
                    {"value": 1.65, "mode": "proportional"},
                    {
                        "value": 0.15,
                        "mode": "base",
                        "when": "on_headshot",
                    },
                ],
                "crit_chance": [{"value": 0.2, "mode": "flat"}],
                "crit_damage": [
                    {
                        "value": 0.1,
                        "mode": "proportional",
                        "stacks": {"when": "stacks", "max": 5},
                    }
                ],
            },
            "runtime": {
                "rank": 10 if config["kind"] == "mod" else 5,
                "stacks": 5,
                "on_headshot": True,
            },
        }
        if config["exilus"]:
            entry["compatibility"] = {"exilus": True}
        if config.get("stance"):
            entry["compatibility"] = {**(entry.get("compatibility") or {}), "stance": True}
            entry["combos"] = {
                "neutral": {"name": "Neutral", "multiplier": 1.0, "hits": 1, "duration": 1.0},
            }
            entry["stats"] = {}
        entries.append(json.dumps(entry, indent=2))
    return entries


def _default_custom_upgrade_entries() -> list[str]:
    return ["" for _ in SLOT_CONFIGS]


def _empty_custom_upgrade_entry(index: int) -> str:
    config = SLOT_CONFIGS[index]
    return json.dumps(
        {
            "name": config["label"],
            "type": config["kind"],
            "max_rank": 0,
            "stats": {},
        }
    )


class CalculatorState(rx.State):
    """All browser-facing state is JSON-serializable.

    Calculator model objects are rebuilt inside `_recalculate` and never synced to
    the browser. This keeps the state small and compatible with Reflex/Redis.
    """

    initialized: bool = False
    selected_weapon_type: str = "Primary"
    selected_weapon_category: str = "Rifle"
    selected_weapon: str = NONE

    weapon_options: list[str] = rx.field(default_factory=lambda: [NONE])
    selected_enemy: str = NONE
    enemy_options: list[str] = rx.field(default_factory=lambda: [NONE, CUSTOM])
    custom_enemy_entry: str = ""
    custom_enemy_placeholder: str = rx.field(default_factory=_custom_enemy_template)
    enemy_level: int = 100
    enemy_steel_path: bool = False
    enemy_empowered: bool = False
    enemy_identity_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_bodypart_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_modifier_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    enemy_has_weakpoint: bool = False
    enemy_has_resistant: bool = False
    enemy_error: str = ""
    attack_mode_options: list[str] = rx.field(default_factory=list)
    selected_attack_mode: str = ""
    evolution_labels: list[str] = rx.field(default_factory=list)
    evolution_options: list[list[str]] = rx.field(default_factory=list)
    evolution_selections: list[str] = rx.field(default_factory=list)
    mod_options: list[str] = rx.field(default_factory=lambda: [NONE])
    stance_options: list[str] = rx.field(default_factory=lambda: [NONE])
    exilus_options: list[str] = rx.field(default_factory=lambda: [NONE])
    arcane_options: list[str] = rx.field(default_factory=lambda: [NONE])
    stance_combo_options: list[str] = rx.field(default_factory=lambda: ["neutral"])
    selected_stance_combo: str = "neutral"
    stance_combo_locked: bool = False
    exclusive_stance_weapon: bool = False
    stance_slot_available: bool = False
    stance_combo_available: bool = False
    riven_available: bool = False
    slot_upgrade_options: list[list[str]] = rx.field(
        default_factory=lambda: [[NONE] for _ in SLOT_CONFIGS]
    )
    custom_weapon_entry: str = ""
    custom_weapon_placeholder: str = rx.field(default_factory=_custom_weapon_template)
    custom_upgrade_entries: list[str] = rx.field(
        default_factory=_default_custom_upgrade_entries
    )
    custom_upgrade_placeholders: list[str] = rx.field(
        default_factory=_custom_upgrade_templates
    )

    progenitor_element: str = NO_EFFECT
    progenitor_value: float = 0.0
    ability_strength: float = 100.0
    ability_strength_available: bool = False

    is_battery: bool = False
    is_charge_weapon: bool = False
    is_burst_weapon: bool = False
    is_beam: bool = False

    base_crit_chance: float = 0.0
    base_crit_damage: float = 1.0
    base_status_chance: float = 0.0
    base_multishot: float = 1.0
    base_fire_rate: float = 0.05
    base_reload_speed: float = 0.0
    base_magazine_capacity: int = 1
    base_weakpoint_damage: float = 3.0
    base_attack_speed: float = 1.0
    base_recharge_rate: float = 0.0
    base_charge_time: float = 0.0
    base_burst_count: int = 1
    base_burst_delay: float = 0.0

    direct_damage_fields: list[EditorField] = rx.field(
        default_factory=_default_direct_damage_fields
    )
    forced_proc_fields: list[EditorField] = rx.field(default_factory=list)
    explosion_damage_fields: list[EditorField] = rx.field(default_factory=list)
    explosion_forced_proc_fields: list[EditorField] = rx.field(default_factory=list)

    direct_damage_options: list[str] = rx.field(default_factory=list)
    forced_proc_options: list[str] = rx.field(default_factory=list)
    explosion_damage_options: list[str] = rx.field(default_factory=list)
    explosion_forced_proc_options: list[str] = rx.field(default_factory=list)

    direct_damage_pending: str = ""
    forced_proc_pending: str = ""
    explosion_damage_pending: str = ""
    explosion_forced_proc_pending: str = ""

    slot_selected_upgrades: list[str] = rx.field(
        default_factory=lambda: [NONE for _ in SLOT_CONFIGS]
    )
    slot_policies: list[str] = rx.field(
        default_factory=lambda: [SLOT_POLICY_DISCARD for _ in SLOT_CONFIGS]
    )
    slot_ranks: list[int] = rx.field(default_factory=lambda: [0 for _ in SLOT_CONFIGS])
    slot_max_ranks: list[int] = rx.field(default_factory=_default_slot_max_ranks)
    slot_stacks: list[int] = rx.field(default_factory=lambda: [0 for _ in SLOT_CONFIGS])
    slot_max_stacks: list[int] = rx.field(
        default_factory=lambda: [0 for _ in SLOT_CONFIGS]
    )
    slot_has_conditionals: list[bool] = rx.field(
        default_factory=lambda: [False for _ in SLOT_CONFIGS]
    )
    slot_conditions_enabled: list[bool] = rx.field(
        default_factory=lambda: [True for _ in SLOT_CONFIGS]
    )
    slot_condition_labels: list[str] = rx.field(
        default_factory=lambda: ["" for _ in SLOT_CONFIGS]
    )
    slot_fields: list[list[EditorField]] = rx.field(default_factory=_empty_nested_list)
    slot_available_fields: list[list[str]] = rx.field(default_factory=_empty_nested_list)
    slot_pending_fields: list[str] = rx.field(
        default_factory=lambda: ["" for _ in SLOT_CONFIGS]
    )
    slot_riven_rolls: list[str] = rx.field(
        default_factory=lambda: [
            "2 Positive + 1 Negative" for _ in SLOT_CONFIGS
        ]
    )
    slot_stat_rows: list[list[DisplayRow]] = rx.field(default_factory=_empty_nested_list)
    slot_contributions: list[str] = rx.field(
        default_factory=lambda: ["—" for _ in SLOT_CONFIGS]
    )
    slot_editor_open: list[bool] = rx.field(default_factory=lambda: [False for _ in SLOT_CONFIGS])
    clear_keep_slots: list[bool] = rx.field(default_factory=lambda: [False for _ in SLOT_CONFIGS])
    optimize_find_riven: bool = False
    optimize_find_evolutions: bool = False
    optimize_maximize_target: str = DEFAULT_OPTIMIZE_MAXIMIZE
    optimize_maximize_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_MAXIMIZE_OPTIONS))
    optimize_status: str = ""
    optimize_running: bool = False
    optimize_best_dps: str = ""
    optimize_progress: float = 0.0
    optimize_progress_width: str = "0%"
    optimize_phase: str = ""
    optimize_evaluations: int = 0
    optimize_revision: int = 0
    optimize_excluded_upgrades: list[str] = rx.field(default_factory=list)
    optimize_default_exclusion_overrides: list[str] = rx.field(default_factory=list)
    optimize_upgrade_exclusion_options: list[str] = rx.field(default_factory=list)
    optimize_pending_excluded_upgrade: str = ""
    optimize_excluded_riven_stats: list[str] = rx.field(default_factory=list)
    optimize_default_riven_exclusion_overrides: list[str] = rx.field(default_factory=list)
    optimize_riven_stat_exclusion_options: list[str] = rx.field(default_factory=list)
    optimize_pending_excluded_riven_stat: str = ""

    external_fields: list[EditorField] = rx.field(default_factory=list)
    external_available_fields: list[str] = rx.field(default_factory=list)
    external_pending_field: str = ""

    main_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    weakpoint_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    resistant_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    ranged_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    misc_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    result_metrics: list[MetricRow] = rx.field(default_factory=list)
    damage_result_rows: list[DamageResultRow] = rx.field(default_factory=list)
    contribution_result_rows: list[ContributionRow] = rx.field(default_factory=list)
    result_summary: str = ""
    result_contribution_summary: str = ""
    result_error: str = ""
    result_errors: list[str] = rx.field(default_factory=list)
    result_ready: bool = False

    @rx.var
    def custom_weapon(self) -> bool:
        return self.selected_weapon == CUSTOM

    @rx.var
    def custom_enemy(self) -> bool:
        return self.selected_enemy == CUSTOM

    @rx.var
    def no_enemy(self) -> bool:
        return self.selected_enemy == NONE

    @rx.var
    def show_enemy_inline_error(self) -> bool:
        return bool(self.enemy_error and not (self.selected_enemy == CUSTOM and not self.custom_enemy_entry.strip()))

    @rx.var
    def no_weapon(self) -> bool:
        return self.selected_weapon == NONE

    @rx.var
    def has_equipped_upgrades(self) -> bool:
        return any(selected != NONE for selected in self.slot_selected_upgrades)

    @rx.var
    def has_build_or_buffs(self) -> bool:
        return any(selected != NONE for selected in self.slot_selected_upgrades) or bool(self.external_fields)

    @rx.var
    def optimizer_enabled(self) -> bool:
        return self.selected_weapon != NONE

    @rx.var
    def riven_optimize_disabled(self) -> bool:
        if not self.riven_available:
            return True
        return any(
            selected == RIVEN and policy in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT}
            for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
        )

    @rx.var
    def evolution_optimize_available(self) -> bool:
        return len(self.evolution_options) > 0

    @rx.var
    def ranged_weapon(self) -> bool:
        return self.selected_weapon_type != "Melee"

    @rx.var
    def melee_weapon(self) -> bool:
        return self.selected_weapon_type == "Melee"

    @rx.var
    def has_error(self) -> bool:
        return bool(self.result_errors)

    @rx.var
    def supports_progenitor(self) -> bool:
        return self._supports_progenitor()

    def _ability_strength_multiplier(self) -> float | None:
        if not self.ability_strength_available:
            return None
        return max(float(self.ability_strength), 0.0) / 100.0

    def _clear_optimizer_result(self):
        self.optimize_status = ""
        self.optimize_best_dps = ""
        self.optimize_progress = 0.0
        self.optimize_progress_width = "0%"
        self.optimize_phase = ""
        self.optimize_evaluations = 0

    def _invalidate_optimizer_result(self):
        self.optimize_revision += 1
        self._clear_optimizer_result()

    def _reset_optimizer_settings(self):
        self._invalidate_optimizer_result()
        self.optimize_find_riven = False
        self.optimize_find_evolutions = False
        self.optimize_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE
        self.optimize_excluded_upgrades = []
        self.optimize_default_exclusion_overrides = []
        self.optimize_upgrade_exclusion_options = []
        self.optimize_pending_excluded_upgrade = ""
        self.optimize_excluded_riven_stats = []
        self.optimize_default_riven_exclusion_overrides = []
        self.optimize_riven_stat_exclusion_options = []
        self.optimize_pending_excluded_riven_stat = ""

    def _clear_build_state(self, *, keep_marked: bool = False):
        keep_slots = list(self.clear_keep_slots)
        for index in range(len(SLOT_CONFIGS)):
            if keep_marked and keep_slots[index] and self.slot_selected_upgrades[index] != NONE:
                continue
            self._clear_slot(index)
            keep_slots[index] = False
        self.clear_keep_slots = keep_slots
        self.slot_editor_open = [False for _ in SLOT_CONFIGS]
        self.external_fields = []
        self._refresh_external_field_options()

    def _reset_for_weapon_change(self):
        self._clear_build_state()
        self._reset_optimizer_settings()

    @rx.event
    def initialize(self):
        if self.initialized:
            return
        self.initialized = True
        self._refresh_enemy_options()
        self._refresh_weapon_options()
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_damage_options()
        self._refresh_all_field_options()
        self._recalculate()

    @rx.event
    def set_weapon_type(self, value: str):
        if value not in WEAPON_CATEGORY_TYPES or value == self.selected_weapon_category:
            return
        self._reset_for_weapon_change()
        self.selected_weapon_category = value
        self.selected_weapon_type = WEAPON_CATEGORY_TYPES[value]
        self.selected_weapon = NONE
        self.custom_weapon_entry = ""
        self.custom_weapon_placeholder = _custom_weapon_template(
            self.selected_weapon_type,
            self.selected_weapon_category,
        )
        self.custom_upgrade_placeholders = _custom_upgrade_templates(
            self.selected_weapon_type,
            self.selected_weapon_category,
        )
        if self.selected_weapon_type == "Melee":
            self.is_battery = False
            self.is_charge_weapon = False
            self.is_burst_weapon = False
            self.is_beam = False
        self._refresh_weapon_options()
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._filter_disallowed_custom_fields()
        self._refresh_all_riven_field_limits()
        self._refresh_all_field_options()
        self._recalculate()

    @rx.event
    def set_weapon(self, value: str):
        selected_weapon = value if value in self.weapon_options else NONE
        if selected_weapon == self.selected_weapon:
            return
        self._reset_for_weapon_change()
        self.selected_weapon = selected_weapon
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_enemy(self, value: str):
        self.selected_enemy = value if value in self.enemy_options else NONE
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_custom_enemy_entry(self, value: str):
        self.custom_enemy_entry = value
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_enemy_level(self, value: str):
        self.enemy_level = max(1, min(parse_int(value, self.enemy_level), 9999))
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_enemy_toggle(self, field_name: str, value: bool):
        if field_name not in {"enemy_steel_path", "enemy_empowered"}:
            return
        setattr(self, field_name, bool(value))
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_custom_weapon_entry(self, value: str):
        self.custom_weapon_entry = value
        self._invalidate_optimizer_result()
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_custom_upgrade_entry(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        entries = list(self.custom_upgrade_entries)
        entries[index] = value
        self.custom_upgrade_entries = entries
        if index == STANCE_SLOT_INDEX:
            self._refresh_stance_combo_options()
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_attack_mode(self, value: str):
        if value not in self.attack_mode_options:
            return
        self.selected_attack_mode = value
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_evolution(self, index: int, value: str):
        if not 0 <= index < len(self.evolution_options) or value not in self.evolution_options[index]:
            return
        selections = list(self.evolution_selections)
        selections[index] = value
        self.evolution_selections = selections
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_progenitor_element(self, value: str):
        self.progenitor_element = value
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_base_number(self, field_name: str, value: str):
        bounds = BASE_NUMBER_BOUNDS.get(field_name)
        if bounds is None:
            return
        minimum, maximum, integer = bounds
        current = getattr(self, field_name)
        parsed = parse_int(value, int(current)) if integer else parse_float(value, float(current))
        parsed = clamp_number(float(parsed), minimum, maximum)
        setattr(self, field_name, int(parsed) if integer else float(parsed))
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_base_toggle(self, field_name: str, value: bool):
        if field_name not in {
            "is_battery",
            "is_charge_weapon",
            "is_burst_weapon",
            "is_beam",
        }:
            return
        setattr(self, field_name, bool(value))
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._recalculate()

    @rx.event
    def set_damage_pending(self, group: str, value: str):
        if group not in self._damage_groups():
            return
        setattr(self, f"{group}_pending", value)

    @rx.event
    def add_damage_type(self, group: str):
        fields = copy.deepcopy(self._get_damage_fields(group))
        pending = getattr(self, f"{group}_pending", "")
        damage_name = DAMAGE_LABEL_TO_NAME.get(pending)
        if not damage_name or any(field.name == damage_name for field in fields):
            return
        fields.append(
            EditorField(damage_name, field_label(damage_name), 0.0, 0.0, 1_000_000_000.0, False)
        )
        self._set_damage_fields(group, fields)
        self._refresh_damage_options()
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def remove_damage_type(self, group: str, damage_name: str):
        fields = [
            field
            for field in copy.deepcopy(self._get_damage_fields(group))
            if field.name != damage_name
        ]
        self._set_damage_fields(group, fields)
        self._refresh_damage_options()
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_damage_value(self, group: str, damage_name: str, value: str):
        fields = copy.deepcopy(self._get_damage_fields(group))
        for field in fields:
            if field.name == damage_name:
                field.value = max(0.0, parse_float(value, field.value))
                break
        self._set_damage_fields(group, fields)
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_slot_editor_open(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        open_editors = list(self.slot_editor_open)
        open_editors[index] = bool(value)
        self.slot_editor_open = open_editors

    @rx.event
    def set_clear_keep_slot(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS) or self.slot_selected_upgrades[index] == NONE:
            return
        keep_slots = list(self.clear_keep_slots)
        keep_slots[index] = bool(value)
        self.clear_keep_slots = keep_slots

    @rx.event
    def clear_build_and_buffs(self):
        self._clear_build_state(keep_marked=True)
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_all_field_options()
        self._recalculate()

    @rx.event
    def remove_build_upgrade(self, index: int):
        if not 0 <= index < len(SLOT_CONFIGS) or self.slot_selected_upgrades[index] == NONE:
            return
        self._clear_slot(index)
        keep_slots = list(self.clear_keep_slots)
        keep_slots[index] = False
        self.clear_keep_slots = keep_slots
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_all_field_options()
        self._recalculate()

    @rx.event
    def set_slot_upgrade(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        if value not in self.slot_upgrade_options[index]:
            return
        self._invalidate_optimizer_result()
        selected = list(self.slot_selected_upgrades)
        previous = selected[index]
        selected[index] = value
        self.slot_selected_upgrades = selected

        policies = list(self.slot_policies)
        if value == NONE:
            self._clear_slot(index, reset_policy=True)
            if index == STANCE_SLOT_INDEX:
                self._refresh_stance_combo_options()
            self._refresh_slot_upgrade_options()
            self._refresh_slot_condition_metadata()
            self._refresh_slot_field_options()
            self._recalculate()
            return
        if previous == NONE or value in self.optimize_excluded_upgrades:
            policies[index] = SLOT_POLICY_DISCARD
            self.slot_policies = policies

        max_ranks = list(self.slot_max_ranks)
        ranks = list(self.slot_ranks)
        max_stacks = list(self.slot_max_stacks)
        stacks = list(self.slot_stacks)

        if value == CUSTOM:
            max_ranks[index] = 0
            ranks[index] = 0
            max_stacks[index] = 0
            stacks[index] = 0
        elif value == RIVEN:
            max_ranks[index] = 0
            ranks[index] = 0
            max_stacks[index] = 0
            stacks[index] = 0
            if previous != RIVEN:
                all_fields = copy.deepcopy(self.slot_fields)
                all_fields[index] = []
                self.slot_fields = all_fields
        else:
            is_arcane = SLOT_CONFIGS[index]["kind"] == "arcane"
            _, maximum_rank = database_rank_bounds(value, is_arcane_slot=is_arcane)
            maximum_stacks = database_max_stacks(value, is_arcane_slot=is_arcane) or 0
            max_ranks[index] = maximum_rank
            ranks[index] = maximum_rank
            max_stacks[index] = maximum_stacks
            stacks[index] = maximum_stacks

        self.slot_max_ranks = max_ranks
        self.slot_ranks = ranks
        self.slot_max_stacks = max_stacks
        self.slot_stacks = stacks

        conditions_enabled = list(self.slot_conditions_enabled)
        conditions_enabled[index] = True
        self.slot_conditions_enabled = conditions_enabled
        if index == STANCE_SLOT_INDEX:
            self._refresh_stance_combo_options()
        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_stance_combo(self, value: str):
        if value not in self.stance_combo_options:
            return
        self.selected_stance_combo = value
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_slot_policy(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS) or value not in SLOT_POLICY_OPTIONS:
            return
        policies = list(self.slot_policies)
        policies[index] = value
        self.slot_policies = policies
        self._invalidate_optimizer_result()
        selected = self.slot_selected_upgrades[index]
        if value in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT} and selected in self.optimize_excluded_upgrades:
            if optimizer_excludes_upgrade_by_default(selected) and selected not in self.optimize_default_exclusion_overrides:
                self.optimize_default_exclusion_overrides = [*self.optimize_default_exclusion_overrides, selected]
            self.optimize_excluded_upgrades = [name for name in self.optimize_excluded_upgrades if name != selected]
            self._refresh_optimizer_exclusion_options()

    @rx.event
    def set_optimize_pending_excluded_upgrade(self, value: str):
        if value in self.optimize_upgrade_exclusion_options:
            self.optimize_pending_excluded_upgrade = value

    @rx.event
    def add_optimize_excluded_upgrade(self):
        name = self.optimize_pending_excluded_upgrade
        if not name or name not in self.optimize_upgrade_exclusion_options:
            return
        self.optimize_default_exclusion_overrides = [item for item in self.optimize_default_exclusion_overrides if item != name]
        self.optimize_excluded_upgrades = [*self.optimize_excluded_upgrades, name]
        policies = list(self.slot_policies)
        for index, selected in enumerate(self.slot_selected_upgrades):
            if selected == name:
                policies[index] = SLOT_POLICY_DISCARD
        self.slot_policies = policies
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def remove_optimize_excluded_upgrade(self, name: str):
        if optimizer_excludes_upgrade_by_default(name) and name not in self.optimize_default_exclusion_overrides:
            self.optimize_default_exclusion_overrides = [*self.optimize_default_exclusion_overrides, name]
        self.optimize_excluded_upgrades = [item for item in self.optimize_excluded_upgrades if item != name]
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def clear_optimize_excluded_upgrades(self):
        defaults = [name for name in self.optimize_excluded_upgrades if optimizer_excludes_upgrade_by_default(name)]
        self.optimize_default_exclusion_overrides = list(dict.fromkeys([*self.optimize_default_exclusion_overrides, *defaults]))
        self.optimize_excluded_upgrades = []
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def set_optimize_pending_excluded_riven_stat(self, value: str):
        if value in self.optimize_riven_stat_exclusion_options:
            self.optimize_pending_excluded_riven_stat = value

    @rx.event
    def add_optimize_excluded_riven_stat(self):
        label = self.optimize_pending_excluded_riven_stat
        if not label or label not in self.optimize_riven_stat_exclusion_options:
            return
        self.optimize_default_riven_exclusion_overrides = [item for item in self.optimize_default_riven_exclusion_overrides if item != label]
        self.optimize_excluded_riven_stats = [*self.optimize_excluded_riven_stats, label]
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def remove_optimize_excluded_riven_stat(self, label: str):
        field_name = self._riven_field_from_label(label)
        if field_name and is_faction_damage_stat(field_name) and label not in self.optimize_default_riven_exclusion_overrides:
            self.optimize_default_riven_exclusion_overrides = [*self.optimize_default_riven_exclusion_overrides, label]
        self.optimize_excluded_riven_stats = [item for item in self.optimize_excluded_riven_stats if item != label]
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def clear_optimize_excluded_riven_stats(self):
        defaults = [label for label in self.optimize_excluded_riven_stats if (field_name := self._riven_field_from_label(label)) and is_faction_damage_stat(field_name)]
        self.optimize_default_riven_exclusion_overrides = list(dict.fromkeys([*self.optimize_default_riven_exclusion_overrides, *defaults]))
        self.optimize_excluded_riven_stats = []
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def set_optimize_find_riven(self, value: bool):
        locked = (not self.riven_available) or any(
            selected == RIVEN and policy in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT}
            for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
        )
        self.optimize_find_riven = bool(value) and not locked
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_find_evolutions(self, value: bool):
        self.optimize_find_evolutions = bool(value) and bool(self.evolution_options)
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_maximize_target(self, value: str):
        if value in self.optimize_maximize_options:
            self.optimize_maximize_target = value
            self._invalidate_optimizer_result()

    @rx.event(background=True)
    async def optimize_build(self):
        import asyncio
        import queue as sync_queue

        async with self:
            if self.selected_weapon == NONE or self.optimize_running:
                return
            self.optimize_running = True
            self.optimize_status = ""
            self.optimize_phase = "Starting…"
            self.optimize_progress = 0.0
            self.optimize_progress_width = "0%"
            self.optimize_evaluations = 0
            self.optimize_best_dps = ""
            revision = self.optimize_revision
            evolutions = {
                parse_int(self.evolution_labels[index].rsplit(" ", 1)[-1]): parse_int(selection.split()[1])
                for index, selection in enumerate(self.evolution_selections)
                if selection != "None"
            }
            riven_locked = any(
                selected == RIVEN and policy in {SLOT_POLICY_KEEP, SLOT_POLICY_KEEP_IN_SLOT}
                for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
            )
            custom_weapon = self.selected_weapon == CUSTOM
            request = OptimizeRequest(
                weapon_type=self.selected_weapon_type,
                weapon_category=self.selected_weapon_category,
                weapon_name=self.selected_weapon,
                custom_weapon=custom_weapon,
                custom_weapon_entry=self.custom_weapon_entry,
                attack_mode=self.selected_attack_mode,
                evolutions=evolutions,
                progenitor_element=self.progenitor_element if self._supports_progenitor() else NO_EFFECT,
                progenitor_value=self.progenitor_value,
                external_fields={field.name: field.value for field in self.external_fields},
                enemy_name=self.selected_enemy,
                custom_enemy_entry=self.custom_enemy_entry,
                enemy_level=self.enemy_level,
                enemy_steel_path=self.enemy_steel_path,
                enemy_empowered=self.enemy_empowered,
                slots=[
                    SlotSpec(
                        index=index,
                        kind=config["kind"],
                        exilus=bool(config["exilus"]),
                        stance=bool(config.get("stance")),
                        selected=NONE if config.get("stance") and not self.stance_combo_available else self.slot_selected_upgrades[index],
                        policy=SLOT_POLICY_KEEP_IN_SLOT if config.get("stance") and not self.stance_combo_available else self.slot_policies[index],
                        rank=self.slot_ranks[index],
                        stacks=self.slot_stacks[index],
                        condition=self.slot_conditions_enabled[index],
                        custom_entry=self.custom_upgrade_entries[index],
                        riven_roll=self.slot_riven_rolls[index],
                        riven_fields={field.name: float(field.value) for field in self.slot_fields[index]},
                    )
                    for index, config in enumerate(SLOT_CONFIGS)
                ],
                find_optimal_riven=bool(self.optimize_find_riven) and not riven_locked and self.riven_available,
                find_optimal_evolutions=bool(self.optimize_find_evolutions) and bool(self.evolution_options),
                maximize_target=OPTIMIZE_MAXIMIZE_TARGETS.get(self.optimize_maximize_target, OPTIMIZE_MAXIMIZE_TARGETS[DEFAULT_OPTIMIZE_MAXIMIZE]),
                stance_combo=self.selected_stance_combo if self.stance_combo_available else "neutral",
                ability_strength=self._ability_strength_multiplier(),
                excluded_upgrades=set(self.optimize_excluded_upgrades),
                excluded_riven_stats={
                    name
                    for label in self.optimize_excluded_riven_stats
                    if (name := self._riven_field_from_label(label)) is not None
                },
                riven_disposition=self._riven_disposition(),
                riven_base_stats=self._riven_base_stats(),
                riven_non_negative=set(RIVEN_NON_NEGATIVE_STATS),
            )

        q: sync_queue.Queue = sync_queue.Queue()

        def on_progress(phase: str, fraction: float, evaluations: int, best_dps: float | None):
            q.put(("progress", phase, fraction, evaluations, best_dps))

        def worker():
            try:
                result = run_optimize_build(request, progress=on_progress)
                q.put(("done", result))
            except Exception as exc:
                q.put(("error", exc))

        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, worker)

        while True:
            await asyncio.sleep(0.15)
            drained = False
            while True:
                try:
                    msg = q.get_nowait()
                except sync_queue.Empty:
                    break
                drained = True
                if msg[0] == "progress":
                    _, phase, fraction, evaluations, best_dps = msg
                    async with self:
                        if self.optimize_revision != revision:
                            continue
                        self.optimize_phase = phase
                        self.optimize_progress = float(fraction) * 100.0
                        self.optimize_progress_width = f"{self.optimize_progress:.1f}%"
                        self.optimize_evaluations = int(evaluations)
                        if best_dps is not None:
                            self.optimize_best_dps = f"{best_dps:,.2f}"
                elif msg[0] == "done":
                    result = msg[1]
                    async with self:
                        if self.optimize_revision != revision:
                            self.optimize_running = False
                        else:
                            self._apply_optimize_result(result)
                            self.optimize_status = result.message
                            self.optimize_best_dps = f"{result.total_dps:,.2f}"
                            self.optimize_phase = "Done"
                            self.optimize_progress = 100.0
                            self.optimize_progress_width = "100%"
                            self.optimize_evaluations = result.evaluations
                            self._refresh_upgrade_options()
                            self._refresh_all_riven_field_limits()
                            self._refresh_slot_field_options()
                            self._recalculate()
                            self.optimize_running = False
                    await fut
                    return
                elif msg[0] == "error":
                    exc = msg[1]
                    async with self:
                        if self.optimize_revision == revision:
                            self.optimize_status = f"{type(exc).__name__}: {exc}"
                            self.optimize_phase = "Failed"
                        self.optimize_running = False
                    await fut
                    return
            if fut.done() and not drained:
                exc = fut.exception()
                async with self:
                    if exc and self.optimize_revision == revision:
                        self.optimize_status = f"{type(exc).__name__}: {exc}"
                        self.optimize_phase = "Failed"
                    self.optimize_running = False
                return

    @rx.event
    def set_slot_condition(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        enabled = list(self.slot_conditions_enabled)
        enabled[index] = bool(value)
        self.slot_conditions_enabled = enabled
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_slot_rank(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        ranks = list(self.slot_ranks)
        ranks[index] = max(0, min(parse_int(value, ranks[index]), self.slot_max_ranks[index]))
        self.slot_ranks = ranks
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_slot_stacks(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        stacks = list(self.slot_stacks)
        stacks[index] = max(
            0,
            min(parse_int(value, stacks[index]), self.slot_max_stacks[index]),
        )
        self.slot_stacks = stacks
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_slot_pending_field(self, index: int, value: str):
        pending = list(self.slot_pending_fields)
        if 0 <= index < len(pending):
            pending[index] = value
            self.slot_pending_fields = pending

    @rx.event
    def set_riven_roll(self, index: int, value: str):
        if (
            not 0 <= index < len(SLOT_CONFIGS)
            or value not in RIVEN_ROLL_OPTIONS
        ):
            return
        rolls = list(self.slot_riven_rolls)
        if rolls[index] == value:
            return
        rolls[index] = value
        self.slot_riven_rolls = rolls
        all_fields = copy.deepcopy(self.slot_fields)
        all_fields[index] = []
        self.slot_fields = all_fields
        self._invalidate_optimizer_result()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def add_slot_field(self, index: int):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        label = self.slot_pending_fields[index]
        field_name = (
            self._riven_field_from_label(label)
            if self.slot_selected_upgrades[index] == RIVEN
            else FIELD_LABEL_TO_NAME.get(label)
        )
        if not field_name:
            return

        all_fields = copy.deepcopy(self.slot_fields)
        if any(field.name == field_name for field in all_fields[index]):
            return
        if self.slot_selected_upgrades[index] == RIVEN:
            positive_count, negative_count, _bonus, _malus = (
                self._riven_roll_config(index)
            )
            position = len(all_fields[index])
            if position >= positive_count + negative_count:
                return
            negative = position >= positive_count
            limits = self._riven_field_limits(index, field_name, negative)
            if limits is None:
                return
            min_value, max_value = limits
            all_fields[index].append(
                EditorField(
                    field_name,
                    field_label(field_name),
                    (min_value + max_value) / 2,
                    min_value,
                    max_value,
                    False,
                )
            )
            self.slot_fields = all_fields
            self._invalidate_optimizer_result()
            self._refresh_slot_field_options()
            self._recalculate()
            return
        config = SLOT_CONFIGS[index]
        min_value, max_value, default_value, integer = upgrade_field_input_config(
            config["options"].get(field_name),
            allow_negative=config["kind"] != "arcane",
        )
        all_fields[index].append(
            EditorField(
                field_name,
                field_label(field_name),
                default_value,
                min_value,
                max_value,
                integer,
            )
        )
        self.slot_fields = all_fields
        self._invalidate_optimizer_result()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def remove_slot_field(self, index: int, field_name: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        all_fields = copy.deepcopy(self.slot_fields)
        all_fields[index] = [field for field in all_fields[index] if field.name != field_name]
        self.slot_fields = all_fields
        self._invalidate_optimizer_result()
        self._refresh_riven_field_limits(index)
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_slot_field_value(self, index: int, field_name: str, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        all_fields = copy.deepcopy(self.slot_fields)
        for field in all_fields[index]:
            if field.name == field_name:
                parsed = parse_int(value, int(field.value)) if field.integer else parse_float(value, field.value)
                parsed = clamp_number(float(parsed), field.min_value, field.max_value)
                field.value = int(parsed) if field.integer else float(parsed)
                break
        self.slot_fields = all_fields
        self._invalidate_optimizer_result()
        self._recalculate()

    @rx.event
    def set_external_pending_field(self, value: str):
        self.external_pending_field = value

    @rx.event
    def add_external_field(self):
        field_name = FIELD_LABEL_TO_NAME.get(self.external_pending_field)
        if not field_name or any(field.name == field_name for field in self.external_fields):
            return
        min_value, max_value, default_value, integer = upgrade_field_input_config(
            BUFF_FIELD.get(field_name),
            allow_negative=False,
        )
        fields = copy.deepcopy(self.external_fields)
        fields.append(
            EditorField(
                field_name,
                field_label(field_name),
                default_value,
                min_value,
                max_value,
                integer,
            )
        )
        self.external_fields = fields
        self._invalidate_optimizer_result()
        self._refresh_external_field_options()
        self._recalculate()

    @rx.event
    def remove_external_field(self, field_name: str):
        self.external_fields = [
            field
            for field in copy.deepcopy(self.external_fields)
            if field.name != field_name
        ]
        self._invalidate_optimizer_result()
        self._refresh_external_field_options()
        self._recalculate()

    @rx.event
    def set_external_field_value(self, field_name: str, value: str):
        fields = copy.deepcopy(self.external_fields)
        for field in fields:
            if field.name == field_name:
                parsed = parse_int(value, int(field.value)) if field.integer else parse_float(value, field.value)
                parsed = clamp_number(float(parsed), field.min_value, field.max_value)
                field.value = int(parsed) if field.integer else float(parsed)
                break
        self.external_fields = fields
        self._invalidate_optimizer_result()
        self._recalculate()

    def _refresh_enemy_options(self):
        self.enemy_options = [NONE, CUSTOM, *enemy_names_for_ui()]
        if self.selected_enemy not in self.enemy_options:
            self.selected_enemy = NONE

    def _refresh_weapon_options(self):
        self.weapon_options = [
            NONE,
            CUSTOM,
            *weapon_names_for_type(
                self.selected_weapon_type,
                self.selected_weapon_category,
            ),
        ]
        if self.selected_weapon not in self.weapon_options:
            self.selected_weapon = NONE

    def _refresh_ability_strength_available(self, *, custom_metadata: dict | None = None):
        if self.selected_weapon == NONE:
            self.ability_strength_available = False
            return
        weapon_name = None if self.custom_weapon else self.selected_weapon
        metadata = custom_metadata if self.custom_weapon else None
        if self.custom_weapon and metadata is None:
            metadata = self._custom_weapon_metadata()
        self.ability_strength_available = weapon_uses_ability_strength(weapon_name, custom_metadata=metadata)

    def _refresh_weapon_features(self):
        if self.selected_weapon == NONE:
            self.attack_mode_options = []
            self.selected_attack_mode = ""
            self.evolution_labels = []
            self.evolution_options = []
            self.evolution_selections = []
            self.ability_strength_available = False
            return
        if self.custom_weapon:
            if not self.custom_weapon_entry.strip():
                metadata = {}
            else:
                try:
                    metadata = parse_database_entry(
                        self.custom_weapon_entry,
                        default_name="Custom Weapon",
                        default_type=self.selected_weapon_type.casefold(),
                    )
                except ValueError:
                    metadata = {}
            self._refresh_ability_strength_available(custom_metadata=metadata)
            attacks = metadata.get("attacks") or {}
            child_names = {
                child
                for attack in attacks.values()
                if isinstance(attack, dict)
                for child in attack.get("children", [])
            }
            names = [name for name in attacks if name not in child_names] or list(attacks)
            modes = [name.replace("_", " ").title() for name in names]
            self.attack_mode_options = modes
            if self.selected_attack_mode not in modes:
                self.selected_attack_mode = modes[0] if modes else ""
            tiers = []
            for tier, perks in (metadata.get("evolutions") or {}).items():
                options = ["None"]
                for perk, data in perks.items():
                    description = str((data or {}).get("description", "")).strip()
                    options.append(
                        f"Perk {perk}" + (f" — {description}" if description else "")
                    )
                tiers.append(
                    {
                        "label": f"Evolution {tier}",
                        "options": options,
                    }
                )
            previous = list(self.evolution_selections)
            self.evolution_labels = [tier["label"] for tier in tiers]
            self.evolution_options = [tier["options"] for tier in tiers]
            self.evolution_selections = [
                previous[index]
                if index < len(previous) and previous[index] in tier["options"]
                else "None"
                for index, tier in enumerate(tiers)
            ]
            if not tiers:
                self.optimize_find_evolutions = False
            return
        self._refresh_ability_strength_available()
        modes = list(weapon_attack_modes(self.selected_weapon))
        self.attack_mode_options = modes
        if self.selected_attack_mode not in modes:
            self.selected_attack_mode = modes[0] if modes else ""
        tiers = weapon_evolution_options(self.selected_weapon)
        self.evolution_labels = [tier["label"] for tier in tiers]
        self.evolution_options = [tier["options"] for tier in tiers]
        self.evolution_selections = ["None" for _ in tiers]
        if not tiers:
            self.optimize_find_evolutions = False

    def _clear_slot(self, index: int, *, reset_policy: bool = True):
        selected = list(self.slot_selected_upgrades)
        selected[index] = NONE
        self.slot_selected_upgrades = selected
        keep_slots = list(self.clear_keep_slots)
        keep_slots[index] = False
        self.clear_keep_slots = keep_slots
        max_ranks, ranks = list(self.slot_max_ranks), list(self.slot_ranks)
        max_stacks, stacks = list(self.slot_max_stacks), list(self.slot_stacks)
        max_ranks[index] = 5 if SLOT_CONFIGS[index]["kind"] == "arcane" else 10
        ranks[index] = stacks[index] = max_stacks[index] = 0
        self.slot_max_ranks, self.slot_ranks = max_ranks, ranks
        self.slot_max_stacks, self.slot_stacks = max_stacks, stacks
        all_fields = copy.deepcopy(self.slot_fields)
        all_fields[index] = []
        self.slot_fields = all_fields
        entries = list(self.custom_upgrade_entries)
        entries[index] = ""
        self.custom_upgrade_entries = entries
        if reset_policy:
            policies = list(self.slot_policies)
            policies[index] = SLOT_POLICY_DISCARD
            self.slot_policies = policies

    def _apply_optimize_result(self, result):
        self.slot_selected_upgrades = list(result.slot_names)
        self.slot_ranks = list(result.slot_ranks)
        self.slot_stacks = list(result.slot_stacks)
        self.slot_policies = list(result.slot_policies)
        self.slot_riven_rolls = list(result.riven_rolls)
        self.custom_upgrade_entries = list(result.custom_entries)
        max_ranks, max_stacks = list(self.slot_max_ranks), list(self.slot_max_stacks)
        all_fields = copy.deepcopy(self.slot_fields)
        for index, config in enumerate(SLOT_CONFIGS):
            name = result.slot_names[index]
            if name in {NONE, CUSTOM, RIVEN}:
                max_ranks[index] = 0 if name != NONE else (5 if config["kind"] == "arcane" else 10)
                max_stacks[index] = 0
            else:
                _, maximum_rank = database_rank_bounds(name, is_arcane_slot=config["kind"] == "arcane")
                maximum_stacks = database_max_stacks(name, is_arcane_slot=config["kind"] == "arcane") or 0
                max_ranks[index], max_stacks[index] = maximum_rank, maximum_stacks
            if name == RIVEN:
                fields = []
                for field_name, value in result.riven_fields[index].items():
                    fields.append(EditorField(field_name, field_label(field_name), float(value), float(value), float(value), False))
                all_fields[index] = fields
            else:
                all_fields[index] = []
        self.slot_max_ranks, self.slot_max_stacks, self.slot_fields = max_ranks, max_stacks, all_fields
        if result.evolutions_optimized:
            selected = []
            for index, label in enumerate(self.evolution_labels):
                tier = parse_int(label.rsplit(" ", 1)[-1])
                perk = result.evolutions.get(tier)
                options = self.evolution_options[index] if index < len(self.evolution_options) else ["None"]
                if perk is None:
                    selected.append("None")
                    continue
                prefix = f"Perk {perk}"
                match = next((option for option in options if option == prefix or option.startswith(f"{prefix} —") or option.startswith(f"{prefix} -")), "None")
                selected.append(match)
            self.evolution_selections = selected
        previous_combo = self.selected_stance_combo
        self._refresh_stance_combo_options()
        if previous_combo in self.stance_combo_options:
            self.selected_stance_combo = previous_combo

    def _custom_weapon_metadata(self) -> dict | None:
        if not self.custom_weapon or not self.custom_weapon_entry.strip():
            return None
        try:
            return parse_database_entry(
                self.custom_weapon_entry,
                default_name="Custom Weapon",
                default_type=self.selected_weapon_type.casefold(),
            )
        except ValueError:
            return None

    def _refresh_upgrade_options(self):
        weapon_name = None if self.custom_weapon or self.selected_weapon == NONE else self.selected_weapon
        custom_metadata = self._custom_weapon_metadata() if self.custom_weapon else None
        names_for_ui = _upgrade_names_for_ui if custom_metadata is not None else upgrade_names_for_ui

        def upgrade_names(*args, stance_only: bool = False):
            if custom_metadata is not None:
                return names_for_ui(
                    self.selected_weapon_category,
                    weapon_name,
                    self.selected_attack_mode,
                    *args,
                    stance_only=stance_only,
                    custom_metadata=custom_metadata,
                )
            return names_for_ui(
                self.selected_weapon_category,
                weapon_name,
                self.selected_attack_mode,
                *args,
                stance_only,
            )

        has_weapon = self.selected_weapon != NONE
        self._refresh_ability_strength_available(custom_metadata=custom_metadata)
        self.riven_available = has_weapon and weapon_has_riven_disposition(weapon_name, custom_metadata=custom_metadata)
        if not self.riven_available:
            self.optimize_find_riven = False
        self.mod_options = [NONE, CUSTOM, *([RIVEN] if self.riven_available else []), *upgrade_names(True, False, False)]
        exclusive_stances = weapon_exclusive_stance_names(weapon_name) if self.selected_weapon_type == "Melee" and weapon_name else ()
        allows_stance = self.selected_weapon_type == "Melee" and has_weapon and weapon_allows_stance(weapon_name, custom_metadata=custom_metadata)
        self.exclusive_stance_weapon = bool(exclusive_stances)
        self.stance_slot_available = allows_stance
        if not allows_stance:
            self.stance_options = [NONE]
        elif exclusive_stances:
            self.stance_options = list(exclusive_stances)
        else:
            self.stance_options = [NONE, CUSTOM, *upgrade_names(True, False, False, stance_only=True)]
        self.exilus_options = [NONE, CUSTOM, *upgrade_names(True, False, True)]
        self.arcane_options = [NONE, CUSTOM, *upgrade_names(False, True, False)]

        for index, config in enumerate(SLOT_CONFIGS):
            if config.get("stance") and not allows_stance:
                if self.slot_selected_upgrades[index] != NONE:
                    self._clear_slot(index)
                continue
            if config.get("stance") and exclusive_stances:
                preferred = preferred_exclusive_stance(weapon_name, exclusive_stances)
                if self.slot_selected_upgrades[index] not in exclusive_stances:
                    selected = list(self.slot_selected_upgrades)
                    selected[index] = preferred
                    self.slot_selected_upgrades = selected
                    max_ranks, ranks = list(self.slot_max_ranks), list(self.slot_ranks)
                    max_stacks, stacks = list(self.slot_max_stacks), list(self.slot_stacks)
                    max_ranks[index] = ranks[index] = max_stacks[index] = stacks[index] = 0
                    self.slot_max_ranks, self.slot_ranks = max_ranks, ranks
                    self.slot_max_stacks, self.slot_stacks = max_stacks, stacks
                continue
            allowed = (
                self.arcane_options
                if config["kind"] == "arcane"
                else self.stance_options
                if config.get("stance")
                else self.exilus_options
                if config["exilus"]
                else self.mod_options
            )
            if self.slot_selected_upgrades[index] not in allowed:
                self._clear_slot(index)

        self._refresh_stance_combo_options()
        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()
        self._refresh_optimizer_exclusion_options()

    def _refresh_optimizer_exclusion_options(self):
        valid_upgrades = sorted(
            {
                name
                for name in (*self.mod_options, *self.stance_options, *self.exilus_options, *self.arcane_options)
                if name not in {NONE, CUSTOM, RIVEN}
            },
            key=str.casefold,
        )
        valid_upgrade_set = set(valid_upgrades)
        default_overrides = set(self.optimize_default_exclusion_overrides)
        default_exclusions = {name for name in valid_upgrades if name not in default_overrides and optimizer_excludes_upgrade_by_default(name)}
        self.optimize_excluded_upgrades = sorted({name for name in self.optimize_excluded_upgrades if name in valid_upgrade_set} | default_exclusions, key=str.casefold)
        excluded_upgrade_set = set(self.optimize_excluded_upgrades)
        self.optimize_upgrade_exclusion_options = [name for name in valid_upgrades if name not in excluded_upgrade_set]
        if self.optimize_pending_excluded_upgrade not in self.optimize_upgrade_exclusion_options:
            self.optimize_pending_excluded_upgrade = self.optimize_upgrade_exclusion_options[0] if self.optimize_upgrade_exclusion_options else ""

        valid_riven_stats = sorted((field_label(name) for name in self._riven_base_stats()), key=str.casefold)
        valid_riven_stat_set = set(valid_riven_stats)
        default_riven_overrides = set(self.optimize_default_riven_exclusion_overrides)
        default_riven_exclusions = {field_label(name) for name in self._riven_base_stats() if field_label(name) not in default_riven_overrides and is_faction_damage_stat(name)}
        self.optimize_excluded_riven_stats = sorted({label for label in self.optimize_excluded_riven_stats if label in valid_riven_stat_set} | default_riven_exclusions, key=str.casefold)
        excluded_riven_stat_set = set(self.optimize_excluded_riven_stats)
        self.optimize_riven_stat_exclusion_options = [label for label in valid_riven_stats if label not in excluded_riven_stat_set]
        if self.optimize_pending_excluded_riven_stat not in self.optimize_riven_stat_exclusion_options:
            self.optimize_pending_excluded_riven_stat = self.optimize_riven_stat_exclusion_options[0] if self.optimize_riven_stat_exclusion_options else ""

    def _refresh_stance_combo_options(self):
        weapon_name = None if self.custom_weapon or self.selected_weapon == NONE else self.selected_weapon
        custom_metadata = self._custom_weapon_metadata() if self.custom_weapon else None
        allows_stance = self.selected_weapon_type == "Melee" and self.selected_weapon != NONE and weapon_allows_stance(weapon_name, custom_metadata=custom_metadata)
        self.stance_slot_available = allows_stance
        self.stance_combo_available = allows_stance
        if not allows_stance:
            self.stance_combo_options = ["neutral"]
            self.selected_stance_combo = "neutral"
            self.stance_combo_locked = True
            return
        category = selected_attack_category(weapon_name, self.selected_attack_mode, custom_metadata=custom_metadata)
        keys = stance_combo_options_for_attack(category)
        self.stance_combo_options = keys
        self.stance_combo_locked = stance_combo_key_for_attack_category(category) is not None
        if self.selected_stance_combo not in keys:
            self.selected_stance_combo = keys[0]

    def _refresh_slot_upgrade_options(self):
        selected = self.slot_selected_upgrades
        options: list[list[str]] = []
        for index, config in enumerate(SLOT_CONFIGS):
            base_options = (
                self.arcane_options
                if config["kind"] == "arcane"
                else self.stance_options
                if config.get("stance")
                else self.exilus_options
                if config["exilus"]
                else self.mod_options
            )
            selected_elsewhere = {
                upgrade
                for other_index, upgrade in enumerate(selected)
                if other_index != index and upgrade not in {CUSTOM, NONE}
            }
            current = selected[index]
            filtered = []
            for upgrade in base_options:
                if upgrade in {NONE, CUSTOM} or upgrade == current:
                    filtered.append(upgrade)
                    continue
                if upgrade in selected_elsewhere:
                    continue
                if upgrade_conflicts_with_selected(upgrade, selected_elsewhere):
                    continue
                filtered.append(upgrade)
            options.append(filtered)
        self.slot_upgrade_options = options

    def _refresh_slot_condition_metadata(self):
        has_conditionals: list[bool] = []
        labels: list[str] = []
        enabled = list(self.slot_conditions_enabled)

        for index, config in enumerate(SLOT_CONFIGS):
            selected = self.slot_selected_upgrades[index]
            if selected in {RIVEN, CUSTOM, NONE}:
                has_conditionals.append(False)
                labels.append("")
                enabled[index] = True
                continue

            has_conditional, label = database_conditional_info(
                selected,
                is_arcane_slot=config["kind"] == "arcane",
            )
            has_conditionals.append(has_conditional)
            labels.append(label or "Conditional Bonus")
            if not has_conditional:
                enabled[index] = True

        self.slot_has_conditionals = has_conditionals
        self.slot_condition_labels = labels
        self.slot_conditions_enabled = enabled

    def _filter_disallowed_custom_fields(self):
        all_fields = copy.deepcopy(self.slot_fields)
        for index, config in enumerate(SLOT_CONFIGS):
            if self.slot_selected_upgrades[index] == RIVEN:
                continue
            all_fields[index] = [
                field
                for field in all_fields[index]
                if field.name in config["options"]
                and is_field_allowed(
                    field.name,
                    self.selected_weapon_type,
                    FIELD_WEAPON_RULES,
                )
            ]
        self.slot_fields = all_fields
        self.external_fields = [
            field
            for field in copy.deepcopy(self.external_fields)
            if field.name in BUFF_FIELD
            and is_field_allowed(
                field.name,
                self.selected_weapon_type,
                FIELD_WEAPON_RULES,
            )
        ]

    def _riven_weapon_metadata(self) -> dict:
        if not self.custom_weapon:
            return raw_weapon_metadata(
                self.selected_weapon_type,
                self.selected_weapon,
            )
        if not self.custom_weapon_entry.strip():
            return {}
        try:
            return parse_database_entry(
                self.custom_weapon_entry,
                default_name="Custom Weapon",
                default_type=self.selected_weapon_type.casefold(),
            )
        except ValueError:
            return {}

    def _riven_base_stats(self) -> dict[str, float]:
        category = {
            "Shotgun": "shotgun",
            "Pistol": "pistol",
            "Melee": "melee",
        }.get(self.selected_weapon_category, "rifle")
        raw_stats = raw_riven_stats_database().get(category, {}) or {}
        stats = {
            RIVEN_STAT_ALIASES.get(name, name): float(value)
            for name, value in raw_stats.items()
        }

        metadata = self._riven_weapon_metadata()
        attacks = metadata.get("attacks") or {}
        wanted = " ".join(
            self.selected_attack_mode.casefold().replace("_", " ").split()
        )
        attack = next(
            (
                value
                for name, value in attacks.items()
                if " ".join(name.casefold().replace("_", " ").split())
                == wanted
            ),
            next(iter(attacks.values()), {}),
        )
        damage = ((attack or {}).get("stats") or {}).get("damage") or {}
        for physical in ("impact", "puncture", "slash"):
            if float(damage.get(physical, 0) or 0) <= 0:
                stats.pop(physical, None)
        return stats

    def _riven_disposition(self) -> float:
        try:
            value = float(self._riven_weapon_metadata().get("disposition", 1.0))
        except (TypeError, ValueError):
            value = 1.0
        return clamp_number(value, 0.5, 1.55)

    def _riven_roll_config(self, index: int) -> tuple[int, int, float, float]:
        selected = (
            self.slot_riven_rolls[index]
            if 0 <= index < len(self.slot_riven_rolls)
            else ""
        )
        return RIVEN_ROLL_CONFIGS.get(
            selected,
            RIVEN_ROLL_CONFIGS["2 Positive + 1 Negative"],
        )

    def _riven_field_from_label(self, label: str) -> str | None:
        return next(
            (
                name
                for name in self._riven_base_stats()
                if field_label(name) == label
            ),
            None,
        )

    def _riven_field_limits(
        self,
        index: int,
        field_name: str,
        negative: bool,
    ) -> tuple[float, float] | None:
        base_value = self._riven_base_stats().get(field_name)
        if base_value is None:
            return None
        _positive_count, negative_count, bonus_factor, malus_factor = (
            self._riven_roll_config(index)
        )
        disposition = self._riven_disposition()
        if negative:
            if (
                not negative_count
                or field_name in RIVEN_NON_NEGATIVE_STATS
            ):
                return None
            center = base_value * disposition * malus_factor
            return center * 1.1, center * 0.9
        center = base_value * disposition * bonus_factor
        return center * 0.9, center * 1.1

    def _refresh_riven_field_limits(self, index: int):
        if self.slot_selected_upgrades[index] != RIVEN:
            return
        positive_count, negative_count, _bonus, _malus = (
            self._riven_roll_config(index)
        )
        maximum_fields = positive_count + negative_count
        fields = copy.deepcopy(self.slot_fields)
        refreshed: list[EditorField] = []
        for position, field in enumerate(fields[index][:maximum_fields]):
            limits = self._riven_field_limits(
                index,
                field.name,
                position >= positive_count,
            )
            if limits is None:
                continue
            minimum, maximum = limits
            field.min_value = minimum
            field.max_value = maximum
            field.value = clamp_number(float(field.value), minimum, maximum)
            field.integer = False
            refreshed.append(field)
        fields[index] = refreshed
        self.slot_fields = fields

    def _refresh_all_riven_field_limits(self):
        for index in range(len(SLOT_CONFIGS)):
            self._refresh_riven_field_limits(index)

    def _refresh_all_field_options(self):
        self._refresh_slot_field_options()
        self._refresh_external_field_options()

    def _refresh_slot_field_options(self):
        available_all: list[list[str]] = []
        pending = list(self.slot_pending_fields)
        for index, config in enumerate(SLOT_CONFIGS):
            selected_names = {field.name for field in self.slot_fields[index]}
            if self.slot_selected_upgrades[index] == RIVEN:
                positive_count, negative_count, _bonus, _malus = (
                    self._riven_roll_config(index)
                )
                position = len(self.slot_fields[index])
                maximum_fields = positive_count + negative_count
                available_names = (
                    [
                        field_name
                        for field_name in self._riven_base_stats()
                        if field_name not in selected_names
                        and (
                            position < positive_count
                            or field_name not in RIVEN_NON_NEGATIVE_STATS
                        )
                    ]
                    if position < maximum_fields
                    else []
                )
                labels = [field_label(field_name) for field_name in available_names]
                available_all.append(labels)
                if pending[index] not in labels:
                    pending[index] = labels[0] if labels else ""
                continue
            available_names = [
                field_name
                for field_name in config["options"]
                if field_name not in selected_names
                and is_field_allowed(
                    field_name,
                    self.selected_weapon_type,
                    FIELD_WEAPON_RULES,
                )
            ]
            labels = [field_label(field_name) for field_name in available_names]
            available_all.append(labels)
            if pending[index] not in labels:
                pending[index] = labels[0] if labels else ""
        self.slot_available_fields = available_all
        self.slot_pending_fields = pending

    def _refresh_external_field_options(self):
        selected_names = {field.name for field in self.external_fields}
        available_names = [
            field_name
            for field_name in BUFF_FIELD
            if field_name not in selected_names
            and is_field_allowed(
                field_name,
                self.selected_weapon_type,
                FIELD_WEAPON_RULES,
            )
        ]
        self.external_available_fields = [field_label(name) for name in available_names]
        if self.external_pending_field not in self.external_available_fields:
            self.external_pending_field = (
                self.external_available_fields[0]
                if self.external_available_fields
                else ""
            )

    def _damage_groups(self) -> tuple[str, ...]:
        return (
            "direct_damage",
            "forced_proc",
            "explosion_damage",
            "explosion_forced_proc",
        )

    def _supports_progenitor(self) -> bool:
        if self.custom_weapon:
            return True
        metadata = raw_weapon_metadata(
            self.selected_weapon_type,
            self.selected_weapon,
        )
        return bool(metadata.get("progenitor", False))

    def _get_damage_fields(self, group: str) -> list[EditorField]:
        return getattr(self, f"{group}_fields", [])

    def _set_damage_fields(self, group: str, fields: list[EditorField]):
        if group in self._damage_groups():
            setattr(self, f"{group}_fields", fields)

    def _refresh_damage_options(self):
        for group in self._damage_groups():
            selected = {field.name for field in self._get_damage_fields(group)}
            labels = [
                field_label(damage_type)
                for damage_type in DAMAGE_TYPES
                if damage_type not in selected
            ]
            setattr(self, f"{group}_options", labels)
            pending_name = f"{group}_pending"
            if getattr(self, pending_name, "") not in labels:
                setattr(self, pending_name, labels[0] if labels else "")

    def _damage_dist(self, fields: list[EditorField]) -> Dist:
        return Dist(
            {
                field.name: float(field.value)
                for field in fields
                if float(field.value) > 0
            }
        )

    def _target_enemy(self):
        return configured_enemy(
            self.selected_enemy,
            custom_enemy=self.custom_enemy,
            custom_entry=self.custom_enemy_entry if self.custom_enemy else None,
            level=self.enemy_level,
            steel_path=self.enemy_steel_path,
            empowered=self.enemy_empowered,
        )

    def _refresh_optimize_maximize_options(self):
        options = [
            label
            for label, target in OPTIMIZE_MAXIMIZE_TARGETS.items()
            if ("weakpoint" not in target or self.enemy_has_weakpoint) and ("resistant" not in target or self.enemy_has_resistant)
        ]
        self.optimize_maximize_options = options
        if self.optimize_maximize_target not in options:
            self.optimize_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE

    def _refresh_enemy_preview(self, enemy) -> None:
        if self.no_enemy:
            self.enemy_identity_rows = []
            self.enemy_bodypart_rows = []
            self.enemy_modifier_rows = []
            self.enemy_result_metrics = []
            self.enemy_has_weakpoint = False
            self.enemy_has_resistant = False
            self._refresh_optimize_maximize_options()
            self.enemy_error = ""
            return
        data = enemy.data
        effective = enemy.results.effective
        part_types = {str(part.type).casefold() for part in data.bodyparts.values()}
        self.enemy_has_weakpoint = any("weakpoint" in part_type for part_type in part_types)
        self.enemy_has_resistant = any("resistant" in part_type for part_type in part_types)
        self._refresh_optimize_maximize_options()
        self.enemy_identity_rows = [
            DisplayRow("Name", str(data.name)),
            DisplayRow("Faction", str(data.faction)),
            DisplayRow("Base Level", f"{float(data.base_level):g}"),
            DisplayRow("Current Level", str(self.enemy_level)),
        ]
        self.enemy_bodypart_rows = [
            DisplayRow(f"{str(name).replace('_', ' ').title()} ({str(part.type).title()})", f"{float(part.multiplier):g}x")
            for name, part in data.bodyparts.items()
        ]
        self.enemy_modifier_rows = [
            DisplayRow(field_label(str(name)), f"{float(value):g}x")
            for name, value in data.modifiers.items()
        ]
        self.enemy_result_metrics = [
            MetricRow("Effective Health", f"{float(effective.health):,.2f}"),
            MetricRow("Effective Shields", f"{float(effective.shields):,.2f}"),
            MetricRow("Effective Armor", f"{float(effective.armor):,.0f}"),
            MetricRow("Effective Overguard", f"{float(effective.overguard):,.2f}"),
        ]
        self.enemy_error = ""

    def _custom_base_stats(self) -> dict:
        if self.selected_weapon_type == "Melee":
            return {
                "type": "melee",
                "damage": self._damage_dist(self.direct_damage_fields),
                "forced_procs": self._damage_dist(self.forced_proc_fields),
                "crit_chance": self.base_crit_chance,
                "crit_damage": self.base_crit_damage,
                "status_chance": self.base_status_chance,
                "attack_speed": self.base_attack_speed,
            }

        weapon_subtype = self.selected_weapon_category.casefold()
        return {
            "type": weapon_subtype,
            "damage": self._damage_dist(self.direct_damage_fields),
            "forced_procs": self._damage_dist(self.forced_proc_fields),
            "explosion_damage": self._damage_dist(self.explosion_damage_fields),
            "explosion_forced_procs": self._damage_dist(
                self.explosion_forced_proc_fields
            ),
            "crit_chance": self.base_crit_chance,
            "crit_damage": self.base_crit_damage,
            "status_chance": self.base_status_chance,
            "multishot": self.base_multishot,
            "fire_rate": self.base_fire_rate,
            "reload_speed": self.base_reload_speed,
            "magazine_capacity": self.base_magazine_capacity,
            "weakpoint_damage": self.base_weakpoint_damage,
            "recharge_rate": self.base_recharge_rate if self.is_battery else 0.0,
            "charge_time": self.base_charge_time if self.is_charge_weapon else 0.0,
            "burst_count": self.base_burst_count if self.is_burst_weapon else 1,
            "burst_delay": self.base_burst_delay if self.is_burst_weapon else 0.0,
            "is_battery": self.is_battery,
            "is_beam": self.is_beam,
        }

    def _custom_upgrade_from_fields(
        self,
        name: str,
        fields: list[EditorField],
    ) -> Upgrade:
        return build_upgrade(name, {field.name: field.value for field in fields})

    def _riven_stat_rows(self, index: int) -> list[DisplayRow]:
        rows: list[DisplayRow] = []
        for field in self.slot_fields[index]:
            value = float(field.value)
            if field.name in RIVEN_FLAT_STAT_UNITS:
                unit = RIVEN_FLAT_STAT_UNITS[field.name]
                formatted = f"{value:,.3f}".rstrip("0").rstrip(".")
                if unit:
                    formatted = f"{formatted} {unit}"
            else:
                formatted = f"{value:,.1%}"
            rows.append(DisplayRow(field.label, formatted))
        return rows

    def _pad_slot_preview_rows(self, rows: list[DisplayRow], *, minimum: int = 4) -> list[DisplayRow]:
        padded = list(rows) if rows else [DisplayRow("No stats.", "")]
        while len(padded) < minimum:
            padded.append(DisplayRow("\u00a0", "\u00a0"))
        return padded

    def _slot_preview_rows(self, index: int, upgrade: Upgrade) -> list[DisplayRow]:
        if self.slot_selected_upgrades[index] == RIVEN:
            return self._pad_slot_preview_rows(self._riven_stat_rows(index))
        rows = upgrade_stat_rows(upgrade, self._slot_extra_preview_stats(index))
        if SLOT_CONFIGS[index].get("stance") or bool((upgrade.data.compatibility or {}).get("stance")):
            combos = getattr(upgrade.data, "combos", None)
            combo_mapping = dict(combos) if combos else self._slot_stance_combos(index)
            selected_combo = self.selected_stance_combo
            if selected_combo in combo_mapping:
                combo_mapping = {selected_combo: combo_mapping[selected_combo]}
            elif combo_mapping:
                fallback = next(iter(combo_mapping))
                combo_mapping = {fallback: combo_mapping[fallback]}
            combo_rows = stance_combo_rows(combo_mapping)
            if combo_rows:
                rows = [*rows, *combo_rows] if rows else combo_rows
        return self._pad_slot_preview_rows(rows)

    def _slot_stance_combos(self, index: int) -> dict:
        selected = self.slot_selected_upgrades[index]
        if selected == CUSTOM:
            try:
                return parse_database_entry(
                    self.custom_upgrade_entries[index] or _empty_custom_upgrade_entry(index),
                    default_name=SLOT_CONFIGS[index]["label"],
                    default_type=SLOT_CONFIGS[index]["kind"],
                ).get("combos") or {}
            except ValueError:
                return {}
        if selected in {NONE, RIVEN}:
            return {}
        return raw_upgrade_metadata(selected).get("combos") or {}

    def _slot_extra_preview_stats(self, index: int) -> dict:
        selected = self.slot_selected_upgrades[index]
        config = SLOT_CONFIGS[index]
        if selected == NONE:
            return {}
        if selected == CUSTOM:
            try:
                metadata = parse_database_entry(
                    self.custom_upgrade_entries[index]
                    or _empty_custom_upgrade_entry(index),
                    default_name=config["label"],
                    default_type=config["kind"],
                )
            except ValueError:
                return {}
            return metadata.get("stats") or {}
        if selected in {RIVEN, CUSTOM}:
            return {}
        return (
            raw_upgrade_metadata(selected, kind=config["kind"]).get("stats")
            or {}
        )

    def _slot_upgrade(self, index: int) -> Upgrade:
        config = SLOT_CONFIGS[index]
        selected = self.slot_selected_upgrades[index]
        if selected == NONE:
            return Upgrade({"name": NONE, "type": config["kind"], "stats": {}, "runtime": {"rank": 0}})
        if selected == RIVEN:
            return self._custom_upgrade_from_fields(
                RIVEN,
                self.slot_fields[index],
            )
        if selected == CUSTOM:
            return custom_upgrade_from_entry(
                self.custom_upgrade_entries[index]
                or _empty_custom_upgrade_entry(index),
                default_name=config["label"],
                default_type=config["kind"],
            )
        loaded = database_upgrade(
            selected,
            kind=config["kind"],
            rank=self.slot_ranks[index],
            stacks=(
                self.slot_stacks[index]
                if self.slot_max_stacks[index] > 0
                else None
            ),
            condition=self.slot_conditions_enabled[index],
        )
        return loaded or Upgrade(
            {"name": selected, "type": config["kind"], "stats": {}, "runtime": {"rank": 0}}
        )

    def _clear_calculation_results(self):
        self.slot_contributions = ["—" for _ in SLOT_CONFIGS]
        self.main_result_metrics = []
        self.weakpoint_result_metrics = []
        self.resistant_result_metrics = []
        self.ranged_result_metrics = []
        self.misc_result_metrics = []
        self.result_metrics = []
        self.damage_result_rows = []
        self.contribution_result_rows = []
        self.result_summary = ""
        self.result_contribution_summary = ""
        self.result_ready = False

    def _recalculate(self):
        try:
            configuration_errors: list[str] = []
            try:
                target = self._target_enemy()
                self._refresh_enemy_preview(target)
            except Exception as exc:
                self.enemy_identity_rows = []
                self.enemy_bodypart_rows = []
                self.enemy_modifier_rows = []
                self.enemy_result_metrics = []
                self.enemy_has_weakpoint = False
                self.enemy_has_resistant = False
                self._refresh_optimize_maximize_options()
                self.enemy_error = f"{type(exc).__name__}: {exc}"
                configuration_errors.append(self.enemy_error)
                target = None
            if self.custom_weapon and not self.custom_weapon_entry.strip():
                configuration_errors.append("ValueError: Custom Weapon JSON is required.")
            if configuration_errors:
                self._clear_calculation_results()
                self.result_errors = configuration_errors
                self.result_error = "\n".join(configuration_errors)
                return
            if self.selected_weapon == NONE:
                slot_upgrades = [self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))]
                self.slot_stat_rows = [
                    self._slot_preview_rows(index, upgrade)
                    for index, upgrade in enumerate(slot_upgrades)
                ]
                self._clear_calculation_results()
                self.result_error = "Select a weapon to calculate."
                self.result_errors = [self.result_error]
                return

            slot_upgrades = [
                self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))
            ]
            self.slot_stat_rows = [
                self._slot_preview_rows(index, upgrade)
                for index, upgrade in enumerate(slot_upgrades)
            ]
            progenitor = progenitor_upgrade(
                self.progenitor_element
                if self._supports_progenitor()
                else NO_EFFECT,
                self.progenitor_value,
                NO_EFFECT,
            )
            external = self._custom_upgrade_from_fields(
                "External Buffs",
                self.external_fields,
            )
            upgrades: list[Upgrade] = []
            if is_non_empty_upgrade(progenitor):
                upgrades.append(progenitor)
            upgrades.extend(
                upgrade
                for upgrade in slot_upgrades
                if is_non_empty_upgrade(upgrade)
            )
            if is_non_empty_upgrade(external):
                upgrades.append(external)

            evolutions = {
                parse_int(self.evolution_labels[index].rsplit(" ", 1)[-1]): parse_int(
                    selection.split()[1]
                )
                for index, selection in enumerate(self.evolution_selections)
                if selection != "None"
            }
            weapon = configured_weapon(
                self.selected_weapon_type,
                self.selected_weapon,
                custom_weapon=self.custom_weapon,
                base_stats={},
                upgrades=upgrades,
                custom_entry=self.custom_weapon_entry if self.custom_weapon else None,
                selected_mode=self.selected_attack_mode or None,
                evolutions=evolutions,
                stance_combo=self.selected_stance_combo if self.stance_combo_available else None,
                ability_strength=self._ability_strength_multiplier(),
                target=target,
            )
            contribution_lookup = contribution_lookup_for_weapon(
                weapon,
                self.selected_weapon_type,
                None,
                upgrades,
            )

            contributions = []
            for index, config in enumerate(SLOT_CONFIGS):
                selected = self.slot_selected_upgrades[index]
                contribution_name = (
                    config["label"]
                    if selected in {CUSTOM, NONE}
                    else selected
                )
                contributions.append(
                    format_contribution(
                        contribution_for_category(contribution_lookup, contribution_name)
                    )
                )
            self.slot_contributions = contributions

            self.main_result_metrics = main_metrics(weapon)
            self.weakpoint_result_metrics = weakpoint_metrics(weapon) if self.enemy_has_weakpoint else []
            self.resistant_result_metrics = resistant_metrics(weapon) if self.enemy_has_resistant else []
            self.misc_result_metrics = [] if self.selected_weapon_type == "Melee" else ranged_misc_metrics(weapon)
            self.result_metrics = self.main_result_metrics + self.weakpoint_result_metrics + self.resistant_result_metrics + self.misc_result_metrics
            self.ranged_result_metrics = self.result_metrics
            self.damage_result_rows = effective_damage_rows(
                weapon,
                melee=self.selected_weapon_type == "Melee",
            )
            self.contribution_result_rows = contribution_rows(contribution_lookup)
            self.result_summary = weapon.format.summary()
            self.result_contribution_summary = format_upgrade_contributions(
                contribution_lookup
            )
            self.result_error = ""
            self.result_errors = []
            self.result_ready = True
        except Exception as exc:
            self._clear_calculation_results()
            self.result_error = f"{type(exc).__name__}: {exc}"
            self.result_errors = [self.result_error]
