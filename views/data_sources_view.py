import logging
from typing import Callable
from uuid import uuid1, UUID

from injector import inject, singleton
from urwid import Frame, Text, connect_signal, LineBox, WidgetWrap

import state.data_sources
from lib.data_source import DataSource
from lib.redux.reselect import create_selector, SelectorOptions
from lib.redux.store import Store, Action
from lib.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue
from lib.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from lib.widgets.table import Column, Row, Table
from lib.widgets.views.linked_view import LinkedView
from lib.widgets.views.view_manager import ViewManager
from state import State
from state.data_sources import MOVE_DATA_SOURCE_DOWN, MOVE_DATA_SOURCE_UP
from views.helpers.data_source_dialog_config import DefaultDataSourceDialogConfigFactory, \
    apply_data_source_to_data_source_dialog_config, data_source_from_config_values

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(1, u'Name'),
    Column(1, u'Type'),
)


class UnknownDataSource(Exception):
    name: str

    def __init__(self, name: str):
        self.name = name


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Data sources')))


@singleton
class DataSourcesView(LinkedView):
    _store: Store[State]
    _view_manager: ViewManager
    _default_data_source_dialog_config_factory: DefaultDataSourceDialogConfigFactory
    _data_sources: tuple[DataSource, ...]
    _table: Table
    _select_rows: Callable[[State], tuple[Row[DataSource], ...]]

    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_data_source_dialog_config_factory: DefaultDataSourceDialogConfigFactory,
                 data_sources: tuple[DataSource, ...]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._default_data_source_dialog_config_factory = default_data_source_dialog_config_factory
        self._data_sources = data_sources
        self._select_rows = self._create_rows_selector()
        self._table = Table(COLUMNS, self._select_rows(self._store.get_state()))
        super().__init__(Frame(
            LineBox(self._table),
            Header(),
            LineBox(Text(u'h - Help')),
        ), store)

    def _get_data_source(self, name) -> DataSource:
        for data_source in self._data_sources:
            if data_source.get_name() == name:
                return data_source
        raise UnknownDataSource(name)

    def _create_rows_selector(self) -> Callable[[State], tuple[Row[DataSource], ...]]:
        return create_selector((
            lambda state: state.data_sources,
        ), lambda data_source: Row(
            data_source.uuid,
            (
                data_source.name,
                self._get_data_source(data_source.type).get_display_name()
            ),
            data_source,
        ), SelectorOptions(dimensions=(1,)))

    def keypress(self, size: int, key: str) -> str | None:
        if super().keypress(size, key) is None:
            return None
        if key in ('h', 'H'):
            self._show_help()
            return None
        if key == 'enter':
            row = self._table.get_focused()
            if row is not None:
                self._edit_data_source(row.data)
                return None
        if key in ('a', 'A'):
            self._add_data_source()
            return None
        if key == 'backspace':
            row = self._table.get_focused()
            if row is not None:
                self._delete_data_source(row.data)
                return None
        if key in ('j', 'J'):
            row = self._table.get_focused()
            if row is not None:
                self._store.dispatch(Action(MOVE_DATA_SOURCE_DOWN, row.data))
            return None
        if key in ('k', 'K'):
            row = self._table.get_focused()
            if row is not None:
                self._store.dispatch(Action(MOVE_DATA_SOURCE_UP, row.data))
            return None
        return key

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

    def _edit_data_source(self, data_source: state.data_sources.DataSource):
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

    def _delete_data_source(self, data_source: state.data_sources.DataSource):
        confirm_dialog = MessageBox(u'Delete: %s' % data_source.name,
                                    u'Are you sure you wish to delete data source: %s' % data_source.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_data_source, data_source)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_data_source(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(state.data_sources.UPDATE_DATA_SOURCE,
                                    data_source_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_add_data_source(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        self._store.dispatch(Action(state.data_sources.ADD_DATA_SOURCE,
                                    data_source_from_config_values(uuid, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_data_source(self, _, data_source: state.data_sources.DataSource):
        self._store.dispatch(Action(state.data_sources.DELETE_DATA_SOURCE, data_source))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(self._select_rows(self._store.get_state()))
