from __future__ import annotations

from typing import Callable

import reflex as rx

from .constants import (
    ARCANE_SLOT_INDEX,
    EXILUS_SLOT_INDEX,
    INITIAL_COMBO_OPTION,
    MELEE_COMBO_OPTIONS,
    MOD_SLOT_INDICES,
    NO_EFFECT,
    OPTIMIZER_SLOT_ORDER,
    PROGENITOR_ELEMENT_OPTIONS,
    RIVEN_ROLL_OPTIONS,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP,
    SLOT_POLICY_KEEP_IN_SLOT,
    STANCE_SLOT_INDEX,
    WEAPON_TYPE_OPTIONS,
)
from .models import ClearBuffRow, ContributionRow, DamageResultRow, DisplayRow, EditorField, MetricRow, RuntimeStackField, RuntimeToggleField
from .state import CUSTOM, NONE, RIVEN, CalculatorState


def panel(*children, class_name: str = "panel", **props) -> rx.Component:
    return rx.box(*children, class_name=class_name, **props)


def section_title(title: str, subtitle: str | None = None) -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="6"),
        rx.cond(
            subtitle is not None,
            rx.text(subtitle or "", class_name="section-subtitle"),
        ),
        align="start",
        gap="1",
        width="100%",
    )


def labeled_control(label: str, control: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.text(label, class_name="field-label"),
        control,
        align="stretch",
        gap="1",
        width="100%",
        min_width="0",
        class_name="labeled-control",
    )


def select_input(
    options,
    value,
    on_change,
    *,
    disabled=False,
) -> rx.Component:
    """Radix select — matches app chrome."""
    return rx.select.root(
        rx.select.trigger(
            width="100%",
            min_width="0",
            max_width="100%",
            height="32px",
            min_height="32px",
            class_name="full-width-select-trigger",
            custom_attrs={"data-full-width-select": "true"},
        ),
        rx.select.content(
            rx.select.group(
                rx.foreach(options, lambda option: rx.select.item(option, value=option)),
            ),
            position="popper",
        ),
        value=value,
        on_change=on_change,
        disabled=disabled,
        width="100%",
    )


def lazy_select_input(
    options,
    value,
    on_change,
    *,
    open_var,
    set_open,
    disabled=False,
) -> rx.Component:
    """Radix select that only mounts options while open — keeps large lists fast without native styling."""
    return rx.select.root(
        rx.select.trigger(
            rx.text(value),
            width="100%",
            min_width="0",
            max_width="100%",
            height="32px",
            min_height="32px",
            class_name="full-width-select-trigger",
            custom_attrs={"data-full-width-select": "true"},
        ),
        rx.cond(
            open_var,
            rx.select.content(
                rx.select.group(
                    rx.foreach(options, lambda option: rx.select.item(option, value=option)),
                ),
                position="popper",
            ),
        ),
        value=value,
        open=open_var,
        on_open_change=set_open,
        on_change=on_change,
        disabled=disabled,
        width="100%",
    )


def select_control(
    label: str,
    options,
    value,
    on_change,
    *,
    disabled=False,
    native: bool = False,
) -> rx.Component:
    control = native_select_input if native else select_input
    return labeled_control(
        label,
        control(options, value, on_change, disabled=disabled),
    )


def native_select_input(
    options,
    value,
    on_change,
    *,
    disabled=False,
) -> rx.Component:
    """Native select for very large lists (enemies) — browsers handle thousands of options cheaply."""
    return rx.el.select(
        rx.foreach(options, lambda option: rx.el.option(option, value=option)),
        value=value,
        on_change=on_change,
        disabled=disabled,
        class_name="native-select full-width-select-trigger",
        custom_attrs={"data-full-width-select": "true"},
    )


def lazy_select_control(
    label: str,
    options,
    value,
    on_change,
    *,
    open_var,
    set_open,
    disabled=False,
) -> rx.Component:
    return labeled_control(
        label,
        lazy_select_input(options, value, on_change, open_var=open_var, set_open=set_open, disabled=disabled),
    )


def number_control(
    label: str,
    value,
    on_change,
    *,
    minimum=None,
    maximum=None,
    step: str = "0.001",
) -> rx.Component:
    return labeled_control(
        label,
        rx.input(
            type="number",
            value=value,
            on_change=on_change,
            min=minimum,
            max=maximum,
            step=step,
            width="100%",
            debounce_timeout=400,
        ),
    )


def toggle_control(label: str, checked, on_change) -> rx.Component:
    return rx.hstack(
        rx.text(label, class_name="toggle-label"),
        rx.spacer(),
        rx.switch(checked=checked, on_change=on_change),
        width="100%",
        align="center",
        class_name="toggle-control",
    )


def header() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.heading("Warframe Damage Calculator", size="7"),
            rx.text(
                "Configure a weapon, enemy target, build, and external buffs with deterministic DPH/DPS calculations.",
                class_name="header-subtitle",
            ),
            align="start",
            gap="1",
        ),
        rx.spacer(),
        rx.badge("Reflex", variant="soft", size="2"),
        width="100%",
        align="center",
        class_name="app-header",
    )


def mobile_quick_nav() -> rx.Component:
    """Compact section navigation shown only on phone-sized screens."""
    return rx.hstack(
        rx.link("Weapon", href="#weapon", class_name="mobile-nav-link"),
        rx.link("Enemy", href="#enemy", class_name="mobile-nav-link"),
        rx.link("Upgrades", href="#upgrades", class_name="mobile-nav-link"),
        rx.link("Optimizer", href="#optimizer", class_name="mobile-nav-link"),
        rx.link("Results", href="#results", class_name="mobile-nav-link"),
        width="100%",
        class_name="mobile-quick-nav",
        aria_label="Calculator sections",
    )


