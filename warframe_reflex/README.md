# Warframe Damage Calculator — Reflex UI

This project is a Reflex port of the Streamlit application. It keeps the existing `warframe_damage_calculator` library as the calculation engine and moves only JSON-serializable editor data through Reflex state.

## Included functionality

- Database and custom Primary, Secondary, and Melee weapons
- Direct-hit, explosion, and forced-proc editors
- Progenitor element support
- Eight normal mod slots, one Exilus slot, and one Arcane slot
- Fixed 5 × 2 upgrade grid with horizontal scrolling on narrow windows
- Conditional bonus checkboxes shown only for upgrades that need them
- Rank, stack, compatibility, requirement, and bow fire-rate handling
- Custom upgrades and external buffs
- Live DPH/DPS, weakpoint, fire-rate, proc, damage-distribution, summary, and contribution results

## Run locally

### With `uv`

```bash
uv sync
uv run reflex run
```

### With `pip`

```bash
py -m pip install -r requirements.txt
reflex run
```

The frontend opens at `http://localhost:3000` and the Reflex backend uses port `8000` by default.

## Developing against a local calculator library

When both repositories are next to each other, install the library in editable mode before running the app:

```bash
py -m pip install -e ../warframe-damage-calculator
py -m pip install -r requirements.txt
reflex run
```

If the Git dependency in `pyproject.toml` would overwrite the editable install, replace it temporarily with a local path dependency or remove that dependency from the file.

## Project structure

```text
warframe_reflex_app/
├── assets/styles.css
├── rxconfig.py
├── pyproject.toml
├── requirements.txt
└── warframe_reflex/
    ├── constants.py
    ├── data.py
    ├── engine.py
    ├── models.py
    ├── state.py
    ├── components.py
    └── warframe_reflex.py
```

## Notes

Reflex state variables must be JSON serializable. The app therefore stores primitive editor values and small dataclasses in state, then reconstructs `Weapon`, `Build`, `Upgrade`, and `dist` objects inside the backend recalculation method. This is intentional and is the main difference from the Streamlit version.
