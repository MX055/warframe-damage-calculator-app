from types import SimpleNamespace

from warframe_reflex.engine import contribution_lookup_for_weapon


def test_contribution_lookup_targets_total_weakpoint_dps():
    requested = []

    def removal_contributions(*, target):
        requested.append(target)
        return {"Upgrade A": 3.0, "Upgrade B": 1.0}

    weapon = SimpleNamespace(results=SimpleNamespace(removal_contributions=removal_contributions))
    contributions = contribution_lookup_for_weapon(weapon, "Primary", None, [object()], target_metric="total_weakpoint_dps")
    assert requested == ["total_weakpoint_dps"]
    assert contributions == [("Upgrade A", 0.75), ("Upgrade B", 0.25)]
