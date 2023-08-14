from dataclasses import replace
from datetime import datetime
from uuid import UUID

from urwid_assets.ui.widgets.dialogs.config_dialog import ConfigField, StringConfigField, DateTimeConfigField, \
    ConfigValue, \
    StringConfigValue, DateTimeConfigValue
from urwid_assets.state.snapshots.snapshots import Snapshot, AssetSnapshot


def snapshot_from_add_config_values(uuid: UUID,
                                    snapshot_assets: tuple[AssetSnapshot, ...],
                                    config_values: tuple[ConfigValue, ...]) -> Snapshot:
    name = config_values[0]
    assert isinstance(name, StringConfigValue)
    timestamp = config_values[1]
    assert isinstance(timestamp, DateTimeConfigValue)
    return Snapshot(
        uuid=uuid,
        name=name.value,
        timestamp=timestamp.value,
        assets=snapshot_assets,
    )


def snapshot_from_edit_config_values(snapshot: Snapshot, config_values: tuple[ConfigValue, ...]) -> Snapshot:
    name = config_values[0]
    assert isinstance(name, StringConfigValue)
    return replace(snapshot, name=name.value)


def create_add_snapshot_dialog_config() -> tuple[ConfigField, ...]:
    return (
        StringConfigField(
            name='name',
            display_name=u'Name',
            value=u'New snapshot',
        ),
        DateTimeConfigField(
            name='timestamp',
            display_name=u'Timestamp',
            value=datetime.now(),
        ),
    )


def create_edit_snapshot_dialog_config(name: str) -> tuple[ConfigField, ...]:
    return (
        StringConfigField(
            name='name',
            display_name=u'Name',
            value=name,
        ),
    )
