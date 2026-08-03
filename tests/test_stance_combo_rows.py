from warframe_damage_calculator.domain.upgrades import Combo

from warframe_reflex.engine import stance_combo_rows


def test_stance_combo_rows_read_library_combo_objects():
    combos = {
        "lethal_gust": Combo(type="neutral", name="Lethal Gust", multiplier=1.25, hits=4, duration=0.95),
    }
    rows = stance_combo_rows(combos)
    assert len(rows) == 1
    assert rows[0].label == "Lethal Gust"
    assert rows[0].value == "x1.25 · 4 hits / 0.95s"


def test_stance_combo_rows_still_accept_dict_records():
    combos = {
        "crushing_blow": {"type": "heavy", "name": "Crushing Blow", "multiplier": 2.0, "hits": 1, "duration": 0},
    }
    rows = stance_combo_rows(combos)
    assert rows[0].label == "Crushing Blow"
    assert rows[0].value == "x2 · 1 hits"
