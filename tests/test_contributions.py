import pytest

from warframe_damage_calculator import Calculator, Formatter

from warframe_reflex.data import database_enemy, database_upgrade
from warframe_reflex.engine import configured_weapon, contribution_lookup_for_weapon, library_contribution_bundle, result_contributions_summary, result_summary_table_rows


def test_current_library_contributions_use_library_removal_scores():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10), database_upgrade("Vital Sense", kind="mod", rank=5)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", upgrades=upgrades, selected_mode="Normal Attack", target=target)
    contributions = contribution_lookup_for_weapon(resolved, "Primary", None, upgrades, target_metric="total_dps")
    assert {name for name, _ in contributions} == {"Serration", "Vital Sense"}
    assert sum(value for _, value in contributions) == pytest.approx(1.0)
    _calculator, result = resolved
    library = Calculator(result.weapon, result.target, result.loadout).contributions(attack=result.selected_attack, metric="total_dps", body_part=result.selected_bodypart, state=result.state)
    assert dict(contributions) == library.contribution
    lookup, summary, rows = library_contribution_bundle(resolved)
    assert dict(lookup) == library.contribution
    assert summary == Formatter(result).contributions(metric="total_dps", body_part=result.selected_bodypart)
    assert summary == result_contributions_summary(resolved)
    assert "Serration" in summary
    assert "Vital Sense" in summary
    assert "Relative Contribution" in summary
    assert [row.name for row in rows] == ["Serration", "Vital Sense"] or [row.name for row in rows] == ["Vital Sense", "Serration"]
    assert all(row.kind == "Regular Mod" for row in rows)
    assert all(row.rank and row.share and row.removal and "│" in row.impact for row in rows)


def test_summary_table_rows_match_formatter_summary_sections():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", upgrades=upgrades, selected_mode="Normal Attack", target=target)
    rows = result_summary_table_rows(resolved)
    assert sum(1 for row in rows if row.section_start) == 3
    assert rows[0].stat != "" and not rows[0].section_start
    assert any(row.stat == "Total DPS" and row.average != "" for row in rows)
    assert any(row.stat == "Critical Chance" and row.base and row.modded and row.section_start for row in rows)
