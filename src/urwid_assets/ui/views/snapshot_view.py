import logging
from decimal import Decimal
from pathlib import Path
from typing import Callable
from uuid import UUID

from injector import inject, singleton, ClassAssistedBuilder
from urwid import Frame, Text, connect_signal, LineBox, RIGHT, Columns

from urwid_assets.lib.redux.reselect import SelectorOptions, create_selector
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.selectors.selectors import select_snapshots
from urwid_assets.state.saved.snapshots.snapshots import Snapshot, get_snapshot, SnapshotAsset, MOVE_ASSET_SNAPSHOT_UP, \
    MOVE_ASSET_SNAPSHOT_DOWN
from urwid_assets.state.state import State
from urwid_assets.ui.views.helpers.export_csv_dialog_config import create_export_csv_dialog_config, \
    get_csv_export_path
from urwid_assets.ui.views.helpers.format import format_amount, format_currency, get_price_text, get_value_text, \
    format_timestamp
from urwid_assets.ui.widgets.dialogs.config_dialog.config_dialog import ConfigDialog
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox
from urwid_assets.ui.widgets.keys import KeyHandler, keys
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Amount', RIGHT),
    Column(1, u'Price', RIGHT),
    Column(1, u'Value', RIGHT),
)

_DEFAULT_EXPORT_PATH = Path('export.csv')


def _select_snapshot(snapshots: tuple[Snapshot, ...], uuid: UUID) -> Snapshot:
    return get_snapshot(uuid, snapshots)


def _select_assets_from_snapshot(snapshot: Snapshot) -> tuple[SnapshotAsset, ...]:
    return snapshot.assets


def _select_row_from_snapshot_asset(snapshot_asset: SnapshotAsset) -> Row[SnapshotAsset]:
    return Row[SnapshotAsset](
        snapshot_asset.uuid,
        (
            snapshot_asset.name,
            format_amount(snapshot_asset.amount),
            get_price_text(snapshot_asset.rate),
            get_value_text(snapshot_asset.rate, snapshot_asset.amount),
        ),
        snapshot_asset,
    )


def _select_total_from_assets(snapshot_assets: tuple[SnapshotAsset, ...]) -> str:
    values = tuple(snapshot_asset.rate * snapshot_asset.amount if snapshot_asset.rate is not None else Decimal(0.0)
                   for snapshot_asset in snapshot_assets)
    return u'Total: ' + format_currency(
        sum(values)
    )


def _quote(text: str) -> str:
    return u'"%s"' % text


def _select_csv_from_assets(snapshot_assets: tuple[SnapshotAsset, ...]) -> str:
    header_row = (_quote(u'Name'), _quote(u'Amount'), _quote(u'Price'))
    asset_rows = tuple((_quote(asset_snapshot.name),
                        _quote(str(asset_snapshot.amount)),
                        _quote(str(asset_snapshot.rate)))
                       for asset_snapshot in snapshot_assets)
    rows = (header_row,) + asset_rows
    return u'\n'.join(u','.join(row) for row in rows) + u'\n'


def _select_name_from_snapshot(snapshot: Snapshot) -> str:
    return u'Snapshot: %s' % snapshot.name


def _select_timestamp_from_snapshot(snapshot: Snapshot) -> str:
    return format_timestamp(snapshot.timestamp)


@singleton
class SnapshotView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 config_dialog_builder: ClassAssistedBuilder[ConfigDialog],
                 uuid: UUID) -> None:
        self._store = store
        self._view_manager = view_manager
        self._config_dialog_builder = config_dialog_builder
        self._uuid = uuid
        self._select_snapshot = self._create_snapshot_selector()
        self._select_assets = self._create_assets_selector()
        self._select_rows = self._create_rows_selector()
        self._select_total = self._create_total_selector()
        self._select_name = self._create_name_selector()
        self._select_timestamp = self._create_timestamp_selector()
        self._select_csv = self._create_csv_selector()
        self._table = Table(COLUMNS, self._select_rows(store.get_state()))
        self._total_text = Text(self._select_total(store.get_state()), align=RIGHT)
        self._name_text = Text(self._select_name(store.get_state()))
        self._timestamp_text = Text(self._select_timestamp(store.get_state()), align=RIGHT)
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('e', 'E'), self._get_csv_export_path),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_asset_snapshot_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_asset_snapshot_up)),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            LineBox(Columns((
                ('weight', 1, self._name_text),
                ('weight', 1, self._timestamp_text),
            ))),
            LineBox(Columns((
                ('weight', 1, Text(u'h - Help')),
                ('weight', 1, self._total_text),
            ))),
        ), store)

    def _select_uuid(self, _):
        return self._uuid

    def _create_snapshot_selector(self) -> Callable[[State], tuple[SnapshotAsset, ...]]:
        return create_selector((
            select_snapshots,
            self._select_uuid,
        ), _select_snapshot)

    def _create_assets_selector(self) -> Callable[[State], tuple[SnapshotAsset, ...]]:
        return create_selector((
            self._select_snapshot,
        ), _select_assets_from_snapshot)

    def _create_rows_selector(self) -> Callable[[State], tuple[Row[SnapshotAsset], ...]]:
        return create_selector((
            self._select_assets,
        ), _select_row_from_snapshot_asset, SelectorOptions(dimensions=(1,)))

    def _create_name_selector(self) -> Callable[[State], str]:
        return create_selector((
            self._select_snapshot,
        ), _select_name_from_snapshot)

    def _create_timestamp_selector(self) -> Callable[[State], str]:
        return create_selector((
            self._select_snapshot,
        ), _select_timestamp_from_snapshot)

    def _create_total_selector(self) -> Callable[[State], str]:
        return create_selector((
            self._select_assets,
        ), _select_total_from_assets)

    def _create_csv_selector(self) -> Callable[[State], str]:
        return create_selector((
            self._select_assets,
        ), _select_csv_from_assets)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _move_asset_snapshot_up(self, snapshot_asset: SnapshotAsset):
        self._store.dispatch(Action(MOVE_ASSET_SNAPSHOT_UP, (self._uuid, snapshot_asset)))

    def _move_asset_snapshot_down(self, snapshot_asset: SnapshotAsset):
        self._store.dispatch(Action(MOVE_ASSET_SNAPSHOT_DOWN, (self._uuid, snapshot_asset)))

    def _get_csv_export_path(self):
        export_csv_dialog = self._config_dialog_builder.build(
            title=u'Export CSV',
            config_fields=create_export_csv_dialog_config(_DEFAULT_EXPORT_PATH)
        )
        connect_signal(export_csv_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(export_csv_dialog, 'ok', self._export_csv)
        self._view_manager.open_dialog(export_csv_dialog)

    def _export_csv(self, _, config_values: tuple[ConfigValue, ...]):
        output_file = get_csv_export_path(config_values)
        csv = self._select_csv(self._store.get_state())
        output_file.write_text(csv)
        self._view_manager.close_dialog()

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' e - Export snapshot to CSV file',
                                     u' k - Move the selected asset UP',
                                     u' j - Move the selected asset DOWN',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _update(self) -> None:
        self._table.update(self._select_rows(self._store.get_state()))
        self._total_text.set_text(self._select_total(self._store.get_state()))
        self._name_text.set_text(self._select_name(self._store.get_state()))
        self._timestamp_text.set_text(self._select_timestamp(self._store.get_state()))
