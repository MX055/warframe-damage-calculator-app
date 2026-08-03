from types import SimpleNamespace

from warframe_damage_calculator import balanced_damage_metric

import warframe_reflex.optimizer as opt


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
        aoe_weight=1.0,
    )
    for key, value in overrides.items():
        setattr(request, key, value)
    return request


def test_default_aoe_weight_uses_library_balanced_damage_metric():
    assert opt._metric_for(_balanced_request()) is balanced_damage_metric


def test_aoe_weight_scales_damage_mass_in_the_balanced_metric():
    spatial = SimpleNamespace(damage_mass=8.0)
    attack = SimpleNamespace(damage=SimpleNamespace(direct_dph=100.0, dot_dph=0.0), spatial=spatial)
    result = SimpleNamespace(
        aggregate=SimpleNamespace(damage=SimpleNamespace(total_dps=100.0, total_dph=100.0, direct_dph=100.0, dot_dph=0.0, direct_dps=100.0, dot_dps=0.0)),
        attacks={"grenade_impact": attack},
    )

    full = opt._metric_for(_balanced_request(aoe_weight=1.0, dph_weight=0.6))
    none = opt._metric_for(_balanced_request(aoe_weight=0.0, dph_weight=0.6))
    half = opt._metric_for(_balanced_request(aoe_weight=0.5, dph_weight=0.6))

    assert full(result) > half(result) > none(result)
    assert none(result) == (100.0 ** (2 * 0.4) * 100.0 ** (2 * 0.6) * 1.0) ** (1 / 3)
    assert full(result) == (100.0 ** (2 * 0.4) * 100.0 ** (2 * 0.6) * 8.0) ** (1 / 3)
