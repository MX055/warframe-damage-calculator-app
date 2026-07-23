from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Iterable

from warframe_damage_calculator import Build, Upgrade
from warframe_damage_calculator.models.dist import Dist

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
    mode_fields = {
        "base_damage": ("damage_bonus", "additive"),
        "multiplicative_base_damage": ("damage_bonus", "multiplicative"),
        "flat_crit_chance": ("crit_chance", "flat"),
        "multiplicative_crit_chance": ("crit_chance", "multiplicative"),
        "flat_crit_damage": ("crit_damage", "flat"),
        "multiplicative_fire_rate": ("fire_rate", "multiplicative"),
        "multiplicative_weakpoint_crit_chance": (
            "weakpoint_crit_chance",
            "multiplicative",
        ),
    }
    stats: dict[str, object] = {}

    def add_effect(stat: str, value: float | int | bool, mode: str = "additive"):
        if value == 0 or value is False:
            return
        effect = {"value": value, "mode": mode}
        existing = stats.get(stat)
        if existing is None:
            stats[stat] = [effect]
        else:
            existing.append(effect)

    for field_name in (*DAMAGE_TYPES, *UPGRADE_SCALAR_FIELDS):
        value = values.get(field_name, 0)
        if field_name == "secondary_enervate":
            value = int(value)
        stat, mode = mode_fields.get(field_name, (field_name, "additive"))
        add_effect(stat, value, mode)
    for field_name in UPGRADE_BOOL_FIELDS:
        add_effect(field_name, bool(values.get(field_name, False)))
    return Upgrade(
        {
            "name": name,
            "type": "buff",
            "max_rank": 0,
            "compatibility": {},
            "stats": stats,
        }
    )


def parse_database_entry(
    text: str,
    *,
    default_name: str,
    default_type: str,
) -> dict:
    try:
        entry = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{default_name} JSON is invalid at line {exc.lineno}, column {exc.colno}: "
            f"{exc.msg}"
        ) from exc
    if not isinstance(entry, dict):
        raise ValueError(f"{default_name} must be a JSON object.")
    if "name" not in entry and len(entry) == 1:
        wrapped_name, wrapped_entry = next(iter(entry.items()))
        if isinstance(wrapped_entry, dict):
            entry = dict(wrapped_entry)
            entry.setdefault("name", wrapped_name)
    entry.setdefault("name", default_name)
    entry.setdefault("type", default_type)
    return entry


def custom_upgrade_from_entry(
    text: str,
    *,
    default_name: str,
    default_type: str,
) -> Upgrade:
    entry = parse_database_entry(
        text,
        default_name=default_name,
        default_type=default_type,
    )
    runtime = entry.pop("runtime", None)
    if not isinstance(entry.get("stats", {}), dict):
        raise ValueError(f"{default_name} stats must be a JSON object.")
    upgrade = Upgrade(entry)
    if runtime is not None:
        if not isinstance(runtime, dict):
            raise ValueError(f"{default_name} runtime must be a JSON object.")
        upgrade.configure(runtime)
    return upgrade


