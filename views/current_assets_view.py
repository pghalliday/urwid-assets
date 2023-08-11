import logging
from asyncio import create_task
from decimal import Decimal
from uuid import uuid1, UUID

from injector import inject, singleton
from urwid import Frame, Columns, Text, connect_signal, LineBox, WidgetWrap, RIGHT

from lib.data_sources.data_source import DataSource
from lib.data_sources.data_sources import DataSources
from lib.redux.reselect import create_selector, SelectorOptions
from lib.redux.store import Store, Action
from lib.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue
from lib.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from lib.widgets.table import Column, Row, Table
from lib.widgets.views.linked_view import LinkedView
from lib.widgets.views.view_manager import ViewManager
from state.assets.assets import MOVE_ASSET_DOWN, MOVE_ASSET_UP, Asset, UPDATE_ASSET, ADD_ASSET, DELETE_ASSET
from state.state import State
from views.helpers.asset_dialog_config import DefaultAssetDialogConfigFactory, apply_asset_to_asset_dialog_config, \
    asset_from_config_values

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Amount', RIGHT),
    Column(1, u'Price', RIGHT),
    Column(1, u'Value', RIGHT),
)
NOT_LOADED_TEXT = u'Not loaded'


def _format_amount(amount: Decimal) -> str:
    return f'{amount:,.2f}'


def _format_currency(currency: Decimal) -> str:
    return f'{currency:,.2f}'


def _get_value_text(asset: Asset) -> str:
    if asset.error is None:
        if asset.price is None:
            return NOT_LOADED_TEXT
        return _format_currency(asset.price * asset.amount)
    return asset.error


def _get_price_text(asset: Asset) -> str:
    if asset.error is None:
        if asset.price is None:
            return NOT_LOADED_TEXT
        return _format_currency(asset.price)
    return asset.error


_select_rows = create_selector((
    lambda state: state.assets,
), lambda asset: Row(
    asset.uuid,
    (
        asset.name,
        _format_amount(asset.amount),
        _get_price_text(asset),
        _get_value_text(asset),
    ),
    asset,
), SelectorOptions(dimensions=(1,)))

_select_total = create_selector((
    lambda state: state.assets,
), lambda assets: 'Total: ' + _format_currency(
    sum(tuple(asset.price * asset.amount if asset.price is not None else Decimal(0.0)
              for asset in assets))
))


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Current assets')))


@singleton
class CurrentAssetsView(LinkedView):
    _store: Store[State]
    _view_manager: ViewManager
    _default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory
    _data_sources: DataSources
    _data_source_list: tuple[DataSource, ...]
    _table: Table
    _total_text: Text

    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory,
                 data_sources: DataSources,
                 data_source_list: tuple[DataSource, ...]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._default_asset_dialog_config_factory = default_asset_dialog_config_factory
        self._data_sources = data_sources
        self._data_source_list = data_source_list
        self._table = Table(COLUMNS, _select_rows(self._store.get_state()))
        self._total_text = Text(_select_total(self._store.get_state()), align=RIGHT)
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            LineBox(Columns((
                ('weight', 1, Text(u'h - Help')),
                ('weight', 1, self._total_text),
            ))),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('h', 'H'):
            self._show_help()
            return None
        if key == 'enter':
            row = self._table.get_focused()
            if row is not None:
                self._edit_asset(row.data)
                return None
        if key in ('a', 'A'):
            self._add_asset()
            return None
        if key == 'backspace':
            row = self._table.get_focused()
            if row is not None:
                self._delete_asset(row.data)
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
        if key in ('r', 'R'):
            create_task(self._data_sources.refresh_all())
            return None
        if key in ('s', 'S'):
            LOGGER.info('TODO: snapshots')
            return None
        return key

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a         - Add a new asset',
                                     u' enter     - Edit the selected asset',
                                     u' backspace - Delete the selected asset',
                                     u' k         - Move the selected asset UP',
                                     u' j         - Move the selected asset DOWN',
                                     u' r         - Refresh prices',
                                     u' s         - take a snapshot (TODO)',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_asset(self, asset: Asset):
        edit_asset_dialog = ConfigDialog(
            u'Edit: %s' % asset.name,
            apply_asset_to_asset_dialog_config(self._default_asset_dialog_config_factory.create(), asset),
        )
        connect_signal(edit_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_asset_dialog, 'ok', self._dispatch_update_asset, asset.uuid)
        self._view_manager.open_dialog(edit_asset_dialog)

    def _add_asset(self):
        add_asset_dialog = ConfigDialog(
            u'Add asset',
            self._default_asset_dialog_config_factory.create(),
        )
        connect_signal(add_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_asset_dialog, 'ok', self._dispatch_add_asset, uuid1())
        self._view_manager.open_dialog(add_asset_dialog)

    def _delete_asset(self, asset: Asset):
        confirm_dialog = MessageBox(u'Delete: %s' % asset.name,
                                    u'Are you sure you wish to delete asset: %s' % asset.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_asset, asset)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(UPDATE_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(ADD_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_asset(self, _, asset: Asset):
        self._store.dispatch(Action(DELETE_ASSET, asset))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(_select_rows(self._store.get_state()))
        self._total_text.set_text(_select_total(self._store.get_state()))
