from types import SimpleNamespace

from warframe_damage_calculator import balanced_damage_metric

import warframe_reflex.optimizer as opt
from warframe_reflex.constants import DEFAULT_OPTIMIZE_SPATIAL, OPTIMIZE_SPATIAL_AOE, OPTIMIZE_SPATIAL_SINGLE



def _balanced_request(**overrides):
    request = opt.OptimizeRequest(
        weapon_type="Primary",
        weapon_category="Rifle",
        weapon_name="Tonkor",
        attack_mode="Grenade Impact",
        evolutions={},
        combo_count=1,
        evolution_runtime={},
        progenitor_element="None",
        progenitor_value=0.0,
        external_fields={},
        slots=[],
        find_optimal_riven=False,
        maximize_target="balanced_total_dps_dph",
        dph_weight=0.5,
        flat_dot_weight=0.5,
        spatial=DEFAULT_OPTIMIZE_SPATIAL,
    )
    for key, value in overrides.items():
        setattr(request, key, value)
    return request


def test_default_balanced_metric_uses_library_balanced_damage_metric():
    metric, compact = opt._metrics_for(_balanced_request())
    assert metric is balanced_damage_metric
    assert compact is None


def test_custom_dph_weight_uses_compact_metric():
    metric, compact = opt._metrics_for(_balanced_request(dph_weight=0.6))
    assert metric is not balanced_damage_metric
    assert compact is not None
    assert compact(100, 0, 100, 0, 8.0) == opt._compact_balanced(100, 0, 100, 0, 8.0, dph_weight=0.6)


def test_optimize_build_passes_spatial_mode(monkeypatch):
    captured = {}

    class FakeOptimizer:
        def __init__(self, calculator):
            captured["build"] = calculator.build

        def resolve(self, metric, **kwargs):
            captured["metric"] = metric
            captured["kwargs"] = kwargs
            return SimpleNamespace(build=captured["build"], score=1.0, evaluations=1, elapsed=0.01, budget_exhausted=False)

    monkeypatch.setattr(opt, "Optimizer", FakeOptimizer)
    opt.optimize_build(_balanced_request(spatial=OPTIMIZE_SPATIAL_SINGLE, weapon_name="Kuva Ogris", enemy_name="Exo Gokstad Officer"), progress=None)
    assert captured["kwargs"]["spatial"] == "none"
    opt.optimize_build(_balanced_request(spatial=OPTIMIZE_SPATIAL_AOE, weapon_name="Kuva Ogris", enemy_name="Exo Gokstad Officer"), progress=None)
    assert captured["kwargs"]["spatial"] == "full"
    opt.optimize_build(_balanced_request(spatial=DEFAULT_OPTIMIZE_SPATIAL, weapon_name="Kuva Ogris", enemy_name="Exo Gokstad Officer"), progress=None)
    assert captured["kwargs"]["spatial"] == "auto"