def read_me() -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.hstack(
                rx.text("Read Me"),
                rx.spacer(),
                width="100%",
            ),
            content=rx.vstack(
                    rx.heading("Disclaimer", size="4"),
                    rx.text(
                        "This interface is a companion for the warframe_damage_calculator Python library. The library remains the source of truth for all damage calculations."
                    ),
                    rx.heading("Instructions", size="4"),
                    rx.text(
                        "Select a weapon and enemy target, configure custom entries when needed, fill the upgrade slots, add external buffs, then inspect the live results."
                    ),
                    rx.heading("Notes", size="4"),
                    rx.text(
                        "Percentage bonuses use decimal values: +75% is entered as 0.75. Multiplicative bonuses use the bonus over base: ×1.30 is entered as 0.30."
                    ),
                    rx.hstack(
                        rx.link(
                            "Web app source",
                            href="https://github.com/MX055/warframe-damage-calculator-app",
                            is_external=True,
                        ),
                        rx.link(
                            "Python library",
                            href="https://github.com/MX055/warframe-damage-calculator",
                            is_external=True,
                        ),
                        gap="4",
                        wrap="wrap",
                    ),
                    align="start",
                    gap="3",
                    width="100%",
                    padding_top="0.5rem",
            ),
            value="read-me",
        ),
        type="single",
        collapsible=True,
        width="100%",
        class_name="read-me",
    )


def damage_field_row(field: rx.Var[EditorField], group: str) -> rx.Component:
    return rx.grid(
        rx.text(field.label, class_name="compact-label"),
        rx.input(
            type="number",
            value=field.value,
            min=0,
            step="0.001",
            on_change=lambda value: CalculatorState.set_damage_value(
                group, field.name, value
            ),
            debounce_timeout=400,
            width="100%",
        ),
        rx.button(
            "×",
            on_click=CalculatorState.remove_damage_type(group, field.name),
            class_name="icon-button",
            variant="soft",
        ),
        columns="76px minmax(0, 1fr) 32px",
        column_gap="8px",
        align="center",
        width="100%",
    )


def damage_editor(
    title: str,
    group: str,
    fields,
    options,
    pending,
) -> rx.Component:
    return panel(
        rx.vstack(
            rx.text(title, class_name="card-title"),
            rx.grid(
                rx.select(
                    options,
                    value=pending,
                    on_change=lambda value: CalculatorState.set_damage_pending(
                        group, value
                    ),
                    disabled=options.length() == 0,
                    width="100%",
                    position="popper",
                ),
                rx.button(
                    "+",
                    on_click=CalculatorState.add_damage_type(group),
                    disabled=options.length() == 0,
                    class_name="icon-button",
                ),
                columns="minmax(0, 1fr) 32px",
                column_gap="8px",
                width="100%",
            ),
            rx.cond(
                fields.length() > 0,
                rx.vstack(
                    rx.foreach(fields, lambda field: damage_field_row(field, group)),
                    width="100%",
                    gap="2",
                ),
                rx.text("No damage types added.", class_name="empty-text"),
            ),
            align="start",
            gap="3",
            width="100%",
        ),
        class_name="subpanel",
    )


def progenitor_controls() -> rx.Component:
    return rx.grid(
        select_control(
            "Progenitor Element",
            [NO_EFFECT, *PROGENITOR_ELEMENT_OPTIONS],
            CalculatorState.progenitor_element,
            CalculatorState.set_progenitor_element,
        ),
        number_control(
            "Progenitor Value",
            CalculatorState.progenitor_value,
            lambda value: CalculatorState.set_base_number("progenitor_value", value),
            minimum=0,
            maximum=0.6,
        ),
        columns=rx.breakpoints(initial="1", sm="2"),
        gap="4",
        width="100%",
        class_name="form-grid form-grid-2 progenitor-grid",
    )


def supported_progenitor_controls() -> rx.Component:
    return rx.cond(CalculatorState.supports_progenitor, progenitor_controls())


def ability_strength_control() -> rx.Component:
    return number_control(
        "Ability Strength (%)",
        CalculatorState.ability_strength,
        lambda value: CalculatorState.set_base_number("ability_strength", value),
        minimum=0,
        maximum=1000,
        step="1",
    )


def supported_ability_strength_control() -> rx.Component:
    return rx.cond(CalculatorState.ability_strength_available, ability_strength_control())


def database_entry_input(
    label: str,
    value,
    on_change,
    *,
    placeholder="",
    help_text: str,
    min_height: str,
) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(label, class_name="field-label entry-label"),
            rx.spacer(),
            rx.text(help_text, class_name="entry-help"),
            width="100%",
            align="center",
        ),
        rx.text_area(
            value=value,
            placeholder=placeholder,
            on_change=on_change,
            debounce_timeout=400,
            width="100%",
            min_height=min_height,
            resize="vertical",
            spell_check=False,
            class_name="database-entry-input",
        ),
        width="100%",
        gap="2",
        align="stretch",
    )


def custom_damage_controls() -> rx.Component:
    ranged_tabs = rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Direct Hit", value="direct"),
            rx.tabs.trigger("Explosion", value="explosion"),
        ),
        rx.tabs.content(
            rx.grid(
                damage_editor(
                    "Base Damage",
                    "direct_damage",
                    CalculatorState.direct_damage_fields,
                    CalculatorState.direct_damage_options,
                    CalculatorState.direct_damage_pending,
                ),
                damage_editor(
                    "Forced Procs",
                    "forced_proc",
                    CalculatorState.forced_proc_fields,
                    CalculatorState.forced_proc_options,
                    CalculatorState.forced_proc_pending,
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                gap="0",
                width="100%",
                padding_top="1rem",
                class_name="damage-editor-grid",
            ),
            value="direct",
        ),
        rx.tabs.content(
            rx.grid(
                damage_editor(
                    "Explosion Damage",
                    "explosion_damage",
                    CalculatorState.explosion_damage_fields,
                    CalculatorState.explosion_damage_options,
                    CalculatorState.explosion_damage_pending,
                ),
                damage_editor(
                    "Explosion Forced Procs",
                    "explosion_forced_proc",
                    CalculatorState.explosion_forced_proc_fields,
                    CalculatorState.explosion_forced_proc_options,
                    CalculatorState.explosion_forced_proc_pending,
                ),
                columns=rx.breakpoints(initial="1", md="2"),
                gap="0",
                width="100%",
                padding_top="1rem",
                class_name="damage-editor-grid",
            ),
            value="explosion",
        ),
        default_value="direct",
        width="100%",
    )

    melee_panel = rx.grid(
        damage_editor(
            "Light Attack Damage",
            "direct_damage",
            CalculatorState.direct_damage_fields,
            CalculatorState.direct_damage_options,
            CalculatorState.direct_damage_pending,
        ),
        damage_editor(
            "Light Attack Forced Procs",
            "forced_proc",
            CalculatorState.forced_proc_fields,
            CalculatorState.forced_proc_options,
            CalculatorState.forced_proc_pending,
        ),
        columns=rx.breakpoints(initial="1", md="2"),
        gap="0",
        width="100%",
        class_name="damage-editor-grid",
    )

    return rx.cond(CalculatorState.ranged_weapon, ranged_tabs, melee_panel)


