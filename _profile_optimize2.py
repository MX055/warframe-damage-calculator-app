"""Warmed microbench + phase split for optimize (short hill optional via monkeypatch)."""
from __future__ import annotations
import time
from warframe_reflex.constants import SLOT_CONFIGS, SLOT_POLICY_DISCARD
from warframe_reflex.data import upgrade_names_for_ui, database_upgrade, raw_upgrade_metadata
from warframe_reflex.engine import configured_weapon
from warframe_reflex import optimizer as opt
from warframe_reflex.optimizer import (
    OptimizeRequest, SlotSpec, _cap_candidates, optimize_build, _db_upgrade, _max_runtime,
)

WEAPON_TYPE, WEAPON_CATEGORY, WEAPON_NAME = "Primary", "Shotgun", "Corinth Prime"

def upgrade_name(u):
    meta = getattr(u, "name", None)
    if isinstance(meta, str):
        return meta
    raw = getattr(u, "raw", None) or getattr(u, "data", None) or {}
    if isinstance(raw, dict) and raw.get("name"):
        return raw["name"]
    d = getattr(u, "__dict__", {})
    return str(d.get("name") or u)

def main():
    mod_pool = _cap_candidates(upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, "", True, False, False))
    exilus_pool = _cap_candidates(upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, "", True, False, True))
    arcane_pool = _cap_candidates(upgrade_names_for_ui(WEAPON_CATEGORY, WEAPON_NAME, "", False, True, False))
    print(f"pools after cap: mod={len(mod_pool)} exilus={len(exilus_pool)} arcane={len(arcane_pool)}")
    greedy_est = sum(len(arcane_pool) if c["kind"]=="arcane" else (len(exilus_pool) if c["exilus"] else len(mod_pool)) for c in SLOT_CONFIGS)
    print(f"greedy estimate open_slots*pool (typed)={greedy_est}")

    # Warm up engine
    configured_weapon(WEAPON_TYPE, WEAPON_NAME, custom_weapon=False, base_stats={}, upgrades=[], custom_entry=None, selected_mode=None, evolutions=None)

    times_empty = []
    for _ in range(5):
        t0 = time.perf_counter()
        configured_weapon(WEAPON_TYPE, WEAPON_NAME, custom_weapon=False, base_stats={}, upgrades=[], custom_entry=None, selected_mode=None, evolutions=None)
        times_empty.append(time.perf_counter() - t0)

    picked_names = []
    picked = []
    for name in mod_pool:
        u = database_upgrade(name, kind="mod", rank=None, stacks=None, condition=True)
        if u is None:
            continue
        picked.append(u)
        picked_names.append(name)
        if len(picked) >= 8:
            break

    times_mods = []
    for _ in range(5):
        t0 = time.perf_counter()
        configured_weapon(WEAPON_TYPE, WEAPON_NAME, custom_weapon=False, base_stats={}, upgrades=picked, custom_entry=None, selected_mode=None, evolutions=None)
        times_mods.append(time.perf_counter() - t0)

    # Time _db_upgrade alone
    t0 = time.perf_counter()
    for name in mod_pool[:50]:
        mr, ms = _max_runtime(name, kind="mod")
        _db_upgrade(name, "mod", mr, ms, True)
    t_db = (time.perf_counter() - t0) / 50

    print(f"configured_weapon empty (n=5): mean={sum(times_empty)/5*1000:.1f} ms  min={min(times_empty)*1000:.1f} max={max(times_empty)*1000:.1f}")
    print(f"configured_weapon ~8 mods (n=5): mean={sum(times_mods)/5*1000:.1f} ms  min={min(times_mods)*1000:.1f} max={max(times_mods)*1000:.1f}")
    print(f"  mods={picked_names}")
    print(f"_db_upgrade+_max_runtime mean (50): {t_db*1000:.2f} ms")

    # Score-cache hit rate estimate: frozenset of upgrade names during greedy
    # (reuse previous full run numbers: 1109 evals, 264s)
    ms_eval = (sum(times_mods)/5) * 1000
    print(f"\nUsing ~{ms_eval:.0f} ms/eval steady-state:")
    print(f"  greedy-only ~{greedy_est} evals => {greedy_est*ms_eval/1000:.1f}s")
    print(f"  greedy+hill200 ~{greedy_est+200} => {(greedy_est+200)*ms_eval/1000:.1f}s")
    print(f"  if soft-cap 40 on mod/arcane: greedy~{8*40+17+40} => ~{(8*40+17+40)*ms_eval/1000:.1f}s")
    print(f"  if soft-cap 60: greedy~{8*60+17+60} => ~{(8*60+17+60)*ms_eval/1000:.1f}s")
    print(f"  skip hill: save ~200*{ms_eval/1000:.2f}s = {200*ms_eval/1000:.1f}s")
    print(f"  cache identical frozensets: greedy revisits rare but hill swaps re-eval many near-duplicates")

    # Quick: time only greedy by setting HILL_CLIMB_SWAP_LIMIT=0
    old = opt.HILL_CLIMB_SWAP_LIMIT
    opt.HILL_CLIMB_SWAP_LIMIT = 0
    slots = [SlotSpec(index=i, kind=c["kind"], exilus=c["exilus"], selected="None", policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, condition=True) for i, c in enumerate(SLOT_CONFIGS)]
    req = OptimizeRequest(weapon_type=WEAPON_TYPE, weapon_category=WEAPON_CATEGORY, weapon_name=WEAPON_NAME, custom_weapon=False, custom_weapon_entry="", attack_mode="", evolutions={}, progenitor_element="None", progenitor_value=0.0, external_fields={}, slots=slots, find_optimal_riven=False)
    marks = []
    def progress(phase, frac, evals, best):
        marks.append((phase, frac, evals, best, time.perf_counter()))
    t0 = time.perf_counter()
    marks.append(("start", 0, 0, None, t0))
    res = optimize_build(req, progress=progress)
    dt = time.perf_counter() - t0
    opt.HILL_CLIMB_SWAP_LIMIT = old
    print(f"\noptimize greedy-only (HILL=0): {dt:.2f}s  evals={res.evaluations}  dps={res.total_dps:,.1f}")
    print(f"  ms/eval={dt*1000/max(res.evaluations,1):.1f}")
    print(f"  message={res.message}")
    for row in marks:
        if str(row[0]).startswith("Greedy") or row[0] in ("Seeded baseline", "Finishing", "Preparing", "start") or "Finishing" in str(row[0]) or "Preparing" in str(row[0]):
            if "Greedy" in str(row[0]) and not any(x in str(row[0]) for x in ("1/", "5/", "10/")):
                continue
            print(f"  {row[0]!r} evals={row[2]} t+{row[4]-t0:.2f}s best={row[3]}")

if __name__ == "__main__":
    main()
