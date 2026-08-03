from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Iterable

from warframe_damage_calculator import Arcane, Build, Calculator, Dist, Effect, Enemy, Formatter, Mod, Progenitor, State, Upgrade, UpgradeStats
from warframe_damage_calculator.domain.attacks import match_related_keys

from .constants import INITIAL_COMBO_RUNTIME, UPGRADE_BOOL_FIELDS, WEAPON_TYPES
from .data import database_enemy, database_weapon
from .models import ContributionRow, DamageResultRow, DisplayRow, MetricRow, SummaryTableRow


FIELD_LABEL_OVERRIDES = {
    "base_damage": "Damage",
    "crit_chance": "Critical Chance",
    "crit_damage": "Critical Damage",
    "slide_crit_chance": "Critical Chance on Slide Attack",
}


def field_label(field_name: str) -> str:
    if field_name in FIELD_LABEL_OVERRIDES:
        return FIELD_LABEL_OVERRIDES[field_name]
    return field_name.replace("_", " ").title().replace("Crit ", "Critical ")


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


def build_calculation_state(*, combo: int | str | None = None, stance_combo: str | None = None, ability_strength: float | None = None) -> State:
    kwargs: dict[str, object] = {}
    if combo is not None and combo != INITIAL_COMBO_RUNTIME:
        kwargs["combo_multiplier"] = int(combo)
    if stance_combo:
        kwargs["stance_combo"] = stance_combo
    if ability_strength is not None:
        kwargs["ability_strength"] = float(ability_strength)
    return State(**kwargs)


def apply_loadout_runtime(build: Build, runtime: Mapping[str, object] | None) -> Build:
    if not runtime:
        return build
    consumable: set[str] = set()
    for upgrade in build.ranked_upgrades:
        consumable |= {"rank"} | set(upgrade.stats.manual_fields)
    for perk in build.evolutions:
        consumable |= set(perk.stats.manual_fields)
    accepted = {key: value for key, value in runtime.items() if key in consumable}
    if accepted:
        build.set(**accepted)
    return build


def weapon_combo_rules(weapon) -> tuple[int, int]:
    """Return the weapon-specific hits-per-tier interval and maximum combo multiplier."""
    data = weapon.data
    combo_interval = parse_int(
        getattr(data, "combo_interval", getattr(data, "combo_hit_interval", 20)),
        20,
    )
    max_combo = parse_int(
        getattr(data, "max_combo", getattr(data, "max_combo_multiplier", 12)),
        12,
    )
    return max(1, combo_interval), max(1, max_combo)


