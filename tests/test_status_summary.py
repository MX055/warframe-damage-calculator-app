from warframe_reflex.data import database_enemy, database_upgrade
from warframe_reflex.engine import configured_weapon, effective_damage_rows


def test_status_summary_includes_forced_procs_in_proc_rate():
    upgrades = [database_upgrade("Serration", kind="mod", rank=10)]
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Vectis Prime", upgrades=upgrades, selected_mode="Normal Attack", target=target)
    rows = {row.damage_type: row for row in effective_damage_rows(resolved, melee=False)}

    assert rows["Impact"].forced_procs == "0.0%"
    assert rows["Stagger"].damage == "0.00"
    assert rows["Stagger"].forced_procs == "100.0%"
    assert rows["Stagger"].proc_rate == "100.0%"
    assert rows["Impact"].explosion_damage == "—"
    assert rows["Impact"].explosion_proc_rate == "—"

    _calculator, result = resolved
    selected = result.attacks[result.selected_attack]
    expected_slash = selected.effective.damage.weight("slash") * float(selected.effective.status_chance) + float(selected.effective.forced_procs.get("slash", 0.0))
    assert rows["Slash"].proc_rate == f"{expected_slash:.1%}"


def test_status_summary_fills_explosion_group_for_aoe_children():
    target = database_enemy("Heavy Gunner", level=100, steel_path=False, empowered=False)
    resolved = configured_weapon("Primary", "Tonkor", upgrades=[], selected_mode="Grenade Impact", target=target)
    rows = {row.damage_type: row for row in effective_damage_rows(resolved, melee=False)}
    _calculator, result = resolved
    explosion = result.attacks["grenade_explosion"]
    assert any(row.explosion_damage != "—" for row in rows.values())
    for damage_type, row in rows.items():
        key = damage_type.casefold()
        assert row.explosion_damage == f"{explosion.effective.damage.get(key, 0.0):,.2f}"
        assert row.explosion_weight == f"{explosion.effective.damage.weight(key):,.2f}"
        assert row.explosion_forced_procs == f"{explosion.effective.forced_procs.get(key, 0.0):.1%}"