def custom_base_stats() -> rx.Component:
    return rx.vstack(
        database_entry_input(
            "Custom Weapon Entry",
            CalculatorState.custom_weapon_entry,
            CalculatorState.set_custom_weapon_entry,
            placeholder=CalculatorState.custom_weapon_placeholder,
            help_text="JSON",
            min_height="320px",
        ),
        supported_progenitor_controls(),
        width="100%",
        gap="4",
    )


def incarnon_toggle_control(field: rx.Var[RuntimeToggleField]) -> rx.Component:
    return labeled_control(
        field.label,
        rx.hstack(
            rx.text(rx.cond(field.value, "On", "Off"), class_name="enemy-toggle-state"),
            rx.spacer(),
            rx.switch(checked=field.value, on_change=lambda value: CalculatorState.set_evolution_condition(field.name, value)),
            width="100%",
            align="center",
            class_name="enemy-toggle-control",
        ),
    )


def incarnon_stack_control(field: rx.Var[RuntimeStackField]) -> rx.Component:
    return select_control(field.label, field.options, field.value, lambda value: CalculatorState.set_evolution_stacks(field.name, value))


def incarnon_runtime_controls() -> rx.Component:
    return rx.cond(
        (CalculatorState.evolution_condition_toggles.length() > 0) | (CalculatorState.evolution_stack_fields.length() > 0),
        rx.vstack(
            rx.text("Incarnon Conditions", class_name="optimizer-group-title"),
            rx.grid(
                rx.foreach(CalculatorState.evolution_condition_toggles, incarnon_toggle_control),
                rx.foreach(CalculatorState.evolution_stack_fields, incarnon_stack_control),
                columns=rx.breakpoints(initial="1", md="2"),
                gap="4",
                width="100%",
                class_name="form-grid form-grid-2 incarnon-conditions-grid",
            ),
            width="100%",
            gap="3",
            class_name="incarnon-runtime-panel",
        ),
    )


