from types import SimpleNamespace

import pytest

from warframe_reflex.data import database_enemy, database_upgrade
from warframe_reflex.engine import configured_weapon, contribution_lookup_for_weapon


def test_contribution_lookup_targets_total_weakpoint_dps():
    requested = []

    def removal_contributions(*, target):
        requested.append(target)
        return {"Upgrade A": 3.0, "Upgrade B": 1.0}

    weapon = SimpleNamespace(results=SimpleNamespace(removal_contributions=removal_contributions))
    contributions = contribution_lookup_for_weapon(weapon, "Primary", None, [object()], target_metric="total_weakpoint_dps")
    assert requested == ["total_weakpoint_dps"]
    assert contributions == [("Upgrade A", 0.75), ("Upgrade B", 0.25)]


def test_current_library_contributions_use_fast_removal_scores():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10), database_upgrade("Vital Sense", kind="mod", rank=5)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", custom_weapon=False, base_stats={}, upgrades=upgrades, selected_mode="Normal Attack", target=target)
    contributions = contribution_lookup_for_weapon(resolved, "Primary", None, upgrades, target_metric="total_dps")
    assert {name for name, _ in contributions} == {"Serration", "Vital Sense"}
    assert sum(value for _, value in contributions) == pytest.approx(1.0)
