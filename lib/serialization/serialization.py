from __future__ import annotations

import json
from decimal import Decimal
from types import UnionType
from typing import Any, get_type_hints, Callable, Type, TypeVar, get_origin, get_args
from uuid import UUID

T = TypeVar('T')


class UnknownSubType(Exception):
    tag: str

    def __init__(self, tag: str):
        self.tag = tag


def _serialize(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, tuple):
        return tuple(_serialize(item) for item in value)
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, (str, int, bool)):
        return value
    return _serialize_kwargs(value)


def _deserialize(arg: Any, field_type: type):
    if arg is None:
        return None
    type_origin = get_origin(field_type)
    type_args = get_args(field_type)
    if type_origin is UnionType:
        return _deserialize(arg, type_args[0])
    if type_origin is tuple:
        assert isinstance(arg, list)
        return tuple(_deserialize(item, type_args[0]) for item in arg)
    if issubclass(field_type, Decimal):
        assert isinstance(arg, str)
        return Decimal(arg)
    if issubclass(field_type, UUID):
        assert isinstance(arg, str)
        return UUID(arg)
    if issubclass(field_type, (str, int, bool)):
        assert isinstance(arg, field_type)
        return arg
    return _deserialize_kwargs(field_type, **arg)


def _get_full_class_name(cls) -> str:
    return '{}.{}'.format(cls.__module__, cls.__qualname__)


class _SubTypeRegistry:
    _field_registry: dict[str, str] = {}
    _tag_registry: dict[str, str] = {}
    _sub_type_registry: dict[str, str] = {}
    _base_type_registry: dict[str, dict[str, type]] = {}

    def register_field(self, cls: type, field: str):
        self._field_registry[_get_full_class_name(cls)] = field

    def register_tag(self, cls: type, tag: str):
        cls_name = _get_full_class_name(cls)
        base: type = cls.__bases__[0]
        base_name = _get_full_class_name(base)
        self._tag_registry[cls_name] = tag
        self._sub_type_registry[cls_name] = base_name
        try:
            d = self._base_type_registry[base_name]
        except KeyError:
            d = {}
            self._base_type_registry[base_name] = d
        d[tag] = cls

    def set_tag(self, cls: type, d: dict[str, Any]) -> None:
        cls_name = _get_full_class_name(cls)
        try:
            tag = self._tag_registry[cls_name]
            base_name = self._sub_type_registry[cls_name]
            field = self._field_registry[base_name]
            d[field] = tag
        except KeyError:
            pass

    def get_sub(self, cls: type, d: dict[str, Any]) -> type | None:
        cls_name = _get_full_class_name(cls)
        try:
            field = self._field_registry[cls_name]
            tag = d[field]
            del d[field]
            return self._base_type_registry[cls_name][tag]
        except KeyError:
            return None


_SUB_TYPE_REGISTRY = _SubTypeRegistry()


def _serialize_kwargs(instance: Any) -> dict[Any, Any]:
    kwargs = {}
    for prop, value in vars(instance).items():
        kwargs[prop] = _serialize(value)
    _SUB_TYPE_REGISTRY.set_tag(instance.__class__, kwargs)
    return kwargs


def serialize(instance: Any):
    kwargs = _serialize_kwargs(instance)
    return json.dumps(kwargs)


def _deserialize_kwargs(cls: type, **kwargs) -> Any:
    sub = _SUB_TYPE_REGISTRY.get_sub(cls, kwargs)
    if sub is None:
        field_types = {field_name: field_type
                       for field_name, field_type in get_type_hints(cls).items()}
        deserialized_kwargs = {key: _deserialize(arg, field_types[key])
                               for key, arg in kwargs.items()}
        return cls(**deserialized_kwargs)
    return _deserialize_kwargs(sub, **kwargs)


def deserialize(cls: type, serialized: str) -> Any:
    kwargs = json.loads(serialized)
    return _deserialize_kwargs(cls, **kwargs)


def serializable(
        sub_type_tag: str | None = None,
        sub_type_field: str = '__type__',
) -> Callable[[Type[T]], Type[T]]:
    def decorator(cls: Type[T]) -> Type[T]:
        if sub_type_field:
            _SUB_TYPE_REGISTRY.register_field(cls, sub_type_field)
        if sub_type_tag:
            _SUB_TYPE_REGISTRY.register_tag(cls, sub_type_tag)
        return cls

    return decorator
