from types import SimpleNamespace

from warframe_damage_calculator import Arcane, Mod
from warframe_damage_calculator.optimizer.candidates import DEFAULT_UPGRADE_BLACKLIST

from warframe_reflex.data import database_conditional_info, database_enemy, database_max_stacks, database_upgrade
from warframe_reflex.engine import build_upgrade, configured_weapon, main_metrics, upgrade_stat_rows
from warframe_reflex.state import CalculatorState, _optimizer_progress, _optimizer_upgrade_blacklist


def test_upgrade_stats_render_current_effect_tuples():
    upgrade = database_upgrade("Serration", kind="mod", rank=10)
    rows = upgrade_stat_rows(upgrade)
    assert rows
    assert rows[0].label == "Damage Bonus"
    assert rows[0].value != ""


def test_crit_tier_upgrade_stats_display_as_crit_chance():
    upgrade = database_upgrade("Vigilante Supplies", kind="mod", rank=5)
    rows = upgrade_stat_rows(upgrade)
    assert rows[0].label == "Crit Chance on Critical Hit (5% trigger chance)"


def test_automatic_upgrade_stats_display_trigger_context():
    cases = {
        ("Hemorrhage", "mod"): "Slash Proc Chance on Impact Status Proc (35% trigger chance)",
        ("Cascadia Flare", "arcane"): "Damage Bonus per Heat Status Proc",
        ("Blood Rush", "mod"): "Crit Chance per Weapon Combo",
        ("Sacrificial Pressure", "mod"): "Damage Bonus on Sacrificial Steel Equipped",
        ("Galvanized Aptitude", "mod"): "Damage Bonus per Kill per Unique Status Count",
    }
    for (name, kind), expected in cases.items():
        labels = {row.label for row in upgrade_stat_rows(database_upgrade(name, kind=kind))}
        assert expected in labels


def test_manual_stacking_conditions_use_per_wording():
    labels = {row.label for row in upgrade_stat_rows(database_upgrade("Galvanized Chamber", kind="mod", rank=10))}
    assert "Multishot per Kill" in labels


def test_stacked_upgrade_conditions_do_not_require_toggles():
    assert database_max_stacks("Galvanized Aptitude", is_arcane_slot=False) == 2
    assert database_conditional_info("Galvanized Aptitude", is_arcane_slot=False) == (False, "")
    assert database_max_stacks("Galvanized Scope", is_arcane_slot=False) == 5
    assert database_conditional_info("Galvanized Scope", is_arcane_slot=False) == (False, "")


def test_boolean_only_upgrade_conditions_keep_toggles():
    assert database_max_stacks("Bladed Rounds", is_arcane_slot=False) is None
    assert database_conditional_info("Bladed Rounds", is_arcane_slot=False) == (True, "Kill")


def test_slot_editor_hides_stacked_condition_and_keeps_boolean_condition():
    state = CalculatorState(_reflex_internal_init=True)
    state.initialize()
    selected = list(state.slot_selected_upgrades)
    selected[1] = "Galvanized Aptitude"
    state.slot_selected_upgrades = selected
    state._refresh_slot_condition_metadata()
    assert not state.slot_has_conditionals[1]
    assert state.slot_condition_labels[1] == ""
    selected[1] = "Bladed Rounds"
    state.slot_selected_upgrades = selected
    state._refresh_slot_condition_metadata()
    assert state.slot_has_conditionals[1]
    assert state.slot_condition_labels[1] == "Kill"


def test_current_library_calculation_path():
    enemy = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    upgrade = database_upgrade("Serration", kind="mod", rank=10)
    resolved = configured_weapon("Primary", "Vectis Prime", custom_weapon=False, base_stats={}, upgrades=[upgrade], selected_mode="Normal Attack", target=enemy)
    metrics = main_metrics(resolved)
    assert len(metrics) == 6
    assert any(row.label == "Total DPS" and float(row.value.replace(",", "")) > 0 for row in metrics)


def test_database_max_stacks_accepts_scalar_current_schema():
    value = database_max_stacks("Galvanized Chamber", is_arcane_slot=False)
    assert value is None or isinstance(value, int)


def test_state_initializes_empty_upgrade_slots_with_current_library_types():
    state = CalculatorState(_reflex_internal_init=True)
    state.initialize()

    assert isinstance(state._slot_upgrade(0), Mod)
    assert isinstance(state._slot_upgrade(10), Arcane)
    assert state.result_error == "Select a weapon to calculate."


def test_state_displays_upgrades_and_results_with_empty_slots():
    state = CalculatorState(_reflex_internal_init=True)
    state.initialize()
    state.set_weapon_type("Sniper")
    state.set_weapon("Vectis Prime")
    state.set_enemy_faction("grineer")
    state.set_enemy("Heavy Gunner")
    state.set_slot_upgrade(1, "Serration")

    assert state.result_error == ""
    assert state.result_ready
    assert state.slot_stat_rows[1][0].label == "Damage Bonus"
    assert any(row.label == "Total DPS" for row in state.result_metrics)


def test_optimizer_progress_uses_planned_work_fraction():
    assert _optimizer_progress(0.25) == 25.0
    assert _optimizer_progress(1.0) == 100.0
    assert _optimizer_progress(1.5) == 100.0


def test_optimizer_request_preserves_the_library_default_blacklist():
    assert _optimizer_upgrade_blacklist([], []) == set(DEFAULT_UPGRADE_BLACKLIST)
    assert "Primary Overcharge" not in _optimizer_upgrade_blacklist([], ["Primary Overcharge"])


def test_custom_upgrade_preserves_riven_only_stats():
    upgrade = build_upgrade("Riven", {"punch_through": 2.5, "status_duration": -0.4})

    assert upgrade.stats.punch_through[0].value == 2.5
    assert upgrade.stats.status_duration[0].value == -0.4


def test_optimizer_application_keeps_statless_special_upgrades():
    state = CalculatorState(_reflex_internal_init=True)
    state.initialize()
    state.set_weapon_type("Rifle")
    state.set_weapon("Kuva Ogris")
    state.set_enemy_faction("grineer")
    state.set_enemy("Exo Gokstad Officer")
    state.set_enemy_level("235")
    state.set_enemy_toggle("enemy_steel_path", True)
    state.set_progenitor_element("heat")
    state.progenitor_value = 0.6
    result = SimpleNamespace(
        slot_names=["Primed Stabilizer", "Nightwatch Napalm", "Galvanized Aptitude", "Continuous Misery", "Hellfire", "Rime Rounds", "Malignant Force", "Galvanized Chamber", "Rifle Elementalist", "None", "Primary Compression"],
        slot_ranks=[10, 5, 10, 3, 5, 3, 3, 10, 5, 0, 5],
        slot_stacks=[0, 0, 2, 0, 0, 0, 0, 5, 0, 0, 0],
        slot_conditions=[False] * 10 + [True],
        slot_policies=["discard"] * 11,
        riven_rolls=["2 Positive + 1 Negative"] * 11,
        riven_fields=[{} for _ in range(11)],
        custom_entries=[""] * 11,
        progenitor_optimized=False,
        evolutions_optimized=False,
    )

    state._apply_optimize_result(result)
    state._recalculate()
    state._apply_contribution_summary_sync()

    assert next(row.value for row in state.main_result_metrics if row.label == "Total DPS") == "1,577,486.46"
    assert "Nightwatch Napalm" in state.result_contribution_summary