def weapon_section() -> rx.Component:
    return rx.vstack(
        section_title("Weapon", "Choose a database weapon or define a custom one."),
        panel(
            rx.vstack(
                rx.grid(
                    select_control(
                        "Weapon Category",
                        WEAPON_TYPE_OPTIONS,
                        CalculatorState.selected_weapon_category,
                        CalculatorState.set_weapon_type,
                    ),
                    lazy_select_control(
                        "Weapon",
                        CalculatorState.weapon_options,
                        CalculatorState.selected_weapon,
                        CalculatorState.set_weapon,
                        open_var=CalculatorState.weapon_select_open,
                        set_open=CalculatorState.set_weapon_select_open,
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    gap="4",
                    width="100%",
                    class_name="form-grid form-grid-2",
                ),
                rx.cond(
                    CalculatorState.attack_mode_options.length() > 1,
                    select_control(
                        "Attack Mode",
                        CalculatorState.attack_mode_options,
                        CalculatorState.selected_attack_mode,
                        CalculatorState.set_attack_mode,
                    ),
                ),
                rx.cond(
                    CalculatorState.melee_weapon & (~CalculatorState.no_weapon),
                    rx.vstack(
                        select_control("Combo Count", MELEE_COMBO_OPTIONS, CalculatorState.melee_combo_count, CalculatorState.set_melee_combo_count),
                        rx.cond(CalculatorState.melee_combo_count == INITIAL_COMBO_OPTION, rx.text("Uses the build's modded Initial Combo to determine the heavy-attack multiplier.", class_name="optimizer-help")),
                        width="100%",
                        gap="1",
                    ),
                ),
                rx.cond(
                    CalculatorState.stance_combo_available,
                    stance_combo_control(),
                ),
                rx.cond(
                    CalculatorState.evolution_options.length() > 0,
                    rx.grid(
                        rx.foreach(
                            CalculatorState.evolution_options,
                            lambda options, index: select_control(
                                CalculatorState.evolution_labels[index],
                                options,
                                CalculatorState.evolution_selections[index],
                                lambda value: CalculatorState.set_evolution(index, value),
                            ),
                        ),
                        columns=rx.breakpoints(initial="1", md="2"),
                        gap="4",
                        width="100%",
                        class_name="form-grid form-grid-2",
                    ),
                ),
                incarnon_runtime_controls(),
                rx.cond(
                    CalculatorState.custom_weapon,
                    custom_base_stats(),
                    supported_progenitor_controls(),
                ),
                supported_ability_strength_control(),
                width="100%",
                gap="5",
            )
        ),
        width="100%",
        gap="3",
        id="weapon",
        class_name="page-section",
    )


def enemy_toggle_control(label: str, checked, on_change) -> rx.Component:
    return labeled_control(
        label,
        rx.hstack(
            rx.text(rx.cond(checked, "On", "Off"), class_name="enemy-toggle-state"),
            rx.spacer(),
            rx.switch(checked=checked, on_change=on_change),
            width="100%",
            align="center",
            class_name="enemy-toggle-control",
        ),
    )


def enemy_section() -> rx.Component:
    return rx.vstack(
        section_title("Enemy", "Choose a faction and target, or define a custom enemy."),
        panel(
            rx.vstack(
                rx.grid(
                    select_control(
                        "Faction",
                        CalculatorState.enemy_faction_options,
                        CalculatorState.selected_enemy_faction,
                        CalculatorState.set_enemy_faction,
                    ),
                    lazy_select_control(
                        "Enemy",
                        CalculatorState.enemy_options,
                        CalculatorState.selected_enemy,
                        CalculatorState.set_enemy,
                        open_var=CalculatorState.enemy_select_open,
                        set_open=CalculatorState.set_enemy_select_open,
                    ),
                    columns=rx.breakpoints(initial="1", md="2"),
                    gap="4",
                    width="100%",
                    class_name="form-grid form-grid-2",
                ),
                rx.cond(
                    CalculatorState.custom_enemy,
                    database_entry_input(
                        "Custom Enemy Entry",
                        CalculatorState.custom_enemy_entry,
                        CalculatorState.set_custom_enemy_entry,
                        placeholder=CalculatorState.custom_enemy_placeholder,
                        help_text="JSON",
                        min_height="320px",
                    ),
                ),
                rx.cond(
                    (~CalculatorState.no_enemy) & (~CalculatorState.custom_enemy),
                    rx.grid(
                        number_control("Level", CalculatorState.enemy_level, CalculatorState.set_enemy_level, minimum=1, maximum=9999, step="1"),
                        enemy_toggle_control("Steel Path", CalculatorState.enemy_steel_path, lambda value: CalculatorState.set_enemy_toggle("enemy_steel_path", value)),
                        enemy_toggle_control("Empowered", CalculatorState.enemy_empowered, lambda value: CalculatorState.set_enemy_toggle("enemy_empowered", value)),
                        columns=rx.breakpoints(initial="1", md="3"),
                        gap="4",
                        width="100%",
                        class_name="form-grid enemy-runtime-grid",
                    ),
                ),
                rx.cond(
                    CalculatorState.show_enemy_inline_error,
                    rx.box(rx.text("The enemy could not be loaded."), rx.code(CalculatorState.enemy_error), class_name="error-box", width="100%"),
                ),
                width="100%",
                gap="3",
                align="start",
            )
        ),
        width="100%",
        gap="3",
        id="enemy",
        class_name="page-section",
    )


def display_stat_row(row: rx.Var[DisplayRow]) -> rx.Component:
    return rx.hstack(
        rx.text(row.label, class_name="preview-label"),
        rx.spacer(),
        rx.text(row.value, class_name="preview-value"),
        width="100%",
        align="center",
        class_name="preview-stat-row",
    )


def stat_preview(rows) -> rx.Component:
    return rx.cond(
        rows.length() > 0,
        rx.vstack(
            rx.foreach(rows, display_stat_row),
            width="100%",
            gap="1",
        ),
        rx.text("No stats.", class_name="empty-text"),
    )


def slot_stat_preview(rows) -> rx.Component:
    return rx.vstack(
        rx.cond(
            rows.length() > 0,
            rx.foreach(rows, display_stat_row),
            rx.text("No stats.", class_name="empty-text preview-stat-row"),
        ),
        width="100%",
        class_name="slot-stat-preview",
    )


def slot_editor_field(field: rx.Var[EditorField], index: int) -> rx.Component:
    return rx.grid(
        rx.text(field.label, class_name="compact-label"),
        rx.input(
            type="number",
            value=field.value,
            min=field.min_value,
            max=field.max_value,
            step=rx.cond(field.integer, "1", "0.001"),
            on_change=lambda value: CalculatorState.set_slot_field_value(
                index, field.name, value
            ),
            debounce_timeout=400,
            width="100%",
        ),
        rx.button(
            "×",
            on_click=CalculatorState.remove_slot_field(index, field.name),
            class_name="icon-button field-action-button",
            variant="soft",
        ),
        columns="84px minmax(0, 1fr) 32px",
        column_gap="8px",
        align="center",
        width="100%",
    )


def slot_options(index: int):
    return CalculatorState.slot_upgrade_options[index]


def upgrade_runtime_controls(index: int) -> rx.Component:
    return rx.vstack(
        rx.cond(
            CalculatorState.slot_max_ranks[index] > 0,
            rx.grid(
                number_control(
                    "Rank",
                    CalculatorState.slot_ranks[index],
                    lambda value: CalculatorState.set_slot_rank(index, value),
                    minimum=0,
                    maximum=CalculatorState.slot_max_ranks[index],
                    step="1",
                ),
                rx.cond(
                    CalculatorState.slot_max_stacks[index] > 0,
                    number_control(
                        "Stacks",
                        CalculatorState.slot_stacks[index],
                        lambda value: CalculatorState.set_slot_stacks(index, value),
                        minimum=0,
                        maximum=CalculatorState.slot_max_stacks[index],
                        step="1",
                    ),
                ),
                columns="repeat(2, minmax(0, 1fr))",
                column_gap="8px",
                width="100%",
            ),
        ),
        rx.cond(
            CalculatorState.slot_has_conditionals[index],
            rx.hstack(
                rx.checkbox(
                    checked=CalculatorState.slot_conditions_enabled[index],
                    on_change=lambda value: CalculatorState.set_slot_condition(
                        index, value
                    ),
                    class_name="conditional-checkbox-control",
                ),
                rx.text(
                    "Enable conditional: ",
                    CalculatorState.slot_condition_labels[index],
                    class_name="conditional-checkbox-label",
                ),
                class_name="conditional-checkbox-row",
            ),
        ),
        width="100%",
        gap="3",
    )


def stance_combo_control() -> rx.Component:
    return rx.vstack(
        select_control(
            "Stance Combo",
            CalculatorState.stance_combo_options,
            CalculatorState.selected_stance_combo,
            CalculatorState.set_stance_combo,
            disabled=CalculatorState.stance_combo_locked,
        ),
        rx.cond(
            CalculatorState.stance_combo_locked,
            rx.text("Combo is determined by the selected attack mode.", class_name="optimizer-help"),
        ),
        width="100%",
        gap="1",
    )


def database_slot_body(index: int) -> rx.Component:
    return rx.vstack(
        upgrade_runtime_controls(index),
        width="100%",
        gap="3",
    )


def custom_slot_body(index: int) -> rx.Component:
    return rx.vstack(
        database_entry_input(
            "Custom Upgrade Entry",
            CalculatorState.custom_upgrade_entries[index],
            lambda value: CalculatorState.set_custom_upgrade_entry(index, value),
            placeholder=CalculatorState.custom_upgrade_placeholders[index],
            help_text="JSON",
            min_height="220px",
        ),
        width="100%",
        gap="3",
    )


def riven_editor_row(field: rx.Var[EditorField], position, index: int) -> rx.Component:
    return rx.vstack(
        rx.text(CalculatorState.slot_riven_row_labels[index][position], class_name="compact-label"),
        rx.grid(
            select_input(CalculatorState.slot_riven_field_options[index][position], field.label, lambda value: CalculatorState.set_riven_stat(index, position, value)),
            rx.input(type="number", value=field.value, min=field.min_value, max=field.max_value, step="0.001", on_change=lambda value: CalculatorState.set_slot_field_value(index, field.name, value), debounce_timeout=400, disabled=field.name == "", width="100%"),
            columns="minmax(0, 1fr) minmax(96px, 0.42fr)",
            column_gap="8px",
            width="100%",
            class_name="riven-stat-row",
        ),
        width="100%",
        gap="1",
        align="start",
    )


def riven_slot_body(index: int) -> rx.Component:
    return rx.vstack(
        select_control(
            "Riven Type",
            RIVEN_ROLL_OPTIONS,
            CalculatorState.slot_riven_rolls[index],
            lambda value: CalculatorState.set_riven_roll(index, value),
        ),
        rx.vstack(
            rx.foreach(CalculatorState.slot_fields[index], lambda field, position: riven_editor_row(field, position, index)),
            width="100%",
            gap="3",
            class_name="riven-stat-list",
        ),
        width="100%",
        gap="3",
    )


def upgrade_slot(index: int) -> rx.Component:
    config = SLOT_CONFIGS[index]
    toggle_id = f"slot-editor-toggle-{index}"
    return panel(
        rx.box(
            rx.el.input(type="checkbox", id=toggle_id, checked=CalculatorState.slot_editor_open[index], on_change=lambda value: CalculatorState.set_slot_editor_open(index, value), class_name="slot-editor-toggle-input"),
            rx.el.label(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text(config["label"], class_name="slot-editor-slot-label"),
                            rx.text(CalculatorState.slot_selected_upgrades[index], class_name="card-title slot-editor-upgrade-name"),
                            align="start",
                            gap="1",
                            min_width="0",
                        ),
                        rx.spacer(),
                        rx.badge(CalculatorState.slot_contributions[index], variant="soft", class_name="contribution-badge"),
                        width="100%",
                        align="center",
                    ),
                    slot_stat_preview(CalculatorState.slot_stat_rows[index]),
                    width="100%",
                    gap="3",
                    align="start",
                ),
                html_for=toggle_id,
                class_name="slot-editor-summary",
            ),
            rx.cond(
                CalculatorState.slot_editor_open[index],
                rx.vstack(
                    select_input(slot_options(index), CalculatorState.slot_selected_upgrades[index], lambda value: CalculatorState.set_slot_upgrade(index, value)),
                    *([rx.cond(CalculatorState.exclusive_stance_weapon, rx.text("Exalted weapons always use their own stance.", class_name="optimizer-help"))] if index == STANCE_SLOT_INDEX else []),
                    rx.cond(
                        CalculatorState.slot_selected_upgrades[index] == NONE,
                        rx.text("Select an upgrade to edit its settings.", class_name="empty-text"),
                        rx.cond(
                            CalculatorState.slot_selected_upgrades[index] == CUSTOM,
                            custom_slot_body(index),
                            rx.cond(
                                CalculatorState.slot_selected_upgrades[index] == RIVEN,
                                riven_slot_body(index),
                                database_slot_body(index),
                            ),
                        ),
                    ),
                    width="100%",
                    gap="3",
                    align="start",
                    class_name="slot-editor-controls",
                ),
            ),
            width="100%",
            class_name="slot-editor-shell",
        ),
        class_name="slot-card",
    )


