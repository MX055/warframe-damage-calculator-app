from __future__ import annotations

import copy
import json
from typing import Any

import reflex as rx
from warframe_damage_calculator import Upgrade
from warframe_damage_calculator.models.dist import Dist

from .constants import (
    ARCANE_FIELD,
    BUFF_FIELD,
    DAMAGE_TYPES,
    DEFAULT_DAMAGE_TYPES,
    FIELD_WEAPON_RULES,
    MOD_FIELD,
    NO_EFFECT,
    RIVEN_NON_NEGATIVE_STATS,
    RIVEN_ROLL_CONFIGS,
    RIVEN_ROLL_OPTIONS,
    RIVEN_STAT_ALIASES,
    SLOT_CONFIGS,
    WEAPON_CATEGORY_TYPES,
    UPGRADE_BOOL_FIELDS,
    UPGRADE_SCALAR_FIELDS,
)
from .data import (
    database_conditional_info,
    database_max_stacks,
    database_rank_bounds,
    database_upgrade,
    raw_riven_stats_database,
    raw_upgrade_metadata,
    raw_weapon_metadata,
    upgrade_names_for_ui,
    weapon_attack_modes,
    weapon_evolution_options,
    weapon_names_for_type,
)
from .engine import (
    build_upgrade,
    clamp_number,
    configured_weapon,
    contribution_for_category,
    contribution_lookup_for_weapon,
    contribution_rows,
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
            "is_progenitor": True,
        }
        entry["evolutions"] = {
            "2": {
                "1": {
                    "description": "Example: +20 base damage",
                    "stats": {"damage": [{"value": 20, "mode": "base"}]},
                },
                "2": {
                    "description": "Example: +25% fire rate",
                    "stats": {
                        "fire_rate": [{"value": 0.25, "mode": "additive"}]
                    },
                },
            }
        }
    return json.dumps(entry, indent=2)


