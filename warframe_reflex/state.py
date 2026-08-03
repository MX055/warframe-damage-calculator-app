from __future__ import annotations

import copy
import threading
import time
import uuid
from typing import Any

import reflex as rx
from warframe_damage_calculator import Arcane, Dist, Mod, Progenitor, Upgrade
from warframe_damage_calculator.optimizer.candidates import DEFAULT_UPGRADE_BLACKLIST

from .constants import (
    ARCANE_FIELD,
    BUFF_FIELD,
    DAMAGE_TYPES,
    DEFAULT_DAMAGE_TYPES,
    DEFAULT_OPTIMIZE_SPATIAL,
    DEFAULT_OPTIMIZE_DPH_WEIGHT,
    DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT,
    DEFAULT_OPTIMIZE_MAXIMIZE,
    DEFAULT_OPTIMIZE_SEARCH,
    FIELD_WEAPON_RULES,
    INITIAL_COMBO_OPTION,
    INITIAL_COMBO_RUNTIME,
    MELEE_COMBO_OPTIONS,
    MOD_FIELD,
    NO_EFFECT,
    OPTIMIZE_MAXIMIZE_OPTIONS,
    OPTIMIZE_MAXIMIZE_TARGETS,
    OPTIMIZE_SPATIAL_OPTIONS,
    OPTIMIZE_SEARCH_EVALUATION_BUDGETS,
    OPTIMIZE_SEARCH_OPTIONS,
    PROGENITOR_ELEMENT_OPTIONS,
    RIVEN_NON_NEGATIVE_STATS,
    RIVEN_ROLL_CONFIGS,
    RIVEN_ROLL_OPTIONS,
    RIVEN_STAT_ALIASES,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP,
    SLOT_POLICY_OPTIONS,
    STANCE_SLOT_INDEX,
    WEAPON_CATEGORY_TYPES,
    UPGRADE_BOOL_FIELDS,
    UPGRADE_SCALAR_FIELDS,
)
from .data import (
    clean_evolution_description,
    database_conditional_info,
    database_max_stacks,
    database_rank_bounds,
    database_upgrade,
    enemies_for_faction,
    enemy_faction_for,
    enemy_faction_options,
    is_faction_damage_stat,
    optimizer_excludes_upgrade_by_default,
    raw_riven_stats_database,
    raw_upgrade_metadata,
    raw_weapon_metadata,
    upgrades_blocked_by_selected,
    preferred_exclusive_stance,
    selected_attack_category,
    stance_combo_key_for_attack_category,
    stance_combo_options_for_attack,
    upgrade_names_for_ui,
    _upgrade_names_for_ui,
    weapon_attack_modes,
    weapon_evolution_options,
    weapon_evolution_runtime_controls,
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
    contribution_lookup_map,
    contribution_value_for_name,
    stance_combo_rows,
    field_label,
    format_contribution,
    is_field_allowed,
    is_non_empty_upgrade,
    library_contribution_bundle,
    main_metrics,
    parse_float,
    parse_int,
    progenitor_upgrade,
    ranged_misc_metrics,
    result_summary,
    result_status_summary,
    resistant_metrics,
    upgrade_field_input_config,
    upgrade_description_rows,
    weak_point_metrics,
)
from .models import (
    ClearBuffRow,
    DisplayRow,
    EditorField,
    MetricRow,
    RuntimeStackField,
    RuntimeToggleField,
    SavedBuildRow,
)
from .persistence import (
    resolve_optimize_spatial,
    default_settings,
    delete_build,
    encode_builds,
    encode_settings,
    empty_build_slot_defaults,
    find_build,
    hydrate_editor_fields,
    hydrate_slot_fields,
    hydrate_stacks,
    hydrate_toggles,
    new_build_entry,
    pad_list,
    parse_builds,
    parse_settings,
    rename_build,
    snapshot_from_state_values,
    upsert_build,
)

NONE = "None"
RIVEN = "Riven"


def _format_elapsed(seconds: float) -> str:
    total = max(int(seconds), 0)
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}"


def _format_timestamp(seconds: float) -> str:
    total = max(int(seconds), 0)
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(total))


def _optimizer_progress(fraction: float) -> float:
    return min(max(float(fraction), 0.0) * 100.0, 100.0)


def _optimizer_progress_from_snapshot(progress) -> float:
    fraction = _optimizer_progress(progress.fraction)
    budget = int(getattr(progress, "evaluation_budget", 0) or 0)
    if budget > 0:
        fraction = max(fraction, _optimizer_progress(int(progress.evaluations) / budget))
    return fraction


def _optimizer_upgrade_blacklist(excluded: list[str] | set[str], default_overrides: list[str] | set[str]) -> set[str]:
    return (set(DEFAULT_UPGRADE_BLACKLIST) - set(default_overrides)) | set(excluded)


def _describe_optimize_phase(phase: str) -> str:
    lowered = phase.casefold()
    mappings = (
        ("preparing", "Preparing weapon, enemy, and compatible upgrades"),
        ("incarnon seed", "Testing initial Incarnon perk combinations"),
        ("greedy fill", "Building the initial upgrade loadout"),
        ("progenitor", "Testing progenitor elements"),
        ("riven slot", "Testing the best Riven in every compatible slot"),
        ("riven search", "Constructing and scoring Riven stat combinations"),
        ("two-move beam", "Exploring coordinated two-upgrade replacements"),
        ("rebuild", "Rebuilding from diversified candidate loadouts"),
        ("full-pool", "Searching the full compatible upgrade pool"),
        ("final", "Refining the best complete build"),
        ("incarnon", "Refining Incarnon perks and the surrounding build"),
        ("search", "Testing upgrade replacements and mod ordering"),
        ("finishing", "Validating and preparing the best build"),
    )
    description = next((text for key, text in mappings if key in lowered), phase)
    detail = phase[phase.find("("):] if "(" in phase else ""
    return f"{description} {detail}".strip()
RIVEN_EMPTY_STAT = "Select stat"

_OPTIMIZE_CANCEL_EVENTS: dict[str, threading.Event] = {}

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
    "base_weak_point_damage": (1.0, 20.0, False),
    "base_attack_speed": (0.0, 20.0, False),
    "base_recharge_rate": (0.0, 1000.0, False),
    "base_charge_time": (0.0, 20.0, False),
    "base_burst_count": (1.0, 100.0, True),
    "base_burst_delay": (0.0, 20.0, False),
    "progenitor_value": (0.0, 0.6, False),
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