def external_editor_field(field: rx.Var[EditorField]) -> rx.Component:
    return rx.grid(
        rx.text(field.label, class_name="compact-label"),
        rx.input(
            type="number",
            value=field.value,
            min=field.min_value,
            max=field.max_value,
            step=rx.cond(field.integer, "1", "0.001"),
            on_change=lambda value: CalculatorState.set_external_field_value(
                field.name, value
            ),
            debounce_timeout=400,
            width="100%",
        ),
        rx.button(
            "×",
            on_click=CalculatorState.remove_external_field(field.name),
            class_name="icon-button",
            variant="soft",
        ),
        columns="110px minmax(0, 1fr) 32px",
        column_gap="8px",
        align="center",
        width="100%",
    )


def external_buffs() -> rx.Component:
    return panel(
        rx.vstack(
            rx.grid(
                rx.select(
                    CalculatorState.external_available_fields,
                    value=CalculatorState.external_pending_field,
                    on_change=CalculatorState.set_external_pending_field,
                    disabled=CalculatorState.external_available_fields.length() == 0,
                    width="100%",
                    position="popper",
                ),
                rx.button(
                    "+",
                    on_click=CalculatorState.add_external_field,
                    disabled=CalculatorState.external_available_fields.length() == 0,
                    class_name="icon-button",
                ),
                columns="minmax(0, 1fr) 32px",
                column_gap="8px",
                width="100%",
            ),
            rx.cond(
                CalculatorState.external_fields.length() > 0,
                rx.vstack(
                    rx.foreach(CalculatorState.external_fields, external_editor_field),
                    width="100%",
                    gap="2",
                ),
                rx.text("No external buffs added.", class_name="empty-text"),
            ),
            width="100%",
            gap="3",
        )
    )


def clear_upgrade_row(index: int) -> rx.Component:
    config = SLOT_CONFIGS[index]
    return rx.cond(
        CalculatorState.slot_selected_upgrades[index] != NONE,
        rx.grid(
            rx.hstack(
                rx.checkbox(checked=CalculatorState.clear_keep_slots[index], on_change=lambda value: CalculatorState.set_clear_keep_slot(index, value), disabled=CalculatorState.optimize_running),
                rx.text("Keep", class_name="clear-build-keep-label"),
                align="center",
                gap="2",
            ),
            rx.text(config["label"], class_name="clear-build-slot"),
            rx.text(CalculatorState.slot_selected_upgrades[index], class_name="clear-build-upgrade"),
            rx.button("×", on_click=CalculatorState.remove_build_upgrade(index), disabled=CalculatorState.optimize_running, variant="ghost", class_name="clear-build-remove", title="Remove this upgrade"),
            columns="74px 62px minmax(0, 1fr) 30px",
            align="center",
            width="100%",
            class_name="clear-build-row",
        ),
        rx.fragment(),
    )


def clear_external_buff_row(field: rx.Var[ClearBuffRow]) -> rx.Component:
    return rx.grid(
        rx.hstack(
            rx.checkbox(checked=field.keep, on_change=lambda value: CalculatorState.set_clear_keep_buff(field.name, value), disabled=CalculatorState.optimize_running),
            rx.text("Keep", class_name="clear-build-keep-label"),
            align="center",
            gap="2",
        ),
        rx.text("Buff", class_name="clear-build-slot"),
        rx.text(field.label, class_name="clear-build-upgrade"),
        rx.button("×", on_click=CalculatorState.remove_external_field(field.name), disabled=CalculatorState.optimize_running, variant="ghost", class_name="clear-build-remove", title="Remove this external buff"),
        columns="74px 62px minmax(0, 1fr) 30px",
        align="center",
        width="100%",
        class_name="clear-build-row",
    )


