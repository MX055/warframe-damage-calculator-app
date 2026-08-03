from __future__ import annotations

from warframe_damage_calculator import Melee, Primary, Secondary

WEAPON_TYPES = {
    "Melee": Melee,
    "Primary": Primary,
    "Secondary": Secondary,
}

WEAPON_CATEGORY_TYPES = {
    "Rifle": "Primary",
    "Shotgun": "Primary",
    "Bow": "Primary",
    "Sniper": "Primary",
    "Pistol": "Secondary",
    "Melee": "Melee",
}

WEAPON_TYPE_OPTIONS = list(WEAPON_CATEGORY_TYPES)
INITIAL_COMBO_OPTION = "Initial Combo"
INITIAL_COMBO_RUNTIME = "initial_combo"
MELEE_COMBO_OPTIONS = (INITIAL_COMBO_OPTION, *(f"{value}x" for value in range(13)))

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
    "tau",
    "true",
)

DEFAULT_DAMAGE_TYPES = ("impact", "puncture", "slash")
NO_EFFECT = "None"

SLOT_POLICY_DISCARD = "discard"
SLOT_POLICY_KEEP = "keep"
SLOT_POLICY_OPTIONS = (SLOT_POLICY_DISCARD, SLOT_POLICY_KEEP)

RIVEN_ROLL_CONFIGS = {
    "2 Positive": (2, 0, 0.99, 0.0),
    "2 Positive + 1 Negative": (2, 1, 1.2375, -0.495),
    "3 Positive": (3, 0, 0.75, 0.0),
    "3 Positive + 1 Negative": (3, 1, 0.9375, -0.75),
}

RIVEN_ROLL_OPTIONS = tuple(RIVEN_ROLL_CONFIGS)

# These are the Riven attributes that affect calculations exposed by this app.
# The database uses ``damage_bonus`` while the legacy field editor calls it
# ``base_damage``.
RIVEN_STAT_ALIASES = {
    "damage_bonus": "base_damage",
}

RIVEN_NON_NEGATIVE_STATS = {
    "cold",
    "electricity",
    "heat",
    "punch_through",
    "toxin",
}

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
    "Primary": "primary",
    "Secondary": "secondary",
    "Melee": "melee",
}

WEAPON_COMPATIBILITY_FAMILIES = {
    category: {weapon_type.casefold(), category.casefold()}
    for category, weapon_type in WEAPON_CATEGORY_TYPES.items()
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
    "corpus_damage": (-0.523125, 0.86315625),
    "grineer_damage": (-0.523125, 0.86315625),
    "infested_damage": (-0.523125, 0.86315625),
    "orokin_damage": (-0.523125, 0.86315625),
    "murmur_damage": (-0.523125, 0.86315625),
    "sentient_damage": (-0.523125, 0.86315625),
    "weak_point_damage": (0.0, 3.5),
    "attack_speed": (-1.0357875, 1.70904937),
    "fire_rate": (-1.0357875, 1.70904937),
    "reload_speed": (-0.58125, 0.9590625),
    "magazine_capacity": (-0.58125, 0.9590625),
    "ammo_efficiency": (0.0, 1.0),
    "multishot": (-1.3915125, 2.29599563),
    "crit_chance": (-2.0925, 3.452625),
    "slide_crit_chance": (-1.674, 2.763),
    "multiplicative_weak_point_crit_chance": (0.0, 3.5),
    "weak_point_crit_chance": (0.0, 3.5),
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
    "weak_point_damage": (0.0, 0.3),
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
    "corpus_damage": (0.0, 9.0),
    "grineer_damage": (0.0, 9.0),
    "infested_damage": (0.0, 9.0),
    "orokin_damage": (0.0, 9.0),
    "murmur_damage": (0.0, 9.0),
    "sentient_damage": (0.0, 9.0),
    "weak_point_damage": (0.0, 9.0),
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
    "slide_crit_chance": (0.0, 9.0),
    "multiplicative_weak_point_crit_chance": (0.0, 9.0),
    "weak_point_crit_chance": (0.0, 9.0),
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
    "weak_point_damage": {"Primary", "Secondary"},
    "multiplicative_fire_rate": {"Primary", "Secondary"},
    "multiplicative_weak_point_crit_chance": {"Primary", "Secondary"},
    "weak_point_crit_chance": {"Primary", "Secondary"},
    "is_beam": {"Primary", "Secondary"},
    "is_battery": {"Primary", "Secondary"},
    "attack_speed": {"Melee"},
    "slide_crit_chance": {"Melee"},
    "melee_duplicate": {"Melee"},
    "melee_doughty": {"Melee"},
    "secondary_enervate": {"Secondary"},
    "secondary_encumber": {"Secondary"},
}