def weapon_payload(weapon_type_name: str, base_stats: dict, *, name: str = "") -> dict:
    stats = dict(base_stats)
    subtype = str(stats.pop("type", weapon_type_name.casefold()))
    weapon_name = name or "Custom Weapon"
    damage = stats.pop("damage", Dist())
    forced_procs = stats.pop("forced_procs", Dist())
    explosion_damage = stats.pop("explosion_damage", Dist())
    explosion_procs = stats.pop("explosion_forced_procs", Dist())
    is_battery = bool(stats.pop("is_battery", False))
    is_beam = bool(stats.pop("is_beam", False))
    reload_time = stats.pop("reload_speed", 0.0)
    magazine_size = stats.pop("magazine_capacity", 1)
    recharge_rate = stats.pop("recharge_rate", 0.0)
    trigger = "charge" if stats.get("charge_time", 0) else "burst" if stats.get("burst_count", 1) > 1 else "auto"
    attack = {
        "trigger": trigger,
        "delivery": "beam" if is_beam else "hitscan",
        "stats": {"damage": damage, "forced_procs": forced_procs, **stats},
    }
    attacks = {"normal_attack": attack}
    if Dist(explosion_damage).total_damage() or Dist(explosion_procs).total_damage():
        attack["children"] = ["explosion"]
        attacks["explosion"] = {
            "trigger": trigger,
            "delivery": "projectile",
            "aoe": True,
            "stats": {
                "damage": explosion_damage,
                "forced_procs": explosion_procs,
                **{key: value for key, value in stats.items() if key not in {"burst_count", "burst_delay", "charge_time"}},
            },
        }
    ammo = {"reload_time": reload_time, "magazine_size": magazine_size}
    if is_battery:
        ammo.update({"recharge_rate": recharge_rate, "recharge_delay": 0.0})
    return {
        "name": weapon_name,
        "type": weapon_type_name.casefold(),
        "subtype": subtype,
        "ammo": ammo,
        "attacks": attacks,
    }


def is_non_empty_upgrade(item: Upgrade) -> bool:
    return bool(item.data.stats)


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

    flat_units = {
        "combo_duration": "s",
        "initial_combo": "",
        "punch_through": "m",
        "range": "m",
    }
    if field_name in flat_units:
        unit = flat_units[field_name]
        formatted = f"{float(value):,.3f}".rstrip("0").rstrip(".")
        return f"{formatted} {unit}".rstrip()

    if isinstance(value, int):
        return str(value)
    return f"{value:,.1%}"


def upgrade_stat_rows(
    upgrade: Upgrade,
    extra_stats: Mapping[str, object] | None = None,
) -> list[DisplayRow]:
    rows: list[DisplayRow] = []

    def add_stat(field_name: str, value, suffix: str = "") -> None:
        if field_name == "damage" and isinstance(value, (Dist, Mapping)):
            for damage_type, damage_value in Dist(value):
                if damage_value != 0:
                    rows.append(DisplayRow(field_label(damage_type) + suffix, format_stat_value(damage_value, field_name=damage_type)))
            return
        if value != 0 and value is not False:
            rows.append(DisplayRow(field_label(field_name) + suffix, format_stat_value(value, field_name=field_name)))

    for field_name, effects in upgrade.data.stats.items():
        for raw_effect in effects if isinstance(effects, list) else [effects]:
            if isinstance(raw_effect, Mapping) and "value" in raw_effect:
                value = raw_effect["value"]
                stack = raw_effect.get("stacks")
                stacks_on = stack.get("when") if isinstance(stack, Mapping) else None
                condition = stacks_on or raw_effect.get("when")
                required_rank = raw_effect.get("rank")
                qualifiers = []
                mode = raw_effect.get("mode", "additive")
                if mode != "additive":
                    qualifiers.append(str(mode))
                if required_rank is not None:
                    qualifiers.append(f"rank {required_rank}")
                elif condition:
                    qualifiers.append(str(condition))
                required_upgrade = raw_effect.get("equipped")
                if required_upgrade:
                    required_names = (
                        required_upgrade
                        if isinstance(required_upgrade, list)
                        else [required_upgrade]
                    )
                    qualifiers.append(f"with {', '.join(map(str, required_names))}")
                stacking = stacks_on is not None
                suffix = " / stack" if stacking else ""
                if qualifiers:
                    suffix += f" ({'; '.join(qualifiers)})"
                add_stat(field_name, value, suffix)
            else:
                add_stat(field_name, raw_effect)

    flat_units = {
        "combo_duration": "s",
        "initial_combo": "",
        "punch_through": "m",
        "range": "m",
    }
    existing_fields = set(upgrade.data.stats)
    for field_name, effects in (extra_stats or {}).items():
        if field_name in existing_fields:
            continue
        for raw_effect in effects if isinstance(effects, list) else [effects]:
            value = (
                raw_effect.get("value")
                if isinstance(raw_effect, Mapping)
                else raw_effect
            )
            if value in (None, 0, False):
                continue
            qualifiers: list[str] = []
            if isinstance(raw_effect, Mapping):
                mode = raw_effect.get("mode", "additive")
                if mode != "additive":
                    qualifiers.append(str(mode))
                condition = raw_effect.get("when")
                stacks = raw_effect.get("stacks")
                if isinstance(stacks, Mapping):
                    condition = stacks.get("when", condition)
                    maximum = stacks.get("max")
                    qualifiers.append(
                        f"{condition or 'stacks'}"
                        + (f", max {maximum}" if maximum is not None else "")
                    )
                elif condition:
                    qualifiers.append(str(condition))
            label = field_label(field_name)
            if qualifiers:
                label += f" ({'; '.join(qualifiers)})"
            if isinstance(value, bool):
                formatted = "Yes" if value else "No"
            elif field_name in flat_units:
                unit = flat_units[field_name]
                formatted = f"{float(value):,.3f}".rstrip("0").rstrip(".")
                if unit:
                    formatted = f"{formatted} {unit}"
            elif isinstance(value, (int, float)):
                formatted = f"{float(value):,.1%}"
            else:
                formatted = str(value)
            rows.append(DisplayRow(label, formatted))
    return rows

