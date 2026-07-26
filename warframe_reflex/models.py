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
class RuntimeToggleField:
    name: str
    label: str
    value: bool = True


@dataclass
class RuntimeStackField:
    name: str
    label: str
    value: int
    max_value: int


@dataclass
class ClearBuffRow:
    name: str
    label: str
    keep: bool


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