UPGRADE_SCALAR_FIELDS = (
    "base_damage",
    "corpus_damage",
    "grineer_damage",
    "infested_damage",
    "orokin_damage",
    "murmur_damage",
    "sentient_damage",
    "crit_chance",
    "slide_crit_chance",
    "crit_damage",
    "status_chance",
    "status_damage",
    "weak_point_damage",
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
    "weak_point_crit_chance",
    "multiplicative_weak_point_crit_chance",
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

# Build order: stance (melee), mods 1-8, exilus, arcane. Layout is separate.
SLOT_CONFIGS = (
    {"label": "Stance", "kind": "mod", "exilus": False, "stance": True, "options": MOD_FIELD},
    {"label": "Mod 1", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 2", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 3", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 4", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 5", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 6", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 7", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Mod 8", "kind": "mod", "exilus": False, "stance": False, "options": MOD_FIELD},
    {"label": "Exilus", "kind": "mod", "exilus": True, "stance": False, "options": MOD_FIELD},
    {"label": "Arcane", "kind": "arcane", "exilus": False, "stance": False, "options": ARCANE_FIELD},
)
STANCE_SLOT_INDEX = 0
MOD_SLOT_INDICES = tuple(index for index, config in enumerate(SLOT_CONFIGS) if config["kind"] == "mod" and not config["exilus"] and not config["stance"])
EXILUS_SLOT_INDEX = next(index for index, config in enumerate(SLOT_CONFIGS) if config["exilus"])
ARCANE_SLOT_INDEX = next(index for index, config in enumerate(SLOT_CONFIGS) if config["kind"] == "arcane")
OPTIMIZER_SLOT_ORDER = (STANCE_SLOT_INDEX, *MOD_SLOT_INDICES, EXILUS_SLOT_INDEX, ARCANE_SLOT_INDEX)

# Labels match result metric cards; values are AverageStats attributes or synthetic optimizer scores.
OPTIMIZE_MAXIMIZE_TARGETS = {
    "Balanced (DPS · DPH)": "balanced_total_dps_dph",
    "Total DPS": "total_dps",
    "Flat DPS": "flat_dps",
    "Flat DOTPS": "flat_dotps",
    "Total DPH": "total_dph",
    "Flat DPH": "flat_dph",
    "Flat DOTPH": "flat_dotph",
    "Total Weak Point DPS": "total_weak_point_dps",
    "Flat Weak Point DPS": "flat_weak_point_dps",
    "Flat Weak Point DOTPS": "flat_weak_point_dotps",
    "Total Weak Point DPH": "total_weak_point_dph",
    "Flat Weak Point DPH": "flat_weak_point_dph",
    "Flat Weak Point DOTPH": "flat_weak_point_dotph",
    "Total Resistant DPS": "total_resistant_dps",
    "Flat Resistant DPS": "flat_resistant_dps",
    "Flat Resistant DOTPS": "flat_resistant_dotps",
    "Total Resistant DPH": "total_resistant_dph",
    "Flat Resistant DPH": "flat_resistant_dph",
    "Flat Resistant DOTPH": "flat_resistant_dotph",
}
OPTIMIZE_MAXIMIZE_OPTIONS = tuple(OPTIMIZE_MAXIMIZE_TARGETS)
DEFAULT_OPTIMIZE_MAXIMIZE = "Balanced (DPS · DPH)"
DEFAULT_OPTIMIZE_DPH_WEIGHT = 50
DEFAULT_OPTIMIZE_FLAT_DOT_WEIGHT = 50
OPTIMIZE_SPATIAL_AUTO = "Auto"
OPTIMIZE_SPATIAL_AOE = "AoE"
OPTIMIZE_SPATIAL_SINGLE = "Single-target"
OPTIMIZE_SPATIAL_OPTIONS = (OPTIMIZE_SPATIAL_AUTO, OPTIMIZE_SPATIAL_AOE, OPTIMIZE_SPATIAL_SINGLE)
DEFAULT_OPTIMIZE_SPATIAL = OPTIMIZE_SPATIAL_AUTO
OPTIMIZE_SPATIAL_MODES = {
    OPTIMIZE_SPATIAL_AUTO: "auto",
    OPTIMIZE_SPATIAL_AOE: "full",
    OPTIMIZE_SPATIAL_SINGLE: "none",
}
BALANCED_MAXIMIZE_TARGETS = {
    "balanced_total_dps_dph": ("total_dps", "total_dph"),
}
OPTIMIZE_SEARCH_LOW = "Low"
OPTIMIZE_SEARCH_MEDIUM = "Medium"
OPTIMIZE_SEARCH_HIGH = "High"
OPTIMIZE_SEARCH_MAX = "Max"
OPTIMIZE_SEARCH_OPTIONS = (OPTIMIZE_SEARCH_LOW, OPTIMIZE_SEARCH_MEDIUM, OPTIMIZE_SEARCH_HIGH, OPTIMIZE_SEARCH_MAX)
DEFAULT_OPTIMIZE_SEARCH = OPTIMIZE_SEARCH_MEDIUM
OPTIMIZE_SEARCH_EVALUATION_BUDGETS = {
    OPTIMIZE_SEARCH_LOW: 5_000,
    OPTIMIZE_SEARCH_MEDIUM: 10_000,
    OPTIMIZE_SEARCH_HIGH: 20_000,
    OPTIMIZE_SEARCH_MAX: 100_000,
}