def _empty_riven_editor_field() -> EditorField:
    return EditorField("", RIVEN_EMPTY_STAT, 0.0, 0.0, 0.0, False)



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
    weapon_select_open: bool = False
    selected_enemy_faction: str = ""
    enemy_faction_options: list[str] = rx.field(default_factory=list)
    selected_enemy: str = NONE
    enemy_options: list[str] = rx.field(default_factory=lambda: [NONE])
    enemy_select_open: bool = False
    enemy_level: int = 100
    enemy_steel_path: bool = False
    enemy_empowered: bool = False
    enemy_identity_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_body_part_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_modifier_rows: list[DisplayRow] = rx.field(default_factory=list)
    enemy_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    enemy_has_weak_point: bool = False
    enemy_has_resistant: bool = False
    enemy_error: str = ""
    attack_mode_options: list[str] = rx.field(default_factory=list)
    selected_attack_mode: str = ""
    evolution_labels: list[str] = rx.field(default_factory=list)
    evolution_options: list[list[str]] = rx.field(default_factory=list)
    evolution_selections: list[str] = rx.field(default_factory=list)
    evolution_condition_toggles: list[RuntimeToggleField] = rx.field(default_factory=list)
    evolution_stack_fields: list[RuntimeStackField] = rx.field(default_factory=list)
    melee_combo_count: str = INITIAL_COMBO_OPTION
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
    base_weak_point_damage: float = 3.0
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
    slot_riven_field_options: list[list[list[str]]] = rx.field(default_factory=_empty_nested_list)
    slot_riven_row_labels: list[list[str]] = rx.field(default_factory=_empty_nested_list)
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
    clear_keep_buff_fields: list[str] = rx.field(default_factory=list)
    optimize_find_riven: bool = False
    optimize_find_evolutions: bool = False
    optimize_find_progenitor: bool = False
    optimize_maximize_target: str = DEFAULT_OPTIMIZE_MAXIMIZE
    optimize_search_quality: str = DEFAULT_OPTIMIZE_SEARCH
    optimize_dph_weight: int = DEFAULT_OPTIMIZE_DPH_WEIGHT
    optimize_body_part_options: list[str] = rx.field(default_factory=list)
    optimize_body_part: str = ""
    optimize_flat_dot_weight: int = DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT
    optimize_spatial: str = DEFAULT_OPTIMIZE_SPATIAL
    optimize_spatial_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_SPATIAL_OPTIONS))
    optimize_maximize_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_MAXIMIZE_OPTIONS))
    optimize_search_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_SEARCH_OPTIONS))
    optimize_status: str = ""
    optimize_running: bool = False
    optimize_best_dps: str = ""
    optimize_progress: float = 0.0
    optimize_progress_width: str = "0%"
    optimize_phase: str = ""
    optimize_elapsed: str = "00:00:00"
    optimize_evaluations: int = 0
    optimize_evaluation_budget: int = 0
    optimize_revision: int = 0
    optimize_cancel_token: str = ""
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
    weak_point_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    resistant_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    ranged_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    misc_result_metrics: list[MetricRow] = rx.field(default_factory=list)
    result_metrics: list[MetricRow] = rx.field(default_factory=list)
    result_summary: str = ""
    result_status_summary: str = ""
    result_contribution_summary: str = ""
    contribution_revision: int = 0
    contributions_pending: bool = False
    result_error: str = ""
    result_errors: list[str] = rx.field(default_factory=list)
    result_ready: bool = False

    persisted_settings_json: str = rx.LocalStorage("{}", name="wfdc_settings")
    persisted_builds_json: str = rx.LocalStorage("{}", name="wfdc_builds")
    saved_build_rows: list[SavedBuildRow] = rx.field(default_factory=list)
    save_build_name: str = ""
    save_build_status: str = ""
    active_build_id: str = ""
    pending_build_id: str = ""
    calculator_bootstrapped: bool = False
    naming_new_build: bool = False
    new_build_name: str = ""
    rename_build_id: str = ""
    rename_build_name: str = ""
    hub_status: str = ""

    settings_enemy_faction: str = ""
    settings_enemy: str = NONE
    settings_enemy_options: list[str] = rx.field(default_factory=lambda: [NONE])
    settings_enemy_level: int = 100
    settings_enemy_steel_path: bool = False
    settings_enemy_empowered: bool = False
    settings_body_part: str = ""
    settings_body_part_options: list[str] = rx.field(default_factory=list)
    settings_maximize_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_MAXIMIZE_OPTIONS))
    settings_search_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_SEARCH_OPTIONS))
    settings_maximize_target: str = DEFAULT_OPTIMIZE_MAXIMIZE
    settings_search_quality: str = DEFAULT_OPTIMIZE_SEARCH
    settings_dph_weight: int = DEFAULT_OPTIMIZE_DPH_WEIGHT
    settings_flat_dot_weight: int = DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT
    settings_spatial: str = DEFAULT_OPTIMIZE_SPATIAL
    settings_spatial_options: list[str] = rx.field(default_factory=lambda: list(OPTIMIZE_SPATIAL_OPTIONS))
    settings_find_riven: bool = False
    settings_find_evolutions: bool = False
    settings_find_progenitor: bool = False
    settings_status: str = ""

    @rx.var
    def no_enemy(self) -> bool:
        return self.selected_enemy == NONE

    @rx.var
    def show_enemy_inline_error(self) -> bool:
        return bool(self.enemy_error)

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
    def clear_has_kept_items(self) -> bool:
        return any(self.clear_keep_slots) or bool(self.clear_keep_buff_fields)

    @rx.var
    def clear_external_buff_rows(self) -> list[ClearBuffRow]:
        kept = set(self.clear_keep_buff_fields)
        return [ClearBuffRow(field.name, field.label, field.name in kept) for field in self.external_fields]

    @rx.var
    def optimizer_enabled(self) -> bool:
        return self.selected_weapon != NONE and self.selected_enemy != NONE

    @rx.var
    def riven_optimize_disabled(self) -> bool:
        if not self.riven_optimize_available:
            return True
        return any(
            selected == RIVEN and policy == SLOT_POLICY_KEEP
            for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
        )

    @rx.var
    def riven_optimize_available(self) -> bool:
        return self.riven_available and not self.ability_strength_available

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

    @rx.var(cache=True)
    def editor_subtitle(self) -> str:
        name = self.save_build_name.strip()
        return name if name else "Edit build"

    @rx.var
    def supports_progenitor(self) -> bool:
        return self._supports_progenitor()

    @rx.var
    def optimize_dps_weight(self) -> int:
        return 100 - self.optimize_dph_weight

    def _ability_strength_multiplier(self) -> float | None:
        if not self.ability_strength_available:
            return None
        return max(float(self.ability_strength), 0.0) / 100.0

    def _selected_evolutions(self) -> dict[int, int]:
        return {
            parse_int(self.evolution_labels[index].rsplit(" ", 1)[-1]): parse_int(selection.split()[1])
            for index, selection in enumerate(self.evolution_selections)
            if selection != NONE
        }

    def _evolution_runtime_context(self) -> dict[str, bool | int]:
        return {
            **{field.name: bool(field.value) for field in self.evolution_condition_toggles},
            **{field.name: parse_int(field.value) for field in self.evolution_stack_fields},
        }

    def _combo_runtime_value(self) -> int | str:
        return INITIAL_COMBO_RUNTIME if self.melee_combo_count == INITIAL_COMBO_OPTION else parse_int(self.melee_combo_count, 12)

    def _selected_attack_category(self) -> str:
        weapon_name = None if self.selected_weapon == NONE else self.selected_weapon
        return selected_attack_category(weapon_name, self.selected_attack_mode)

    def _set_default_melee_combo_for_selected_attack(self):
        self.melee_combo_count = INITIAL_COMBO_OPTION

    def _clear_optimizer_result(self):
        self.optimize_status = ""
        self.optimize_best_dps = ""
        self.optimize_progress = 0.0
        self.optimize_progress_width = "0%"
        self.optimize_phase = ""
        self.optimize_elapsed = "00:00:00"
        self.optimize_evaluations = 0
        self.optimize_evaluation_budget = 0

    def _invalidate_optimizer_result(self):
        self.optimize_revision += 1
        self._clear_optimizer_result()

    def _reset_optimizer_settings(self):
        self._invalidate_optimizer_result()
        self.optimize_find_riven = False
        self.optimize_find_evolutions = False
        self.optimize_find_progenitor = False
        self.optimize_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE
        self.optimize_search_quality = DEFAULT_OPTIMIZE_SEARCH
        self.optimize_dph_weight = DEFAULT_OPTIMIZE_DPH_WEIGHT
        self.optimize_body_part_options = []
        self.optimize_body_part = ""
        self.optimize_flat_dot_weight = DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT
        self.optimize_spatial = DEFAULT_OPTIMIZE_SPATIAL
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
        if keep_marked:
            keep_buff_names = set(self.clear_keep_buff_fields)
            self.external_fields = [field for field in self.external_fields if field.name in keep_buff_names]
            self.clear_keep_buff_fields = [field.name for field in self.external_fields]
        else:
            self.external_fields = []
            self.clear_keep_buff_fields = []
        self._refresh_external_field_options()

    def _reset_for_weapon_change(self):
        self._clear_build_state()
        self._reset_optimizer_settings()
        self.melee_combo_count = INITIAL_COMBO_OPTION
        self.evolution_condition_toggles = []
        self.evolution_stack_fields = []

    def _settings(self) -> dict:
        return parse_settings(self.persisted_settings_json)

    def _builds(self) -> list[dict]:
        return parse_builds(self.persisted_builds_json)

    def _persist_settings(self, settings: dict):
        self.persisted_settings_json = encode_settings(settings)

    def _persist_builds(self, builds: list[dict]):
        self.persisted_builds_json = encode_builds(builds)
        self._refresh_saved_build_rows()

    def _refresh_saved_build_rows(self):
        rows = []
        for entry in self._builds():
            rows.append(SavedBuildRow(
                id=str(entry["id"]),
                name=str(entry["name"]),
                weapon=str(entry.get("weapon") or NONE),
                enemy=str(entry.get("enemy") or NONE),
                updated_label=_format_timestamp(float(entry.get("updated_at") or 0)),
            ))
        self.saved_build_rows = rows

    def _build_snapshot(self) -> dict:
        return snapshot_from_state_values(
            selected_weapon_type=self.selected_weapon_type,
            selected_weapon_category=self.selected_weapon_category,
            selected_weapon=self.selected_weapon,
            selected_attack_mode=self.selected_attack_mode,
            evolution_selections=self.evolution_selections,
            evolution_condition_toggles=self.evolution_condition_toggles,
            evolution_stack_fields=self.evolution_stack_fields,
            melee_combo_count=self.melee_combo_count,
            selected_stance_combo=self.selected_stance_combo,
            progenitor_element=self.progenitor_element,
            progenitor_value=self.progenitor_value,
            ability_strength=self.ability_strength,
            selected_enemy_faction=self.selected_enemy_faction,
            selected_enemy=self.selected_enemy,
            enemy_level=self.enemy_level,
            enemy_steel_path=self.enemy_steel_path,
            enemy_empowered=self.enemy_empowered,
            optimize_body_part=self.optimize_body_part,
            slot_selected_upgrades=self.slot_selected_upgrades,
            slot_policies=self.slot_policies,
            slot_ranks=self.slot_ranks,
            slot_stacks=self.slot_stacks,
            slot_conditions_enabled=self.slot_conditions_enabled,
            slot_fields=self.slot_fields,
            slot_riven_rolls=self.slot_riven_rolls,
            external_fields=self.external_fields,
            optimize_find_riven=self.optimize_find_riven,
            optimize_find_evolutions=self.optimize_find_evolutions,
            optimize_find_progenitor=self.optimize_find_progenitor,
            optimize_maximize_target=self.optimize_maximize_target,
            optimize_search_quality=self.optimize_search_quality,
            optimize_dph_weight=self.optimize_dph_weight,
            optimize_flat_dot_weight=self.optimize_flat_dot_weight,
            optimize_spatial=self.optimize_spatial,
            optimize_excluded_upgrades=self.optimize_excluded_upgrades,
            optimize_default_exclusion_overrides=self.optimize_default_exclusion_overrides,
            optimize_excluded_riven_stats=self.optimize_excluded_riven_stats,
            optimize_default_riven_exclusion_overrides=self.optimize_default_riven_exclusion_overrides,
        )

    def _apply_optimizer_settings(self, optimizer: dict):
        self.optimize_find_riven = bool(optimizer.get("find_riven", False))
        self.optimize_find_evolutions = bool(optimizer.get("find_evolutions", False))
        self.optimize_find_progenitor = bool(optimizer.get("find_progenitor", False))
        self.optimize_maximize_target = str(optimizer.get("maximize_target") or DEFAULT_OPTIMIZE_MAXIMIZE)
        if self.optimize_maximize_target not in OPTIMIZE_MAXIMIZE_OPTIONS:
            self.optimize_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE
        self.optimize_search_quality = str(optimizer.get("search_quality") or DEFAULT_OPTIMIZE_SEARCH)
        if self.optimize_search_quality not in OPTIMIZE_SEARCH_OPTIONS:
            self.optimize_search_quality = DEFAULT_OPTIMIZE_SEARCH
        self.optimize_dph_weight = int(optimizer.get("dph_weight", DEFAULT_OPTIMIZE_DPH_WEIGHT))
        self.optimize_flat_dot_weight = int(optimizer.get("flat_dot_weight", DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT))
        self.optimize_spatial = resolve_optimize_spatial(optimizer)
        self.optimize_excluded_upgrades = list(optimizer.get("excluded_upgrades") or [])
        self.optimize_default_exclusion_overrides = list(optimizer.get("default_exclusion_overrides") or [])
        self.optimize_excluded_riven_stats = list(optimizer.get("excluded_riven_stats") or [])
        self.optimize_default_riven_exclusion_overrides = list(optimizer.get("default_riven_exclusion_overrides") or [])
        self.optimize_pending_excluded_upgrade = ""
        self.optimize_pending_excluded_riven_stat = ""

    def _apply_settings(self, settings: dict | None = None):
        data = settings or self._settings()
        enemy = data.get("enemy") or {}
        optimizer = data.get("optimizer") or {}
        self._refresh_enemy_options()
        faction = str(enemy.get("faction") or "")
        if faction and faction in self.enemy_faction_options:
            self.selected_enemy_faction = faction
            self.enemy_options = [NONE, *enemies_for_faction(faction)]
        enemy_name = str(enemy.get("name") or NONE)
        self.selected_enemy = enemy_name if enemy_name in self.enemy_options else NONE
        self.enemy_level = int(enemy.get("level", 100))
        self.enemy_steel_path = bool(enemy.get("steel_path", False))
        self.enemy_empowered = bool(enemy.get("empowered", False))
        self.optimize_body_part = str(enemy.get("body_part") or "")
        self._apply_optimizer_settings(optimizer)
        maximize = self.optimize_maximize_target
        self._sync_enemy_preview()
        if maximize in OPTIMIZE_MAXIMIZE_OPTIONS:
            self.optimize_maximize_target = maximize

    def _sync_enemy_preview(self):
        try:
            target = self._target_enemy()
            self._refresh_enemy_preview(target)
        except Exception as exc:
            self.enemy_error = f"{type(exc).__name__}: {exc}"
            if self.no_enemy:
                self._refresh_enemy_preview(None)

    def _apply_build_snapshot(self, snapshot: dict):
        defaults = empty_build_slot_defaults()
        data = {**defaults, **(snapshot or {})}
        category = str(data.get("selected_weapon_category") or "Rifle")
        if category not in WEAPON_CATEGORY_TYPES:
            category = "Rifle"
        self.selected_weapon_category = category
        self.selected_weapon_type = str(data.get("selected_weapon_type") or WEAPON_CATEGORY_TYPES[category])
        if self.selected_weapon_type not in {"Primary", "Secondary", "Melee"}:
            self.selected_weapon_type = WEAPON_CATEGORY_TYPES[category]
        self._refresh_weapon_options()
        weapon_name = str(data.get("selected_weapon") or NONE)
        self.selected_weapon = weapon_name if weapon_name in self.weapon_options else NONE
        saved_attack_mode = str(data.get("selected_attack_mode") or "")
        saved_evolutions = list(data.get("evolution_selections") or [])
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        if saved_attack_mode and saved_attack_mode in self.attack_mode_options:
            self.selected_attack_mode = saved_attack_mode
        elif self.attack_mode_options:
            self.selected_attack_mode = self.attack_mode_options[0]
        else:
            self.selected_attack_mode = ""
        self.evolution_selections = [
            saved_evolutions[index] if index < len(saved_evolutions) and saved_evolutions[index] in (self.evolution_options[index] if index < len(self.evolution_options) else []) else "None"
            for index, _ in enumerate(self.evolution_labels)
        ]
        self._refresh_evolution_runtime_controls()
        saved_toggles = {field.name: field.value for field in hydrate_toggles(data.get("evolution_condition_toggles"))}
        saved_stacks = {field.name: field.value for field in hydrate_stacks(data.get("evolution_stack_fields"))}
        if saved_toggles:
            toggles = copy.deepcopy(self.evolution_condition_toggles)
            for field in toggles:
                if field.name in saved_toggles:
                    field.value = bool(saved_toggles[field.name])
            self.evolution_condition_toggles = toggles
        if saved_stacks:
            stacks = copy.deepcopy(self.evolution_stack_fields)
            for field in stacks:
                if field.name in saved_stacks:
                    field.value = str(saved_stacks[field.name])
            self.evolution_stack_fields = stacks

        self.melee_combo_count = str(data.get("melee_combo_count") or INITIAL_COMBO_OPTION)
        if self.melee_combo_count not in MELEE_COMBO_OPTIONS:
            self.melee_combo_count = INITIAL_COMBO_OPTION
        self.progenitor_element = str(data.get("progenitor_element") or NO_EFFECT)
        self.progenitor_value = float(data.get("progenitor_value") or 0.0)
        if self.progenitor_element not in {NO_EFFECT, NONE, ""} and self.progenitor_value <= 0:
            self.progenitor_value = 0.6
        self.ability_strength = float(data.get("ability_strength") or 100.0)

        self._refresh_enemy_options()
        faction = str(data.get("selected_enemy_faction") or "")
        if faction and faction in self.enemy_faction_options:
            self.selected_enemy_faction = faction
            self.enemy_options = [NONE, *enemies_for_faction(faction)]
        enemy_name = str(data.get("selected_enemy") or NONE)
        self.selected_enemy = enemy_name if enemy_name in self.enemy_options else NONE
        self.enemy_level = int(data.get("enemy_level") or 100)
        self.enemy_steel_path = bool(data.get("enemy_steel_path", False))
        self.enemy_empowered = bool(data.get("enemy_empowered", False))
        self.optimize_body_part = str(data.get("optimize_body_part") or "")
        self._sync_enemy_preview()

        slot_count = len(SLOT_CONFIGS)
        self.slot_selected_upgrades = pad_list(data.get("slot_selected_upgrades"), slot_count, NONE)
        self.slot_policies = pad_list(data.get("slot_policies"), slot_count, SLOT_POLICY_DISCARD)
        self.slot_ranks = [int(value) for value in pad_list(data.get("slot_ranks"), slot_count, 0)]
        self.slot_stacks = [int(value) for value in pad_list(data.get("slot_stacks"), slot_count, 0)]
        self.slot_conditions_enabled = [bool(value) for value in pad_list(data.get("slot_conditions_enabled"), slot_count, True)]
        self.slot_riven_rolls = pad_list(data.get("slot_riven_rolls"), slot_count, "2 Positive + 1 Negative")
        self.slot_fields = hydrate_slot_fields(data.get("slot_fields"))
        self.external_fields = hydrate_editor_fields(data.get("external_fields"))
        max_ranks, max_stacks = list(self.slot_max_ranks), list(self.slot_max_stacks)
        for index, config in enumerate(SLOT_CONFIGS):
            name = self.slot_selected_upgrades[index]
            if name in {NONE, RIVEN}:
                max_ranks[index] = 0 if name != NONE else (5 if config["kind"] == "arcane" else 10)
                max_stacks[index] = 0
            else:
                _, maximum_rank = database_rank_bounds(name, is_arcane_slot=config["kind"] == "arcane")
                maximum_stacks = database_max_stacks(name, is_arcane_slot=config["kind"] == "arcane") or 0
                max_ranks[index], max_stacks[index] = maximum_rank, maximum_stacks
        self.slot_max_ranks, self.slot_max_stacks = max_ranks, max_stacks
        self._ensure_selected_upgrades_in_options()
        self._refresh_slot_condition_metadata()
        self._refresh_all_riven_field_limits()
        self._refresh_all_field_options()
        self._refresh_external_field_options()
        previous_combo = str(data.get("selected_stance_combo") or "neutral")
        self._refresh_stance_combo_options()
        self.selected_stance_combo = previous_combo if previous_combo in self.stance_combo_options else (self.stance_combo_options[0] if self.stance_combo_options else "neutral")

        self._apply_optimizer_settings({
            "find_riven": data.get("optimize_find_riven", False),
            "find_evolutions": data.get("optimize_find_evolutions", False),
            "find_progenitor": data.get("optimize_find_progenitor", False),
            "maximize_target": data.get("optimize_maximize_target", DEFAULT_OPTIMIZE_MAXIMIZE),
            "search_quality": data.get("optimize_search_quality", DEFAULT_OPTIMIZE_SEARCH),
            "dph_weight": data.get("optimize_dph_weight", DEFAULT_OPTIMIZE_DPH_WEIGHT),
            "flat_dot_weight": data.get("optimize_flat_dot_weight", DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT),
            "spatial": resolve_optimize_spatial({"spatial": data.get("optimize_spatial"), "aoe_weight": data.get("optimize_aoe_weight")}),
            "excluded_upgrades": data.get("optimize_excluded_upgrades") or [],
            "default_exclusion_overrides": data.get("optimize_default_exclusion_overrides") or [],
            "excluded_riven_stats": data.get("optimize_excluded_riven_stats") or [],
            "default_riven_exclusion_overrides": data.get("optimize_default_riven_exclusion_overrides") or [],
        })
        self._refresh_optimizer_exclusion_options()
        self._invalidate_optimizer_result()

    def _prepare_new_calculator_session(self):
        self.active_build_id = ""
        self.pending_build_id = ""
        self.save_build_name = ""
        self.save_build_status = ""
        self._clear_build_state()
        self._reset_optimizer_settings()
        self.selected_weapon_category = "Rifle"
        self.selected_weapon_type = "Primary"
        self.selected_weapon = NONE
        self.selected_attack_mode = ""
        self.evolution_selections = []
        self.evolution_condition_toggles = []
        self.evolution_stack_fields = []
        self.melee_combo_count = INITIAL_COMBO_OPTION
        self.selected_stance_combo = "neutral"
        self.progenitor_element = NO_EFFECT
        self.progenitor_value = 0.0
        self.ability_strength = 100.0
        self._refresh_weapon_options()
        self._refresh_weapon_features()
        self._refresh_upgrade_options()
        self._apply_settings()
        self._refresh_all_riven_field_limits()
        self._refresh_damage_options()
        self._refresh_all_field_options()

    def _load_settings_form(self):
        settings = self._settings()
        enemy = settings["enemy"]
        optimizer = settings["optimizer"]
        self._refresh_enemy_options()
        faction = str(enemy.get("faction") or self.selected_enemy_faction or (self.enemy_faction_options[0] if self.enemy_faction_options else ""))
        self.settings_enemy_faction = faction if faction in self.enemy_faction_options else (self.enemy_faction_options[0] if self.enemy_faction_options else "")
        self.settings_enemy_options = [NONE, *enemies_for_faction(self.settings_enemy_faction)]
        enemy_name = str(enemy.get("name") or NONE)
        self.settings_enemy = enemy_name if enemy_name in self.settings_enemy_options else NONE
        self.settings_enemy_level = int(enemy.get("level", 100))
        self.settings_enemy_steel_path = bool(enemy.get("steel_path", False))
        self.settings_enemy_empowered = bool(enemy.get("empowered", False))
        self.settings_body_part = str(enemy.get("body_part") or "")
        self._refresh_settings_body_parts()
        self.settings_maximize_target = str(optimizer.get("maximize_target") or DEFAULT_OPTIMIZE_MAXIMIZE)
        if self.settings_maximize_target not in OPTIMIZE_MAXIMIZE_OPTIONS:
            self.settings_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE
        self.settings_search_quality = str(optimizer.get("search_quality") or DEFAULT_OPTIMIZE_SEARCH)
        if self.settings_search_quality not in OPTIMIZE_SEARCH_OPTIONS:
            self.settings_search_quality = DEFAULT_OPTIMIZE_SEARCH
        self.settings_dph_weight = int(optimizer.get("dph_weight", DEFAULT_OPTIMIZE_DPH_WEIGHT))
        self.settings_flat_dot_weight = int(optimizer.get("flat_dot_weight", DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT))
        self.settings_spatial = resolve_optimize_spatial(optimizer)
        self.settings_find_riven = bool(optimizer.get("find_riven", False))
        self.settings_find_evolutions = bool(optimizer.get("find_evolutions", False))
        self.settings_find_progenitor = bool(optimizer.get("find_progenitor", False))
        self.settings_status = ""

    def _refresh_settings_body_parts(self):
        if self.settings_enemy == NONE:
            self.settings_body_part_options = []
            self.settings_body_part = ""
            return
        try:
            enemy = configured_enemy(
                self.settings_enemy,
                level=self.settings_enemy_level,
                steel_path=self.settings_enemy_steel_path,
                empowered=self.settings_enemy_empowered,
            )
        except Exception:
            self.settings_body_part_options = []
            self.settings_body_part = ""
            return
        options = list(getattr(enemy, "body_parts", {}) or {})
        self.settings_body_part_options = options
        if self.settings_body_part not in options:
            self.settings_body_part = options[0] if options else ""

    def _settings_from_form(self) -> dict:
        settings = default_settings()
        settings["enemy"] = {
            "faction": self.settings_enemy_faction,
            "name": self.settings_enemy,
            "level": int(self.settings_enemy_level),
            "steel_path": bool(self.settings_enemy_steel_path),
            "empowered": bool(self.settings_enemy_empowered),
            "body_part": self.settings_body_part,
        }
        settings["optimizer"] = {
            "maximize_target": self.settings_maximize_target,
            "search_quality": self.settings_search_quality,
            "dph_weight": int(self.settings_dph_weight),
            "flat_dot_weight": int(self.settings_flat_dot_weight),
            "spatial": self.settings_spatial,
            "find_riven": bool(self.settings_find_riven),
            "find_evolutions": bool(self.settings_find_evolutions),
            "find_progenitor": bool(self.settings_find_progenitor),
            "excluded_upgrades": list(self._settings()["optimizer"].get("excluded_upgrades") or []),
            "default_exclusion_overrides": list(self._settings()["optimizer"].get("default_exclusion_overrides") or []),
            "excluded_riven_stats": list(self._settings()["optimizer"].get("excluded_riven_stats") or []),
            "default_riven_exclusion_overrides": list(self._settings()["optimizer"].get("default_riven_exclusion_overrides") or []),
        }
        return settings

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
        self._refresh_saved_build_rows()
        return self._recalculate()

    @rx.event
    def hub_on_load(self):
        if not self.initialized:
            self.initialized = True
            self._refresh_enemy_options()
            self._refresh_weapon_options()
            self._refresh_weapon_features()
            self._refresh_upgrade_options()
            self._refresh_all_riven_field_limits()
            self._refresh_damage_options()
            self._refresh_all_field_options()
        if self.calculator_bootstrapped and self.active_build_id:
            self._autosave_active_build()
        self._refresh_saved_build_rows()
        self.hub_status = ""
        self.rename_build_id = ""
        self.rename_build_name = ""
        self.naming_new_build = False
        self.new_build_name = ""

    @rx.event
    def settings_on_load(self):
        if not self.initialized:
            self.initialized = True
            self._refresh_enemy_options()
            self._refresh_weapon_options()
            self._refresh_weapon_features()
            self._refresh_upgrade_options()
            self._refresh_all_riven_field_limits()
            self._refresh_damage_options()
            self._refresh_all_field_options()
            self._refresh_saved_build_rows()
        if self.calculator_bootstrapped and self.active_build_id:
            self._autosave_active_build()
        self._load_settings_form()

    @rx.event
    def calculator_on_load(self):
        if not self.initialized:
            self.initialized = True
            self._refresh_enemy_options()
            self._refresh_weapon_options()
            self._refresh_weapon_features()
            self._refresh_upgrade_options()
            self._refresh_all_riven_field_limits()
            self._refresh_damage_options()
            self._refresh_all_field_options()
            self._refresh_saved_build_rows()
        if self.pending_build_id:
            entry = find_build(self._builds(), self.pending_build_id)
            self.pending_build_id = ""
            if entry is not None:
                self.active_build_id = str(entry["id"])
                self.save_build_name = str(entry.get("name") or "")
                self._apply_build_snapshot(entry.get("snapshot") or {})
                self.calculator_bootstrapped = True
                return self._recalculate()
        if not self.calculator_bootstrapped:
            return rx.redirect("/")

    def _autosave_active_build(self) -> bool:
        name = self.save_build_name.strip()
        if not self.active_build_id or not name:
            return False
        entry = new_build_entry(name, self._build_snapshot())
        entry["id"] = self.active_build_id
        builds = upsert_build(self._builds(), entry, replace_id=self.active_build_id)
        self._persist_builds(builds)
        self._refresh_saved_build_rows()
        return True

    @rx.event
    def exit_to_hub(self):
        self._autosave_active_build()
        return rx.redirect("/")

    @rx.event
    def begin_new_build(self):
        self.naming_new_build = True
        self.new_build_name = ""
        self.hub_status = ""

    @rx.event
    def cancel_new_build(self):
        self.naming_new_build = False
        self.new_build_name = ""

    @rx.event
    def set_new_build_name(self, value: str):
        self.new_build_name = value

    @rx.event
    def confirm_new_build(self):
        name = self.new_build_name.strip()
        if not name:
            self.hub_status = "Enter a build name."
            return
        self._prepare_new_calculator_session()
        entry = new_build_entry(name, self._build_snapshot())
        builds = upsert_build(self._builds(), entry)
        self.active_build_id = entry["id"]
        self.save_build_name = name
        self.naming_new_build = False
        self.new_build_name = ""
        self.calculator_bootstrapped = True
        self.hub_status = ""
        self._persist_builds(builds)
        self._refresh_saved_build_rows()
        self._recalculate()
        return rx.redirect("/calculator")

    @rx.event
    def open_saved_build(self, build_id: str):
        entry = find_build(self._builds(), build_id)
        if entry is None:
            self.hub_status = "Saved build not found."
            self._refresh_saved_build_rows()
            return
        if self.calculator_bootstrapped and self.active_build_id and self.active_build_id != build_id:
            self._autosave_active_build()
        self.pending_build_id = str(entry["id"])
        self.calculator_bootstrapped = False
        self.hub_status = ""
        return rx.redirect("/calculator")

    @rx.event
    def delete_saved_build(self, build_id: str):
        builds = delete_build(self._builds(), build_id)
        self._persist_builds(builds)
        if self.active_build_id == build_id:
            self.active_build_id = ""
        if self.rename_build_id == build_id:
            self.rename_build_id = ""
            self.rename_build_name = ""
        self.hub_status = "Build deleted."

    @rx.event
    def begin_rename_build(self, build_id: str):
        entry = find_build(self._builds(), build_id)
        if entry is None:
            return
        self.rename_build_id = build_id
        self.rename_build_name = str(entry.get("name") or "")

    @rx.event
    def set_rename_build_name(self, value: str):
        self.rename_build_name = value

    @rx.event
    def confirm_rename_build(self):
        if not self.rename_build_id:
            return
        builds = rename_build(self._builds(), self.rename_build_id, self.rename_build_name)
        self._persist_builds(builds)
        self.rename_build_id = ""
        self.rename_build_name = ""
        self.hub_status = "Build renamed."

    @rx.event
    def cancel_rename_build(self):
        self.rename_build_id = ""
        self.rename_build_name = ""

    @rx.event
    def set_save_build_name(self, value: str):
        self.save_build_name = value

    @rx.event
    def save_current_build(self):
        if self._autosave_active_build():
            self.save_build_status = "Build saved."
            return
        name = self.save_build_name.strip()
        if not name:
            self.save_build_status = "Enter a build name."
            return
        entry = new_build_entry(name, self._build_snapshot())
        builds = upsert_build(self._builds(), entry)
        self.active_build_id = entry["id"]
        self._persist_builds(builds)
        self._refresh_saved_build_rows()
        self.save_build_status = "Build saved."

    @rx.event
    def set_settings_enemy_faction(self, value: str):
        if value not in self.enemy_faction_options:
            return
        self.settings_enemy_faction = value
        self.settings_enemy_options = [NONE, *enemies_for_faction(value)]
        if self.settings_enemy not in self.settings_enemy_options:
            self.settings_enemy = NONE
        self._refresh_settings_body_parts()

    @rx.event
    def set_settings_enemy(self, value: str):
        self.settings_enemy = value if value in self.settings_enemy_options else NONE
        self._refresh_settings_body_parts()

    @rx.event
    def set_settings_enemy_level(self, value: str):
        self.settings_enemy_level = max(1, parse_int(value, self.settings_enemy_level))
        self._refresh_settings_body_parts()

    @rx.event
    def set_settings_enemy_steel_path(self, value: bool):
        self.settings_enemy_steel_path = bool(value)
        self._refresh_settings_body_parts()

    @rx.event
    def set_settings_enemy_empowered(self, value: bool):
        self.settings_enemy_empowered = bool(value)
        self._refresh_settings_body_parts()

    @rx.event
    def set_settings_body_part(self, value: str):
        if value in self.settings_body_part_options:
            self.settings_body_part = value

    @rx.event
    def set_settings_maximize_target(self, value: str):
        if value in OPTIMIZE_MAXIMIZE_OPTIONS:
            self.settings_maximize_target = value

    @rx.event
    def set_settings_search_quality(self, value: str):
        if value in OPTIMIZE_SEARCH_OPTIONS:
            self.settings_search_quality = value

    @rx.event
    def set_settings_dph_weight(self, value: str | int | float):
        try:
            weight = int(float(value))
        except (TypeError, ValueError):
            return
        self.settings_dph_weight = max(0, min(weight, 100))

    @rx.event
    def set_settings_flat_dot_weight(self, value: str | int | float):
        try:
            weight = int(float(value))
        except (TypeError, ValueError):
            return
        self.settings_flat_dot_weight = max(0, min(weight, 100))

    @rx.event
    def set_settings_spatial(self, value: str):
        if value not in OPTIMIZE_SPATIAL_OPTIONS:
            return
        self.settings_spatial = value

    @rx.event
    def set_settings_find_riven(self, value: bool):
        self.settings_find_riven = bool(value)

    @rx.event
    def set_settings_find_evolutions(self, value: bool):
        self.settings_find_evolutions = bool(value)

    @rx.event
    def set_settings_find_progenitor(self, value: bool):
        self.settings_find_progenitor = bool(value)

    @rx.event
    def save_settings(self):
        self._persist_settings(self._settings_from_form())
        self.settings_status = "Settings saved."

    @rx.event
    def reset_settings(self):
        self._persist_settings(default_settings())
        self._load_settings_form()
        self.settings_status = "Settings reset to defaults."

    @rx.event
    def set_weapon_type(self, value: str):
        if value not in WEAPON_CATEGORY_TYPES or value == self.selected_weapon_category:
            return
        self._reset_for_weapon_change()
        self.selected_weapon_category = value
        self.selected_weapon_type = WEAPON_CATEGORY_TYPES[value]
        self.selected_weapon = NONE
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
        return self._recalculate()

    @rx.event
    def set_weapon_select_open(self, value: bool):
        self.weapon_select_open = bool(value)

    @rx.event
    def set_enemy_select_open(self, value: bool):
        self.enemy_select_open = bool(value)

    @rx.event
    def set_enemy_faction(self, value: str):
        if value not in self.enemy_faction_options or value == self.selected_enemy_faction:
            return
        self.selected_enemy_faction = value
        self.enemy_select_open = False
        previous = self.selected_enemy
        self.enemy_options = [NONE, *enemies_for_faction(value)]
        if self.selected_enemy not in self.enemy_options:
            self.selected_enemy = NONE
        if self.selected_enemy != previous:
            self._invalidate_optimizer_result()
            return self._recalculate()

    @rx.event
    def set_weapon(self, value: str):
        self.weapon_select_open = False
        selected_weapon = value if value in self.weapon_options else NONE
        if selected_weapon == self.selected_weapon:
            return
        self._reset_for_weapon_change()
        self.selected_weapon = selected_weapon
        self._refresh_weapon_features()
        self._set_default_melee_combo_for_selected_attack()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        return self._recalculate()

    @rx.event
    def set_enemy(self, value: str):
        self.enemy_select_open = False
        self.selected_enemy = value if value in self.enemy_options else NONE
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_enemy_level(self, value: str):
        self.enemy_level = max(1, min(parse_int(value, self.enemy_level), 9999))
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_enemy_toggle(self, field_name: str, value: bool):
        if field_name not in {"enemy_steel_path", "enemy_empowered"}:
            return
        setattr(self, field_name, bool(value))
        self._invalidate_optimizer_result()
        return self._recalculate()


    @rx.event
    def set_attack_mode(self, value: str):
        if value not in self.attack_mode_options:
            return
        self.selected_attack_mode = value
        self._set_default_melee_combo_for_selected_attack()
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_slot_field_options()
        return self._recalculate()

    @rx.event
    def set_evolution(self, index: int, value: str):
        if not 0 <= index < len(self.evolution_options) or value not in self.evolution_options[index]:
            return
        selections = list(self.evolution_selections)
        selections[index] = value
        self.evolution_selections = selections
        self._refresh_evolution_runtime_controls()
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_melee_combo_count(self, value: str):
        if value not in MELEE_COMBO_OPTIONS:
            return
        self.melee_combo_count = value
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_evolution_condition(self, name: str, value: bool):
        fields = copy.deepcopy(self.evolution_condition_toggles)
        for field in fields:
            if field.name == name:
                field.value = bool(value)
                self.evolution_condition_toggles = fields
                self._invalidate_optimizer_result()
                return self._recalculate()

    @rx.event
    def set_evolution_stacks(self, name: str, value: str):
        fields = copy.deepcopy(self.evolution_stack_fields)
        for field in fields:
            if field.name == name and value in field.options:
                field.value = value
                self.evolution_stack_fields = fields
                self._invalidate_optimizer_result()
                return self._recalculate()

    @rx.event
    def set_progenitor_element(self, value: str):
        self.progenitor_element = value
        if value not in {NO_EFFECT, NONE, ""} and self.progenitor_value <= 0:
            self.progenitor_value = 0.6
        self._invalidate_optimizer_result()
        return self._recalculate()

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
        return self._recalculate()

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
        return self._recalculate()

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
        return self._recalculate()

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
        return self._recalculate()

    @rx.event
    def set_damage_value(self, group: str, damage_name: str, value: str):
        fields = copy.deepcopy(self._get_damage_fields(group))
        for field in fields:
            if field.name == damage_name:
                field.value = max(0.0, parse_float(value, field.value))
                break
        self._set_damage_fields(group, fields)
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def toggle_slot_editor(self, index: int):
        if not 0 <= index < len(SLOT_CONFIGS) or self.optimize_busy:
            return
        should_open = not self.slot_editor_open[index]
        self.slot_editor_open = [should_open and position == index for position in range(len(SLOT_CONFIGS))]

    @rx.event
    def set_clear_keep_slot(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS) or self.slot_selected_upgrades[index] == NONE:
            return
        keep_slots = list(self.clear_keep_slots)
        keep_slots[index] = bool(value)
        self.clear_keep_slots = keep_slots

    @rx.event
    def set_clear_keep_buff(self, field_name: str, value: bool):
        if not any(field.name == field_name for field in self.external_fields):
            return
        names = [name for name in self.clear_keep_buff_fields if name != field_name]
        if value:
            names.append(field_name)
        self.clear_keep_buff_fields = names

    @rx.event
    def clear_build_and_buffs(self):
        self._clear_build_state(keep_marked=True)
        self._invalidate_optimizer_result()
        self._refresh_upgrade_options()
        self._refresh_all_riven_field_limits()
        self._refresh_all_field_options()
        return self._recalculate()

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
        return self._recalculate()

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
            return self._recalculate()
        if previous == NONE or value in self.optimize_excluded_upgrades:
            policies[index] = SLOT_POLICY_DISCARD
            self.slot_policies = policies

        max_ranks = list(self.slot_max_ranks)
        ranks = list(self.slot_ranks)
        max_stacks = list(self.slot_max_stacks)
        stacks = list(self.slot_stacks)

        if value == RIVEN:
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
        if value == RIVEN and self.slot_policies[index] == SLOT_POLICY_KEEP:
            self.optimize_find_riven = False
        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()
        self._refresh_slot_field_options()
        return self._recalculate()

    @rx.event
    def set_stance_combo(self, value: str):
        if value not in self.stance_combo_options:
            return
        self.selected_stance_combo = value
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_slot_policy(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS) or value not in SLOT_POLICY_OPTIONS:
            return
        policies = list(self.slot_policies)
        policies[index] = value
        self.slot_policies = policies
        if self.slot_selected_upgrades[index] == RIVEN and value == SLOT_POLICY_KEEP:
            self.optimize_find_riven = False
        self._invalidate_optimizer_result()
        selected = self.slot_selected_upgrades[index]
        if value == SLOT_POLICY_KEEP and selected in self.optimize_excluded_upgrades:
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
    def restore_optimize_excluded_upgrades(self):
        self.optimize_default_exclusion_overrides = []
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
    def restore_optimize_excluded_riven_stats(self):
        self.optimize_default_riven_exclusion_overrides = []
        self.optimize_excluded_riven_stats = []
        self._invalidate_optimizer_result()
        self._refresh_optimizer_exclusion_options()

    @rx.event
    def set_optimize_find_riven(self, value: bool):
        locked = (not self.riven_optimize_available) or any(
            selected == RIVEN and policy == SLOT_POLICY_KEEP
            for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
        )
        self.optimize_find_riven = bool(value) and not locked
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_find_evolutions(self, value: bool):
        self.optimize_find_evolutions = bool(value) and bool(self.evolution_options)
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_find_progenitor(self, value: bool):
        self.optimize_find_progenitor = bool(value) and self._supports_progenitor()
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_search_quality(self, value: str):
        if value in self.optimize_search_options:
            self.optimize_search_quality = value
            self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_dph_weight(self, value: str | int | float):
        try:
            weight = int(float(value))
        except (TypeError, ValueError):
            return
        self.optimize_dph_weight = max(0, min(weight, 100))
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_dps_weight(self, value: str | int | float):
        try:
            weight = int(float(value))
        except (TypeError, ValueError):
            return
        self.optimize_dph_weight = 100 - max(0, min(weight, 100))
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_body_part(self, value: str):
        if value in self.optimize_body_part_options:
            self.optimize_body_part = value
            self._invalidate_optimizer_result()
            return self._recalculate()

    @rx.event
    def set_optimize_flat_dot_weight(self, value: str | int | float):
        try:
            weight = int(float(value))
        except (TypeError, ValueError):
            return
        self.optimize_flat_dot_weight = max(0, min(weight, 100))
        self._invalidate_optimizer_result()

    @rx.event
    def set_optimize_spatial(self, value: str):
        if value not in OPTIMIZE_SPATIAL_OPTIONS:
            return
        self.optimize_spatial = value
        self._invalidate_optimizer_result()

    @rx.var
    def optimize_direct_weight(self) -> int:
        return 100 - self.optimize_flat_dot_weight

    @rx.var
    def optimize_busy(self) -> bool:
        return self.optimize_running or bool(self.optimize_cancel_token)

    @rx.var
    def optimize_upgrade_exclusions_customized(self) -> bool:
        if self.optimize_default_exclusion_overrides:
            return True
        return any(not optimizer_excludes_upgrade_by_default(name) for name in self.optimize_excluded_upgrades)

    @rx.var
    def optimize_riven_exclusions_customized(self) -> bool:
        if self.optimize_default_riven_exclusion_overrides:
            return True
        for label in self.optimize_excluded_riven_stats:
            field_name = self._riven_field_from_label(label)
            if not field_name or not is_faction_damage_stat(field_name):
                return True
        return False

    @rx.var
    def any_slot_editor_open(self) -> bool:
        return any(self.slot_editor_open)

    @rx.event
    def close_slot_editors(self):
        if any(self.slot_editor_open):
            self.slot_editor_open = [False for _ in SLOT_CONFIGS]

    @rx.event
    def abort_optimization(self):
        if not self.optimize_busy:
            return
        cancel_event = _OPTIMIZE_CANCEL_EVENTS.get(self.optimize_cancel_token)
        if cancel_event is not None:
            cancel_event.set()
        self.optimize_revision += 1
        self.optimize_running = False
        self.optimize_phase = "Aborted"
        self.optimize_status = "Optimization aborted."
        self.optimize_cancel_token = ""

    @rx.event(background=True)
    async def optimize_build(self):
        import asyncio
        import queue as sync_queue
        import time

        async with self:
            if self.selected_weapon == NONE or self.selected_enemy == NONE or self.optimize_busy:
                return
            self.optimize_running = True
            self.slot_editor_open = [False for _ in SLOT_CONFIGS]
            self.optimize_status = ""
            self.optimize_phase = "Preparing weapon, enemy, and compatible upgrades"
            self.optimize_progress = 0.0
            self.optimize_progress_width = "0%"
            self.optimize_evaluations = 0
            self.optimize_best_dps = "0.00"
            self.optimize_elapsed = "00:00:00"
            revision = self.optimize_revision
            cancel_token = uuid.uuid4().hex
            cancel_event = threading.Event()
            _OPTIMIZE_CANCEL_EVENTS[cancel_token] = cancel_event
            self.optimize_cancel_token = cancel_token
            evolutions = self._selected_evolutions()
            riven_locked = any(
                selected == RIVEN and policy == SLOT_POLICY_KEEP
                for selected, policy in zip(self.slot_selected_upgrades, self.slot_policies)
            )
            selected_effort = self.optimize_search_quality if self.optimize_search_quality in OPTIMIZE_SEARCH_EVALUATION_BUDGETS else DEFAULT_OPTIMIZE_SEARCH
            self.optimize_search_quality = selected_effort
            request = OptimizeRequest(
                weapon_type=self.selected_weapon_type,
                weapon_category=self.selected_weapon_category,
                weapon_name=self.selected_weapon,
                attack_mode=self.selected_attack_mode,
                evolutions=evolutions,
                combo_count=self._combo_runtime_value(),
                evolution_runtime=self._evolution_runtime_context(),
                progenitor_element=self.progenitor_element if self._supports_progenitor() else NO_EFFECT,
                progenitor_value=self.progenitor_value,
                external_fields={field.name: field.value for field in self.external_fields},
                enemy_name=self.selected_enemy,
                enemy_level=self.enemy_level,
                enemy_steel_path=self.enemy_steel_path,
                enemy_empowered=self.enemy_empowered,
                slots=[
                    SlotSpec(
                        index=index,
                        kind=config["kind"],
                        exilus=bool(config["exilus"]),
                        stance=bool(config.get("stance")),
                        selected=self.slot_selected_upgrades[index] if self.slot_policies[index] == SLOT_POLICY_KEEP else NONE,
                        policy=SLOT_POLICY_KEEP if self.slot_policies[index] == SLOT_POLICY_KEEP else SLOT_POLICY_DISCARD,
                        rank=self.slot_ranks[index],
                        stacks=self.slot_stacks[index],
                        condition=self.slot_conditions_enabled[index],
                        riven_roll=self.slot_riven_rolls[index],
                        riven_fields={field.name: float(field.value) for field in self.slot_fields[index] if field.name},
                    )
                    for index, config in enumerate(SLOT_CONFIGS)
                ],
                find_optimal_riven=bool(self.optimize_find_riven) and not riven_locked and self.riven_optimize_available,
                find_optimal_evolutions=bool(self.optimize_find_evolutions) and bool(self.evolution_options),
                find_optimal_progenitor=bool(self.optimize_find_progenitor) and self._supports_progenitor(),
                search_quality=selected_effort,
                maximize_target=OPTIMIZE_MAXIMIZE_TARGETS.get(self.optimize_maximize_target, OPTIMIZE_MAXIMIZE_TARGETS[DEFAULT_OPTIMIZE_MAXIMIZE]),
                body_part=self.optimize_body_part or None,
                flat_dot_weight=self.optimize_flat_dot_weight / 100.0,
                dph_weight=self.optimize_dph_weight / 100.0,
                spatial=self.optimize_spatial,
                cancel_event=cancel_event,
                stance_combo=self.selected_stance_combo if self.stance_combo_available else "neutral",
                ability_strength=self._ability_strength_multiplier(),
                excluded_upgrades=_optimizer_upgrade_blacklist(self.optimize_excluded_upgrades, self.optimize_default_exclusion_overrides),
                excluded_riven_stats={
                    name
                    for label in self.optimize_excluded_riven_stats
                    if (name := self._riven_field_from_label(label)) is not None
                },
                riven_disposition=self._riven_disposition(),
                riven_base_stats=self._riven_base_stats(),
                riven_non_negative=set(RIVEN_NON_NEGATIVE_STATS),
            )
            evaluation_budget = OPTIMIZE_SEARCH_EVALUATION_BUDGETS[request.search_quality]
            self.optimize_evaluation_budget = evaluation_budget

        q: sync_queue.Queue = sync_queue.Queue()
        started_at = time.monotonic()
        best_value = 0.0

        def on_progress(progress):
            q.put(("progress", progress))

        def worker():
            try:
                result = run_optimize_build(request, progress=on_progress)
                q.put(("done", result))
            except Exception as exc:
                q.put(("error", exc))

        loop = asyncio.get_running_loop()
        fut = loop.run_in_executor(None, worker)

        def owns_optimize_run() -> bool:
            return self.optimize_cancel_token == cancel_token

        while True:
            await asyncio.sleep(0.5)
            latest_progress = None
            terminal = None
            while True:
                try:
                    msg = q.get_nowait()
                except sync_queue.Empty:
                    break
                if msg[0] == "progress":
                    latest_progress = msg
                else:
                    terminal = msg
            if latest_progress is not None:
                _, progress = latest_progress
                best_value = max(best_value, float(progress.best_score))
            async with self:
                # Only the active run may mutate optimizer UI. An aborted/superseded
                # worker can still finish later; clearing running there unlocked the
                # controls while a newer search kept updating progress.
                if owns_optimize_run() and self.optimize_revision == revision:
                    if latest_progress is not None:
                        self.optimize_phase = _describe_optimize_phase(progress.stage)
                        self.optimize_progress = _optimizer_progress_from_snapshot(progress)
                        self.optimize_progress_width = f"{self.optimize_progress:.1f}%"
                        self.optimize_evaluations = int(progress.evaluations)
                        self.optimize_evaluation_budget = int(progress.evaluation_budget)
                        self.optimize_best_dps = f"{best_value:,.2f}"
                    if self.optimize_running:
                        self.optimize_elapsed = _format_elapsed(time.monotonic() - started_at)
            if terminal is None:
                continue
            if terminal[0] == "done":
                result = terminal[1]
                apply_result = False
                async with self:
                    if owns_optimize_run() and self.optimize_revision == revision:
                        apply_result = True
                        self._apply_optimize_result(result)
                        self.optimize_status = result.message
                        best_value = max(best_value, float(result.total_dps))
                        self.optimize_best_dps = f"{best_value:,.2f}"
                        self.optimize_phase = "Applying build…"
                        self.optimize_progress = 100.0
                        self.optimize_progress_width = f"{self.optimize_progress:.1f}%"
                        self.optimize_evaluations = result.evaluations
                await asyncio.sleep(0)
                refresh = None
                try:
                    if apply_result:
                        async with self:
                            if owns_optimize_run() and self.optimize_revision == revision:
                                try:
                                    self._ensure_selected_upgrades_in_options()
                                    self._refresh_all_riven_field_limits()
                                    self._refresh_slot_field_options()
                                    refresh = self._recalculate()
                                    self.optimize_phase = "Complete"
                                    self.optimize_elapsed = _format_elapsed(result.elapsed_seconds)
                                except Exception as exc:
                                    self.optimize_phase = "Complete"
                                    self.optimize_status = f"Build applied with errors: {type(exc).__name__}: {exc}"
                                    self.optimize_elapsed = _format_elapsed(result.elapsed_seconds)
                finally:
                    async with self:
                        _OPTIMIZE_CANCEL_EVENTS.pop(cancel_token, None)
                        if owns_optimize_run():
                            self.optimize_running = False
                            self.optimize_cancel_token = ""
                await fut
                return refresh
            if terminal[0] == "error":
                exc = terminal[1]
                async with self:
                    _OPTIMIZE_CANCEL_EVENTS.pop(cancel_token, None)
                    if owns_optimize_run():
                        self.optimize_cancel_token = ""
                        self.optimize_running = False
                        if self.optimize_revision == revision:
                            if isinstance(exc, InterruptedError):
                                self.optimize_status = "Optimization aborted."
                                self.optimize_phase = "Aborted"
                            else:
                                self.optimize_status = f"{type(exc).__name__}: {exc}"
                                self.optimize_phase = "Failed"
                await fut
                return
            if fut.done() and terminal is None and latest_progress is None:
                exc = fut.exception()
                async with self:
                    _OPTIMIZE_CANCEL_EVENTS.pop(cancel_token, None)
                    if owns_optimize_run():
                        self.optimize_cancel_token = ""
                        self.optimize_running = False
                        if exc and self.optimize_revision == revision:
                            self.optimize_status = f"{type(exc).__name__}: {exc}"
                            self.optimize_phase = "Failed"
                return

    @rx.event
    def set_slot_condition(self, index: int, value: bool):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        enabled = list(self.slot_conditions_enabled)
        enabled[index] = bool(value)
        self.slot_conditions_enabled = enabled
        self._invalidate_optimizer_result()
        return self._recalculate()

    @rx.event
    def set_slot_rank(self, index: int, value: str):
        if not 0 <= index < len(SLOT_CONFIGS):
            return
        ranks = list(self.slot_ranks)
        ranks[index] = max(0, min(parse_int(value, ranks[index]), self.slot_max_ranks[index]))
        self.slot_ranks = ranks
        self._invalidate_optimizer_result()
        return self._recalculate()

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
        return self._recalculate()

    @rx.event
    def set_slot_pending_field(self, index: int, value: str):
        pending = list(self.slot_pending_fields)
        if 0 <= index < len(pending):
            pending[index] = value
            self.slot_pending_fields = pending

    @rx.event
    def set_riven_stat(self, index: int, position: int, label: str):
        if not 0 <= index < len(SLOT_CONFIGS) or self.slot_selected_upgrades[index] != RIVEN:
            return
        positive_count, negative_count, _bonus, _malus = self._riven_roll_config(index)
        if not 0 <= position < positive_count + negative_count:
            return
        all_fields = copy.deepcopy(self.slot_fields)
        while len(all_fields[index]) < positive_count + negative_count:
            all_fields[index].append(_empty_riven_editor_field())
        if label == RIVEN_EMPTY_STAT:
            all_fields[index][position] = _empty_riven_editor_field()
        else:
            field_name = self._riven_field_from_label(label)
            if not field_name or any(field.name == field_name for other_position, field in enumerate(all_fields[index]) if other_position != position):
                return
            limits = self._riven_field_limits(index, field_name, position >= positive_count)
            if limits is None:
                return
            min_value, max_value = limits
            current = all_fields[index][position]
            value = clamp_number(float(current.value), min_value, max_value) if current.name == field_name else (min_value + max_value) / 2
            all_fields[index][position] = EditorField(field_name, field_label(field_name), value, min_value, max_value, False)
        self.slot_fields = all_fields
        self._invalidate_optimizer_result()
        self._refresh_slot_field_options()
        return self._recalculate()

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
        return self._recalculate()

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
            position = next((position for position, field in enumerate(all_fields[index]) if not field.name), None)
            if position is None or position >= positive_count + negative_count:
                return
            negative = position >= positive_count
            limits = self._riven_field_limits(index, field_name, negative)
            if limits is None:
                return
            min_value, max_value = limits
            all_fields[index][position] = EditorField(field_name, field_label(field_name), (min_value + max_value) / 2, min_value, max_value, False)
            self.slot_fields = all_fields
            self._invalidate_optimizer_result()
            self._refresh_slot_field_options()
            return self._recalculate()
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
        return self._recalculate()

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
        return self._recalculate()

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
        return self._recalculate()

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
        return self._recalculate()

    @rx.event
    def remove_external_field(self, field_name: str):
        self.external_fields = [
            field
            for field in copy.deepcopy(self.external_fields)
            if field.name != field_name
        ]
        self.clear_keep_buff_fields = [name for name in self.clear_keep_buff_fields if name != field_name]
        self._invalidate_optimizer_result()
        self._refresh_external_field_options()
        return self._recalculate()

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
        return self._recalculate()

    def _refresh_enemy_options(self):
        factions = list(enemy_faction_options())
        self.enemy_faction_options = factions
        if self.selected_enemy != NONE:
            synced = enemy_faction_for(self.selected_enemy)
            if synced in factions:
                self.selected_enemy_faction = synced
        if self.selected_enemy_faction not in factions:
            self.selected_enemy_faction = factions[0] if factions else ""
        self.enemy_options = [NONE, *enemies_for_faction(self.selected_enemy_faction)]
        if self.selected_enemy not in self.enemy_options:
            self.selected_enemy = NONE

    def _refresh_weapon_options(self):
        self.weapon_options = [
            NONE,
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
        self.ability_strength_available = weapon_uses_ability_strength(self.selected_weapon, custom_metadata=custom_metadata)

    def _refresh_evolution_runtime_controls(self):
        if self.selected_weapon == NONE:
            self.evolution_condition_toggles = []
            self.evolution_stack_fields = []
            return
        toggle_specs, stack_specs = weapon_evolution_runtime_controls(self.selected_weapon, self._selected_evolutions())
        current_toggles = {field.name: field.value for field in self.evolution_condition_toggles}
        current_stacks = {field.name: str(field.value) for field in self.evolution_stack_fields}
        self.evolution_condition_toggles = [RuntimeToggleField(spec["name"], spec["label"], current_toggles.get(spec["name"], True)) for spec in toggle_specs]
        stack_fields: list[RuntimeStackField] = []
        for spec in stack_specs:
            options = [str(value) for value in range(int(spec["maximum"]) + 1)]
            default = str(spec["maximum"])
            selected = current_stacks.get(spec["name"], default)
            stack_fields.append(RuntimeStackField(spec["name"], spec["label"], selected if selected in options else default, options))
        self.evolution_stack_fields = stack_fields

    def _refresh_weapon_features(self):
        if self.selected_weapon == NONE:
            self.attack_mode_options = []
            self.selected_attack_mode = ""
            self.evolution_labels = []
            self.evolution_options = []
            self.evolution_selections = []
            self._refresh_evolution_runtime_controls()
            self.ability_strength_available = False
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
        self._refresh_evolution_runtime_controls()

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
        if reset_policy:
            policies = list(self.slot_policies)
            policies[index] = SLOT_POLICY_DISCARD
            self.slot_policies = policies

    def _apply_optimize_result(self, result):
        self.slot_selected_upgrades = list(result.slot_names)
        self.slot_ranks = list(result.slot_ranks)
        self.slot_stacks = list(result.slot_stacks)
        self.slot_conditions_enabled = list(result.slot_conditions)
        self.slot_policies = list(result.slot_policies)
        self.slot_riven_rolls = list(result.riven_rolls)
        if result.progenitor_optimized:
            element = str(result.progenitor_element or NO_EFFECT).strip().lower()
            if element in PROGENITOR_ELEMENT_OPTIONS:
                self.progenitor_element = element
                self.progenitor_value = float(result.progenitor_value) if result.progenitor_value > 0 else 0.6
            else:
                self.progenitor_element = NO_EFFECT
        max_ranks, max_stacks = list(self.slot_max_ranks), list(self.slot_max_stacks)
        all_fields = copy.deepcopy(self.slot_fields)
        for index, config in enumerate(SLOT_CONFIGS):
            name = result.slot_names[index]
            if name in {NONE, RIVEN}:
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
        self._refresh_evolution_runtime_controls()
        previous_combo = self.selected_stance_combo
        self._refresh_stance_combo_options()
        if previous_combo in self.stance_combo_options:
            self.selected_stance_combo = previous_combo

    def _ensure_selected_upgrades_in_options(self):
        """Keep current selections visible in dropdowns without a full option rebuild."""
        for index, config in enumerate(SLOT_CONFIGS):
            name = self.slot_selected_upgrades[index]
            if name == NONE:
                continue
            if config["kind"] == "arcane":
                if name not in self.arcane_options:
                    self.arcane_options = [*self.arcane_options, name]
            elif config.get("stance"):
                if name not in self.stance_options:
                    self.stance_options = [*self.stance_options, name]
            elif config["exilus"]:
                if name not in self.exilus_options:
                    self.exilus_options = [*self.exilus_options, name]
            elif name not in self.mod_options:
                self.mod_options = [*self.mod_options, name]
        self._refresh_slot_upgrade_options()
        self._refresh_slot_condition_metadata()

    def _refresh_upgrade_options(self):
        weapon_name = None if self.selected_weapon == NONE else self.selected_weapon
        custom_metadata = None
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
        if not self.riven_available or self.ability_strength_available:
            self.optimize_find_riven = False
        self.mod_options = [NONE, *([RIVEN] if self.riven_available else []), *upgrade_names(True, False, False)]
        exclusive_stances = weapon_exclusive_stance_names(weapon_name) if self.selected_weapon_type == "Melee" and weapon_name else ()
        allows_stance = self.selected_weapon_type == "Melee" and has_weapon and weapon_allows_stance(weapon_name, custom_metadata=custom_metadata)
        self.exclusive_stance_weapon = bool(exclusive_stances)
        self.stance_slot_available = allows_stance
        if not allows_stance:
            self.stance_options = [NONE]
        elif exclusive_stances:
            self.stance_options = list(exclusive_stances)
        else:
            self.stance_options = [NONE, *upgrade_names(True, False, False, stance_only=True)]
        self.exilus_options = [NONE, *upgrade_names(True, False, True)]
        self.arcane_options = [NONE, *upgrade_names(False, True, False)]

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
                if name not in {NONE, RIVEN}
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
        weapon_name = None if self.selected_weapon == NONE else self.selected_weapon
        custom_metadata = None
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
                if other_index != index and upgrade != NONE
            }
            current = selected[index]
            blocked = upgrades_blocked_by_selected(selected_elsewhere)
            options.append([upgrade for upgrade in base_options if upgrade == NONE or upgrade == current or upgrade not in blocked])
        self.slot_upgrade_options = options

    def _refresh_slot_condition_metadata(self):
        has_conditionals: list[bool] = []
        labels: list[str] = []
        enabled = list(self.slot_conditions_enabled)

        for index, config in enumerate(SLOT_CONFIGS):
            selected = self.slot_selected_upgrades[index]
            if selected in {RIVEN, NONE}:
                has_conditionals.append(False)
                labels.append("")
                enabled[index] = True
                continue

            has_conditional, label = database_conditional_info(
                selected,
                is_arcane_slot=config["kind"] == "arcane",
            )
            has_conditionals.append(has_conditional)
            labels.append(label if has_conditional else "")
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
        return raw_weapon_metadata(self.selected_weapon_type, self.selected_weapon)

    def _riven_base_stats(self) -> dict[str, float]:
        if self.selected_weapon_type == "Melee":
            category = "melee"
        elif self.selected_weapon_category == "Shotgun":
            category = "shotgun"
        elif self.selected_weapon_type == "Secondary" or self.selected_weapon_category == "Pistol":
            category = "pistol"
        else:
            category = "rifle"
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
        current_fields = fields[index][:maximum_fields]
        while len(current_fields) < maximum_fields:
            current_fields.append(_empty_riven_editor_field())
        for position, field in enumerate(current_fields):
            if not field.name:
                refreshed.append(_empty_riven_editor_field())
                continue
            limits = self._riven_field_limits(
                index,
                field.name,
                position >= positive_count,
            )
            if limits is None:
                refreshed.append(_empty_riven_editor_field())
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
        riven_options_all: list[list[list[str]]] = [[] for _ in SLOT_CONFIGS]
        riven_labels_all: list[list[str]] = [[] for _ in SLOT_CONFIGS]
        all_fields = copy.deepcopy(self.slot_fields)
        pending = list(self.slot_pending_fields)
        for index, config in enumerate(SLOT_CONFIGS):
            if self.slot_selected_upgrades[index] == RIVEN:
                positive_count, negative_count, _bonus, _malus = self._riven_roll_config(index)
                maximum_fields = positive_count + negative_count
                base_stats = self._riven_base_stats()
                fields = all_fields[index][:maximum_fields]
                while len(fields) < maximum_fields:
                    fields.append(_empty_riven_editor_field())
                seen: set[str] = set()
                for position, field in enumerate(fields):
                    if not field.name or field.name not in base_stats or field.name in seen or (position >= positive_count and field.name in RIVEN_NON_NEGATIVE_STATS):
                        fields[position] = _empty_riven_editor_field()
                    else:
                        seen.add(field.name)
                row_options: list[list[str]] = []
                row_labels: list[str] = []
                for position, field in enumerate(fields):
                    selected_elsewhere = {other.name for other_position, other in enumerate(fields) if other_position != position and other.name}
                    names = [name for name in base_stats if name not in selected_elsewhere and (position < positive_count or name not in RIVEN_NON_NEGATIVE_STATS)]
                    row_options.append([RIVEN_EMPTY_STAT, *(field_label(name) for name in names)])
                    row_labels.append(f"Positive {position + 1}" if position < positive_count else f"Negative {position - positive_count + 1}")
                all_fields[index] = fields
                riven_options_all[index] = row_options
                riven_labels_all[index] = row_labels
                first_empty = next((position for position, field in enumerate(fields) if not field.name), None)
                labels = [label for label in row_options[first_empty] if label != RIVEN_EMPTY_STAT] if first_empty is not None else []
                available_all.append(labels)
                if pending[index] not in labels:
                    pending[index] = labels[0] if labels else ""
                continue
            selected_names = {field.name for field in all_fields[index] if field.name}
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
        self.slot_fields = all_fields
        self.slot_available_fields = available_all
        self.slot_riven_field_options = riven_options_all
        self.slot_riven_row_labels = riven_labels_all
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
        metadata = raw_weapon_metadata(self.selected_weapon_type, self.selected_weapon)
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
            level=self.enemy_level,
            steel_path=self.enemy_steel_path,
            empowered=self.enemy_empowered,
        )

    def _refresh_optimize_maximize_options(self):
        self.optimize_maximize_options = [DEFAULT_OPTIMIZE_MAXIMIZE]
        self.optimize_maximize_target = DEFAULT_OPTIMIZE_MAXIMIZE

    def _refresh_enemy_preview(self, enemy) -> None:
        if self.no_enemy:
            self.enemy_identity_rows = []
            self.enemy_body_part_rows = []
            self.enemy_modifier_rows = []
            self.enemy_result_metrics = []
            self.enemy_has_weak_point = False
            self.enemy_has_resistant = False
            self.optimize_body_part_options = []
            self.optimize_body_part = ""
            self._refresh_optimize_maximize_options()
            self.enemy_error = ""
            return
        data = enemy
        effective = enemy.effective
        part_types = {str(part.type).casefold() for part in data.body_parts.values()}
        self.enemy_has_weak_point = any("weak_point" in part_type for part_type in part_types)
        self.enemy_has_resistant = any("resistant" in part_type for part_type in part_types)
        self.optimize_body_part_options = list(data.body_parts)
        if self.optimize_body_part not in self.optimize_body_part_options:
            self.optimize_body_part = self.optimize_body_part_options[0] if self.optimize_body_part_options else ""
        self._refresh_optimize_maximize_options()
        self.enemy_identity_rows = [
            DisplayRow("Name", str(data.name)),
            DisplayRow("Faction", str(data.faction)),
            DisplayRow("Base Level", f"{float(data.base_level):g}"),
            DisplayRow("Current Level", str(self.enemy_level)),
        ]
        self.enemy_body_part_rows = [
            DisplayRow(f"{str(name).replace('_', ' ').title()} ({str(part.type).replace('_', ' ').title()})", f"{float(part.multiplier):g}x")
            for name, part in data.body_parts.items()
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
            "weak_point_damage": self.base_weak_point_damage,
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
        return build_upgrade(name, {field.name: field.value for field in fields if field.name})

    def _riven_stat_rows(self, index: int) -> list[DisplayRow]:
        rows: list[DisplayRow] = []
        for field in self.slot_fields[index]:
            if not field.name:
                continue
            value = float(field.value)
            stat = field_label(field.name)
            if field.name in RIVEN_FLAT_STAT_UNITS:
                unit = RIVEN_FLAT_STAT_UNITS[field.name]
                amount = f"{abs(value):.2f}"
                signed = f"+{amount}" if value >= 0 else f"-{amount}"
                text = f"{signed}{unit} {stat}" if unit else f"{signed} {stat}"
            else:
                percent = f"{abs(value * 100):.2f}"
                signed = f"+{percent}" if value >= 0 else f"-{percent}"
                text = f"{signed}% {stat}"
            rows.append(DisplayRow(text, ""))
        return rows

    def _pad_slot_preview_rows(self, rows: list[DisplayRow], *, minimum: int = 4) -> list[DisplayRow]:
        padded = list(rows) if rows else [DisplayRow("No description.", "")]
        while len(padded) < minimum:
            padded.append(DisplayRow("\u00a0", "\u00a0"))
        return padded

    def _slot_preview_rows(self, index: int, upgrade: Upgrade) -> list[DisplayRow]:
        if self.slot_selected_upgrades[index] == RIVEN:
            return self._pad_slot_preview_rows(self._riven_stat_rows(index))
        selected = self.slot_selected_upgrades[index]
        if selected == NONE:
            return self._pad_slot_preview_rows([])
        fallback = str(raw_upgrade_metadata(selected, kind=SLOT_CONFIGS[index]["kind"]).get("description") or "")
        rows = upgrade_description_rows(upgrade, fallback_description=fallback)
        if SLOT_CONFIGS[index].get("stance") or getattr(upgrade, "slot", None) == "stance_mod":
            combos = getattr(upgrade, "combos", None)
            combo_mapping = dict(combos) if combos else self._slot_stance_combos(index)
            selected_combo = self.selected_stance_combo
            if selected_combo in combo_mapping:
                combo_mapping = {selected_combo: combo_mapping[selected_combo]}
            elif combo_mapping:
                fallback_combo = next(iter(combo_mapping))
                combo_mapping = {fallback_combo: combo_mapping[fallback_combo]}
            combo_rows = stance_combo_rows(combo_mapping)
            if combo_rows:
                rows = [*rows, *combo_rows] if rows else combo_rows
        return self._pad_slot_preview_rows(rows)

    def _slot_stance_combos(self, index: int) -> dict:
        selected = self.slot_selected_upgrades[index]
        if selected in {NONE, RIVEN}:
            return {}
        return raw_upgrade_metadata(selected).get("combos") or {}

    def _slot_upgrade(self, index: int) -> Upgrade:
        config = SLOT_CONFIGS[index]
        selected = self.slot_selected_upgrades[index]
        if selected == NONE:
            cls = Arcane if config["kind"] == "arcane" else Mod
            slot = "stance_mod" if config.get("stance") else "exilus_mod" if config.get("exilus") else "regular_arcane" if config["kind"] == "arcane" else "regular_mod"
            return cls(name=NONE, slot=slot)
        if selected == RIVEN:
            return self._custom_upgrade_from_fields(
                RIVEN,
                self.slot_fields[index],
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
        if loaded is not None:
            return loaded
        cls = Arcane if config["kind"] == "arcane" else Mod
        slot = "stance_mod" if config.get("stance") else "exilus_mod" if config.get("exilus") else "regular_arcane" if config["kind"] == "arcane" else "regular_mod"
        return cls(name=selected, slot=slot)

    def _clear_calculation_results(self):
        self.slot_contributions = ["—" for _ in SLOT_CONFIGS]
        self.main_result_metrics = []
        self.weak_point_result_metrics = []
        self.resistant_result_metrics = []
        self.ranged_result_metrics = []
        self.misc_result_metrics = []
        self.result_metrics = []
        self.result_summary = ""
        self.result_status_summary = ""
        self.result_contribution_summary = ""
        self.contribution_revision += 1
        self.contributions_pending = False
        self.result_ready = False

    def _build_resolved_weapon(self, target):
        slot_upgrades = [self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))]
        progenitor_bonus = self.progenitor_value if self.progenitor_value > 0 else 0.6
        progenitor = None if not self._supports_progenitor() or self.progenitor_element in {NO_EFFECT, NONE, ""} else Progenitor(element=self.progenitor_element, bonus=progenitor_bonus)
        external = self._custom_upgrade_from_fields("External Buffs", self.external_fields)
        upgrades = [upgrade for selected, upgrade in zip(self.slot_selected_upgrades, slot_upgrades) if selected != NONE]
        if is_non_empty_upgrade(external):
            upgrades.append(external)
        weapon = configured_weapon(
            self.selected_weapon_type,
            self.selected_weapon,
            upgrades=upgrades,
            selected_mode=self.selected_attack_mode or None,
            evolutions=self._selected_evolutions(),
            combo=self._combo_runtime_value() if self.melee_weapon else None,
            runtime_conditions=self._evolution_runtime_context(),
            stance_combo=self.selected_stance_combo if self.stance_combo_available else None,
            ability_strength=self._ability_strength_multiplier(),
            target=target,
            progenitor=progenitor,
        )
        return weapon, upgrades, slot_upgrades

    def _target_for_calculation(self):
        target = self._target_enemy()
        self._refresh_enemy_preview(target)
        if target is not None and self.optimize_body_part:
            if self.optimize_body_part not in target.body_parts:
                raise ValueError(f"Unknown body part: {self.optimize_body_part}")
            target = target.copy()
            target.body_parts = {self.optimize_body_part: target.body_parts[self.optimize_body_part]}
        return target

    def _apply_contribution_summary_sync(self):
        """Compute contribution UI immediately (tests / non-UI callers)."""
        if not self.result_ready or self.selected_weapon == NONE or self.no_enemy:
            self.result_contribution_summary = ""
            self.contributions_pending = False
            return
        target = self._target_for_calculation()
        resolved, upgrades, _slot_upgrades = self._build_resolved_weapon(target)
        contribution_lookup, text, _rows = library_contribution_bundle(resolved)
        contribution_map = contribution_lookup_map(contribution_lookup)
        contributions = []
        for index, config in enumerate(SLOT_CONFIGS):
            selected = self.slot_selected_upgrades[index]
            contribution_name = config["label"] if selected == NONE else selected
            contributions.append(format_contribution(contribution_value_for_name(contribution_map, contribution_name)))
        self.slot_contributions = contributions
        self.result_contribution_summary = text
        self.contributions_pending = False

    @rx.event(background=True)
    async def refresh_contribution_summary(self):
        import asyncio

        async with self:
            revision = self.contribution_revision
            if not self.result_ready or self.selected_weapon == NONE or self.no_enemy:
                self.contributions_pending = False
                return
            selected_upgrades = list(self.slot_selected_upgrades)
            try:
                target = self._target_for_calculation()
                resolved, _upgrades, _slot_upgrades = self._build_resolved_weapon(target)
            except Exception as exc:
                if self.contribution_revision == revision:
                    self.result_contribution_summary = f"{type(exc).__name__}: {exc}"
                    self.contributions_pending = False
                return

        def compute():
            return library_contribution_bundle(resolved)

        loop = asyncio.get_running_loop()
        try:
            contribution_lookup, text, _rows = await loop.run_in_executor(None, compute)
        except Exception as exc:
            async with self:
                if self.contribution_revision == revision:
                    self.result_contribution_summary = f"{type(exc).__name__}: {exc}"
                    self.contributions_pending = False
            return

        contribution_map = contribution_lookup_map(contribution_lookup)
        contributions = []
        for index, config in enumerate(SLOT_CONFIGS):
            selected = selected_upgrades[index]
            contribution_name = config["label"] if selected == NONE else selected
            contributions.append(format_contribution(contribution_value_for_name(contribution_map, contribution_name)))
        async with self:
            if self.contribution_revision == revision:
                self.slot_contributions = contributions
                self.result_contribution_summary = text
                self.contributions_pending = False

    def _recalculate(self):
        try:
            configuration_errors: list[str] = []
            try:
                target = self._target_for_calculation()
            except Exception as exc:
                self.enemy_identity_rows = []
                self.enemy_body_part_rows = []
                self.enemy_modifier_rows = []
                self.enemy_result_metrics = []
                self.enemy_has_weak_point = False
                self.enemy_has_resistant = False
                self._refresh_optimize_maximize_options()
                self.enemy_error = f"{type(exc).__name__}: {exc}"
                configuration_errors.append(self.enemy_error)
                target = None
            if configuration_errors:
                self._clear_calculation_results()
                self.result_errors = configuration_errors
                self.result_error = "\n".join(configuration_errors)
                return None
            if self.selected_weapon == NONE:
                slot_upgrades = [self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))]
                self.slot_stat_rows = [self._slot_preview_rows(index, upgrade) for index, upgrade in enumerate(slot_upgrades)]
                self._clear_calculation_results()
                self.result_error = "Select a weapon to calculate."
                self.result_errors = [self.result_error]
                return None

            if self.no_enemy:
                slot_upgrades = [self._slot_upgrade(index) for index in range(len(SLOT_CONFIGS))]
                self.slot_stat_rows = [self._slot_preview_rows(index, upgrade) for index, upgrade in enumerate(slot_upgrades)]
                self._clear_calculation_results()
                self.result_error = "Select an enemy to calculate."
                self.result_errors = [self.result_error]
                return None

            weapon, _upgrades, slot_upgrades = self._build_resolved_weapon(target)
            self.slot_stat_rows = [self._slot_preview_rows(index, upgrade) for index, upgrade in enumerate(slot_upgrades)]
            self.main_result_metrics = main_metrics(weapon)
            self.weak_point_result_metrics = []
            self.resistant_result_metrics = []
            self.misc_result_metrics = [] if self.selected_weapon_type == "Melee" else ranged_misc_metrics(weapon)
            self.result_metrics = self.main_result_metrics + self.weak_point_result_metrics + self.resistant_result_metrics + self.misc_result_metrics
            self.ranged_result_metrics = self.result_metrics
            self.result_summary = result_summary(weapon)
            self.result_status_summary = result_status_summary(weapon)
            self.contribution_revision += 1
            self.contributions_pending = True
            self.result_contribution_summary = "Computing upgrade contributions…"
            self.result_error = ""
            self.result_errors = []
            self.result_ready = True
            return CalculatorState.refresh_contribution_summary
        except Exception as exc:
            self._clear_calculation_results()
            self.result_error = f"{type(exc).__name__}: {exc}"
            self.result_errors = [self.result_error]
            return None
