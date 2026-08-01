from warframe_reflex.data import raw_upgrade_metadata, upgrade_matches_weapon_type, upgrade_names_for_ui


def matches_cannonade(upgrade_name: str, weapon_category: str, weapon_name: str) -> bool:
    return upgrade_matches_weapon_type(raw_upgrade_metadata(upgrade_name), weapon_category, selected_weapon_name=weapon_name)


def test_semi_only_weapons_allow_cannonade_even_with_linked_aoe_attacks():
    assert matches_cannonade("Semi-Rifle Cannonade", "Rifle", "Tonkor")
    assert matches_cannonade("Semi-Rifle Cannonade", "Rifle", "Latron Prime")
    assert matches_cannonade("Semi-Rifle Cannonade", "Sniper", "Vectis Prime")
    assert matches_cannonade("Semi-Shotgun Cannonade", "Shotgun", "Corinth Prime")


def test_non_semi_or_mixed_trigger_weapons_reject_cannonade():
    assert not matches_cannonade("Semi-Rifle Cannonade", "Rifle", "Braton Prime")
    assert not matches_cannonade("Semi-Rifle Cannonade", "Rifle", "Phenmor")
    assert not matches_cannonade("Semi-Rifle Cannonade", "Bow", "Paris Prime")


def test_updated_slot_metadata_populates_exilus_options():
    options = upgrade_names_for_ui("Sniper", "Vectis Prime", "Normal Attack", True, False, True)

    assert "Vile Precision" in options
