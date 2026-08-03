from __future__ import annotations

import pytest

from warframe_reflex.constants import OPTIMIZE_SEARCH_BALANCED, OPTIMIZE_SEARCH_EVALUATION_BUDGETS, OPTIMIZE_SEARCH_FAST, SLOT_CONFIGS, SLOT_POLICY_DISCARD
from warframe_reflex.data import database_upgrade, optimizer_excludes_upgrade_by_default, raw_riven_stats_database, upgrade_names_for_ui
from warframe_reflex.engine import build_upgrade, configured_enemy, configured_weapon
from warframe_reflex.optimizer import RIVEN, OptimizeRequest, SlotSpec, optimize_build


@pytest.mark.slow
def test_balanced_corinth_regression_finds_the_viral_build():
    pools = set()
    for include_mods, include_arcanes, exilus_only in ((True, False, False), (True, False, True), (False, True, False)):
        pools.update(upgrade_names_for_ui("Shotgun", "Corinth Prime", "", include_mods, include_arcanes, exilus_only))
    slots = [
        SlotSpec(index=index, kind=config["kind"], exilus=config["exilus"], stance=bool(config.get("stance")), selected="None", policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, condition=True)
        for index, config in enumerate(SLOT_CONFIGS)
    ]
    request = OptimizeRequest(
        weapon_type="Primary", weapon_category="Shotgun", weapon_name="Corinth Prime", custom_weapon=False, custom_weapon_entry="",
        attack_mode="", evolutions={}, combo_count=1, evolution_runtime={}, progenitor_element="None", progenitor_value=0.0,
        external_fields={}, slots=slots, find_optimal_riven=False, enemy_name="Aerial Commander", enemy_level=100,
        excluded_upgrades={name for name in pools if optimizer_excludes_upgrade_by_default(name)}, search_quality=OPTIMIZE_SEARCH_BALANCED,
    )

    result = optimize_build(request)

    assert result.evaluations <= OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_BALANCED]
    assert result.total_dps >= 2_100_000
    assert {"Primed Chilling Grasp", "Contagious Spread"} <= set(result.slot_names)
    assert result.search_quality == OPTIMIZE_SEARCH_BALANCED


@pytest.mark.slow
def test_vectis_riven_incumbent_score_matches_a_clean_result():
    names = ["None", "Primary Acuity", "Primed Chamber", RIVEN, "None", "None", "None", "None", "None", "Vigilante Supplies", "Primary Deadhead"]
    ranks = [0, 10, 3, 0, 0, 0, 0, 0, 0, 5, 5]
    stacks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3]
    riven_fields = {"crit_chance": 2.041738875, "crit_damage": 1.6335}
    slots = [SlotSpec(index=index, kind=config["kind"], exilus=config["exilus"], stance=bool(config.get("stance")), selected=names[index], policy=SLOT_POLICY_DISCARD, rank=ranks[index], stacks=stacks[index], condition=True, riven_fields=riven_fields if names[index] == RIVEN else {}) for index, config in enumerate(SLOT_CONFIGS)]
    pools = set()
    for include_mods, include_arcanes, exilus_only in ((True, False, False), (True, False, True), (False, True, False)):
        pools.update(upgrade_names_for_ui("Sniper", "Vectis Prime", "Normal Attack", include_mods, include_arcanes, exilus_only))
    request = OptimizeRequest(
        weapon_type="Primary", weapon_category="Sniper", weapon_name="Vectis Prime", custom_weapon=False, custom_weapon_entry="", attack_mode="Normal Attack",
        evolutions={1: 1, 2: 1, 3: 1, 4: 2}, combo_count=1, evolution_runtime={"channeled_ability": True}, progenitor_element="None", progenitor_value=0.0,
        external_fields={}, slots=slots, find_optimal_riven=True, find_optimal_evolutions=True, enemy_name="Exo Gokstad Officer", enemy_level=235,
        enemy_steel_path=True, maximize_target="total_weakpoint_dps", excluded_upgrades={name for name in pools if optimizer_excludes_upgrade_by_default(name)},
        search_quality=OPTIMIZE_SEARCH_FAST, riven_disposition=1.0, riven_base_stats=dict(raw_riven_stats_database()["rifle"]),
    )

    result = optimize_build(request)
    upgrades = []
    for index, name in enumerate(result.slot_names):
        if name == "None":
            continue
        if name == RIVEN:
            upgrades.append(build_upgrade(RIVEN, result.riven_fields[index]))
        else:
            upgrades.append(database_upgrade(name, kind=SLOT_CONFIGS[index]["kind"], rank=result.slot_ranks[index], stacks=result.slot_stacks[index] or None, condition=True))
    target = configured_enemy(request.enemy_name, level=request.enemy_level, steel_path=request.enemy_steel_path, empowered=False)
    weapon = configured_weapon("Primary", "Vectis Prime", custom_weapon=False, base_stats={}, upgrades=upgrades, selected_mode=request.attack_mode, evolutions=result.evolutions, runtime_conditions=request.evolution_runtime, target=target)

    assert result.total_dps == pytest.approx(weapon.results.main.final.total_weakpoint_dps)
