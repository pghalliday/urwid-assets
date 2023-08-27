from typing import Any, Callable

from urwid_assets.migration.migrate_0_1 import migrate_0_1

_MIGRATIONS: tuple[Callable[[dict[str, Any]], dict[str, Any]], ...] = (
    migrate_0_1,
)


def migrate(serialized: dict[str, Any]) -> dict[str, Any]:
    try:
        version = serialized['version']
    except KeyError:
        version = 0
    for i in range(version, len(_MIGRATIONS)):
        serialized = _MIGRATIONS[i](serialized)
    return serialized
