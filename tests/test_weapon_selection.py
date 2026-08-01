from warframe_reflex.data import raw_weapons_database, weapon_names_for_type


def test_flattened_weapon_database_preserves_section_type():
    weapons = raw_weapons_database()
    assert weapons
    assert {metadata["type"] for metadata in weapons.values()} <= {"primary", "secondary", "melee", "archgun"}


def test_sniper_category_lists_database_weapons():
    names = weapon_names_for_type("Primary", "Sniper")
    assert "Vectis Prime" in names


def test_weapon_categories_are_separated():
    assert "Vectis Prime" not in weapon_names_for_type("Secondary", "Pistol")
    assert "Vectis Prime" not in weapon_names_for_type("Melee", "Melee")
