from __future__ import annotations

import itertools
import threading
from types import SimpleNamespace

import pytest

from warframe_reflex import optimizer as opt
from warframe_reflex.constants import (
    DEFAULT_OPTIMIZE_SEARCH,
    OPTIMIZE_SEARCH_BALANCED,
    OPTIMIZE_SEARCH_EVALUATION_BUDGETS,
    OPTIMIZE_SEARCH_FAST,
    OPTIMIZE_SEARCH_MAX,
    SLOT_CONFIGS,
    SLOT_POLICY_DISCARD,
    SLOT_POLICY_KEEP_IN_SLOT,
)
from warframe_reflex.optimizer import OptimizeRequest, SlotSpec


class FakeUpgrade:
    def __init__(self, name: str):
        self.name = name


class FakeRuntime(SimpleNamespace):
    def update(self, values):
        for name, value in values.items():
            setattr(self, name, value)


class FakeWeapon:
    def __init__(self, objective):
        self.build = None
        self.data = SimpleNamespace(runtime=FakeRuntime(combo=1, evolutions={}))
        self.results = SimpleNamespace(main=SimpleNamespace(final=SimpleNamespace(total_dps=0.0)))
        self.results.resolve = self.resolve
        self.objective = objective

    def resolve(self, validate_cycles=False):
        names = [upgrade.name for upgrade in self.build.upgrades if upgrade.name != opt.NONE]
        self.results.main.final.total_dps = float(self.objective(names))


@pytest.fixture
def fake_optimizer(monkeypatch):
    def configure(candidates, objective):
        def upgrade_names(_category, _weapon, _mode, include_mods, include_arcanes, exilus_only, stance_only=False, **_kwargs):
            return tuple(candidates) if include_mods and not include_arcanes and not exilus_only and not stance_only else ()

        monkeypatch.setattr(opt, "Build", lambda: SimpleNamespace(upgrades=[]))
        monkeypatch.setattr(opt, "Upgrade", lambda entry: FakeUpgrade(entry["name"]))
        monkeypatch.setattr(opt, "upgrade_names_for_ui", upgrade_names)
        monkeypatch.setattr(opt, "_upgrade_names_for_ui", upgrade_names)
        monkeypatch.setattr(opt, "database_upgrade", lambda name, **_kwargs: FakeUpgrade(name))
        monkeypatch.setattr(opt, "database_rank_bounds", lambda _name, **_kwargs: (0, 0))
        monkeypatch.setattr(opt, "database_max_stacks", lambda _name, **_kwargs: 0)
        monkeypatch.setattr(opt, "upgrade_conflicts_with_selected", lambda _name, _selected: False)
        monkeypatch.setattr(opt, "configured_enemy", lambda *_args, **_kwargs: None)
        def configured_weapon(*_args, **kwargs):
            weapon = FakeWeapon(objective)
            weapon.build = SimpleNamespace(upgrades=list(kwargs.get("upgrades") or []))
            weapon.resolve()
            return weapon
        monkeypatch.setattr(opt, "configured_weapon", configured_weapon)
        monkeypatch.setattr(opt, "build_upgrade", lambda name, fields: FakeUpgrade(name if fields else opt.NONE))
        monkeypatch.setattr(opt, "progenitor_upgrade", lambda *_args, **_kwargs: FakeUpgrade(opt.NONE))
        monkeypatch.setattr(opt, "is_non_empty_upgrade", lambda upgrade: upgrade.name != opt.NONE)
    return configure


def make_request(candidates, *, quality=OPTIMIZE_SEARCH_BALANCED, open_values=(opt.NONE, opt.NONE), cancel_event=None):
    open_indices = (1, 2)
    slots = []
    for index, config in enumerate(SLOT_CONFIGS):
        if index in open_indices:
            selected = open_values[open_indices.index(index)]
            policy = SLOT_POLICY_DISCARD
        else:
            selected = f"Locked {index}"
            policy = SLOT_POLICY_KEEP_IN_SLOT
        slots.append(SlotSpec(index=index, kind=config["kind"], exilus=config["exilus"], stance=bool(config.get("stance")), selected=selected, policy=policy, rank=0, stacks=0, condition=True))
    return OptimizeRequest(
        weapon_type="Primary", weapon_category="Rifle", weapon_name="Synthetic", custom_weapon=False, custom_weapon_entry="",
        attack_mode="", evolutions={}, combo_count=1, evolution_runtime={}, progenitor_element=opt.NONE, progenitor_value=0.0,
        external_fields={}, slots=slots, find_optimal_riven=False, enemy_name="Synthetic Enemy", maximize_target="total_dps",
        excluded_upgrades=set(), search_quality=quality, cancel_event=cancel_event,
    )


def candidate_order(names, candidates):
    allowed = set(candidates)
    return tuple(name for name in names if name in allowed)


def exact_two_slot_score(candidates, objective):
    best = float("-inf")
    for first, second in itertools.product((opt.NONE, *candidates), repeat=2):
        chosen = tuple(name for name in (first, second) if name != opt.NONE)
        if len(chosen) != len(set(chosen)):
            continue
        best = max(best, float(objective(chosen)))
    return best