def clear_build_menu() -> rx.Component:
    return rx.accordion.root(
        rx.accordion.item(
            header=rx.hstack(rx.text("Clear", class_name="clear-build-title"), rx.badge("Build + buffs", variant="soft", color_scheme="gray"), width="100%", align="center", gap="2"),
            content=rx.vstack(
                rx.text("Mark upgrades or buffs to keep, or remove one directly.", class_name="optimizer-help"),
                rx.cond(
                    CalculatorState.has_build_or_buffs,
                    rx.vstack(*[clear_upgrade_row(index) for index in OPTIMIZER_SLOT_ORDER], rx.foreach(CalculatorState.clear_external_buff_rows, clear_external_buff_row), width="100%", gap="0", class_name="clear-build-list"),
                    rx.text("The build and external buffs are empty.", class_name="empty-text"),
                ),
                rx.button(rx.cond(CalculatorState.clear_has_kept_items, "Clear unmarked items", "Clear build & buffs"), on_click=CalculatorState.clear_build_and_buffs, disabled=(~CalculatorState.has_build_or_buffs) | CalculatorState.optimize_running, color_scheme="red", variant="soft", width="100%"),
                width="100%",
                align="start",
                gap="3",
                class_name="clear-build-content",
            ),
            value="clear-build",
        ),
        type="single",
        collapsible=True,
        color_scheme="gray",
        variant="surface",
        class_name="clear-build-menu",
    )


def slot_spacer() -> rx.Component:
    return rx.box(class_name="slot-spacer", aria_hidden=True)


def mod_upgrade_grid() -> rx.Component:
    return rx.box(
        *[upgrade_slot(index) for index in MOD_SLOT_INDICES],
        class_name="slot-grid slot-grid-mods",
    )


def ranged_upgrade_grid() -> rx.Component:
    return rx.vstack(
        rx.box(
            slot_spacer(),
            upgrade_slot(EXILUS_SLOT_INDEX),
            upgrade_slot(ARCANE_SLOT_INDEX),
            slot_spacer(),
            class_name="slot-grid slot-grid-top slot-grid-top-ranged",
        ),
        mod_upgrade_grid(),
        width="100%",
        gap="3",
        class_name="slot-grid-stack",
    )


def melee_upgrade_grid() -> rx.Component:
    return rx.vstack(
        rx.cond(
            CalculatorState.stance_slot_available,
            rx.box(
                slot_spacer(),
                upgrade_slot(STANCE_SLOT_INDEX),
                upgrade_slot(EXILUS_SLOT_INDEX),
                upgrade_slot(ARCANE_SLOT_INDEX),
                slot_spacer(),
                class_name="slot-grid slot-grid-top slot-grid-top-melee",
            ),
            rx.box(
                slot_spacer(),
                upgrade_slot(EXILUS_SLOT_INDEX),
                upgrade_slot(ARCANE_SLOT_INDEX),
                slot_spacer(),
                class_name="slot-grid slot-grid-top slot-grid-top-ranged",
            ),
        ),
        mod_upgrade_grid(),
        width="100%",
        gap="3",
        class_name="slot-grid-stack",
    )


def upgrades_section() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            section_title("Upgrades", "Stance (melee), eight mod slots, Exilus, Arcane, and external buffs."),
            clear_build_menu(),
            width="100%",
            align="start",
            justify="between",
            gap="4",
            class_name="upgrades-heading-row",
        ),
        rx.box(
            rx.cond(CalculatorState.melee_weapon, melee_upgrade_grid(), ranged_upgrade_grid()),
            class_name="slot-grid-scroll",
            width="100%",
        ),
        rx.vstack(
            external_buffs(),
            align="start",
            gap="3",
            width="100%",
        ),
        width="100%",
        gap="4",
        id="upgrades",
        class_name="page-section",
    )


def optimizer_policy_select(index: int) -> rx.Component:
    return rx.select.root(
        rx.select.trigger(width="100%", min_width="0", class_name="optimizer-policy-trigger"),
        rx.select.content(
            rx.select.group(
                rx.select.item("Replace", value=SLOT_POLICY_DISCARD),
                rx.select.item("Keep in this build", value=SLOT_POLICY_KEEP),
                rx.select.item("Keep in this slot", value=SLOT_POLICY_KEEP_IN_SLOT),
            ),
            position="popper",
        ),
        value=CalculatorState.slot_policies[index],
        on_change=lambda value: CalculatorState.set_slot_policy(index, value),
        disabled=(CalculatorState.slot_selected_upgrades[index] == NONE) | CalculatorState.optimize_running,
        width="100%",
    )


def optimizer_rule_row(index: int) -> rx.Component:
    config = SLOT_CONFIGS[index]
    return rx.grid(
        rx.text(config["label"], class_name="optimizer-rule-slot"),
        rx.text(CalculatorState.slot_selected_upgrades[index], class_name="optimizer-rule-upgrade"),
        optimizer_policy_select(index),
        columns="76px minmax(150px, 1fr) minmax(190px, 0.8fr)",
        align="center",
        class_name="optimizer-rule-row",
        width="100%",
    )


def optimizer_exclusion_chip(value, remove_event, *, disabled) -> rx.Component:
    return rx.hstack(
        rx.text(value, class_name="optimizer-chip-label"),
        rx.button("×", on_click=remove_event, disabled=disabled, variant="ghost", class_name="optimizer-chip-remove"),
        align="center",
        gap="1",
        class_name="optimizer-exclusion-chip",
    )


