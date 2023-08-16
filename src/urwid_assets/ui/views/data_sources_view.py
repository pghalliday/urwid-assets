import logging
from typing import Callable
from uuid import uuid1, UUID

from injector import inject, singleton
from urwid import Frame, Text, connect_signal, LineBox, WidgetWrap

from urwid_assets.ui.views.helpers.data_source_dialog_config import DefaultDataSourceDialogConfigFactory, \
    apply_data_source_to_data_source_dialog_config, data_source_from_config_values
from urwid_assets.ui.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.state.data_sources.data_sources import MOVE_DATA_SOURCE_DOWN, MOVE_DATA_SOURCE_UP, DataSourceInstance, \
    UPDATE_DATA_SOURCE, \
    ADD_DATA_SOURCE, DELETE_DATA_SOURCE
from urwid_assets.state.state import State

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(1, u'Name'),
    Column(1, u'Type'),
)


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Data sources')))


def _select_data_sources(state: State) -> tuple[DataSourceInstance, ...]:
    return state.data_sources


@singleton
class DataSourcesView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_data_source_dialog_config_factory: DefaultDataSourceDialogConfigFactory,
                 data_source_registry: DataSourceRegistry) -> None:
        self._store = store
        self._view_manager = view_manager
        self._default_data_source_dialog_config_factory = default_data_source_dialog_config_factory
        self._data_source_registry = data_source_registry
        self._select_rows = self._create_rows_selector()
        self._table = Table(COLUMNS, self._select_rows(self._store.get_state()))
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('enter',), self._table.with_current_row_data(self._edit_data_source)),
            KeyHandler(('a', 'A'), self._add_data_source),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_data_source)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_data_source_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_data_source_up)),
        ))
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            LineBox(Text(u'h - Help')),
        ), store)

    def _create_rows_selector(self) -> Callable[[State], tuple[Row[DataSourceInstance], ...]]:
        return create_selector((
            _select_data_sources,
        ), self._select_row_from_data_source, SelectorOptions(dimensions=(1,)))

    def _select_row_from_data_source(self, data_source: DataSourceInstance) -> Row[DataSourceInstance]:
        return Row(
            data_source.uuid,
            (
                data_source.name,
                self._data_source_registry.get_data_source(data_source.type).get_display_name()
            ),
            data_source,
        )

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        return self._keys(key)

    def _move_data_source_up(self, data_source: DataSourceInstance):
        self._store.dispatch(Action(MOVE_DATA_SOURCE_UP, data_source))

    def _move_data_source_down(self, data_source: DataSourceInstance):
        self._store.dispatch(Action(MOVE_DATA_SOURCE_DOWN, data_source))

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' a         - Add a new data source',
                                     u' enter     - Edit the selected data source',
                                     u' backspace - Delete the selected data source',
                                     u' k         - Move the selected data source UP',
                                     u' j         - Move the selected data source DOWN',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_data_source(self, data_source: DataSourceInstance):
        edit_data_source_dialog = ConfigDialog(
            u'Edit: %s' % data_source.name,
            apply_data_source_to_data_source_dialog_config(self._default_data_source_dialog_config_factory.create(),
                                                           data_source),
        )
        connect_signal(edit_data_source_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_data_source_dialog, 'ok', self._dispatch_update_data_source, data_source.uuid)
        self._view_manager.open_dialog(edit_data_source_dialog)

    def _add_data_source(self):
        add_data_source_dialog = ConfigDialog(
            u'Add data source',
            self._default_data_source_dialog_config_factory.create(),
        )
        connect_signal(add_data_source_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_data_source_dialog, 'ok', self._dispatch_add_data_source, uuid1())
        self._view_manager.open_dialog(add_data_source_dialog)

    def _delete_data_source(self, data_source: DataSourceInstance):
        confirm_dialog = MessageBox(u'Delete: %s' % data_source.name,
                                    u'Are you sure you wish to delete data source: %s' % data_source.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_data_source, data_source)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_data_source(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(UPDATE_DATA_SOURCE,
                                    data_source_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_data_source(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(ADD_DATA_SOURCE,
                                    data_source_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_data_source(self, _, data_source: DataSourceInstance):
        self._store.dispatch(Action(DELETE_DATA_SOURCE, data_source))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(self._select_rows(self._store.get_state()))
