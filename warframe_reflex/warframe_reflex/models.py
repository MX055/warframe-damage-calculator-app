from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EditorField:
    name: str
    label: str
    value: float = 0.0
    min_value: float = -1_000_000_000.0
    max_value: float = 1_000_000_000.0
    integer: bool = False


@dataclass
class DisplayRow:
    label: str
    value: str


@dataclass
class MetricRow:
    label: str
    value: str


@dataclass
class DamageResultRow:
    damage_type: str
    damage: str
    weight: str = ""
    direct_weight: str = ""
    explosion_weight: str = ""
    proc_chance: str = ""


@dataclass
class ContributionRow:
    name: str
    value: str
