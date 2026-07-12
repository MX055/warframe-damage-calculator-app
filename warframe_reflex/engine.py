from __future__ import annotations

from typing import Iterable

from warframe_damage_calculator import Build, Upgrade, dist

from .constants import (
    DAMAGE_TYPES,
    UPGRADE_BOOL_FIELDS,
    UPGRADE_SCALAR_FIELDS,
    WEAPON_TYPES,
)
from .data import database_weapon
from .models import ContributionRow, DamageResultRow, DisplayRow, MetricRow


def field_label(field_name: str) -> str:
    return field_name.replace("_", " ").title()


def parse_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_int(value: object, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def clamp_number(
    value: float,
    min_value: float | None,
    max_value: float | None,
) -> float:
    if min_value is not None:
        value = max(value, min_value)
    if max_value is not None:
        value = min(value, max_value)
    return value


def upgrade_field_input_config(
    field_limits: tuple[float | int, ...] | None,
    allow_negative: bool,
) -> tuple[float, float, float, bool]:
    if field_limits is None:
        return (-1_000_000_000.0 if allow_negative else 0.0), 1_000_000_000.0, 0.0, False

    min_limit, max_limit = field_limits[:2]
    min_value = float(min_limit) if allow_negative else max(float(min_limit), 0.0)
    max_value = float(max_limit)
    default_value = (
        float(field_limits[2])
        if len(field_limits) > 2
        else (min_value if min_value > 0 else 0.0)
    )
    default_value = max(default_value, min_value)
    is_integer_field = all(
        isinstance(value, int)
        for value in (min_limit, max_limit, field_limits[2] if len(field_limits) > 2 else 0)
    )
    return min_value, max_value, default_value, is_integer_field


def is_field_allowed(field_name: str, weapon_type_name: str, rules: dict) -> bool:
    allowed_weapon_types = rules.get(field_name)
    return allowed_weapon_types is None or weapon_type_name in allowed_weapon_types


def build_upgrade(name: str, values: dict[str, float | int]) -> Upgrade:
    damage_values = {
        damage_type: float(values.get(damage_type, 0.0))
        for damage_type in DAMAGE_TYPES
        if float(values.get(damage_type, 0.0)) != 0
    }
    damage_distribution = dist(**damage_values) if damage_values else dist()

    scalar_values = {
        field_name: float(values.get(field_name, 0.0))
        for field_name in UPGRADE_SCALAR_FIELDS
        if field_name != "secondary_enervate"
    }
    stats = dict(scalar_values)
    if damage_values:
        stats["damage_dist"] = damage_distribution
    secondary_enervate = int(values.get("secondary_enervate", 0))
    if secondary_enervate:
        stats["secondary_enervate"] = secondary_enervate
    for field_name in UPGRADE_BOOL_FIELDS:
        if bool(values.get(field_name, False)):
            stats[field_name] = True
    return Upgrade(name=name, stats=stats)


def is_non_empty_upgrade(item: Upgrade) -> bool:
    return bool(item.stats or item.conditional_stats or item.stacking_stats)


def format_stat_value(
    value: float | int | bool,
    *,
    field_name: str | None = None,
) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"

    # Secondary Enervate stores the number of Big Critical Hits required
    # before the bonus resets. It is a count, not a percentage.
    if field_name == "secondary_enervate":
        return str(int(value))

    if isinstance(value, int):
        return str(value)
    return f"{value:,.1%}"


def upgrade_stat_rows(upgrade: Upgrade) -> list[DisplayRow]:
    rows: list[DisplayRow] = []

    def add_stat(field_name: str, value, suffix: str = "") -> None:
        if field_name == "damage_dist" and isinstance(value, dist):
            for damage_type, damage_value in value:
                if damage_value != 0:
                    rows.append(DisplayRow(field_label(damage_type) + suffix, format_stat_value(damage_value, field_name=damage_type)))
            return
        if value != 0 and value is not False:
            rows.append(DisplayRow(field_label(field_name) + suffix, format_stat_value(value, field_name=field_name)))

    for field_name, value in upgrade.stats.items():
        add_stat(field_name, value)
    for field_name, (value, condition) in upgrade.conditional_stats.items():
        add_stat(field_name, value, f" ({condition})")
    for field_name, (value, condition) in upgrade.stacking_stats.items():
        add_stat(field_name, value, f" / stack ({condition})")
    return rows

def progenitor_upgrade(element: str, value: float, no_effect: str) -> Upgrade:
    if element == no_effect or value <= 0:
        return Upgrade(name="Progenitor", category="progenitor")
    return Upgrade(
        name="Progenitor",
        category="progenitor",
        stats={"damage_dist": dist(**{element: value})},
    )


def configured_weapon(
    weapon_type_name: str,
    selected_weapon_name: str,
    *,
    custom_weapon: bool,
    base_stats: dict,
    upgrades: list[Upgrade],
    context: dict[str, bool | int] | None = None,
):
    weapon_type = WEAPON_TYPES[weapon_type_name]
    if custom_weapon:
        weapon = weapon_type(**base_stats)
    else:
        weapon = database_weapon(selected_weapon_name, weapon_type_name)
        if weapon is None:
            raise LookupError(f"Could not load weapon: {selected_weapon_name}")

    if upgrades:
        weapon.configure(Build(*upgrades), context=context)
    return weapon


def contribution_items(contribution_lookup) -> list[tuple[object, float]]:
    if contribution_lookup is None:
        return []
    if hasattr(contribution_lookup, "items"):
        return list(contribution_lookup.items())
    return list(contribution_lookup)


def contribution_key_name(contribution_key: object) -> str:
    if isinstance(contribution_key, str):
        return contribution_key
    return getattr(contribution_key, "name", None) or getattr(
        contribution_key, "category", ""
    )


def contribution_for_category(contribution_lookup, name: str) -> float | None:
    items = contribution_items(contribution_lookup)
    direct = [
        value for key, value in items if contribution_key_name(key) == name
    ]
    if direct:
        return sum(direct)
    prefix = f"{name} (slot "
    slotted = [
        value
        for key, value in items
        if contribution_key_name(key).startswith(prefix)
    ]
    return sum(slotted) if slotted else None


def compute_contribution_proportions(
    weapon_type_name: str,
    base_stats: dict,
    upgrades: list[Upgrade],
    context: dict[str, bool | int] | None = None,
) -> list[tuple[Upgrade, float]]:
    if not upgrades:
        return []

    weapon_type = WEAPON_TYPES[weapon_type_name]
    full_weapon = weapon_type(**base_stats)
    full_weapon.configure(Build(*upgrades), context=context)
    total_dps = full_weapon.stats.total_dps
    contributions: list[tuple[Upgrade, float]] = []

    for index, upgrade in enumerate(upgrades):
        remaining = [item for other_index, item in enumerate(upgrades) if other_index != index]
        comparison_weapon = weapon_type(**base_stats)
        if remaining:
            comparison_weapon.configure(Build(*remaining), context=context)
        contributions.append((upgrade, total_dps - comparison_weapon.stats.total_dps))

    contribution_total = sum(value for _, value in contributions) or 1.0
    return [(upgrade, value / contribution_total) for upgrade, value in contributions]


def contribution_lookup_for_weapon(
    weapon,
    weapon_type_name: str,
    base_stats: dict | None,
    upgrades: list[Upgrade],
    context: dict[str, bool | int] | None = None,
):
    for attribute_name in (
        "contribution_proportions",
        "upgrade_contribution_proportions",
        "contributions_proportions",
    ):
        try:
            return contribution_items(getattr(weapon.stats, attribute_name))
        except (AttributeError, TypeError):
            pass

    if base_stats is None:
        return []
    return compute_contribution_proportions(weapon_type_name, base_stats, upgrades, context)


def format_contribution(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def contribution_rows(contribution_lookup) -> list[ContributionRow]:
    return [
        ContributionRow(contribution_key_name(key), f"{value:.2%}")
        for key, value in contribution_items(contribution_lookup)
    ]


def format_upgrade_contributions(contribution_lookup) -> str:
    items = contribution_items(contribution_lookup)
    if not items:
        return "No upgrade contributions."
    named_items = [(contribution_key_name(key), value) for key, value in items]
    max_label_length = max(len(name) for name, _ in named_items)
    return "\n".join(
        f"{f'{name}:':<{max_label_length + 1}} {value:.2%}"
        for name, value in named_items
    )


def main_metrics(weapon) -> list[MetricRow]:
    return [
        MetricRow("Flat DPH", f"{weapon.stats.flat_dph:,.2f}"),
        MetricRow("Flat DOTPH", f"{weapon.stats.flat_dotph:,.2f}"),
        MetricRow("Total DPH", f"{weapon.stats.total_dph:,.2f}"),
        MetricRow("Flat DPS", f"{weapon.stats.flat_dps:,.2f}"),
        MetricRow("Flat DOTPS", f"{weapon.stats.flat_dotps:,.2f}"),
        MetricRow("Total DPS", f"{weapon.stats.total_dps:,.2f}"),
    ]


def weakpoint_metrics(weapon) -> list[MetricRow]:
    return [
        MetricRow("Flat Weakpoint DPH", f"{weapon.stats.flat_weakpoint_dph:,.2f}"),
        MetricRow("Flat Weakpoint DOTPH", f"{weapon.stats.flat_weakpoint_dotph:,.2f}"),
        MetricRow("Total Weakpoint DPH", f"{weapon.stats.total_weakpoint_dph:,.2f}"),
        MetricRow("Flat Weakpoint DPS", f"{weapon.stats.flat_weakpoint_dps:,.2f}"),
        MetricRow("Flat Weakpoint DOTPS", f"{weapon.stats.flat_weakpoint_dotps:,.2f}"),
        MetricRow("Total Weakpoint DPS", f"{weapon.stats.total_weakpoint_dps:,.2f}"),
    ]


def ranged_misc_metrics(weapon) -> list[MetricRow]:
    proc_total = sum(
        (
            weapon.stats.effective.damage_dist.weight(damage_type)
            + weapon.stats.effective.explosion_damage_dist.weight(damage_type)
        )
        * weapon.stats.average_procs_per_shot
        for damage_type, _ in (
            weapon.stats.effective.damage_dist
            + weapon.stats.effective.explosion_damage_dist
        )
    )
    return [
        MetricRow("Average Fire Rate", f"{weapon.stats.average_fire_rate:,.2f}"),
        MetricRow("Procs / Shot", f"{proc_total:,.2f}"),
    ]


def effective_damage_rows(weapon, *, melee: bool) -> list[DamageResultRow]:
    if melee:
        return [
            DamageResultRow(
                damage_type=damage_type.title(),
                damage=f"{damage:,.2f}",
                weight=f"{weapon.stats.effective.damage_dist.weight(damage_type):,.2f}",
                proc_chance=(
                    f"{weapon.stats.effective.damage_dist.weight(damage_type) * weapon.stats.effective.status_chance:.1%}"
                ),
            )
            for damage_type, damage in weapon.stats.effective.damage_dist
        ]

    combined = weapon.stats.effective.damage_dist + weapon.stats.effective.explosion_damage_dist
    return [
        DamageResultRow(
            damage_type=damage_type.title(),
            damage=f"{damage:,.2f}",
            direct_weight=(
                f"{weapon.stats.effective.damage_dist.weight(damage_type):,.2f}"
            ),
            explosion_weight=(
                f"{weapon.stats.effective.explosion_damage_dist.weight(damage_type):,.2f}"
            ),
            proc_chance=(
                f"{(weapon.stats.effective.damage_dist.weight(damage_type) + weapon.stats.effective.explosion_damage_dist.weight(damage_type)) * weapon.stats.average_procs_per_shot:.1%}"
            ),
        )
        for damage_type, damage in combined
    ]
