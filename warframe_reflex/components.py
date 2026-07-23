from __future__ import annotations

from typing import Callable

import reflex as rx

from .constants import (
    NO_EFFECT,
    PROGENITOR_ELEMENT_OPTIONS,
    RIVEN_ROLL_OPTIONS,
    SLOT_CONFIGS,
    WEAPON_TYPE_OPTIONS,
)
from .models import ContributionRow, DamageResultRow, DisplayRow, EditorField, MetricRow
from .state import CUSTOM, RIVEN, CalculatorState


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
    """Render a full-width, 32px-high Radix select trigger."""
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
                rx.foreach(
                    options,
                    lambda option: rx.select.item(option, value=option),
                ),
            ),
            position="popper",
        ),
        value=value,
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
) -> rx.Component:
    return labeled_control(
        label,
        select_input(
            options,
            value,
            on_change,
            disabled=disabled,
        ),
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
            debounce_timeout=250,
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
                "Configure a weapon, build, and external buffs with deterministic DPH/DPS calculations.",
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
        rx.link("Upgrades", href="#upgrades", class_name="mobile-nav-link"),
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
                        "Select a weapon type and weapon, configure custom base stats when needed, fill the eight mod slots plus Exilus and Arcane, add external buffs, then inspect the live results."
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
            debounce_timeout=250,
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
            maximum=10,
        ),
        columns=rx.breakpoints(initial="1", sm="2"),
        gap="4",
        width="100%",
        class_name="form-grid form-grid-2 progenitor-grid",
    )


def supported_progenitor_controls() -> rx.Component:
    return rx.cond(CalculatorState.supports_progenitor, progenitor_controls())


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
                    select_control(
                        "Weapon",
                        CalculatorState.weapon_options,
                        CalculatorState.selected_weapon,
                        CalculatorState.set_weapon,
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
                rx.cond(
                    CalculatorState.custom_weapon,
                    custom_base_stats(),
                    supported_progenitor_controls(),
                ),
                width="100%",
                gap="5",
            )
        ),
        width="100%",
        gap="3",
        id="weapon",
        class_name="page-section",
    )


def display_stat_row(row: rx.Var[DisplayRow]) -> rx.Component:
    return rx.hstack(
        rx.text(row.label, class_name="preview-label"),
        rx.spacer(),
        rx.text(row.value, class_name="preview-value"),
        width="100%",
        align="center",
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
            debounce_timeout=250,
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


def database_slot_body(index: int) -> rx.Component:
    return rx.vstack(
        upgrade_runtime_controls(index),
        rx.separator(width="100%"),
        stat_preview(CalculatorState.slot_stat_rows[index]),
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
        rx.separator(width="100%"),
        stat_preview(CalculatorState.slot_stat_rows[index]),
        width="100%",
        gap="3",
    )


def riven_slot_body(index: int) -> rx.Component:
    available = CalculatorState.slot_available_fields[index]
    return rx.vstack(
        select_control(
            "Riven Roll",
            RIVEN_ROLL_OPTIONS,
            CalculatorState.slot_riven_rolls[index],
            lambda value: CalculatorState.set_riven_roll(index, value),
        ),
        rx.grid(
            rx.select(
                available,
                value=CalculatorState.slot_pending_fields[index],
                on_change=lambda value: CalculatorState.set_slot_pending_field(
                    index, value
                ),
                disabled=available.length() == 0,
                width="100%",
                position="popper",
            ),
            rx.button(
                "+",
                on_click=CalculatorState.add_slot_field(index),
                disabled=available.length() == 0,
                class_name="icon-button field-action-button",
            ),
            columns="minmax(0, 1fr) 32px",
            column_gap="8px",
            width="100%",
        ),
        rx.cond(
            CalculatorState.slot_fields[index].length() > 0,
            rx.vstack(
                rx.foreach(
                    CalculatorState.slot_fields[index],
                    lambda field: slot_editor_field(field, index),
                ),
                width="100%",
                gap="2",
            ),
            rx.text("No Riven stats added.", class_name="empty-text"),
        ),
        rx.separator(width="100%"),
        stat_preview(CalculatorState.slot_stat_rows[index]),
        width="100%",
        gap="3",
    )


def upgrade_slot(index: int) -> rx.Component:
    config = SLOT_CONFIGS[index]
    return panel(
        rx.vstack(
            rx.hstack(
                rx.text(config["label"], class_name="card-title"),
                rx.spacer(),
                rx.badge(
                    CalculatorState.slot_contributions[index],
                    variant="soft",
                    class_name="contribution-badge",
                ),
                width="100%",
                align="center",
            ),
            select_input(
                slot_options(index),
                CalculatorState.slot_selected_upgrades[index],
                lambda value: CalculatorState.set_slot_upgrade(index, value),
            ),
            rx.cond(
                CalculatorState.slot_selected_upgrades[index] == CUSTOM,
                custom_slot_body(index),
                rx.cond(
                    CalculatorState.slot_selected_upgrades[index] == RIVEN,
                    riven_slot_body(index),
                    database_slot_body(index),
                ),
            ),
            width="100%",
            gap="3",
            align="start",
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
            debounce_timeout=250,
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


def upgrades_section() -> rx.Component:
    # Preserve the familiar card layout without changing the canonical build order.
    display_order = (0, 1, 2, 3, 9, 4, 5, 6, 7, 8)
    return rx.vstack(
        section_title(
            "Upgrades",
            "Eight normal mod slots, one Exilus slot, one Arcane slot, and external buffs.",
        ),
        rx.box(
            rx.box(
                *[upgrade_slot(index) for index in display_order],
                class_name="slot-grid",
            ),
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
            rx.box(
                rx.text("The calculator could not evaluate the current configuration."),
                rx.code(CalculatorState.result_error),
                class_name="error-box",
                width="100%",
            ),
        ),
        rx.cond(
            CalculatorState.result_ready,
            rx.vstack(
                rx.cond(
                    CalculatorState.ranged_weapon,
                    metric_grid(CalculatorState.ranged_result_metrics),
                    metric_grid(CalculatorState.main_result_metrics),
                ),
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
            upgrades_section(),
            results_section(),
            width="100%",
            gap="7",
            align="start",
        ),
        class_name="page-shell",
    )
