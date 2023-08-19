import logging
from asyncio import create_task
from uuid import uuid1, UUID

from injector import inject, singleton, ClassAssistedBuilder
from urwid import Frame, Text, connect_signal, LineBox, Columns, RIGHT

from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.selectors.selectors import select_symbols, select_rates, select_loaded_rates, select_timestamp_text
from urwid_assets.state.saved.rates.rates import Rate, MOVE_RATE_UP, MOVE_RATE_DOWN, UPDATE_RATE, ADD_RATE, DELETE_RATE
from urwid_assets.state.saved.symbols.symbols import Symbol, get_symbol
from urwid_assets.state.state import State
from urwid_assets.state.ui.ui import LoadedRate
from urwid_assets.ui.views.helpers.format import get_loaded_rate_text
from urwid_assets.ui.views.helpers.rate_dialog_config import DefaultRateDialogConfigFactory, \
    apply_rate_to_rate_dialog_config, rate_from_config_values
from urwid_assets.ui.widgets.dialogs.config_dialog.config_dialog import ConfigDialog
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Cost'),
    Column(1, u'From'),
    Column(1, u'To'),
    Column(1, u'Rate'),
)


def _select_row_from_rate(rate: Rate,
                          loaded_rates: tuple[LoadedRate, ...],
                          symbols: tuple[Symbol, ...]) -> Row[Rate]:
    return Row(
        rate.uuid,
        (
            rate.name,
            str(rate.cost),
            get_symbol(rate.from_symbol, symbols).name,
            get_symbol(rate.to_symbol, symbols).name,
            get_loaded_rate_text(rate.uuid, loaded_rates),
        ),
        rate,
    )


select_rows = create_selector((
    select_rates,
    select_loaded_rates,
    select_symbols,
), _select_row_from_rate, SelectorOptions(dimensions=(1,)))


@singleton
class RatesView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 data_source_registry: DataSourceRegistry,
                 default_rate_dialog_config_factory: DefaultRateDialogConfigFactory,
                 config_dialog_builder: ClassAssistedBuilder[ConfigDialog]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._data_source_registry = data_source_registry
        self._default_rate_dialog_config_factory = default_rate_dialog_config_factory
        self._config_dialog_builder = config_dialog_builder
        state = self._store.get_state()
        self._timestamp_text = Text(select_timestamp_text(state), RIGHT)
        self._table = Table(COLUMNS, select_rows(state))
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('a', 'A'), self._add_rate),
            KeyHandler(('enter',), self._table.with_current_row_data(self._edit_rate)),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_rate)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_rate_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_rate_up)),
            KeyHandler(('r', 'R'), self._refresh_rates),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            LineBox(Columns((
                ('weight', 1, Text(u'Rates')),
                ('weight', 1, self._timestamp_text),
            ))),
            LineBox(Text(u'h - Help')),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _refresh_rates(self):
        create_task(self._data_source_registry.refresh_rates())

    def _move_rate_up(self, rate: Rate):
        self._store.dispatch(Action(MOVE_RATE_UP, rate))

    def _move_rate_down(self, rate: Rate):
        self._store.dispatch(Action(MOVE_RATE_DOWN, rate))

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a         - Add a new rate',
                                     u' enter     - Edit the selected rate',
                                     u' backspace - Delete the selected rate',
                                     u' k         - Move the selected rate UP',
                                     u' j         - Move the selected rate DOWN',
                                     u' r         - Refresh rates',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_rate(self, rate: Rate):
        edit_asset_dialog = self._config_dialog_builder.build(
            title=u'Edit: %s' % rate.name,
            config_fields=apply_rate_to_rate_dialog_config(self._default_rate_dialog_config_factory.create(), rate),
        )
        connect_signal(edit_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_asset_dialog, 'ok', self._dispatch_update_rate, rate.uuid)
        self._view_manager.open_dialog(edit_asset_dialog)

    def _add_rate(self):
        add_asset_dialog = self._config_dialog_builder.build(
            title=u'Add rate',
            config_fields=self._default_rate_dialog_config_factory.create(),
        )
        connect_signal(add_asset_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_asset_dialog, 'ok', self._dispatch_add_rate, uuid1())
        self._view_manager.open_dialog(add_asset_dialog)

    def _delete_rate(self, rate: Rate):
        confirm_dialog = MessageBox(u'Delete: %s' % rate.name,
                                    u'Are you sure you wish to delete rate: %s' % rate.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_rate, rate)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_rate(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(UPDATE_RATE,
                                    rate_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_rate(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(ADD_RATE, rate_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_rate(self, _, rate: Rate):
        self._store.dispatch(Action(DELETE_RATE, rate))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        state = self._store.get_state()
        self._timestamp_text.set_text(select_timestamp_text(state))
        self._table.update(select_rows(state))
