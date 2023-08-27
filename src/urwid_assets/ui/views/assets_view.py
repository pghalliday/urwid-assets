import logging
from asyncio import create_task
from decimal import Decimal
from uuid import uuid1, UUID

from injector import inject, singleton, ClassAssistedBuilder
from urwid import Frame, Columns, Text, connect_signal, LineBox, RIGHT

from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.selectors.selectors import \
    select_assets_with_rates, select_target_symbol_uuid, select_timestamp, select_new_snapshot_assets, select_symbols, \
    select_target_symbol_name, select_timestamp_text, select_resolved_timestamp
from urwid_assets.state.saved.assets.assets import MOVE_ASSET_DOWN, MOVE_ASSET_UP, Asset, UPDATE_ASSET, ADD_ASSET, \
    DELETE_ASSET
from urwid_assets.state.saved.snapshots.snapshots import ADD_SNAPSHOT
from urwid_assets.state.saved.symbols.symbols import get_symbol, Symbol, get_symbol_index
from urwid_assets.state.state import State
from urwid_assets.state.ui.ui import SET_TARGET_SYMBOL, SET_TIMESTAMP
from urwid_assets.ui.views.helpers.asset_dialog_config import DefaultAssetDialogConfigFactory, \
    apply_asset_to_asset_dialog_config, \
    asset_from_config_values
from urwid_assets.ui.views.helpers.format import format_amount, format_currency, get_value_text, get_price_text
from urwid_assets.ui.views.helpers.snapshot_dialog_config import create_snapshot_dialog_config, \
    snapshot_from_add_config_values
from urwid_assets.ui.views.helpers.timestamp_dialog_config import create_timestamp_dialog_config, \
    timestamp_from_config_values
from urwid_assets.ui.widgets.dialogs.config_dialog.config_dialog import ConfigDialog
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue
from urwid_assets.ui.widgets.dialogs.list_dialog import ListDialog
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager

_LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Symbol'),
    Column(1, u'Amount', RIGHT),
    Column(1, u'Rate', RIGHT),
    Column(1, u'Value', RIGHT),
)


def _select_row_from_asset(asset_with_rate: tuple[Asset, Decimal | None],
                           symbols: tuple[Symbol, ...]) -> Row[Asset]:
    asset, rate = asset_with_rate
    return Row(
        asset.uuid,
        (
            asset.name,
            get_symbol(asset.symbol, symbols).name,
            format_amount(asset.amount),
            get_price_text(rate),
            get_value_text(rate, asset.amount),
        ),
        asset,
    )


_select_rows = create_selector((
    select_assets_with_rates,
    select_symbols,
), _select_row_from_asset, SelectorOptions(dimensions=(1,)))


def _select_total_from_assets(assets_with_rate: tuple[tuple[Asset, Decimal | None], ...]) -> str:
    values = tuple(asset_with_rate[1] * asset_with_rate[0].amount if asset_with_rate[1] is not None else Decimal(0.0)
                   for asset_with_rate in assets_with_rate)
    return 'Total: ' + format_currency(sum(values))


_select_total = create_selector((
    select_assets_with_rates,
), _select_total_from_assets)


def _select_snapshot_name_from_timestamp(target_symbol_name: str,
                                         timestamp_text: str) -> str:
    return u'%s @ %s' % (target_symbol_name, timestamp_text)


_select_snapshot_name = create_selector((
    select_target_symbol_name,
    select_timestamp_text,
), _select_snapshot_name_from_timestamp)


