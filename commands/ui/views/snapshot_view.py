import logging
from decimal import Decimal
from typing import Callable
from uuid import UUID

from injector import inject, singleton
from urwid import Frame, Text, connect_signal, LineBox, WidgetWrap, RIGHT, Columns

from commands.ui.views.helpers.format import format_amount, format_currency, get_price_text, get_value_text
from commands.ui.widgets.dialogs.message_box import MessageBox
from commands.ui.widgets.keys import KeyHandler, keys
from commands.ui.widgets.table import Column, Row, Table
from commands.ui.widgets.views.linked_view import LinkedView
from commands.ui.widgets.views.view_manager import ViewManager
from lib.redux.reselect import SelectorOptions, create_selector
from lib.redux.store import Store, Action
from state.snapshots.snapshots import Snapshot, AssetSnapshot, get_snapshot, MOVE_ASSET_SNAPSHOT_DOWN, \
    MOVE_ASSET_SNAPSHOT_UP
from state.state import State

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Amount', RIGHT),
    Column(1, u'Price', RIGHT),
    Column(1, u'Value', RIGHT),
)


class Header(WidgetWrap):
    def __init__(self, text: Text) -> None:
        super().__init__(LineBox(text))


def _select_snapshots(state: State) -> tuple[Snapshot, ...]:
    return state.snapshots


def _select_assets_from_snapshot(snapshots: tuple[Snapshot, ...], uuid: UUID) -> tuple[AssetSnapshot, ...]:
    return get_snapshot(uuid, snapshots).assets


def _select_row_from_snapshot_asset(asset_snapshot: AssetSnapshot) -> Row[AssetSnapshot]:
    return Row[AssetSnapshot](
        asset_snapshot.uuid,
        (
            asset_snapshot.name,
            format_amount(asset_snapshot.amount),
            get_price_text(asset_snapshot),
            get_value_text(asset_snapshot),
        ),
        asset_snapshot,
    )


def _select_total_from_snapshots(asset_snapshots: tuple[AssetSnapshot, ...]) -> str:
    return u'Total: ' + format_currency(
        sum(tuple(asset_snapshot.price * asset_snapshot.amount if asset_snapshot.price is not None else Decimal(0.0)
                  for asset_snapshot in asset_snapshots))
    )


def _select_title_from_snapshot(snapshots: tuple[Snapshot, ...], uuid: UUID) -> str:
    snapshot = get_snapshot(uuid, snapshots)
    return u'Snapshot: %s - %s' % (snapshot.name, snapshot.timestamp.isoformat())


@singleton
class SnapshotView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 uuid: UUID) -> None:
        self._store = store
        self._view_manager = view_manager
        self._uuid = uuid
        self._select_rows = self._create_rows_selector()
        self._select_total = self._create_total_selector()
        self._select_title = self._create_title_selector()
        self._table = Table(COLUMNS, self._select_rows(store.get_state()))
        self._total_text = Text(self._select_total(store.get_state()), align=RIGHT)
        self._title_text = Text(self._select_title(store.get_state()))
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_asset_snapshot_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_asset_snapshot_up)),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            Header(self._title_text),
            LineBox(Columns((
                ('weight', 1, Text(u'h - Help')),
                ('weight', 1, self._total_text),
            ))),
        ), store)

    def _select_uuid(self, _):
        return self._uuid

    def _create_rows_selector(self) -> Callable[[State], tuple[Row[AssetSnapshot], ...]]:
        return create_selector((
            _select_snapshots,
            self._select_uuid,
        ), create_selector((
            _select_assets_from_snapshot,
        ), _select_row_from_snapshot_asset, SelectorOptions(dimensions=(1,))))

    def _create_title_selector(self) -> Callable[[State], str]:
        return create_selector((
            _select_snapshots,
            self._select_uuid,
        ), _select_title_from_snapshot)

    def _create_total_selector(self) -> Callable[[State], str]:
        return create_selector((
            _select_snapshots,
            self._select_uuid,
        ), create_selector((
            _select_assets_from_snapshot,
        ), _select_total_from_snapshots))

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _move_asset_snapshot_up(self, asset_snapshot: AssetSnapshot):
        self._store.dispatch(Action(MOVE_ASSET_SNAPSHOT_UP, (self._uuid, asset_snapshot)))

    def _move_asset_snapshot_down(self, asset_snapshot: AssetSnapshot):
        self._store.dispatch(Action(MOVE_ASSET_SNAPSHOT_DOWN, (self._uuid, asset_snapshot)))

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' k         - Move the selected asset UP',
                                     u' j         - Move the selected asset DOWN',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _update(self) -> None:
        self._table.update(self._select_rows(self._store.get_state()))
        self._total_text.set_text(self._select_total(self._store.get_state()))
        self._title_text.set_text(self._select_title(self._store.get_state()))
