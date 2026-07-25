"""Profile optimize_build bottlenecks for Corinth Prime."""
from __future__ import annotations
import time
from warframe_reflex.constants import SLOT_CONFIGS, SLOT_POLICY_DISCARD
from warframe_reflex.data import upgrade_names_for_ui, database_upgrade
from warframe_reflex.engine import configured_weapon, is_non_empty_upgrade
from warframe_reflex.optimizer import (
    CANDIDATE_SOFT_CAP, HILL_CLIMB_SWAP_LIMIT, OptimizeRequest, SlotSpec,
    _cap_candidates, _empty_upgrade, optimize_build,
)

WEAPON_TYPE, WEAPON_CATEGORY, WEAPON_NAME = "Primary", "Shotgun", "Corinth Prime"
ATTACK_MODE = ""

def main():
    print("=== Pool sizes (raw vs after _cap_candidates) ===")
    raw_mod = upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, ATTACK_MODE, True, False, False)
    raw_ex = upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, ATTACK_MODE, True, False, True)
    raw_arc = upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, ATTACK_MODE, False, True, False)
    mod_pool = _cap_candidates(raw_mod)
    exilus_pool = _cap_candidates(raw_ex)
    arcane_pool = _cap_candidates(raw_arc)
    print(f"CANDIDATE_SOFT_CAP={CANDIDATE_SOFT_CAP}  HILL_CLIMB_SWAP_LIMIT={HILL_CLIMB_SWAP_LIMIT}")
    print(f"mod:    raw={len(raw_mod):4d}  capped={len(mod_pool):4d}")
    print(f"exilus: raw={len(raw_ex):4d}  capped={len(exilus_pool):4d}")
    print(f"arcane: raw={len(raw_arc):4d}  capped={len(arcane_pool):4d}")

    n_slots = len(SLOT_CONFIGS)
    open_slots = n_slots  # all discard / None
    # rough greedy estimate: for each open slot, try full pool for that kind
    greedy_est = 0
    for cfg in SLOT_CONFIGS:
        if cfg["kind"] == "arcane":
            greedy_est += len(arcane_pool)
        elif cfg.get("stance"):
            continue
        elif cfg["exilus"]:
            greedy_est += len(exilus_pool)
        else:
            greedy_est += len(mod_pool)
    print(f"\n=== Greedy eval estimate ===")
    print(f"open_slots={open_slots}  (sum pool_size over open slots)={greedy_est}")
    print(f"naive open_slots*mod_pool={open_slots * len(mod_pool)}")
    # hill-climb worst case: up to HILL_CLIMB_SWAP_LIMIT successful-loop evals (each swap attempt scores)
    print(f"hill-climb capped at ~{HILL_CLIMB_SWAP_LIMIT} swap attempts (each is 1 score)")
    print(f"baseline+final extras ~2; total rough lower bound ~{greedy_est + 2}")

    print("\n=== configured_weapon microbench ===")
    empty_ups = []
    t0 = time.perf_counter()
    w0 = configured_weapon(WEAPON_TYPE, WEAPON_NAME, custom_weapon=False, base_stats={}, upgrades=empty_ups, custom_entry=None, selected_mode=None, evolutions=None)
    t_empty = time.perf_counter() - t0
    dps0 = float(w0.results.main.final.total_dps)

    # pick ~8 damage-ish mods from capped pool
    picked = []
    for name in mod_pool:
        u = database_upgrade(name, kind="mod", rank=None, stacks=None, condition=True)
        if u is None:
            continue
        picked.append(u)
        if len(picked) >= 8:
            break
    t1 = time.perf_counter()
    w1 = configured_weapon(WEAPON_TYPE, WEAPON_NAME, custom_weapon=False, base_stats={}, upgrades=picked, custom_entry=None, selected_mode=None, evolutions=None)
    t_mods = time.perf_counter() - t1
    dps1 = float(w1.results.main.final.total_dps)
    print(f"empty build: {t_empty*1000:.2f} ms  dps={dps0:,.1f}")
    print(f"~8 mods ({len(picked)}): {t_mods*1000:.2f} ms  dps={dps1:,.1f}  names={[getattr(u,'name',None) or (u.stats.get('name') if hasattr(u,'stats') else None) for u in picked[:3]]}...")
    # try attribute name
    names8 = []
    for u in picked:
        n = getattr(u, "name", None)
        if n is None and hasattr(u, "raw"):
            n = (u.raw or {}).get("name")
        if n is None:
            n = str(u)[:40]
        names8.append(n)
    print(f"  mod names: {names8}")

    print("\n=== optimize_build (Corinth Prime, all None/discard, find_optimal_riven=False) ===")
    slots = [
        SlotSpec(index=i, kind=cfg["kind"], exilus=cfg["exilus"], stance=bool(cfg.get("stance")), selected="None", policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, condition=True)
        for i, cfg in enumerate(SLOT_CONFIGS)
    ]
    req = OptimizeRequest(
        weapon_type=WEAPON_TYPE, weapon_category=WEAPON_CATEGORY, weapon_name=WEAPON_NAME,
        custom_weapon=False, custom_weapon_entry="", attack_mode=ATTACK_MODE, evolutions={},
        progenitor_element="None", progenitor_value=0.0, external_fields={},
        slots=slots, find_optimal_riven=False,
    )
    phases = []
    def progress(phase, frac, evals, best):
        phases.append((phase, frac, evals, best, time.perf_counter()))

    t_opt0 = time.perf_counter()
    phases.append(("start", 0.0, 0, None, t_opt0))
    result = optimize_build(req, progress=progress)
    t_opt = time.perf_counter() - t_opt0
    print(f"wall_time={t_opt:.2f}s  evaluations={result.evaluations}  dps={result.total_dps:,.1f}")
    print(f"message={result.message}")
    print(f"filled slots: {[n for n in result.slot_names if n != 'None']}")
    if result.evaluations:
        print(f"ms/eval ≈ {t_opt*1000/result.evaluations:.2f}")
        print(f"projected from microbench empty: {result.evaluations * t_empty:.2f}s")
        print(f"projected from microbench 8mods: {result.evaluations * t_mods:.2f}s")

    # phase timing deltas
    print("\n=== progress samples (first/last few) ===")
    for row in phases[:5]:
        print(f"  {row[0]!r} frac={row[1]:.2f} evals={row[2]} best={row[3]} t+{row[4]-t_opt0:.2f}s")
    if len(phases) > 10:
        print("  ...")
    for row in phases[-5:]:
        print(f"  {row[0]!r} frac={row[1]:.2f} evals={row[2]} best={row[3]} t+{row[4]-t_opt0:.2f}s")

    # Find when greedy ended vs hill climb
    greedy_end = next((p for p in phases if str(p[0]).startswith("Greedy fill") and "10/" in str(p[0])), None)
    hill = [p for p in phases if str(p[0]).startswith("Hill")]
    if greedy_end:
        print(f"\nAfter last greedy: evals={greedy_end[2]} t+{greedy_end[4]-t_opt0:.2f}s")
    if hill:
        print(f"First hill: evals={hill[0][2]} t+{hill[0][4]-t_opt0:.2f}s")
        print(f"Last hill:  evals={hill[-1][2]} t+{hill[-1][4]-t_opt0:.2f}s")
    print(f"\nGreedy estimate vs actual evals ratio: actual/greedy_est={result.evaluations/max(greedy_est,1):.2f}")

if __name__ == "__main__":
    main()
