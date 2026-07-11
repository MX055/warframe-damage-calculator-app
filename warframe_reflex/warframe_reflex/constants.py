from __future__ import annotations

from warframe_damage_calculator import Melee, Primary, Secondary

WEAPON_TYPES = {
    "Melee": Melee,
    "Primary": Primary,
    "Secondary": Secondary,
}

WEAPON_TYPE_OPTIONS = list(WEAPON_TYPES)

DAMAGE_TYPES = (
    "impact",
    "puncture",
    "slash",
    "cold",
    "electricity",
    "heat",
    "toxin",
    "blast",
    "corrosive",
    "gas",
    "magnetic",
    "radiation",
    "viral",
    "void",
)

DEFAULT_DAMAGE_TYPES = ("impact", "puncture", "slash")
NO_EFFECT = "None"

PROGENITOR_ELEMENT_OPTIONS = (
    "impact",
    "cold",
    "electricity",
    "heat",
    "toxin",
    "magnetic",
    "radiation",
)

WEAPON_DATABASE_SECTIONS = {
    "Primary": "primaries",
    "Secondary": "secondaries",
    "Melee": "melees",
}

WEAPON_COMPATIBILITY_FAMILIES = {
    "Primary": {"primary", "bow", "rifle", "shotgun", "sniper"},
    "Secondary": {"secondary", "pistol"},
    "Melee": {"melee"},
}

MOD_FIELD: dict[str, tuple[float | int, ...] | None] = {
    "impact": (-1.39465125, 2.3011745625),
    "puncture": (-1.39465125, 2.3011745625),
    "slash": (-1.39465125, 2.3011745625),
    "cold": (0.0, 1.7263125),
    "electricity": (0.0, 1.7263125),
    "heat": (0.0, 1.7263125),
    "toxin": (0.0, 1.7263125),
    "blast": (0.0, 1.7263125),
    "corrosive": (0.0, 1.7263125),
    "gas": (0.0, 1.7263125),
    "magnetic": (0.0, 1.7263125),
    "radiation": (0.0, 1.7263125),
    "viral": (0.0, 1.7263125),
    "void": (0.0, 1.7263125),
    "base_damage": (-2.55285, 4.2122025),
    "multiplicative_base_damage": (0.0, 14.4),
    "faction_damage": (-0.523125, 0.86315625),
    "weakpoint_damage": (0.0, 3.5),
    "attack_speed": (-1.0357875, 1.70904937),
    "fire_rate": (-1.0357875, 1.70904937),
    "reload_speed": (-0.58125, 0.9590625),
    "magazine_capacity": (-0.58125, 0.9590625),
    "ammo_efficiency": (0.0, 1.0),
    "multishot": (-1.3915125, 2.29599563),
    "crit_chance": (-2.0925, 3.452625),
    "multiplicative_weakpoint_crit_chance": (0.0, 3.5),
    "weakpoint_crit_chance": (0.0, 3.5),
    "crit_damage": (-1.395, 2.30175),
    "status_chance": (-1.04625, 1.7263125),
    "status_damage": (0.0, 0.9),
    "hunter_munitions": (0.0, 0.3),
    "internal_bleeding": (0.0, 0.35),
    "primed_chamber": (0.0, 1.0),
    "vigilante_bonus": (0.0, 0.05),
}

ARCANE_FIELD: dict[str, tuple[float | int, ...] | None] = {
    "secondary_enervate": (0, 6),
    "secondary_encumber": (0.0, 0.24),
    "melee_duplicate": (0.0, 1.0),
    "melee_doughty": (0.0, 1.0),
    "base_damage": (0.0, 3.6),
    "reload_speed": (0.0, 0.3),
    "weakpoint_damage": (0.0, 0.3),
    "crit_damage": (0.0, 1.44),
    "multishot": (0.0, 0.9),
    "status_chance": (0.0, 3.0),
    "ammo_efficiency": (0.0, 0.6),
}