def test_balanced_beam_escapes_two_replacement_local_optimum(fake_optimizer, monkeypatch):
    candidates = ("A", "B", "C", "D")

    def objective(names):
        chosen = set(candidate_order(names, candidates))
        if chosen == {"C", "D"}:
            return 20
        if chosen == {"A", "B"}:
            return 10
        if len(chosen) == 1:
            return {"A": 6, "B": 5, "C": 4, "D": 3}[next(iter(chosen))]
        if len(chosen) == 2:
            return 8 if "C" in chosen else 7
        return 0

    fake_optimizer(candidates, objective)
    fast = opt.optimize_build(make_request(candidates, quality=OPTIMIZE_SEARCH_FAST))
    balanced = opt.optimize_build(make_request(candidates, quality=OPTIMIZE_SEARCH_BALANCED))
    monkeypatch.setitem(OPTIMIZE_SEARCH_EVALUATION_BUDGETS, OPTIMIZE_SEARCH_MAX, OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_FAST])
    max_effort = opt.optimize_build(make_request(candidates, quality=OPTIMIZE_SEARCH_MAX))

    assert fast.total_dps == exact_two_slot_score(candidates, objective) == 20
    assert max_effort.total_dps >= balanced.total_dps >= fast.total_dps
    assert max_effort.evaluations <= OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_MAX]
    assert {"C", "D"} == set(fast.slot_names[1:3])


def test_optimizer_swaps_mod_order_and_can_remove_an_upgrade(fake_optimizer):
    order_candidates = ("C", "D")
    fake_optimizer(order_candidates, lambda names: 20 if candidate_order(names, order_candidates) == ("C", "D") else 5 if candidate_order(names, order_candidates) == ("D", "C") else 0)
    ordered = opt.optimize_build(make_request(order_candidates, quality=OPTIMIZE_SEARCH_FAST, open_values=("D", "C")))
    assert ordered.slot_names[1:3] == ["C", "D"]
    assert ordered.total_dps == 20

    removal_candidates = ("A",)
    fake_optimizer(removal_candidates, lambda names: -10 if "A" in names else -5 if "Harmful" in names else 0)
    removed = opt.optimize_build(make_request(removal_candidates, quality=OPTIMIZE_SEARCH_FAST, open_values=("Harmful", opt.NONE)))
    assert removed.slot_names[1] == opt.NONE
    assert removed.total_dps == 0


def test_search_is_deterministic_preserves_locks_and_respects_budget(fake_optimizer):
    candidates = ("A", "B", "C")
    fake_optimizer(candidates, lambda names: sum({"A": 3, "B": 2, "C": 1}.get(name, 0) for name in names))
    first = opt.optimize_build(make_request(candidates))
    second = opt.optimize_build(make_request(candidates))

    assert first.slot_names == second.slot_names
    assert first.total_dps == second.total_dps
    assert first.evaluations <= OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_BALANCED]
    assert first.search_quality == DEFAULT_OPTIMIZE_SEARCH
    for index in range(len(SLOT_CONFIGS)):
        if index not in (1, 2):
            assert first.slot_names[index] == f"Locked {index}"
            assert first.slot_policies[index] == SLOT_POLICY_KEEP_IN_SLOT


def test_optimizer_honors_pre_cancelled_request(fake_optimizer):
    fake_optimizer(("A",), lambda _names: 0)
    cancel_event = threading.Event()
    cancel_event.set()
    with pytest.raises(InterruptedError):
        opt.optimize_build(make_request(("A",), cancel_event=cancel_event))


def test_max_effort_has_a_20k_evaluation_budget():
    assert OPTIMIZE_SEARCH_EVALUATION_BUDGETS[OPTIMIZE_SEARCH_MAX] == 20_000


def test_dps_dph_weight_controls_the_balanced_objective():
    final = SimpleNamespace(total_dps=100.0, total_dph=10.0, total_weakpoint_dps=0.0, total_weakpoint_dph=0.0, flat_dotps=0.0, flat_dotph=0.0, flat_weakpoint_dotps=0.0, flat_weakpoint_dotph=0.0)
    assert opt.score_maximize_target(final, "balanced_total_dps_dph", weakpoint_weight=0, flat_dot_weight=0, dph_weight=0) == 100
    assert opt.score_maximize_target(final, "balanced_total_dps_dph", weakpoint_weight=0, flat_dot_weight=0, dph_weight=1) == 10


def test_optimizer_can_find_a_progenitor_element_without_changing_its_value(fake_optimizer, monkeypatch):
    candidates = ("A",)
    fake_optimizer(candidates, lambda names: 20 if "Progenitor heat" in names else 10 if any(name.startswith("Progenitor ") for name in names) else len(candidate_order(names, candidates)))
    monkeypatch.setattr(opt, "progenitor_upgrade", lambda element, value, _none: FakeUpgrade(f"Progenitor {element}") if value > 0 and element != opt.NONE else FakeUpgrade(opt.NONE))
    request = make_request(candidates, quality=OPTIMIZE_SEARCH_FAST)
    request.progenitor_element = "cold"
    request.progenitor_value = 0.42
    request.find_optimal_progenitor = True
    result = opt.optimize_build(request)
    assert result.progenitor_optimized
    assert result.progenitor_element == "heat"
    assert request.progenitor_value == 0.42