def progenitor_upgrade(element: str, value: float, no_effect: str) -> Upgrade:
    if element == no_effect or value <= 0:
        return Upgrade({"name": "Progenitor", "type": "progenitor", "stats": {}})
    return Upgrade(
        {
            "name": "Progenitor",
            "type": "progenitor",
            "stats": {element: [{"value": value, "mode": "additive"}]},
        }
    )


def configured_weapon(
    weapon_type_name: str,
    selected_weapon_name: str,
    *,
    custom_weapon: bool,
    base_stats: dict,
    upgrades: list[Upgrade],
    custom_entry: str | None = None,
    selected_mode: str | None = None,
    evolutions: dict[int, int] | None = None,
):
    weapon_type = WEAPON_TYPES[weapon_type_name]
    if custom_weapon:
        if custom_entry is None:
            entry = weapon_payload(
                weapon_type_name,
                base_stats,
                name=selected_weapon_name,
            )
        else:
            entry = parse_database_entry(
                custom_entry,
                default_name="Custom Weapon",
                default_type=weapon_type_name.casefold(),
            )
        if not isinstance(entry.get("attacks"), dict) or not entry["attacks"]:
            raise ValueError("Custom Weapon attacks must be a non-empty JSON object.")
        expected_type = weapon_type_name.casefold()
        actual_type = str(entry.get("type", "")).casefold()
        if actual_type != expected_type:
            raise ValueError(
                f"Custom Weapon type must be {expected_type!r} for the selected category."
            )
        weapon = weapon_type(entry)
    else:
        weapon = database_weapon(selected_weapon_name, weapon_type_name)
        if weapon is None:
            raise LookupError(f"Could not load weapon: {selected_weapon_name}")

    attack = None
    if selected_mode:
        wanted = "_".join(selected_mode.casefold().replace("-", " ").split())
        attack = next(
            (
                name
                for name in weapon.data.attacks
                if "_".join(name.casefold().replace("-", " ").split()) == wanted
            ),
            selected_mode,
        )
    weapon.configure(Build(*upgrades), attack=attack, evolutions=evolutions)
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
    return getattr(getattr(contribution_key, "data", None), "name", None) or getattr(contribution_key, "name", None) or getattr(
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
) -> list[tuple[Upgrade, float]]:
    if not upgrades:
        return []

    weapon_type = WEAPON_TYPES[weapon_type_name]
    payload = weapon_payload(weapon_type_name, base_stats)
    full_weapon = weapon_type(payload)
    full_weapon.configure(Build(*upgrades))
    total_dps = full_weapon.results.main.final.total_dps
    contributions: list[tuple[Upgrade, float]] = []

    for index, upgrade in enumerate(upgrades):
        remaining = [item for other_index, item in enumerate(upgrades) if other_index != index]
        comparison_weapon = weapon_type(payload)
        if remaining:
            comparison_weapon.configure(Build(*remaining))
        contributions.append(
            (upgrade, total_dps - comparison_weapon.results.main.final.total_dps)
        )

    contribution_total = sum(value for _, value in contributions) or 1.0
    return [(upgrade, value / contribution_total) for upgrade, value in contributions]


