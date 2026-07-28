"""Run the optimizer quality profiles across representative weapon configurations."""
from __future__ import annotations

import argparse
import time
from dataclasses import dataclass

from warframe_reflex.constants import RIVEN_STAT_ALIASES, SLOT_CONFIGS, SLOT_POLICY_DISCARD
from warframe_reflex.data import is_faction_damage_stat, optimizer_excludes_upgrade_by_default, raw_riven_stats_database, raw_weapon_metadata, upgrade_names_for_ui
from warframe_reflex.optimizer import OptimizeRequest, SlotSpec, optimize_build


@dataclass(frozen=True)
class Case:
    label: str
    weapon_type: str
    category: str
    weapon: str
    evolutions: bool = False
    riven: bool = False


CASES = (
    Case("rifle", "Primary", "Rifle", "Braton Prime"),
    Case("shotgun", "Primary", "Shotgun", "Corinth Prime"),
    Case("pistol", "Secondary", "Pistol", "Lex Prime"),
    Case("melee", "Melee", "Melee", "Nikana Prime"),
    Case("incarnon", "Primary", "Bow", "Paris Prime", evolutions=True),
    Case("riven", "Primary", "Shotgun", "Corinth Prime", riven=True),
)


def default_exclusions(case: Case) -> set[str]:
    names = set()
    for include_mods, include_arcanes, exilus_only, stance_only in ((True, False, False, False), (True, False, True, False), (False, True, False, False), (True, False, False, True)):
        names.update(upgrade_names_for_ui(case.category, case.weapon, "", include_mods, include_arcanes, exilus_only, stance_only))
    return {name for name in names if optimizer_excludes_upgrade_by_default(name)}


def riven_context(case: Case) -> tuple[float, dict[str, float], set[str]]:
    if not case.riven:
        return 1.0, {}, set()
    category = {"Shotgun": "shotgun", "Pistol": "pistol", "Melee": "melee"}.get(case.category, "rifle")
    base_stats = {RIVEN_STAT_ALIASES.get(name, name): float(value) for name, value in (raw_riven_stats_database().get(category, {}) or {}).items()}
    metadata = raw_weapon_metadata("", case.weapon)
    disposition = float(metadata.get("disposition", 1.0) or 1.0)
    return disposition, base_stats, {name for name in base_stats if is_faction_damage_stat(name)}


def request_for(case: Case, quality: str) -> OptimizeRequest:
    disposition, base_stats, excluded_riven_stats = riven_context(case)
    slots = [SlotSpec(index=index, kind=config["kind"], exilus=config["exilus"], stance=bool(config.get("stance")), selected="None", policy=SLOT_POLICY_DISCARD, rank=0, stacks=0, condition=True) for index, config in enumerate(SLOT_CONFIGS)]
    return OptimizeRequest(
        weapon_type=case.weapon_type, weapon_category=case.category, weapon_name=case.weapon, custom_weapon=False, custom_weapon_entry="",
        attack_mode="", evolutions={}, combo_count=12 if case.weapon_type == "Melee" else 1, evolution_runtime={},
        progenitor_element="None", progenitor_value=0.0, external_fields={}, slots=slots, find_optimal_riven=case.riven,
        enemy_name="Aerial Commander", enemy_level=100, find_optimal_evolutions=case.evolutions, excluded_upgrades=default_exclusions(case),
        excluded_riven_stats=excluded_riven_stats, riven_disposition=disposition, riven_base_stats=base_stats, search_quality=quality,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", choices=("Fast", "Balanced", "Thorough"), default="Fast")
    parser.add_argument("--case", action="append", choices=tuple(case.label for case in CASES))
    args = parser.parse_args()
    selected = [case for case in CASES if not args.case or case.label in args.case]
    print("case\tquality\tseconds\tevaluations\tscore\ttermination")
    for case in selected:
        started = time.perf_counter()
        result = optimize_build(request_for(case, args.quality))
        print(f"{case.label}\t{args.quality}\t{time.perf_counter() - started:.2f}\t{result.evaluations}\t{result.total_dps:.2f}\t{result.termination_reason}")


if __name__ == "__main__":
    main()
