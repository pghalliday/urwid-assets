import logging

from injector import inject, singleton, ClassAssistedBuilder
from urwid import Frame, Text, connect_signal, LineBox, WidgetWrap

from urwid_assets.cli.ui import ContentView
from urwid_assets.ui.views.helpers.snapshot_dialog_config import create_edit_snapshot_dialog_config, \
    snapshot_from_edit_config_values
from urwid_assets.ui.views.snapshot_view import SnapshotView
from urwid_assets.ui.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.state.snapshots.snapshots import Snapshot, UPDATE_SNAPSHOT, DELETE_SNAPSHOT, MOVE_SNAPSHOT_UP, \
    MOVE_SNAPSHOT_DOWN
from urwid_assets.state.state import State

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(1, u'Name'),
    Column(1, u'Timestamp'),
)


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Snapshots')))


def _select_snapshots(state: State) -> tuple[Snapshot, ...]:
    return state.snapshots


def _select_row_from_snapshot(snapshot: Snapshot) -> Row[Snapshot]:
    return Row(
        snapshot.uuid,
        (
            snapshot.name,
            snapshot.timestamp.isoformat(),
        ),
        snapshot,
    )


select_rows = create_selector((
    _select_snapshots,
), _select_row_from_snapshot, SelectorOptions(dimensions=(1,)))


@singleton
class SnapshotsView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 content_view: ContentView,
                 snapshot_view_builder: ClassAssistedBuilder[SnapshotView]) -> None:
        self._store = store
        self._view_manager = view_manager
        self._content_view = content_view
        self._snapshot_view_builder = snapshot_view_builder
        self._table = Table(COLUMNS, select_rows(self._store.get_state()))
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('enter',), self._table.with_current_row_data(self._view_snapshot)),
            KeyHandler(('e', 'E'), self._table.with_current_row_data(self._edit_snapshot)),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_snapshot)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_snapshot_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_snapshot_up)),
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

    def _view_snapshot(self, snapshot: Snapshot):
        self._content_view.set_view(self._snapshot_view_builder.build(uuid=snapshot.uuid))

    def _move_snapshot_up(self, snapshot: Snapshot):
        self._store.dispatch(Action(MOVE_SNAPSHOT_UP, snapshot))

    def _move_snapshot_down(self, snapshot: Snapshot):
        self._store.dispatch(Action(MOVE_SNAPSHOT_DOWN, snapshot))

    def _show_help(self):
        help_dialog = MessageBox(u'Help',
                                 (
                                     u' h - Show this help',
                                     u'',
                                     u' enter     - View the selected snapshot',
                                     u' e         - Edit the selected snapshot',
                                     u' backspace - Delete the selected snapshot',
                                     u' k         - Move the selected snapshot UP',
                                     u' j         - Move the selected snapshot DOWN',
                                     u'',
                                     u' q - quit',
                                 )
                                 )
        connect_signal(help_dialog, 'ok', lambda _: self._view_manager.close_dialog())
        self._view_manager.open_dialog(help_dialog)

    def _edit_snapshot(self, snapshot: Snapshot):
        edit_snapshot_dialog = ConfigDialog(
            u'Edit: %s' % snapshot.name,
            create_edit_snapshot_dialog_config(snapshot.name),
        )
        connect_signal(edit_snapshot_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(edit_snapshot_dialog, 'ok', self._dispatch_update_snapshot, snapshot)
        self._view_manager.open_dialog(edit_snapshot_dialog)

    def _delete_snapshot(self, snapshot: Snapshot):
        confirm_dialog = MessageBox(u'Delete: %s' % snapshot.name,
                                    u'Are you sure you wish to delete snapshot: %s' % snapshot.name,
                                    MessageBoxButtons.OK_CANCEL)
        connect_signal(confirm_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(confirm_dialog, 'ok', self._dispatch_delete_snapshot, snapshot)
        self._view_manager.open_dialog(confirm_dialog)

    def _dispatch_update_snapshot(self, _, config_values: tuple[ConfigValue, ...], snapshot: Snapshot):
        self._store.dispatch(Action(UPDATE_SNAPSHOT,
                                    snapshot_from_edit_config_values(snapshot, config_values)))
        self._view_manager.close_dialog()

    def _dispatch_delete_snapshot(self, _, snapshot: Snapshot):
        self._store.dispatch(Action(DELETE_SNAPSHOT, snapshot))
        self._view_manager.close_dialog()

    def _update(self) -> None:
        self._table.update(select_rows(self._store.get_state()))
