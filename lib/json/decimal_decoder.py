from decimal import Decimal
from json import JSONDecoder
from typing import Any


def _parse_decimal(num_str: str) -> Decimal:
    return Decimal(num_str)


def loads_with_decimal(json: str) -> Any:
    return JSONDecoder(parse_float=_parse_decimal, parse_int=_parse_decimal).decode(json)