def optimizer_exclusion_editor(title: str, description: str, options, pending, set_pending, add_event, excluded, remove_event: Callable, clear_event) -> rx.Component:
    disabled = CalculatorState.no_weapon | CalculatorState.optimize_running
    return rx.vstack(
        rx.hstack(
            rx.vstack(rx.text(title, class_name="optimizer-group-title"), rx.text(description, class_name="optimizer-help"), align="start", gap="1"),
            rx.spacer(),
            rx.button("Clear", on_click=clear_event, disabled=disabled | (excluded.length() == 0), variant="ghost", size="1"),
            width="100%",
            align="start",
        ),
        rx.grid(
            select_input(options, pending, set_pending, disabled=disabled | (options.length() == 0)),
            rx.button("Exclude", on_click=add_event, disabled=disabled | (options.length() == 0), width="100%"),
            columns="minmax(0, 1fr) 92px",
            class_name="optimizer-exclusion-picker",
            width="100%",
        ),
        rx.cond(
            excluded.length() > 0,
            rx.hstack(
                rx.foreach(excluded, lambda value: optimizer_exclusion_chip(value, remove_event(value), disabled=disabled)),
                wrap="wrap",
                align="center",
                gap="2",
                width="100%",
            ),
            rx.text("Nothing excluded.", class_name="empty-text"),
        ),
        class_name="optimizer-exclusion-group",
        width="100%",
        align="start",
        gap="3",
    )


def optimizer_run_controls() -> rx.Component:
    disabled = CalculatorState.no_weapon | CalculatorState.no_enemy | CalculatorState.optimize_running
    return rx.vstack(
        select_control(
            "Maximize",
            CalculatorState.optimize_maximize_options,
            CalculatorState.optimize_maximize_target,
            CalculatorState.set_optimize_maximize_target,
            disabled=disabled,
        ),
        rx.hstack(
            rx.checkbox(
                checked=CalculatorState.optimize_find_riven,
                on_change=CalculatorState.set_optimize_find_riven,
                disabled=disabled | CalculatorState.riven_optimize_disabled,
            ),
            rx.vstack(
                rx.text("Find optimal Riven", class_name="toggle-label"),
                rx.text("Search allowed Riven stats after the upgrade build is optimized.", class_name="optimizer-help"),
                align="start",
                gap="1",
            ),
            align="start",
            gap="2",
            width="100%",
        ),
        rx.cond(
            ~CalculatorState.riven_available,
            rx.text("This weapon has no Riven disposition.", class_name="optimizer-warning"),
            rx.cond(
                CalculatorState.riven_optimize_disabled,
                rx.text("Riven search is disabled while a Riven is marked keep or keep in slot.", class_name="optimizer-warning"),
            ),
        ),
        rx.hstack(
            rx.checkbox(
                checked=CalculatorState.optimize_find_evolutions,
                on_change=CalculatorState.set_optimize_find_evolutions,
                disabled=disabled | ~CalculatorState.evolution_optimize_available,
            ),
            rx.vstack(
                rx.text("Find optimal Incarnon perks", class_name="toggle-label"),
                rx.text("Jointly optimize Incarnon perks with the mod build (they depend on each other).", class_name="optimizer-help"),
                align="start",
                gap="1",
            ),
            align="start",
            gap="2",
            width="100%",
        ),
        rx.button(
            rx.cond(CalculatorState.optimize_running, "Optimizing…", "Optimize build"),
            on_click=CalculatorState.optimize_build,
            disabled=disabled,
            width="100%",
            size="3",
        ),
        rx.cond(
            CalculatorState.optimize_running | (CalculatorState.optimize_progress > 0),
            rx.vstack(
                rx.box(
                    rx.box(class_name="optimizer-progress-fill", width=CalculatorState.optimize_progress_width),
                    class_name="optimizer-progress-track",
                ),
                rx.hstack(
                    rx.text(CalculatorState.optimize_phase, class_name="empty-text"),
                    rx.spacer(),
                    rx.text(CalculatorState.optimize_evaluations, " evaluations", class_name="empty-text"),
                    width="100%",
                ),
                width="100%",
                gap="2",
            ),
        ),
        rx.cond(CalculatorState.optimize_status != "", rx.text(CalculatorState.optimize_status, class_name="empty-text")),
        rx.cond(CalculatorState.optimize_best_dps != "", rx.text("Best ", CalculatorState.optimize_maximize_target, ": ", CalculatorState.optimize_best_dps, class_name="preview-value")),
        width="100%",
        gap="3",
        align="start",
        class_name="optimizer-run-controls",
    )


def optimizer_section() -> rx.Component:
    return rx.vstack(
        rx.accordion.root(
            rx.accordion.item(
                header=rx.hstack(
                    rx.vstack(
                        rx.text("Optimization menu", class_name="optimizer-menu-title"),
                        rx.text("Keep, replace, and exclusion rules", class_name="optimizer-help"),
                        align="start",
                        gap="1",
                    ),
                    rx.spacer(),
                    rx.badge(CalculatorState.optimize_excluded_upgrades.length(), " upgrades excluded", variant="soft"),
                    rx.badge(CalculatorState.optimize_excluded_riven_stats.length(), " Riven stats excluded", variant="soft"),
                    width="100%",
                    align="center",
                    wrap="wrap",
                    gap="2",
                ),
                content=rx.vstack(
                    rx.cond(CalculatorState.no_weapon, rx.text("Select a weapon to configure and run optimization.", class_name="optimizer-warning")),
                    rx.cond((~CalculatorState.no_weapon) & CalculatorState.no_enemy, rx.text("Select an enemy to run optimization.", class_name="optimizer-warning")),
                    rx.grid(
                        rx.vstack(
                            rx.text("Current build rules", class_name="optimizer-group-title"),
                            rx.text("Discard lets the optimizer replace an upgrade. Keep may move it; keep in slot locks its position.", class_name="optimizer-help"),
                            rx.vstack(
                                rx.cond(CalculatorState.stance_slot_available, optimizer_rule_row(STANCE_SLOT_INDEX), rx.fragment()),
                                *[optimizer_rule_row(index) for index in OPTIMIZER_SLOT_ORDER if index != STANCE_SLOT_INDEX],
                                width="100%",
                                gap="0",
                                class_name="optimizer-rule-list",
                            ),
                            width="100%",
                            align="start",
                            gap="3",
                            class_name="optimizer-rules-group",
                        ),
                        rx.vstack(
                            optimizer_exclusion_editor(
                                "Excluded upgrades",
                                "Faction damage, external-activation, and reload-triggered upgrades start excluded. Remove any chip to allow one.",
                                CalculatorState.optimize_upgrade_exclusion_options,
                                CalculatorState.optimize_pending_excluded_upgrade,
                                CalculatorState.set_optimize_pending_excluded_upgrade,
                                CalculatorState.add_optimize_excluded_upgrade,
                                CalculatorState.optimize_excluded_upgrades,
                                CalculatorState.remove_optimize_excluded_upgrade,
                                CalculatorState.clear_optimize_excluded_upgrades,
                            ),
                            optimizer_exclusion_editor(
                                "Excluded Riven stats",
                                "Faction damage stats start excluded. Remove any chip to allow one.",
                                CalculatorState.optimize_riven_stat_exclusion_options,
                                CalculatorState.optimize_pending_excluded_riven_stat,
                                CalculatorState.set_optimize_pending_excluded_riven_stat,
                                CalculatorState.add_optimize_excluded_riven_stat,
                                CalculatorState.optimize_excluded_riven_stats,
                                CalculatorState.remove_optimize_excluded_riven_stat,
                                CalculatorState.clear_optimize_excluded_riven_stats,
                            ),
                            width="100%",
                            align="start",
                            gap="3",
                            class_name="optimizer-exclusions-column",
                        ),
                        columns="minmax(0, 1.35fr) minmax(320px, 0.85fr)",
                        class_name="optimizer-settings-grid",
                        width="100%",
                    ),
                    rx.separator(width="100%"),
                    optimizer_run_controls(),
                    width="100%",
                    align="start",
                    gap="4",
                    class_name="optimizer-menu-content",
                ),
                value="optimizer-menu",
            ),
            type="single",
            collapsible=True,
            color_scheme="gray",
            variant="surface",
            width="100%",
            class_name="optimizer-menu",
        ),
        width="100%",
        gap="3",
        id="optimizer",
        class_name="page-section",
    )


