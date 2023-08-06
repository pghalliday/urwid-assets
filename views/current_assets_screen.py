import logging
from decimal import Decimal
from functools import reduce
from uuid import uuid1, UUID

from injector import inject
from urwid import Frame, Columns, Text, connect_signal, LineBox, WidgetWrap

from lib.data_source.data_source import DataSource
from lib.redux.reselect import create_selector, SelectorOptions
from lib.redux.store import Store, Action
from lib.widgets.config_dialog import ConfigDialog, ConfigValue
from lib.widgets.linked_view import LinkedView
from lib.widgets.list_dialog import ListDialog
from lib.widgets.message_box import MessageBox, MessageBoxButtons
from lib.widgets.table import Column, Row, Table
from lib.widgets.view_manager import ViewManager
from state.models import Asset, State
from state.reducer import UPDATE_ASSET, ADD_ASSET, DELETE_ASSET, MOVE_ASSET_DOWN, MOVE_ASSET_UP, APPLY_DATA_SOURCE
from views.asset_dialog_config import DefaultAssetDialogConfigFactory, apply_asset_to_asset_dialog_config, \
    asset_from_config_values
from views.data_source_dialog_config import create_data_source_dialog_config, data_source_from_config_values

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


def _format_currency(currency: Decimal) -> str:
    return '{}'.format(currency)


_select_rows = create_selector((
    lambda state: state.assets.current,
), lambda asset: Row(
    asset.uuid,
    (
        asset.name,
        _format_amount(asset.amount),
        LOADING_TEXT if asset.price < 0 else _format_currency(asset.price),
        LOADING_TEXT if asset.price < 0 else _format_currency(asset.price * asset.amount)),
    asset,
), SelectorOptions(dimensions=(1,)))

_select_total = create_selector((
    lambda state: state.assets.current,
), lambda assets: _format_currency(reduce(
    lambda total, asset:
    total + asset.price * asset.amount
    if asset.price > 0
    else Decimal(0.0),
    assets,
    Decimal(0.0)
)))


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
    _store: Store[State]
    _view_manager: ViewManager
    _default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory
    _data_sources: tuple[DataSource, ...]
    _table: Table
    _total_text: Text

    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory,
                 data_sources: tuple[DataSource, ...]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._default_asset_dialog_config_factory = default_asset_dialog_config_factory
        self._data_sources = data_sources
        self._table = Table(COLUMNS, _select_rows(self._store.get_state()))
        self._total_text = Text(_select_total(self._store.get_state()))
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            LineBox(Columns((
                ('weight', 1, Text(u'h - Help')),
                ('weight', 2, Text(u'')),
                ('weight', 1, Text(u'Total: ', align='right')),
                ('weight', 1, self._total_text),
            ))),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('h', 'H'):
            self._show_help()
            return None
        if key in ('e', 'E'):
            row = self._table.get_focused()
            if row is not None:
                self._edit_asset(row.data)
                return None
        if key in ('a', 'A'):
            self._add_asset()
            return None
        if key in ('d', 'D'):
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
        if key in ('c', 'C'):
            self._configure_data_sources()
            return None
        if key in ('s', 'S'):
            LOGGER.info('TODO: snapshot')
            return None
        return key

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a - Add a new asset',
                                     u' e - Edit the selected asset',
                                     u' d - Delete the selected asset',
                                     u' k - Move the selected asset UP',
                                     u' j - Move the selected asset DOWN',
                                     u' c - Configure data sources',
                                     u' s - take a snapshot (TODO)',
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
        connect_signal(edit_asset_dialog, 'apply', self._dispatch_update_asset, asset.uuid)
        self._view_manager.open_dialog(edit_asset_dialog)

    def _add_asset(self):
        add_asset_dialog = ConfigDialog(
            u'Add asset',
            self._default_asset_dialog_config_factory.create(),
        )
        connect_signal(add_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_asset_dialog, 'apply', self._dispatch_add_asset, uuid1())
        self._view_manager.open_dialog(add_asset_dialog)

    def _delete_asset(self, asset: Asset):
        confirm_dialog = MessageBox(u'Delete: %s' % asset.name,
                                    u'Are you sure you wish to delete asset: %s' % asset.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_asset, asset)
        self._view_manager.open_dialog(confirm_dialog)

    def _configure_data_sources(self):
        data_sources_list_dialog = ListDialog(
            u'Configure data sources',
            tuple(data_source.get_display_name() for data_source in self._data_sources),
            0,
        )
        connect_signal(data_sources_list_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        connect_signal(
            data_sources_list_dialog,
            'select',
            lambda _, selected: self._configure_data_source(self._data_sources[selected])
        )
        self._view_manager.open_dialog(data_sources_list_dialog, ('relative', 60))

    def _configure_data_source(self, data_source: DataSource):
        configure_data_source_dialog = ConfigDialog(
            u'Configure %s' % data_source.get_display_name(),
            create_data_source_dialog_config(data_source, self._store.get_state().data_sources),
        )
        connect_signal(configure_data_source_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(configure_data_source_dialog, 'apply', self._dispatch_apply_data_source, data_source.get_name())
        self._view_manager.open_dialog(configure_data_source_dialog)

    def _dispatch_update_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(UPDATE_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(ADD_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_asset(self, _, asset: Asset):
        self._store.dispatch(Action(DELETE_ASSET, asset))
        self._view_manager.close_dialog()

    def _dispatch_apply_data_source(self, _, config_values: tuple[ConfigValue, ...], name: str):
        self._store.dispatch(Action(APPLY_DATA_SOURCE, data_source_from_config_values(name, config_values)))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(_select_rows(self._store.get_state()))
        self._total_text.set_text(_select_total(self._store.get_state()))