def _custom_upgrade_templates(
    weapon_type_name: str = "Primary",
    weapon_category: str = "Rifle",
) -> list[str]:
    entries = []
    for config in SLOT_CONFIGS:
        compatibility = {
            "types": [weapon_type_name.casefold()],
            "subtypes": [weapon_category.casefold()],
            "exilus": False,
        }
        if config["exilus"]:
            compatibility["exilus"] = True
        entry = {
            "name": f"Custom {config['label']}",
            "type": config["kind"],
            "max_rank": 10 if config["kind"] == "mod" else 5,
            "compatibility": compatibility,
            "incompatibility": ["Example Incompatible Upgrade"],
            "stats": {
                "damage_bonus": [
                    {"value": 1.65, "mode": "additive"},
                    {
                        "value": 0.15,
                        "mode": "multiplicative",
                        "when": "on_headshot",
                    },
                ],
                "crit_chance": [{"value": 0.2, "mode": "flat"}],
                "crit_damage": [
                    {
                        "value": 0.1,
                        "mode": "additive",
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
            "compatibility": {"exilus": bool(config["exilus"])},
            "incompatibility": [],
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
    selected_weapon: str = CUSTOM

    weapon_options: list[str] = rx.field(default_factory=lambda: [CUSTOM])
    attack_mode_options: list[str] = rx.field(default_factory=list)
    selected_attack_mode: str = ""
    evolution_labels: list[str] = rx.field(default_factory=list)
    evolution_options: list[list[str]] = rx.field(default_factory=list)
    evolution_selections: list[str] = rx.field(default_factory=list)
    mod_options: list[str] = rx.field(default_factory=lambda: [CUSTOM])
    exilus_options: list[str] = rx.field(default_factory=lambda: [CUSTOM])
    arcane_options: list[str] = rx.field(default_factory=lambda: [CUSTOM])
    slot_upgrade_options: list[list[str]] = rx.field(
        default_factory=lambda: [[CUSTOM] for _ in SLOT_CONFIGS]
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
        default_factory=lambda: [CUSTOM for _ in SLOT_CONFIGS]
    )
    slot_ranks: list[int] = rx.field(default_factory=lambda: _default_slot_max_ranks())
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

    external_fields: list[EditorField] = rx.field(default_factory=list)
    external_available_fields: list[str] = rx.field(default_factory=list)
    external_pending_field: str = ""

    main_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    weakpoint_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    ranged_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    misc_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    damage_result_rows: list[DamageResultRow] = rx.field(default_factory=list)
    contribution_result_rows: list[ContributionRow] = rx.field(default_factory=list)
    result_summary: str = ""
    result_contribution_summary: str = ""
    result_error: str = ""
    result_ready: bool = False

    @rx.var
    def custom_weapon(self) -> bool:
        return self.selected_weapon == CUSTOM

    @rx.var
    def ranged_weapon(self) -> bool:
        return self.selected_weapon_type != "Melee"

    @rx.var
    def melee_weapon(self) -> bool:
        return self.selected_weapon_type == "Melee"

    @rx.var
    def has_error(self) -> bool:
        return bool(self.result_error)

    @rx.var
    def supports_progenitor(self) -> bool:
        return self._supports_progenitor()

    @rx.event
    def initialize(self):
        if self.initialized:
            return
        self.initialized = True
        self._refresh_weapon_options()
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_damage_options()
        self._refresh_all_field_options()
        self._recalculate()

    @rx.event
    def set_weapon_type(self, value: str):
        if value not in WEAPON_CATEGORY_TYPES:
            return
        self.selected_weapon_category = value
        self.selected_weapon_type = WEAPON_CATEGORY_TYPES[value]
        self.selected_weapon = CUSTOM
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
        self.selected_weapon = value if value in self.weapon_options else CUSTOM
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_custom_weapon_entry(self, value: str):
        self.custom_weapon_entry = value
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
        self._recalculate()

    @rx.event
    def set_attack_mode(self, value: str):
        if value not in self.attack_mode_options:
            return
        self.selected_attack_mode = value
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
        self._recalculate()

    @rx.event
    def set_progenitor_element(self, value: str):
        self.progenitor_element = value
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
        self._recalculate()

    @rx.event
    def set_damage_value(self, group: str, damage_name: str, value: str):
        fields = copy.deepcopy(self._get_damage_fields(group))
        for field in fields:
            if field.name == damage_name:
                field.value = max(0.0, parse_float(value, field.value))
                break
        self._set_damage_fields(group, fields)
        self._recalculate()

    @rx.event
    def set_slot_upgrade(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        if value not in self.slot_upgrade_options[index]:
            return
        selected = list(self.slot_selected_upgrades)
        previous = selected[index]
        selected[index] = value
        self.slot_selected_upgrades = selected

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
        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def set_slot_condition(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        enabled = list(self.slot_conditions_enabled)
        enabled[index] = bool(value)
        self.slot_conditions_enabled = enabled
        self._recalculate()

    @rx.event
    def set_slot_rank(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        ranks = list(self.slot_ranks)
        ranks[index] = max(0, min(parse_int(value, ranks[index]), self.slot_max_ranks[index]))
        self.slot_ranks = ranks
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
        self._refresh_slot_field_options()
        self._recalculate()

    @rx.event
    def remove_slot_field(self, index: int, field_name: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        all_fields = copy.deepcopy(self.slot_fields)
        all_fields[index] = [field for field in all_fields[index] if field.name != field_name]
        self.slot_fields = all_fields
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
        self._refresh_external_field_options()
        self._recalculate()

    @rx.event
    def remove_external_field(self, field_name: str):
        self.external_fields = [
            field
            for field in copy.deepcopy(self.external_fields)
            if field.name != field_name
        ]
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
        self._recalculate()

    def _refresh_weapon_options(self):
        self.weapon_options = [
            CUSTOM,
            *weapon_names_for_type(
                self.selected_weapon_type,
                self.selected_weapon_category,
            ),
        ]
        if self.selected_weapon not in self.weapon_options:
            self.selected_weapon = CUSTOM

    def _refresh_weapon_features(self):
        if self.custom_weapon:
            try:
                metadata = parse_database_entry(
                    self.custom_weapon_entry or self.custom_weapon_placeholder,
                    default_name="Custom Weapon",
                    default_type=self.selected_weapon_type.casefold(),
                )
            except ValueError:
                metadata = {}
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
            return
        modes = list(weapon_attack_modes(self.selected_weapon))
        self.attack_mode_options = modes
        if self.selected_attack_mode not in modes:
            self.selected_attack_mode = modes[0] if modes else ""
        tiers = weapon_evolution_options(self.selected_weapon)
        self.evolution_labels = [tier["label"] for tier in tiers]
        self.evolution_options = [tier["options"] for tier in tiers]
        self.evolution_selections = ["None" for _ in tiers]

    def _refresh_upgrade_options(self):
        weapon_name = None if self.custom_weapon else self.selected_weapon
        self.mod_options = [
            CUSTOM,
            RIVEN,
            *upgrade_names_for_ui(
                self.selected_weapon_category,
                weapon_name,
                self.selected_attack_mode,
                True,
                False,
                False,
            ),
        ]
        self.exilus_options = [
            CUSTOM,
            *upgrade_names_for_ui(
                self.selected_weapon_category,
                weapon_name,
                self.selected_attack_mode,
                True,
                False,
                True,
            ),
        ]
        self.arcane_options = [
            CUSTOM,
            *upgrade_names_for_ui(
                self.selected_weapon_category,
                weapon_name,
                self.selected_attack_mode,
                False,
                True,
                False,
            ),
        ]

        selected = list(self.slot_selected_upgrades)
        changed = False
        for index, config in enumerate(SLOT_CONFIGS):
            allowed = (
                self.arcane_options
                if config["kind"] == "arcane"
                else self.exilus_options
                if config["exilus"]
                else self.mod_options
            )
            if selected[index] not in allowed:
                selected[index] = CUSTOM
                changed = True
        if changed:
            self.slot_selected_upgrades = selected

        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()

    def _refresh_slot_upgrade_options(self):
        selected = self.slot_selected_upgrades
        options: list[list[str]] = []
        for index, config in enumerate(SLOT_CONFIGS):
            base_options = (
                self.arcane_options
                if config["kind"] == "arcane"
                else self.exilus_options
                if config["exilus"]
                else self.mod_options
            )
            selected_elsewhere = {
                upgrade
                for other_index, upgrade in enumerate(selected)
                if other_index != index and upgrade != CUSTOM
            }
            current = selected[index]
            options.append(
                [
                    upgrade
                    for upgrade in base_options
                    if upgrade == CUSTOM
                    or upgrade == current
                    or upgrade not in selected_elsewhere
                ]
            )
        self.slot_upgrade_options = options

    def _refresh_slot_condition_metadata(self):
        has_conditionals: list[bool] = []
        labels: list[str] = []
        enabled = list(self.slot_conditions_enabled)

        for index, config in enumerate(SLOT_CONFIGS):
            selected = self.slot_selected_upgrades[index]
            if selected == RIVEN:
                has_conditionals.append(False)
                labels.append("")
                enabled[index] = True
                continue
            if selected == CUSTOM:
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
        try:
            return parse_database_entry(
                self.custom_weapon_entry or self.custom_weapon_placeholder,
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
        return bool(metadata.get("is_progenitor", False) or (metadata.get("ammo") or {}).get("is_progenitor", False))

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

    def _slot_extra_preview_stats(self, index: int) -> dict:
        selected = self.slot_selected_upgrades[index]
        config = SLOT_CONFIGS[index]
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
            {"name": selected, "type": config["kind"], "stats": {}}
        )

    def _recalculate(self):
        try:
            slot_upgrades = [
                self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))
            ]
            self.slot_stat_rows = [
                (
                    self._riven_stat_rows(index)
                    if self.slot_selected_upgrades[index] == RIVEN
                    else upgrade_stat_rows(
                        upgrade,
                        self._slot_extra_preview_stats(index),
                    )
                )
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
                custom_entry=(
                    self.custom_weapon_entry or self.custom_weapon_placeholder
                )
                if self.custom_weapon
                else None,
                selected_mode=self.selected_attack_mode or None,
                evolutions=evolutions,
            )
            contribution_lookup = contribution_lookup_for_weapon(
                weapon,
                self.selected_weapon_type,
                None,
                upgrades,
            )

            contributions = []
            for index, config in enumerate(SLOT_CONFIGS):
                contribution_name = (
                    self.slot_selected_upgrades[index]
                    if self.slot_selected_upgrades[index] != CUSTOM
                    else config["label"]
                )
                contributions.append(
                    format_contribution(
                        contribution_for_category(contribution_lookup, contribution_name)
                    )
                )
            self.slot_contributions = contributions

            self.main_result_metrics = main_metrics(weapon)
            if self.selected_weapon_type == "Melee":
                self.weakpoint_result_metrics = []
                self.ranged_result_metrics = []
                self.misc_result_metrics = []
            else:
                self.weakpoint_result_metrics = weakpoint_metrics(weapon)
                self.misc_result_metrics = ranged_misc_metrics(weapon)
                self.ranged_result_metrics = (
                    self.main_result_metrics
                    + self.weakpoint_result_metrics
                    + self.misc_result_metrics
                )
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
            self.result_ready = True
        except Exception as exc:
            self.slot_contributions = ["—" for _ in SLOT_CONFIGS]
            self.main_result_metrics = []
            self.weakpoint_result_metrics = []
            self.ranged_result_metrics = []
            self.misc_result_metrics = []
            self.damage_result_rows = []
            self.contribution_result_rows = []
            self.result_summary = ""
            self.result_contribution_summary = ""
            self.result_error = f"{type(exc).__name__}: {exc}"
            self.result_ready = False
