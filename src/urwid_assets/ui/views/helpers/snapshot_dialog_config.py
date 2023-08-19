from dataclasses import replace
from datetime import datetime
from uuid import UUID

from urwid_assets.state.saved.snapshots.snapshots import SnapshotAsset, Snapshot
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue


def snapshot_from_add_config_values(uuid: UUID,
                                    timestamp: datetime,
                                    snapshot_assets: tuple[SnapshotAsset, ...],
                                    config_values: tuple[ConfigValue, ...]) -> Snapshot:
    name = config_values[0]
    assert isinstance(name, StringConfigValue)
    return Snapshot(
        uuid=uuid,
        name=name.value,
        timestamp=timestamp,
        assets=snapshot_assets,
    )


def snapshot_from_edit_config_values(snapshot: Snapshot, config_values: tuple[ConfigValue, ...]) -> Snapshot:
    name = config_values[0]
    assert isinstance(name, StringConfigValue)
    return replace(snapshot, name=name.value)


def create_snapshot_dialog_config(name: str) -> tuple[ConfigField, ...]:
    return (
        StringConfigField(
            name='name',
            display_name=u'Name',
            value=name,
        ),
    )
