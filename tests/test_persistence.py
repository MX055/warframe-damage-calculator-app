from warframe_reflex.constants import DEFAULT_OPTIMIZE_SPATIAL, OPTIMIZE_SPATIAL_AOE, OPTIMIZE_SPATIAL_AUTO, OPTIMIZE_SPATIAL_SINGLE, SLOT_CONFIGS, SLOT_POLICY_DISCARD
from warframe_reflex.persistence import (
    default_settings,
    delete_build,
    encode_builds,
    encode_settings,
    find_build,
    new_build_entry,
    parse_builds,
    parse_settings,
    rename_build,
    resolve_optimize_spatial,
    snapshot_from_state_values,
    upsert_build,
)
from warframe_reflex.models import EditorField


def test_settings_round_trip_preserves_enemy_and_optimizer():
    settings = default_settings()
    settings["enemy"]["name"] = "Heavy Gunner"
    settings["enemy"]["level"] = 150
    settings["optimizer"]["spatial"] = OPTIMIZE_SPATIAL_AOE
    restored = parse_settings(encode_settings(settings))
    assert restored["enemy"]["name"] == "Heavy Gunner"
    assert restored["enemy"]["level"] == 150
    assert restored["optimizer"]["spatial"] == OPTIMIZE_SPATIAL_AOE


def test_legacy_aoe_weight_maps_to_spatial():
    assert resolve_optimize_spatial({"aoe_weight": 0}) == OPTIMIZE_SPATIAL_SINGLE
    assert resolve_optimize_spatial({"aoe_weight": 100}) == OPTIMIZE_SPATIAL_AOE
    assert resolve_optimize_spatial({"aoe_weight": 50}) == OPTIMIZE_SPATIAL_AUTO
    assert resolve_optimize_spatial({"spatial": OPTIMIZE_SPATIAL_SINGLE, "aoe_weight": 100}) == OPTIMIZE_SPATIAL_SINGLE
    assert DEFAULT_OPTIMIZE_SPATIAL == OPTIMIZE_SPATIAL_AUTO


def test_build_upsert_rename_and_delete():
    slot_count = len(SLOT_CONFIGS)
    snapshot = snapshot_from_state_values(
        selected_weapon_type="Primary",
        selected_weapon_category="Rifle",
        selected_weapon="Vectis Prime",
        selected_attack_mode="Normal Attack",
        evolution_selections=[],
        evolution_condition_toggles=[],
        evolution_stack_fields=[],
        melee_combo_count="Initial Combo",
        selected_stance_combo="neutral",
        progenitor_element="None",
        progenitor_value=0.0,
        ability_strength=100.0,
        selected_enemy_faction="Grineer",
        selected_enemy="Heavy Gunner",
        enemy_level=100,
        enemy_steel_path=False,
        enemy_empowered=False,
        optimize_body_part="head",
        slot_selected_upgrades=["None"] * slot_count,
        slot_policies=[SLOT_POLICY_DISCARD] * slot_count,
        slot_ranks=[0] * slot_count,
        slot_stacks=[0] * slot_count,
        slot_conditions_enabled=[True] * slot_count,
        slot_fields=[[] for _ in range(slot_count)],
        slot_riven_rolls=["2 Positive + 1 Negative"] * slot_count,
        external_fields=[EditorField("crit_chance", "Critical Chance", 0.5)],
        optimize_find_riven=False,
        optimize_find_evolutions=False,
        optimize_find_progenitor=False,
        optimize_maximize_target="Balanced (DPS · DPH)",
        optimize_search_quality="High",
        optimize_dph_weight=50,
        optimize_flat_dot_weight=50,
        optimize_spatial=DEFAULT_OPTIMIZE_SPATIAL,
        optimize_excluded_upgrades=[],
        optimize_default_exclusion_overrides=[],
        optimize_excluded_riven_stats=[],
        optimize_default_riven_exclusion_overrides=[],
    )
    entry = new_build_entry("My Vectis", snapshot)
    builds = upsert_build([], entry)
    assert len(builds) == 1
    assert find_build(builds, entry["id"])["name"] == "My Vectis"
    builds = rename_build(builds, entry["id"], "Vectis SP")
    assert find_build(builds, entry["id"])["name"] == "Vectis SP"
    restored = parse_builds(encode_builds(builds))
    assert restored[0]["snapshot"]["selected_weapon"] == "Vectis Prime"
    assert restored[0]["snapshot"]["external_fields"][0]["name"] == "crit_chance"
    builds = delete_build(restored, entry["id"])
    assert builds == []