BUFF_FIELD: dict[str, tuple[float | int, ...] | None] = {
    "impact": (0.0, 9.0),
    "puncture": (0.0, 9.0),
    "slash": (0.0, 9.0),
    "cold": (0.0, 9.0),
    "electricity": (0.0, 9.0),
    "heat": (0.0, 9.0),
    "toxin": (0.0, 9.0),
    "blast": (0.0, 9.0),
    "corrosive": (0.0, 9.0),
    "gas": (0.0, 9.0),
    "magnetic": (0.0, 9.0),
    "radiation": (0.0, 9.0),
    "viral": (0.0, 9.0),
    "void": (0.0, 9.0),
    "base_damage": (0.0, 9.0),
    "multiplicative_base_damage": (0.0, 9.0),
    "faction_damage": (0.0, 9.0),
    "weakpoint_damage": (0.0, 9.0),
    "attack_speed": (0.0, 9.0),
    "multiplicative_fire_rate": (0.0, 9.0),
    "fire_rate": (0.0, 9.0),
    "reload_speed": (0.0, 9.0),
    "magazine_capacity": (0.0, 9.0),
    "ammo_efficiency": (0.0, 1.0),
    "multishot": (0.0, 9.0),
    "flat_crit_chance": (0.0, 9.0),
    "multiplicative_crit_chance": (0.0, 9.0),
    "crit_chance": (0.0, 9.0),
    "multiplicative_weakpoint_crit_chance": (0.0, 9.0),
    "weakpoint_crit_chance": (0.0, 9.0),
    "flat_crit_damage": (0.0, 9.0),
    "crit_damage": (0.0, 9.0),
    "status_chance": (0.0, 9.0),
    "status_damage": (0.0, 9.0),
    "vigilante_bonus": (0.0, 9.0),
}

FIELD_WEAPON_RULES = {
    "ammo_efficiency": {"Primary", "Secondary"},
    "burst_count": {"Primary", "Secondary"},
    "burst_delay": {"Primary", "Secondary"},
    "charge_time": {"Primary", "Secondary"},
    "fire_rate": {"Primary", "Secondary"},
    "magazine_capacity": {"Primary", "Secondary"},
    "reload_speed": {"Primary", "Secondary"},
    "weakpoint_damage": {"Primary", "Secondary"},
    "multiplicative_fire_rate": {"Primary", "Secondary"},
    "multiplicative_weakpoint_crit_chance": {"Primary", "Secondary"},
    "weakpoint_crit_chance": {"Primary", "Secondary"},
    "is_beam": {"Primary", "Secondary"},
    "is_battery": {"Primary", "Secondary"},
    "attack_speed": {"Melee"},
    "melee_duplicate": {"Melee"},
    "melee_doughty": {"Melee"},
    "secondary_enervate": {"Secondary"},
    "secondary_encumber": {"Secondary"},
}

UPGRADE_SCALAR_FIELDS = (
    "base_damage",
    "faction_damage",
    "crit_chance",
    "crit_damage",
    "status_chance",
    "status_damage",
    "weakpoint_damage",
    "reload_speed",
    "fire_rate",
    "multishot",
    "attack_speed",
    "hunter_munitions",
    "internal_bleeding",
    "primed_chamber",
    "vigilante_bonus",
    "multiplicative_base_damage",
    "multiplicative_fire_rate",
    "flat_crit_chance",
    "multiplicative_crit_chance",
    "weakpoint_crit_chance",
    "multiplicative_weakpoint_crit_chance",
    "flat_crit_damage",
    "ammo_efficiency",
    "magazine_capacity",
    "secondary_enervate",
    "secondary_encumber",
    "melee_duplicate",
    "melee_doughty",
)

UPGRADE_BOOL_FIELDS = (
    "fire_rate_lock",
    "multishot_lock",
)

# The order matches the original Streamlit 5 x 2 grid.
SLOT_CONFIGS = (
    {"label": "Mod 1", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 2", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 3", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 4", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Arcane", "kind": "arcane", "exilus": False, "options": ARCANE_FIELD},
    {"label": "Mod 5", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 6", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 7", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Mod 8", "kind": "mod", "exilus": False, "options": MOD_FIELD},
    {"label": "Exilus", "kind": "mod", "exilus": True, "options": MOD_FIELD},
)
