from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TypeVar, Generic, Any

T = TypeVar('T')


@dataclass(frozen=True)
class ConfigField:
    name: str
    display_name: str

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        raise NotImplementedError()


@dataclass(frozen=True)
class StringConfigField(ConfigField):
    value: str
    secret: bool = False

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_string(self)


@dataclass(frozen=True)
class DecimalConfigField(ConfigField):
    value: Decimal

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_decimal(self)


@dataclass(frozen=True)
class IntegerConfigField(ConfigField):
    value: int

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_integer(self)


@dataclass(frozen=True)
class ConfigFieldChoice:
    value: Any
    display_text: str
    sub_fields: tuple[ConfigField, ...]


@dataclass(frozen=True)
class ChoiceConfigField(ConfigField):
    value: Any
    choices: tuple[ConfigFieldChoice, ...]

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_choice(self)


@dataclass(frozen=True)
class CheckBoxConfigField(ConfigField):
    value: bool
    sub_fields: tuple[ConfigField, ...]

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_check_box(self)


@dataclass(frozen=True)
class DateTimeConfigField(ConfigField):
    value: datetime

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_date_time(self)


@dataclass(frozen=True)
class PathConfigField(ConfigField):
    value: Path

    def visit(self, visitor: ConfigFieldVisitor[T]) -> T:
        return visitor.do_path(self)


class ConfigFieldVisitor(Generic[T]):
    def do_string(self, config_field: StringConfigField) -> T:
        raise NotImplementedError()

    def do_decimal(self, config_field: DecimalConfigField) -> T:
        raise NotImplementedError()

    def do_integer(self, config_field: IntegerConfigField) -> T:
        raise NotImplementedError()

    def do_choice(self, config_field: ChoiceConfigField) -> T:
        raise NotImplementedError()

    def do_check_box(self, config_field: CheckBoxConfigField) -> T:
        raise NotImplementedError()

    def do_date_time(self, config_field: DateTimeConfigField) -> T:
        raise NotImplementedError()

    def do_path(self, config_field: PathConfigField) -> T:
        raise NotImplementedError()
