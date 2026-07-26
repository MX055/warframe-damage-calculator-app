from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Iterable

from warframe_damage_calculator import Build, Enemy, Upgrade
from warframe_damage_calculator.core.dist import Dist

from .constants import (
    DAMAGE_TYPES,
    UPGRADE_BOOL_FIELDS,
    UPGRADE_SCALAR_FIELDS,
    WEAPON_TYPES,
)
from .data import database_enemy, database_weapon
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


LEGACY_EFFECT_MODES = {"additive": "proportional", "multiplicative": "base"}


def normalize_effect_mode(mode: object | None) -> str:
    if mode is None or mode == "":
        return "proportional"
    text = str(mode)
    return LEGACY_EFFECT_MODES.get(text, text)


def _normalize_effect_modes_in_stats(stats: object) -> None:
    if not isinstance(stats, dict):
        return
    for effects in stats.values():
        for effect in effects if isinstance(effects, list) else [effects]:
            if isinstance(effect, dict) and "mode" in effect:
                effect["mode"] = normalize_effect_mode(effect.get("mode"))


def build_upgrade(name: str, values: dict[str, float | int]) -> Upgrade:
    mode_fields = {
        "base_damage": ("damage_bonus", "proportional"),
        "multiplicative_base_damage": ("damage_bonus", "base"),
        "flat_crit_chance": ("crit_chance", "flat"),
        "multiplicative_crit_chance": ("crit_chance", "base"),
        "flat_crit_damage": ("crit_damage", "flat"),
        "multiplicative_fire_rate": ("fire_rate", "base"),
        "multiplicative_weakpoint_crit_chance": ("weakpoint_crit_chance", "base"),
    }
    stats: dict[str, object] = {}

    def add_effect(stat: str, value: float | int | bool, mode: str = "proportional"):
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
        stat, mode = mode_fields.get(field_name, (field_name, "proportional"))
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
            "runtime": {"rank": 0},
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
    _normalize_effect_modes_in_stats(entry.get("stats"))
    evolutions = entry.get("evolutions")
    if isinstance(evolutions, dict):
        for perks in evolutions.values():
            if not isinstance(perks, dict):
                continue
            for perk in perks.values():
                if isinstance(perk, dict):
                    _normalize_effect_modes_in_stats(perk.get("stats"))
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
    runtime = entry.get("runtime")
    if not isinstance(entry.get("stats", {}), dict):
        raise ValueError(f"{default_name} stats must be a JSON object.")
    if runtime is not None and not isinstance(runtime, dict):
        raise ValueError(f"{default_name} runtime must be a JSON object.")
    entry["runtime"] = {**dict(runtime or {}), "rank": int((runtime or {}).get("rank", entry.get("max_rank", 0)))}
    return Upgrade(entry)


def custom_enemy_from_entry(text: str, *, level: int | None = None, steel_path: bool | None = None, empowered: bool | None = None) -> Enemy:
    entry = parse_database_entry(text, default_name="Custom Enemy", default_type="enemy")
    entry.pop("type", None)
    for key in ("stats", "bodyparts", "modifiers"):
        if key in entry and not isinstance(entry[key], Mapping):
            raise ValueError(f"Custom Enemy {key} must be a JSON object.")
    runtime = entry.get("runtime")
    if runtime is not None and not isinstance(runtime, Mapping):
        raise ValueError("Custom Enemy runtime must be a JSON object.")
    entry["runtime"] = {"level": max(int(entry.get("base_level", 1)), 1), "steel_path": False, "empowered": False, **dict(runtime or {})}
    if level is not None:
        entry["runtime"]["level"] = level
    if steel_path is not None:
        entry["runtime"]["steel_path"] = steel_path
    if empowered is not None:
        entry["runtime"]["empowered"] = empowered
    enemy = Enemy(entry)
    pools = enemy.data.stats
    if max(float(pools.health), float(pools.shields), float(pools.overguard)) <= 0:
        raise ValueError("Custom Enemy must have nonzero health, shields, or overguard.")
    enemy.results.resolve()
    return enemy


