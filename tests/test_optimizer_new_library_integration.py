from types import SimpleNamespace

from warframe_damage_calculator import Calculator, Effect, Loadout, Mod, Optimizer as LibraryOptimizer, UpgradeStats, arsenal, default_metric

import warframe_reflex.optimizer as app_optimizer
from warframe_reflex.constants import SLOT_POLICY_DISCARD, SLOT_POLICY_KEEP


def _slot(index, name, policy):
    return app_optimizer.SlotSpec(index=index, kind="mod", exilus=False, selected=name, policy=policy, rank=10, stacks=0, condition=True)


def test_only_kept_components_are_passed_to_library_optimizer(monkeypatch):
    captured = {}

    class FakeOptimizer:
        def __init__(self, calculator):
            captured["loadout"] = calculator.loadout

        def resolve(self, metric, **kwargs):
            captured["kwargs"] = kwargs
            return SimpleNamespace(loadout=captured["loadout"], score=1.0, evaluations=1, elapsed=0.01, summary={"budget_exhausted": False})

    monkeypatch.setattr(app_optimizer, "Optimizer", FakeOptimizer)
    request = app_optimizer.OptimizeRequest(
        weapon_type="Primary",
        weapon_category="Rifle",
        weapon_name="Vectis Prime",
        attack_mode="Normal Attack",
        evolutions={},
        combo_count=12,
        evolution_runtime={},
        progenitor_element="None",
        progenitor_value=0.0,
        external_fields={},
        slots=[_slot(1, "Serration", SLOT_POLICY_KEEP), _slot(2, "Split Chamber", SLOT_POLICY_DISCARD)],
        find_optimal_riven=False,
        enemy_name="Heavy Gunner",
        body_part="head",
    )

    app_optimizer.optimize_build(request, progress=None)

    assert [mod.name for mod in captured["loadout"].mods] == ["Serration"]
    assert captured["kwargs"]["body_part"] == "head"
    assert app_optimizer._metric_for(request) is default_metric


def test_app_uses_library_optimizer_class():
    assert app_optimizer.Optimizer is LibraryOptimizer


def test_optimized_runtime_stacks_are_preserved(monkeypatch):
    galvanized = arsenal.mod.get("Galvanized Aptitude").set(rank=10, kill=2)
    compression = arsenal.arcane.get("Primary Compression").set(rank=5, aim=True)

    class FakeOptimizer:
        def __init__(self, calculator):
            pass

        def resolve(self, metric, **kwargs):
            return SimpleNamespace(loadout=Loadout(mods=[galvanized], arcanes=[compression]), score=1.0, evaluations=12, elapsed=0.01, summary={"budget_exhausted": False})

    monkeypatch.setattr(app_optimizer, "Optimizer", FakeOptimizer)
    request = app_optimizer.OptimizeRequest(
        weapon_type="Primary",
        weapon_category="Sniper",
        weapon_name="Vectis Prime",
        attack_mode="Normal Attack",
        evolutions={},
        combo_count=1,
        evolution_runtime={},
        progenitor_element="None",
        progenitor_value=0.0,
        external_fields={},
        slots=[],
        find_optimal_riven=False,
        enemy_name="Exo Gokstad Officer",
        body_part="head",
    )

    result = app_optimizer.optimize_build(request, progress=None)

    assert result.slot_names[1] == "Galvanized Aptitude"
    assert result.slot_stacks[1] == 2
    assert result.slot_conditions[1] is False
    assert result.slot_names[10] == "Primary Compression"
    assert result.slot_conditions[10] is True


def test_riven_damage_bonus_uses_the_editor_field_name():
    riven = Mod(name="Riven", stats=UpgradeStats(damage_bonus=Effect(1.5), crit_chance=Effect(1.2), punch_through=Effect(2.0), status_chance=Effect(-0.5)))

    assert app_optimizer._riven_fields(riven) == {"base_damage": 1.5, "crit_chance": 1.2, "punch_through": 2.0, "status_chance": -0.5}
    assert app_optimizer._riven_roll(riven) == "3 Positive + 1 Negative"
