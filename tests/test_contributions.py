import pytest

from warframe_damage_calculator import Calculator, Formatter

from warframe_reflex.data import database_enemy, database_upgrade
from warframe_reflex.engine import _contribution_metric, configured_weapon, contribution_lookup_for_weapon, library_contribution_bundle, result_contributions_summary, result_status_summary, result_summary


def test_current_library_contributions_use_library_removal_scores():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10), database_upgrade("Vital Sense", kind="mod", rank=5)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", upgrades=upgrades, selected_mode="Normal Attack", target=target)
    contributions = contribution_lookup_for_weapon(resolved, "Primary", None, upgrades, target_metric="total_dps")
    assert {name for name, _ in contributions} == {"Serration", "Vital Sense"}
    assert sum(value for _, value in contributions) == pytest.approx(1.0)
    _calculator, result = resolved
    total_dps_metric = _contribution_metric("total_dps")
    total_dps_library = Calculator(result.weapon, result.target, result.build).contributions(attack=result.selected_attack, metric=total_dps_metric, body_part=result.selected_body_part, state=result.state)
    assert dict(contributions) == total_dps_library.contribution
    balanced_metric = _contribution_metric()
    balanced_library = Calculator(result.weapon, result.target, result.build).contributions(attack=result.selected_attack, metric=balanced_metric, body_part=result.selected_body_part, state=result.state)
    lookup, summary, rows = library_contribution_bundle(resolved)
    assert dict(lookup) == balanced_library.contribution
    assert summary == Formatter(result).build_summary(metric=balanced_metric)
    assert summary == result_contributions_summary(resolved)
    assert "Balanced Damage Contributions" in summary
    assert "Serration" in summary
    assert "Vital Sense" in summary
    assert "Relative Contribution" in summary
    assert [row.name for row in rows] == ["Serration", "Vital Sense"] or [row.name for row in rows] == ["Vital Sense", "Serration"]
    assert all(row.kind == "Regular Mod" for row in rows)
    assert all(row.rank and row.share and row.removal and "│" in row.impact for row in rows)


def test_stat_and_status_summaries_match_formatter_text():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", upgrades=upgrades, selected_mode="Normal Attack", target=target)
    _calculator, result = resolved
    assert result_summary(resolved) == Formatter(result).stat_summary()
    assert result_status_summary(resolved) == Formatter(result).status_summary()
    assert "Total DPS" in result_summary(resolved)
    assert "Critical Chance" in result_summary(resolved)