def configured_enemy(enemy_name: str, *, custom_enemy: bool, custom_entry: str | None, level: int, steel_path: bool, empowered: bool) -> Enemy:
    if custom_enemy:
        if not custom_entry or not custom_entry.strip():
            raise ValueError("Custom Enemy JSON is required.")
        return custom_enemy_from_entry(custom_entry)
    if not enemy_name or enemy_name == "None":
        return Enemy()
    enemy = database_enemy(enemy_name, level=level, steel_path=steel_path, empowered=empowered)
    if enemy is None:
        raise LookupError(f"Could not load enemy: {enemy_name}")
    return enemy


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
    if item.data.stats:
        return True
    combos = getattr(item.data, "combos", None)
    if combos is not None and len(combos) > 0:
        return True
    return bool((item.data.compatibility or {}).get("stance"))


SPECIAL_STAT_LABELS = {
    "afflictions_proc_multiplier": "Proc Stack Multiplier",
    "cascadia_empowered_proc": "Damage per Status Proc",
    "crit_reset_charges": "Big Critical Hits Before Reset",
    "duplicated_hit": "Duplicate Hit Chance",
    "fire_rate_lock": "Fire Rate Locked",
    "hunter_munitions": "Slash Proc Chance on Critical Hit",
    "internal_bleeding": "Slash Proc Chance on Impact Proc",
    "melee_doughty": "Critical Damage / 10% Puncture Status Chance",
    "melee_duplicate": "Duplicate Hit Chance near Yellow Critical Tier",
    "multishot_lock": "Multishot Locked",
    "primed_chamber": "Damage on First Shot",
    "random_proc": "Random Status Effect Chance",
    "secondary_encumber": "Random Status Effect Chance on Status Proc",
    "secondary_enervate": "Big Critical Hits Before Reset",
    "slash_proc": "Slash Proc Chance",
    "vigilante_bonus": "Critical Tier Upgrade Chance",
}


def stat_label(field_name: str) -> str:
    return SPECIAL_STAT_LABELS.get(field_name, field_label(field_name))


def condition_label(condition: object) -> str:
    text = " ".join(str(condition).replace("_", " ").replace("-", " ").split())
    if text.casefold().startswith("on "):
        text = text[3:]
    return text.title()


def behavior_stat_label(field_name: str, behavior: str, behavior_data: Mapping[str, object]) -> str:
    base = stat_label(field_name)
    if behavior == "WEAPON_COMBO":
        return f"{base} / Combo Multiplier"
    if behavior == "FIRST_SHOT":
        return f"{base} on First Shot"
    if behavior == "LAST_SHOT":
        return f"{base} on Last Shot"
    if behavior == "DOUBLE_FOR_BOWS":
        return f"{base} (Doubled for Bows)"
    if behavior == "UNIQUE_STATUS":
        return f"{base} / Unique Status Type"
    if behavior == "ON_NON_CRIT":
        return f"{base} on Non-Critical Hit"
    if behavior == "ON_IMPACT_DOUBLE_BELOW_2_5_FR":
        threshold = behavior_data.get("fire_rate_threshold", 2.5)
        return f"{base} on Impact Proc (Doubled below {float(threshold):g} Fire Rate)"
    if behavior == "ON_CRIT":
        return f"{base} on Critical Hit"
    if behavior == "ON_HIT":
        return "Critical Tier Upgrade Chance on Hit" if field_name == "crit_chance" else f"{base} on Hit"
    if behavior == "ON_ANY_PROC":
        return "Random Status Effect Chance on Status Proc"
    if behavior == "NEAR_YELLOW":
        return "Duplicate Hit Chance near Yellow Critical Tier"
    if behavior == "FROM_PUNCTURE_X_STATUS":
        per = float(behavior_data.get("per", 0.1))
        return f"{base} / {per:.0%} Puncture Status Chance"
    if behavior == "STACK_RESET_CRIT_2_PLUS":
        return "Big Critical Hits Before Critical Chance Reset"
    if behavior == "STATUS_PROC_STACKS":
        status = condition_label(behavior_data.get("status", "Status"))
        return f"{base} / {status} Proc"
    if behavior == "MULTISHOT_CONSUMES_AMMO":
        return f"{base} (Consumes Ammo)"
    return base


