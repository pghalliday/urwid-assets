import logging
from uuid import uuid1, UUID

from injector import inject, singleton, ClassAssistedBuilder
from urwid import Frame, Text, connect_signal, LineBox, WidgetWrap

from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.selectors.selectors import select_symbols
from urwid_assets.state.saved.symbols.symbols import Symbol, MOVE_SYMBOL_UP, MOVE_SYMBOL_DOWN, UPDATE_SYMBOL, \
    DELETE_SYMBOL, ADD_SYMBOL
from urwid_assets.state.state import State
from urwid_assets.ui.views.helpers.symbol_dialog_config import create_symbol_dialog_config, \
    symbol_from_config_values
from urwid_assets.ui.widgets.dialogs.config_dialog.config_dialog import ConfigDialog
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(1, u'Name'),
)


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Symbols')))


def _select_row_from_symbol(symbol: Symbol) -> Row[Symbol]:
    return Row(
        symbol.uuid,
        (
            symbol.name,
        ),
        symbol,
    )


select_rows = create_selector((
    select_symbols,
), _select_row_from_symbol, SelectorOptions(dimensions=(1,)))


@singleton
class SymbolsView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 config_dialog_builder: ClassAssistedBuilder[ConfigDialog]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._config_dialog_builder = config_dialog_builder
        self._table = Table(COLUMNS, select_rows(self._store.get_state()))
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('a', 'A'), self._add_symbol),
            KeyHandler(('enter',), self._table.with_current_row_data(self._edit_symbol)),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_symbol)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_symbol_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_symbol_up)),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            LineBox(Text(u'h - Help')),
        ), store)

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _move_symbol_up(self, symbol: Symbol):
        self._store.dispatch(Action(MOVE_SYMBOL_UP, symbol))

    def _move_symbol_down(self, symbol: Symbol):
        self._store.dispatch(Action(MOVE_SYMBOL_DOWN, symbol))

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a         - Add a new symbol',
                                     u' enter     - Edit the selected symbol',
                                     u' backspace - Delete the selected symbol',
                                     u' k         - Move the selected symbol UP',
                                     u' j         - Move the selected symbol DOWN',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_symbol(self, symbol: Symbol):
        edit_symbol_dialog = self._config_dialog_builder.build(
            title=u'Edit: %s' % symbol.name,
            config_fields=create_symbol_dialog_config(symbol.name),
        )
        connect_signal(edit_symbol_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_symbol_dialog, 'ok', self._dispatch_update_symbol, symbol)
        self._view_manager.open_dialog(edit_symbol_dialog)

    def _add_symbol(self):
        add_symbol_dialog = self._config_dialog_builder.build(
            title=u'Add symbol',
            config_fields=create_symbol_dialog_config(u'New Symbol')
        )
        connect_signal(add_symbol_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_symbol_dialog, 'ok', self._dispatch_add_symbol, uuid1())
        self._view_manager.open_dialog(add_symbol_dialog)

    def _delete_symbol(self, symbol: Symbol):
        confirm_dialog = MessageBox(u'Delete: %s' % symbol.name,
                                    u'Are you sure you wish to delete symbol: %s' % symbol.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_symbol, symbol)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_symbol(self, _, config_values: tuple[ConfigValue, ...], symbol: Symbol):
        self._store.dispatch(Action(UPDATE_SYMBOL,
                                    symbol_from_config_values(symbol.uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_symbol(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(ADD_SYMBOL, symbol_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_symbol(self, _, symbol: Symbol):
        self._store.dispatch(Action(DELETE_SYMBOL, symbol))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(select_rows(self._store.get_state()))