def combo_multiplier_from_initial_combo(value: object, weapon) -> int:
    combo_interval, max_combo = weapon_combo_rules(weapon)
    return max(1, min(max_combo, parse_int(value) // combo_interval + 1))


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
        "multiplicative_weak_point_crit_chance": ("weak_point_crit_chance", "base"),
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

    for field_name, value in values.items():
        if field_name in UPGRADE_BOOL_FIELDS:
            continue
        if field_name == "secondary_enervate":
            value = int(value)
        stat, mode = mode_fields.get(field_name, (field_name, "proportional"))
        add_effect(stat, value, mode)
    for field_name in UPGRADE_BOOL_FIELDS:
        add_effect(field_name, bool(values.get(field_name, False)))
    resolved_stats = {}
    for stat, effects in stats.items():
        resolved_stats[stat] = tuple(Effect.from_record(effect) if isinstance(effect, Mapping) else Effect(effect) for effect in effects)
    return Mod(name=name, stats=UpgradeStats(**resolved_stats))


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
    runtime_values = {**dict(runtime or {}), "rank": int((runtime or {}).get("rank", entry.get("max_rank", 0)))}
    kind = str(entry.pop("type", default_type)).casefold()
    entry.pop("runtime", None)
    cls = Arcane if kind == "arcane" else Mod
    upgrade = cls.from_record(entry)
    allowed_runtime = {key: value for key, value in runtime_values.items() if key == "rank" or key in upgrade.stats.manual_fields}
    upgrade.set(**allowed_runtime)
    return upgrade


def configured_enemy(enemy_name: str, *, level: int, steel_path: bool, empowered: bool) -> Enemy:
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
    combo_interval = stats.pop("combo_interval", stats.pop("combo_hit_interval", 20))
    max_combo = stats.pop("max_combo", stats.pop("max_combo_multiplier", 12))
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
        "combo_interval": combo_interval,
        "max_combo": max_combo,
        "ammo": ammo,
        "attacks": attacks,
    }


def is_non_empty_upgrade(item: Upgrade) -> bool:
    if item.stats:
        return True
    combos = getattr(item, "combos", None)
    if combos is not None and len(combos) > 0:
        return True
    return getattr(item, "slot", None) == "stance_mod"


SPECIAL_STAT_LABELS = {
    "afflictions_proc_multiplier": "Proc Stack Multiplier",
    "cascadia_empowered_proc": "Damage per Status Proc",
    "crit_reset_charges": "Big Critical Hits Before Reset",
    "crit_tier": "Crit Chance",
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
    if behavior in {"STATUS_EFFECT_STACKS", "STATUS_PROC_STACKS"}:
        status = condition_label(behavior_data.get("status", "Status"))
        return f"{base} / {status} Proc"
    if behavior == "MULTISHOT_CONSUMES_AMMO":
        return f"{base} (Consumes Ammo)"
    return base


def _effect_condition(value: object) -> str:
    values = value if isinstance(value, list) else [value]
    return " and ".join(condition_label(item) for item in values)


def effect_context_label(label: str, effect: Mapping[str, object]) -> str:
    automatic = effect.get("automatic")
    automatic = automatic if isinstance(automatic, Mapping) else {}
    on_conditions: list[str] = []
    per_conditions: list[str] = []
    qualifiers: list[str] = []
    stacks = automatic.get("stacks", effect.get("stacks"))
    if effect.get("when") is not None:
        (per_conditions if stacks is not None else on_conditions).append(_effect_condition(effect["when"]))
    if automatic.get("on") is not None:
        on_conditions.append(_effect_condition(automatic["on"]))
    if automatic.get("when") is not None:
        (per_conditions if stacks is not None else on_conditions).append(_effect_condition(automatic["when"]))
    if automatic.get("with") is not None:
        per = automatic.get("per")
        scale = f"{float(per):.0%} " if isinstance(per, (int, float)) and not isinstance(per, bool) else ""
        per_conditions.append(f"{scale}{_effect_condition(automatic['with'])}")
    if automatic.get("equipped") is not None:
        on_conditions.append(f"{_effect_condition(automatic['equipped'])} Equipped")
    chance = automatic.get("chance")
    if isinstance(chance, (int, float)) and not isinstance(chance, bool):
        qualifiers.append(f"{float(chance):.0%} trigger chance")
    multiply = automatic.get("multiply")
    if isinstance(multiply, (int, float)) and not isinstance(multiply, bool):
        qualifiers.append(f"{float(multiply):g}x multiplier")
    if automatic.get("reset") is not None:
        reset = _effect_condition(automatic["reset"])
        qualifiers.append(f"resets at {reset.removeprefix('At ')}")
    if automatic.get("per") is not None and automatic.get("with") is None:
        per = automatic["per"]
        qualifiers.append(f"per {float(per):.0%}" if isinstance(per, (int, float)) and not isinstance(per, bool) else f"per {_effect_condition(per)}")
    clauses = [*(f"per {condition}" for condition in per_conditions)]
    if on_conditions:
        clauses.append(f"on {' and '.join(on_conditions)}")
    contextual = " ".join([label, *clauses])
    return f"{contextual} ({', '.join(qualifiers)})" if qualifiers else contextual


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


def upgrade_description_rows(upgrade: Upgrade, *, fallback_description: str | None = None) -> list[DisplayRow]:
    text = str(getattr(upgrade, "description", "") or fallback_description or "").strip()
    if not text:
        return []
    text = text.replace("\\n", "\n")
    parts = [part.strip() for part in re.split(r"[\r\n]+", text) if part.strip()]
    return [DisplayRow(part, "") for part in parts] if parts else [DisplayRow(text, "")]


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
        if isinstance(raw_effect, Effect):
            raw_effect = raw_effect.to_record()
        if not isinstance(raw_effect, Mapping) or "value" not in raw_effect:
            add_stat(field_name, raw_effect)
            return
        value = raw_effect["value"]
        behavior = str(raw_effect.get("behavior") or "")
        behavior_data = raw_effect.get("behavior_data")
        behavior_data = behavior_data if isinstance(behavior_data, Mapping) else {}
        label = behavior_stat_label(field_name, behavior, behavior_data) if behavior else stat_label(field_name)
        mode = normalize_effect_mode(raw_effect.get("mode"))
        if mode != "proportional" and field_name != "crit_tier":
            label += f" ({field_label(mode)})"
        required_rank = raw_effect.get("rank")
        if required_rank is not None:
            label += f" at Rank {required_rank}"
        label = effect_context_label(label, raw_effect)
        required_upgrade = raw_effect.get("equipped")
        if required_upgrade:
            required_names = required_upgrade if isinstance(required_upgrade, list) else [required_upgrade]
            label += f" with {', '.join(map(str, required_names))}"
        add_stat(field_name, value, label)

    existing_fields = set()
    for field_name, effects in upgrade.stats.items():
        existing_fields.add(field_name)
        for raw_effect in effects if isinstance(effects, (list, tuple)) else [effects]:
            add_effect(field_name, raw_effect)
    for field_name, effects in (extra_stats or {}).items():
        if field_name not in existing_fields:
            for raw_effect in effects if isinstance(effects, (list, tuple)) else [effects]:
                add_effect(field_name, raw_effect)
    return rows

def progenitor_upgrade(element: str, value: float, no_effect: str) -> Upgrade:
    if element == no_effect or value <= 0:
        return Upgrade(name="Progenitor")
    return Upgrade(name="Progenitor", stats=UpgradeStats(**{element: Effect(value)}))


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
    upgrades: list[Upgrade],
    selected_mode: str | None = None,
    evolutions: dict[int, int] | None = None,
    combo: int | str | None = None,
    runtime_conditions: Mapping[str, object] | None = None,
    stance_combo: str | None = None,
    ability_strength: float | None = None,
    target: Enemy | None = None,
    progenitor: Progenitor | None = None,
):
    weapon = database_weapon(selected_weapon_name, weapon_type_name)
    if weapon is None:
        raise LookupError(f"Could not load weapon: {selected_weapon_name}")

    attack = None
    if selected_mode:
        wanted = "_".join(selected_mode.casefold().replace("-", " ").split())
        attack = next((name for name in weapon.attacks if "_".join(name.casefold().replace("-", " ").split()) == wanted), None)
    perks = []
    for tier, choice in (evolutions or {}).items():
        if tier in weapon.perk_choices and choice in weapon.perk_choices[tier]:
            perks.append(weapon.perk_choices[tier][choice])
    mods = [upgrade for upgrade in upgrades if isinstance(upgrade, Mod)]
    arcanes = [upgrade for upgrade in upgrades if isinstance(upgrade, Arcane)]
    build = Build(mods=mods, arcanes=arcanes, evolutions=perks, progenitor=progenitor)
    apply_loadout_runtime(build, runtime_conditions)
    calculator = Calculator(weapon, target, build)
    body_part = next(iter(target.body_parts), None) if target is not None and target.body_parts else None
    result = calculator.resolve(attack=attack, body_part=body_part, state=build_calculation_state(combo=combo, stance_combo=stance_combo, ability_strength=ability_strength))
    return calculator, result

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
    items = contribution_lookup if isinstance(contribution_lookup, list) else contribution_items(contribution_lookup)
    direct = [value for key, value in items if contribution_key_name(key) == name]
    if direct:
        return sum(direct)
    prefix = f"{name} (slot "
    slotted = [value for key, value in items if contribution_key_name(key).startswith(prefix)]
    return sum(slotted) if slotted else None


def contribution_lookup_map(contribution_lookup) -> dict[str, float]:
    totals: dict[str, float] = {}
    for key, value in contribution_items(contribution_lookup):
        name = contribution_key_name(key)
        totals[name] = totals.get(name, 0.0) + float(value)
    return totals


def contribution_value_for_name(contribution_map: Mapping[str, float], name: str) -> float | None:
    if name in contribution_map:
        return contribution_map[name]
    prefix = f"{name} (slot "
    slotted = [value for key, value in contribution_map.items() if key.startswith(prefix)]
    return sum(slotted) if slotted else None


def compute_contribution_proportions(
    weapon_type_name: str,
    base_stats: dict,
    upgrades: list[Upgrade],
    target: Enemy | None = None,
    target_metric: str = "total_weak_point_dps",
) -> list[tuple[Upgrade, float]]:
    raise RuntimeError("compute_contribution_proportions is obsolete; use contribution_lookup_for_weapon with a library Calculator.resolve() result")


def _normalize_contribution_metric(target_metric: str) -> str:
    return target_metric.replace("total_weak_point_", "total_").replace("flat_weak_point_", "direct_").replace("total_resistant_", "total_").replace("flat_resistant_", "direct_").replace("flat_", "direct_")


def library_contribution_bundle(resolved, target_metric: str = "total_dps"):
    """Lookup rows from Calculator.contributions(); summary text from Formatter.build_summary()."""
    if not (isinstance(resolved, tuple) and len(resolved) == 2):
        return [], "", []
    _calculator, result = resolved
    if not result.build.upgrades and result.build.progenitor is None:
        return [], "", []
    metric = _normalize_contribution_metric(target_metric)
    contribution_result = Calculator(result.weapon, result.target, result.build).contributions(attack=result.selected_attack, metric=metric, body_part=result.selected_body_part, state=result.state)
    ordered = sorted(contribution_result.contribution.items(), key=lambda item: item[1], reverse=True)
    formatter = Formatter(result)
    table = formatter.build_summary_table(metric=metric, body_part=result.selected_body_part, contributions=contribution_result)
    text = "" if table is None else formatter._table(table[1], table[2], title=table[0])
    rows = [] if table is None else [ContributionRow(*row) for row in table[2]]
    return ordered, text, rows


def contribution_lookup_for_weapon(
    resolved,
    weapon_type_name: str,
    base_stats: dict | None,
    upgrades: list[Upgrade],
    target_metric: str = "total_dps",
):
    if isinstance(resolved, tuple) and len(resolved) == 2:
        lookup, _text, _rows = library_contribution_bundle(resolved, target_metric=target_metric)
        return lookup
    if not upgrades:
        return []
    removal = getattr(getattr(resolved, "results", None), "removal_contributions", None)
    if callable(removal):
        items = contribution_items(removal(target=target_metric))
        total = sum(value for _, value in items) or 1.0
        return [(key, value / total) for key, value in items]
    return []

def format_contribution(value: float | None) -> str:
    return "—" if value is None else f"{value:.1%}"


def contribution_rows(contribution_lookup) -> list[ContributionRow]:
    """Fallback name/share-only rows when full Formatter table data is unavailable."""
    items = sorted(contribution_items(contribution_lookup), key=lambda item: item[1], reverse=True)
    return [
        ContributionRow(str(rank), "", contribution_key_name(key), f"{value:+.2%}", "", "")
        for rank, (key, value) in enumerate(items, 1)
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


def main_metrics(resolved) -> list[MetricRow]:
    _calculator, result = resolved
    damage = result.aggregate.damage
    return [
        MetricRow("Direct DPH", f"{damage.direct_dph:,.2f}"),
        MetricRow("DoT DPH", f"{damage.dot_dph:,.2f}"),
        MetricRow("Total DPH", f"{damage.total_dph:,.2f}"),
        MetricRow("Direct DPS", f"{damage.direct_dps:,.2f}"),
        MetricRow("DoT DPS", f"{damage.dot_dps:,.2f}"),
        MetricRow("Total DPS", f"{damage.total_dps:,.2f}"),
    ]


def weak_point_metrics(resolved) -> list[MetricRow]:
    return []


def resistant_metrics(resolved) -> list[MetricRow]:
    return []


def ranged_misc_metrics(resolved) -> list[MetricRow]:
    _calculator, result = resolved
    selected = result.attacks[result.selected_attack]
    return [MetricRow("Average Fire Rate", f"{selected.timing.fire_rate:,.2f}"), MetricRow("Procs / Shot", f"{selected.status.status_chance:,.2f}")]


def _status_summary_cells(attack, damage_type: str) -> tuple[str, str, str, str]:
    if attack is None:
        return ("—", "—", "—", "—")
    damage = attack.effective.damage
    forced = attack.effective.forced_procs
    status_chance = float(attack.effective.status_chance)
    return (
        f"{damage.get(damage_type, 0.0):,.2f}",
        f"{damage.weight(damage_type):,.2f}",
        f"{forced.get(damage_type, 0.0):.1%}",
        f"{damage.weight(damage_type) * status_chance + forced.get(damage_type, 0.0):.1%}",
    )


def _related_explosion_attack(result):
    selected_definition = result.weapon.attacks.get(result.selected_attack)
    if selected_definition is None:
        return None
    children = selected_definition.links.children
    if children is None:
        return None
    for key in match_related_keys(children, result.weapon.attacks):
        child_definition = result.weapon.attacks.get(key)
        child = result.attacks.get(key)
        if child is not None and child_definition is not None and child_definition.aoe:
            return child
    return None


def effective_damage_rows(resolved, *, melee: bool = False) -> list[DamageResultRow]:
    _calculator, result = resolved
    primary = result.attacks[result.selected_attack]
    explosion = None if melee else _related_explosion_attack(result)
    damage_types = dict.fromkeys((*primary.effective.damage, *primary.effective.forced_procs, *(explosion.effective.damage if explosion is not None else ()), *(explosion.effective.forced_procs if explosion is not None else ())))
    rows = []
    for damage_type in damage_types:
        damage, weight, forced_procs, proc_rate = _status_summary_cells(primary, damage_type)
        explosion_damage, explosion_weight, explosion_forced_procs, explosion_proc_rate = _status_summary_cells(explosion, damage_type)
        rows.append(DamageResultRow(
            damage_type=damage_type.title(),
            damage=damage,
            weight=weight,
            forced_procs=forced_procs,
            proc_rate=proc_rate,
            explosion_damage=explosion_damage,
            explosion_weight=explosion_weight,
            explosion_forced_procs=explosion_forced_procs,
            explosion_proc_rate=explosion_proc_rate,
        ))
    return rows


def result_summary(resolved) -> str:
    return Formatter(resolved[1]).stat_summary()


def result_status_summary(resolved) -> str:
    return Formatter(resolved[1]).status_summary()


def result_summary_table_rows(resolved) -> list[SummaryTableRow]:
    _title, _headers, rows = Formatter(resolved[1]).stat_summary_table()
    output: list[SummaryTableRow] = []
    section_start = False
    for index, row in enumerate(rows):
        if row[0].startswith("\0"):
            section_start = index > 0
            continue
        output.append(SummaryTableRow(stat=row[0], base=row[1], modded=row[2], effective=row[3], average=row[4], section_start=section_start))
        section_start = False
    return output


def result_contributions_summary(resolved) -> str:
    return Formatter(resolved[1]).build_summary()