def format_stat_value(
    value: object,
    *,
    field_name: str | None = None,
) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, str):
        return condition_label(value)
    if isinstance(value, Mapping):
        return ", ".join(f"{condition_label(key)}: {item}" for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return ", ".join(map(str, value))

    if field_name in {"crit_reset_charges", "secondary_enervate"}:
        return f"{int(float(value))} hits"

    flat_units = {
        "cascadia_empowered_proc": "",
        "combo_duration": "s",
        "explosion_radius": "m",
        "initial_combo": "",
        "punch_through": "m",
        "range": "m",
    }
    if field_name in flat_units:
        unit = flat_units[field_name]
        formatted = f"{float(value):,.3f}".rstrip("0").rstrip(".")
        return f"{formatted} {unit}".rstrip()

    if field_name in {"afflictions_proc_multiplier", "overguard_damage_multiplier"}:
        return f"{float(value):g}x"

    return f"{float(value):,.1%}"


def upgrade_stat_rows(
    upgrade: Upgrade,
    extra_stats: Mapping[str, object] | None = None,
) -> list[DisplayRow]:
    rows: list[DisplayRow] = []

    def add_stat(field_name: str, value, label: str | None = None) -> None:
        if field_name == "damage" and isinstance(value, (Dist, Mapping)):
            for damage_type, damage_value in Dist(value):
                if damage_value != 0:
                    damage_label = stat_label(damage_type)
                    if label and label != stat_label(field_name):
                        suffix = label.removeprefix(stat_label(field_name))
                        damage_label = f"{damage_label}{suffix}" if suffix else damage_label
                    rows.append(DisplayRow(damage_label, format_stat_value(damage_value, field_name=damage_type)))
            return
        if value != 0 and value is not False:
            rows.append(DisplayRow(label or stat_label(field_name), format_stat_value(value, field_name=field_name)))

    def add_effect(field_name: str, raw_effect: object) -> None:
        if not isinstance(raw_effect, Mapping) or "value" not in raw_effect:
            add_stat(field_name, raw_effect)
            return
        value = raw_effect["value"]
        behavior = str(raw_effect.get("behavior") or "")
        behavior_data = raw_effect.get("behavior_data")
        behavior_data = behavior_data if isinstance(behavior_data, Mapping) else {}
        label = behavior_stat_label(field_name, behavior, behavior_data) if behavior else stat_label(field_name)
        mode = normalize_effect_mode(raw_effect.get("mode"))
        if mode != "proportional":
            label += f" ({field_label(mode)})"
        required_rank = raw_effect.get("rank")
        if required_rank is not None:
            label += f" at Rank {required_rank}"
        stacks = raw_effect.get("stacks")
        condition = raw_effect.get("when")
        if isinstance(stacks, Mapping):
            label += f" / {condition_label(stacks.get('when', 'stacks'))}"
        elif condition:
            label += f" on {condition_label(condition)}"
        required_upgrade = raw_effect.get("equipped")
        if required_upgrade:
            required_names = required_upgrade if isinstance(required_upgrade, list) else [required_upgrade]
            label += f" with {', '.join(map(str, required_names))}"
        add_stat(field_name, value, label)

    existing_fields = set()
    for field_name, effects in upgrade.data.stats.items():
        existing_fields.add(field_name)
        for raw_effect in effects if isinstance(effects, list) else [effects]:
            add_effect(field_name, raw_effect)
    for field_name, effects in (extra_stats or {}).items():
        if field_name not in existing_fields:
            for raw_effect in effects if isinstance(effects, list) else [effects]:
                add_effect(field_name, raw_effect)
    return rows

def progenitor_upgrade(element: str, value: float, no_effect: str) -> Upgrade:
    if element == no_effect or value <= 0:
        return Upgrade({"name": "Progenitor", "type": "progenitor", "stats": {}, "runtime": {"rank": 0}})
    return Upgrade(
        {
            "name": "Progenitor",
            "type": "progenitor",
            "stats": {element: [{"value": value, "mode": "proportional"}]},
            "runtime": {"rank": 0},
        }
    )


def stance_combo_rows(combos: Mapping[str, object] | None) -> list[DisplayRow]:
    rows: list[DisplayRow] = []
    for key, raw in (combos or {}).items():
        combo = raw if isinstance(raw, Mapping) else {}
        name = str(combo.get("name") or key.replace("_", " ").title())
        multiplier = float(combo.get("multiplier") or 1.0)
        hits = float(combo.get("hits") or 0.0)
        duration = float(combo.get("duration") or 0.0)
        detail = f"x{multiplier:g} · {hits:g} hits"
        if duration > 0:
            detail = f"{detail} / {duration:g}s"
        rows.append(DisplayRow(name, detail))
    return rows


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
    stance_combo: str | None = None,
    ability_strength: float | None = None,
    target: Enemy | None = None,
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

    context: dict[str, object] = {}
    if selected_mode:
        wanted = "_".join(selected_mode.casefold().replace("-", " ").split())
        context["attack"] = next(
            (
                name
                for name in weapon.data.attacks
                if "_".join(name.casefold().replace("-", " ").split()) == wanted
            ),
            selected_mode,
        )
    if evolutions:
        context["evolutions"] = evolutions
    if stance_combo:
        context["stance_combo"] = stance_combo
    if ability_strength is not None:
        context["ability_strength"] = float(ability_strength)
    weapon.configure(Build(*upgrades), target=target)
    if context:
        weapon.set(context)
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
    target: Enemy | None = None,
) -> list[tuple[Upgrade, float]]:
    if not upgrades:
        return []

    weapon_type = WEAPON_TYPES[weapon_type_name]
    payload = weapon_payload(weapon_type_name, base_stats)
    full_weapon = weapon_type(payload)
    full_weapon.configure(Build(*upgrades), target=target)
    total_dps = full_weapon.results.main.final.total_dps
    contributions: list[tuple[Upgrade, float]] = []

    for index, upgrade in enumerate(upgrades):
        remaining = [item for other_index, item in enumerate(upgrades) if other_index != index]
        comparison_weapon = weapon_type(payload)
        if remaining:
            comparison_weapon.configure(Build(*remaining), target=target)
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
        "shapley_contributions",
        "contribution_proportions",
        "upgrade_contribution_proportions",
        "contributions_proportions",
    ):
        try:
            value = getattr(weapon.results, attribute_name)
            return contribution_items(value() if callable(value) else value)
        except (AttributeError, TypeError):
            pass

    try:
        removal = getattr(weapon.results, "removal_contributions")
        items = contribution_items(removal() if callable(removal) else removal)
        total = sum(value for _, value in items) or 1.0
        return [(key, value / total) for key, value in items]
    except (AttributeError, TypeError):
        pass

    if base_stats is None:
        return []
    return compute_contribution_proportions(weapon_type_name, base_stats, upgrades, target=weapon.target)


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


def resistant_metrics(weapon) -> list[MetricRow]:
    average = weapon.results.main.final
    return [
        MetricRow("Flat Resistant DPH", f"{average.flat_resistant_dph:,.2f}"),
        MetricRow("Flat Resistant DOTPH", f"{average.flat_resistant_dotph:,.2f}"),
        MetricRow("Total Resistant DPH", f"{average.total_resistant_dph:,.2f}"),
        MetricRow("Flat Resistant DPS", f"{average.flat_resistant_dps:,.2f}"),
        MetricRow("Flat Resistant DOTPS", f"{average.flat_resistant_dotps:,.2f}"),
        MetricRow("Total Resistant DPS", f"{average.total_resistant_dps:,.2f}"),
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