@singleton
class AssetsView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory,
                 data_source_registry: DataSourceRegistry,
                 config_dialog_builder: ClassAssistedBuilder[ConfigDialog]) -> None:
        self._store = store
        state = self._store.get_state()
        self._view_manager = view_manager
        self._default_asset_dialog_config_factory = default_asset_dialog_config_factory
        self._data_source_registry = data_source_registry
        self._config_dialog_builder = config_dialog_builder
        self._table = Table(COLUMNS, _select_rows(state))
        self._timestamp_text = Text(select_timestamp_text(state), align=RIGHT)
        self._target_symbol_text = Text(select_target_symbol_name(state), align=RIGHT)
        self._total_text = Text(_select_total(state), align=RIGHT)
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('enter',), self._table.with_current_row_data(self._edit_asset)),
            KeyHandler(('a', 'A'), self._add_asset),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_asset)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_asset_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_asset_up)),
            KeyHandler(('r', 'R'), self._refresh_rates),
            KeyHandler(('b', 'B'), self._set_base_symbol),
            KeyHandler(('t', 'T'), self._set_timestamp),
            KeyHandler(('s', 'S'), self._create_snapshot),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            LineBox(Columns((
                ('weight', 2, Text(u'Current assets')),
                ('weight', 2, self._timestamp_text),
                ('weight', 1, self._target_symbol_text),
            ))),
            LineBox(Columns((
                ('weight', 1, Text(u'h - Help')),
                ('weight', 1, self._total_text),
            ))),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _refresh_rates(self) -> None:
        create_task(self._data_source_registry.refresh_rates())

    def _set_base_symbol(self) -> None:
        state = self._store.get_state()
        symbols = select_symbols(state)
        target_symbol = select_target_symbol_uuid(state)
        selected = get_symbol_index(target_symbol, symbols)
        symbols_dialog = ListDialog(title=u'Select base symbol',
                                    entries=tuple(symbol.name for symbol in symbols),
                                    selected=selected)
        connect_signal(symbols_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(symbols_dialog, 'select', self._dispatch_set_base_symbol)
        self._view_manager.open_dialog(dialog=symbols_dialog,
                                       height=('relative', 60))

    def _dispatch_set_base_symbol(self, _, selected: int) -> None:
        state = self._store.get_state()
        symbols = select_symbols(state)
        self._store.dispatch(Action(SET_TARGET_SYMBOL, symbols[selected].uuid))
        self._view_manager.close_dialog()

    def _set_timestamp(self) -> None:
        state = self._store.get_state()
        timestamp = select_timestamp(state)
        set_timestamp_dialog = self._config_dialog_builder.build(
            title=u'Set timestamp',
            config_fields=create_timestamp_dialog_config(timestamp)
        )
        connect_signal(set_timestamp_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(set_timestamp_dialog, 'ok', self._dispatch_set_timestamp)
        self._view_manager.open_dialog(set_timestamp_dialog)

    def _dispatch_set_timestamp(self, _, config_values: tuple[ConfigValue, ...]) -> None:
        timestamp = timestamp_from_config_values(config_values)
        self._store.dispatch(Action(SET_TIMESTAMP, timestamp))
        self._refresh_rates()
        self._view_manager.close_dialog()

    def _create_snapshot(self) -> None:
        state = self._store.get_state()
        add_snapshot_dialog = self._config_dialog_builder.build(
            title=u'Create snapshot',
            config_fields=create_snapshot_dialog_config(_select_snapshot_name(state))
        )
        connect_signal(add_snapshot_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_snapshot_dialog, 'ok', self._dispatch_create_snapshot, uuid1())
        self._view_manager.open_dialog(add_snapshot_dialog)

    def _dispatch_create_snapshot(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID) -> None:
        timestamp = select_resolved_timestamp(self._store.get_state())
        snapshot_assets = select_new_snapshot_assets(self._store.get_state())
        snapshot = snapshot_from_add_config_values(uuid, timestamp, snapshot_assets, config_values)
        self._store.dispatch(Action(ADD_SNAPSHOT, snapshot))
        self._view_manager.close_dialog()

    def _move_asset_up(self, asset: Asset) -> None:
        self._store.dispatch(Action(MOVE_ASSET_UP, asset))

    def _move_asset_down(self, asset: Asset) -> None:
        self._store.dispatch(Action(MOVE_ASSET_DOWN, asset))

    def _show_help(self) -> None:
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a         - Add a new asset',
                                     u' enter     - Edit the selected asset',
                                     u' backspace - Delete the selected asset',
                                     u' k         - Move the selected asset UP',
                                     u' j         - Move the selected asset DOWN',
                                     u' r         - Refresh rates',
                                     u' b         - Set base symbol',
                                     u' t         - Set timestamp',
                                     u' s         - Take a snapshot',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_asset(self, asset: Asset) -> None:
        edit_asset_dialog = self._config_dialog_builder.build(
            title=u'Edit: %s' % asset.name,
            config_fields=apply_asset_to_asset_dialog_config(self._default_asset_dialog_config_factory.create(), asset),
        )
        connect_signal(edit_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_asset_dialog, 'ok', self._dispatch_update_asset, asset.uuid)
        self._view_manager.open_dialog(edit_asset_dialog)

    def _add_asset(self) -> None:
        add_asset_dialog = self._config_dialog_builder.build(
            title=u'Add asset',
            config_fields=self._default_asset_dialog_config_factory.create(),
        )
        connect_signal(add_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_asset_dialog, 'ok', self._dispatch_add_asset, uuid1())
        self._view_manager.open_dialog(add_asset_dialog)

    def _delete_asset(self, asset: Asset) -> None:
        confirm_dialog = MessageBox(u'Delete: %s' % asset.name,
                                    u'Are you sure you wish to delete asset: %s' % asset.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_asset, asset)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID) -> None:
        self._store.dispatch(Action(UPDATE_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_asset(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID) -> None:
        self._store.dispatch(Action(ADD_ASSET, asset_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_asset(self, _, asset: Asset) -> None:
        self._store.dispatch(Action(DELETE_ASSET, asset))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        state = self._store.get_state()
        self._table.update(_select_rows(state))
        self._total_text.set_text(_select_total(state))
        self._timestamp_text.set_text(select_timestamp_text(state))
        self._target_symbol_text.set_text(select_target_symbol_name(state))
