from warframe_reflex.data import raw_weapons_database, weapon_attack_modes, weapon_names_for_type


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


def test_attack_selector_excludes_linked_child_attacks():
    assert weapon_attack_modes("Corinth Prime") == ("Buckshot", "Air Burst Projectile")
    assert weapon_attack_modes("Tonkor") == ("Grenade Impact",)
    assert weapon_attack_modes("Lenz") == ("Charged Shot",)
    assert "Cannon Mode Explosion" not in weapon_attack_modes("Kuva Zarr")
    assert "Barrage Mode" in weapon_attack_modes("Kuva Zarr")