def contribution_lookup_for_weapon(
    weapon,
    weapon_type_name: str,
    base_stats: dict | None,
    upgrades: list[Upgrade],
):
    for attribute_name in (
        "contribution_proportions",
        "upgrade_contribution_proportions",
        "contributions_proportions",
    ):
        try:
            value = getattr(weapon.results, attribute_name)
            return contribution_items(value() if callable(value) else value)
        except (AttributeError, TypeError):
            pass

    if base_stats is None:
        return []
    return compute_contribution_proportions(weapon_type_name, base_stats, upgrades)


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
    average = weapon.results.main.final
    return [
        MetricRow("Flat DPH", f"{average.flat_dph:,.2f}"),
        MetricRow("Flat DOTPH", f"{average.flat_dotph:,.2f}"),
        MetricRow("Total DPH", f"{average.total_dph:,.2f}"),
        MetricRow("Flat DPS", f"{average.flat_dps:,.2f}"),
        MetricRow("Flat DOTPS", f"{average.flat_dotps:,.2f}"),
        MetricRow("Total DPS", f"{average.total_dps:,.2f}"),
    ]


def weakpoint_metrics(weapon) -> list[MetricRow]:
    average = weapon.results.main.final
    return [
        MetricRow("Flat Weakpoint DPH", f"{average.flat_weakpoint_dph:,.2f}"),
        MetricRow("Flat Weakpoint DOTPH", f"{average.flat_weakpoint_dotph:,.2f}"),
        MetricRow("Total Weakpoint DPH", f"{average.total_weakpoint_dph:,.2f}"),
        MetricRow("Flat Weakpoint DPS", f"{average.flat_weakpoint_dps:,.2f}"),
        MetricRow("Flat Weakpoint DOTPS", f"{average.flat_weakpoint_dotps:,.2f}"),
        MetricRow("Total Weakpoint DPS", f"{average.total_weakpoint_dps:,.2f}"),
    ]


def ranged_misc_metrics(weapon) -> list[MetricRow]:
    selected = weapon.results.main
    return [
        MetricRow("Average Fire Rate", f"{selected.final.fire_rate:,.2f}"),
        MetricRow("Procs / Shot", f"{selected.average.procs_per_shot:,.2f}"),
    ]


def effective_damage_rows(weapon, *, melee: bool) -> list[DamageResultRow]:
    selected = weapon.results.main
    if melee:
        return [
            DamageResultRow(
                damage_type=damage_type.title(),
                damage=f"{damage:,.2f}",
                weight=f"{selected.effective.damage.weight(damage_type):,.2f}",
                proc_chance=(
                    f"{selected.effective.damage.weight(damage_type) * selected.effective.status_chance:.1%}"
                ),
            )
            for damage_type, damage in selected.effective.damage
        ]

    related = weapon.results.child
    related_damage = Dist()
    for child in related:
        related_damage += child.effective.damage
    combined = selected.effective.damage + related_damage
    return [
        DamageResultRow(
            damage_type=damage_type.title(),
            damage=f"{damage:,.2f}",
            direct_weight=(
                f"{selected.effective.damage.weight(damage_type):,.2f}"
            ),
            explosion_weight=f"{related_damage.weight(damage_type):,.2f}",
            proc_chance=(
                f"{selected.effective.damage.weight(damage_type) * selected.effective.status_chance:.1%}"
            ),
        )
        for damage_type, damage in combined
    ]