def metric_card(metric: rx.Var[MetricRow]) -> rx.Component:
    return panel(
        rx.vstack(
            rx.text(metric.label, class_name="metric-label"),
            rx.text(metric.value, class_name="metric-value"),
            align="start",
            gap="1",
        ),
        class_name="metric-card",
    )


def metric_grid(*metric_groups) -> rx.Component:
    return rx.box(
        *(rx.foreach(metrics, metric_card) for metrics in metric_groups),
        class_name="metric-grid",
        width="100%",
    )


def melee_damage_row(row: rx.Var[DamageResultRow]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(row.damage_type),
        rx.table.cell(row.damage),
        rx.table.cell(row.weight),
        rx.table.cell(row.proc_chance),
    )


def ranged_damage_row(row: rx.Var[DamageResultRow]) -> rx.Component:
    return rx.table.row(
        rx.table.row_header_cell(row.damage_type),
        rx.table.cell(row.damage),
        rx.table.cell(row.direct_weight),
        rx.table.cell(row.explosion_weight),
        rx.table.cell(row.proc_chance),
    )


def damage_table() -> rx.Component:
    melee_table = rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Damage Type"),
                rx.table.column_header_cell("Damage"),
                rx.table.column_header_cell("Weight"),
                rx.table.column_header_cell("Proc Chance"),
            )
        ),
        rx.table.body(rx.foreach(CalculatorState.damage_result_rows, melee_damage_row)),
        width="100%",
        variant="surface",
    )
    ranged_table = rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Damage Type"),
                rx.table.column_header_cell("Damage"),
                rx.table.column_header_cell("Direct Hit Weight"),
                rx.table.column_header_cell("Related Attack Weight"),
                rx.table.column_header_cell("Proc Chance"),
            )
        ),
        rx.table.body(rx.foreach(CalculatorState.damage_result_rows, ranged_damage_row)),
        width="100%",
        variant="surface",
    )
    return rx.box(
        rx.cond(CalculatorState.melee_weapon, melee_table, ranged_table),
        class_name="damage-table-container",
        width="100%",
        overflow_x="auto",
    )


def contribution_row(row: rx.Var[ContributionRow]) -> rx.Component:
    return rx.hstack(
        rx.text(row.name),
        rx.spacer(),
        rx.text(row.value, class_name="preview-value"),
        width="100%",
        align="center",
        class_name="contribution-row",
    )


def result_tabs() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            rx.tabs.trigger("Damage Distribution", value="damage"),
            rx.tabs.trigger("Contributions", value="contributions"),
            rx.tabs.trigger("Text Summary", value="summary"),
        ),
        rx.tabs.content(
            damage_table(),
            value="damage",
            padding_top="1rem",
        ),
        rx.tabs.content(
            rx.cond(
                CalculatorState.contribution_result_rows.length() > 0,
                rx.vstack(
                    rx.foreach(
                        CalculatorState.contribution_result_rows,
                        contribution_row,
                    ),
                    width="100%",
                    gap="1",
                ),
                rx.text("No upgrade contributions.", class_name="empty-text"),
            ),
            value="contributions",
            padding_top="1rem",
        ),
        rx.tabs.content(
            rx.vstack(
                rx.text("Weapon Summary", class_name="card-title"),
                rx.el.pre(
                    CalculatorState.result_summary,
                    class_name="plain-text-summary",
                ),
                rx.text("Upgrade Contributions", class_name="card-title"),
                rx.el.pre(
                    CalculatorState.result_contribution_summary,
                    class_name="plain-text-summary",
                ),
                width="100%",
                gap="3",
                align="start",
            ),
            value="summary",
            padding_top="1rem",
        ),
        default_value="damage",
        width="100%",
    )


def results_section() -> rx.Component:
    return rx.vstack(
        section_title("Results", "Updated automatically whenever the build changes."),
        rx.cond(
            CalculatorState.has_error,
            rx.vstack(
                rx.text("The calculator could not evaluate the current configuration."),
                rx.foreach(CalculatorState.result_errors, lambda error: rx.code(error, class_name="result-error-message")),
                class_name="error-box",
                width="100%",
                align="start",
                gap="2",
            ),
        ),
        rx.cond(
            CalculatorState.result_ready,
            rx.vstack(
                metric_grid(CalculatorState.result_metrics),
                panel(result_tabs()),
                width="100%",
                gap="4",
            ),
            rx.cond(
                ~CalculatorState.has_error,
                panel(rx.text("Preparing calculator results…", class_name="empty-text")),
            ),
        ),
        width="100%",
        gap="3",
        id="results",
        class_name="page-section",
    )


def page() -> rx.Component:
    return rx.box(
        rx.vstack(
            header(),
            mobile_quick_nav(),
            read_me(),
            weapon_section(),
            enemy_section(),
            upgrades_section(),
            optimizer_section(),
            results_section(),
            width="100%",
            gap="7",
            align="start",
        ),
        class_name="page-shell",
    )
