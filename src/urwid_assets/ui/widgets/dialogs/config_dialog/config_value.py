from __future__ import annotations

from _decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConfigValue:
    name: str


@dataclass(frozen=True)
class StringConfigValue(ConfigValue):
    value: str


@dataclass(frozen=True)
class DecimalConfigValue(ConfigValue):
    value: Decimal


@dataclass(frozen=True)
class IntegerConfigValue(ConfigValue):
    value: int


@dataclass(frozen=True)
class ChoiceConfigValue(ConfigValue):
    value: Any
    sub_values: tuple[ConfigValue, ...]


@dataclass(frozen=True)
class CheckBoxConfigValue(ConfigValue):
    value: bool
    sub_values: tuple[ConfigValue, ...] | None


@dataclass(frozen=True)
class DateTimeConfigValue(ConfigValue):
    value: datetime


@dataclass(frozen=True)
class PathConfigValue(ConfigValue):
    value: Path
