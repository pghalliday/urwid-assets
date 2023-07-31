import logging
from decimal import Decimal
from uuid import uuid1

from injector import inject
from urwid import Frame, Columns, Text, connect_signal, LineBox, WidgetWrap

from lib.redux.reselect import create_selector, SelectorOptions
from lib.redux.store import Store, Action
from lib.widgets.linked_view import LinkedView
from lib.widgets.message_box import MessageBox
from lib.widgets.table import Column, Row, Table
from lib.widgets.view_manager import ViewManager
from state.models import Asset
from state.reducer import UPDATE_ASSET, ADD_ASSET, DELETE_ASSET, MOVE_ASSET_DOWN, MOVE_ASSET_UP
from views.edit_asset_dialog import EditAssetDialog

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Amount'),
    Column(1, u'Price'),
    Column(1, u'Value'),
)
LOADING_TEXT = u'Loading...'


def _format_amount(amount: Decimal) -> str:
    return '{}'.format(amount)


_select_rows = create_selector((
    lambda state: state.assets.current,
), lambda asset: Row(
    asset.uuid,
    (asset.name, _format_amount(asset.amount), LOADING_TEXT, LOADING_TEXT),
    asset,
), SelectorOptions(dimensions=(1,)))


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Current assets')))


class Instructions(Columns):
    def __init__(self) -> None:
        super().__init__([
            Text(u'e - edit'),
            Text(u'a - add'),
            Text(u'd - delete'),
            Text(u's - snapshot'),
            Text(u'q - exit'),
        ])


class Footer(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Instructions()))


class CurrentAssetsScreen(LinkedView):
    _store: Store
    _view_manager: ViewManager
    _rows: tuple[Row, ...]
    _table: Table

    @inject
    def __init__(self, store: Store, view_manager: ViewManager) -> None:
        self._store = store
        self._view_manager = view_manager
        self._rows = _select_rows(self._store.get_state())
        self._table = Table(COLUMNS, self._rows)
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            Footer(),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('e', 'E'):
            row = self._table.get_focused()
            if row is not None:
                edit_asset_dialog = EditAssetDialog(u'Edit: %s' % row.data.name,
                                                    row.data.uuid,
                                                    row.data.name,
                                                    row.data.amount,
                                                    row.data.price_source)
                connect_signal(edit_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
                connect_signal(edit_asset_dialog, 'apply', self._update_asset)
                self._view_manager.open_dialog(edit_asset_dialog)
                return None
        if key in ('a', 'A'):
            add_asset_dialog = EditAssetDialog(u'Add asset',
                                               uuid1(),
                                               u'New asset',
                                               Decimal(0.0),
                                               u'')
            connect_signal(add_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
            connect_signal(add_asset_dialog, 'apply', self._add_asset)
            self._view_manager.open_dialog(add_asset_dialog)
            return None
        if key in ('d', 'D'):
            row = self._table.get_focused()
            if row is not None:
                confirm_dialog = MessageBox(u'Delete: %s' % row.data.name,
                                            u'Are you sure you wish to delete asset: %s' % row.data.name)
                connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
                connect_signal(confirm_dialog, 'ok', self._delete_asset, row.data)
                self._view_manager.open_dialog(confirm_dialog)
                return None
        if key in ('s', 'S'):
            LOGGER.info('TODO: snapshot')
            return None
        if key in ('j', 'J'):
            row = self._table.get_focused()
            if row is not None:
                self._store.dispatch(Action(MOVE_ASSET_DOWN, row.data))
            return None
        if key in ('k', 'K'):
            row = self._table.get_focused()
            if row is not None:
                self._store.dispatch(Action(MOVE_ASSET_UP, row.data))
            return None
        return key

    def _update_asset(self, _, asset: Asset):
        self._store.dispatch(Action(UPDATE_ASSET, asset))
        self._view_manager.close_dialog()

    def _add_asset(self, _, asset: Asset):
        self._store.dispatch(Action(ADD_ASSET, asset))
        self._view_manager.close_dialog()

    def _delete_asset(self, _, asset: Asset):
        self._store.dispatch(Action(DELETE_ASSET, asset))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._rows = _select_rows(self._store.get_state())
        self._table.update(self._rows)
