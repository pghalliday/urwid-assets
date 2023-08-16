import logging
from asyncio import create_task
from decimal import Decimal
from uuid import uuid1, UUID

from injector import inject, singleton
from urwid import Frame, Columns, Text, connect_signal, LineBox, WidgetWrap, RIGHT

from urwid_assets.ui.views.helpers.asset_dialog_config import DefaultAssetDialogConfigFactory, \
    apply_asset_to_asset_dialog_config, \
    asset_from_config_values
from urwid_assets.ui.views.helpers.format import format_amount, format_currency, get_value_text, get_price_text
from urwid_assets.ui.views.helpers.snapshot_dialog_config import create_add_snapshot_dialog_config, \
    snapshot_from_add_config_values
from urwid_assets.ui.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue
from urwid_assets.ui.widgets.dialogs.message_box import MessageBox, MessageBoxButtons
from urwid_assets.ui.widgets.keys import keys, KeyHandler
from urwid_assets.ui.widgets.table import Column, Row, Table
from urwid_assets.ui.widgets.views.linked_view import LinkedView
from urwid_assets.ui.widgets.views.view_manager import ViewManager
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.lib.redux.reselect import create_selector, SelectorOptions
from urwid_assets.lib.redux.store import Store, Action
from urwid_assets.state.assets.assets import MOVE_ASSET_DOWN, MOVE_ASSET_UP, Asset, UPDATE_ASSET, ADD_ASSET, \
    DELETE_ASSET
from urwid_assets.state.snapshots.snapshots import ADD_SNAPSHOT, AssetSnapshot
from urwid_assets.state.state import State

LOGGER = logging.getLogger(__name__)

COLUMNS = (
    Column(2, u'Name'),
    Column(1, u'Amount', RIGHT),
    Column(1, u'Price', RIGHT),
    Column(1, u'Value', RIGHT),
)


def _select_assets(state: State) -> tuple[Asset, ...]:
    return state.assets


def _select_row_from_asset(asset: Asset) -> Row[Asset]:
    return Row(
        asset.uuid,
        (
            asset.name,
            format_amount(asset.amount),
            get_price_text(asset),
            get_value_text(asset),
        ),
        asset,
    )


_select_rows = create_selector((
    _select_assets,
), _select_row_from_asset, SelectorOptions(dimensions=(1,)))


def _select_total_from_assets(assets: tuple[Asset, ...]) -> str:
    return 'Total: ' + format_currency(
        sum(tuple(asset.price * asset.amount if asset.price is not None else Decimal(0.0)
                  for asset in assets))
    )


_select_total = create_selector((
    _select_assets,
), _select_total_from_assets)


class Header(WidgetWrap):
    def __init__(self) -> None:
        super().__init__(LineBox(Text(u'Current assets')))


@singleton
class AssetsView(LinkedView):
    @inject
    def __init__(self,
                 store: Store[State],
                 view_manager: ViewManager,
                 default_asset_dialog_config_factory: DefaultAssetDialogConfigFactory,
                 data_source_registry: DataSourceRegistry) -> None:
        self._store = store
        self._view_manager = view_manager
        self._default_asset_dialog_config_factory = default_asset_dialog_config_factory
        self._data_source_registry = data_source_registry
        self._table = Table(COLUMNS, _select_rows(self._store.get_state()))
        self._total_text = Text(_select_total(self._store.get_state()), align=RIGHT)
        self._keys = keys((
            KeyHandler(('h', 'H'), self._show_help),
            KeyHandler(('enter',), self._table.with_current_row_data(self._edit_asset)),
            KeyHandler(('a', 'A'), self._add_asset),
            KeyHandler(('backspace',), self._table.with_current_row_data(self._delete_asset)),
            KeyHandler(('j', 'J'), self._table.with_current_row_data(self._move_asset_down)),
            KeyHandler(('k', 'K'), self._table.with_current_row_data(self._move_asset_up)),
            KeyHandler(('r', 'R'), self._refresh_all),
            KeyHandler(('s', 'S'), self._create_snapshot),
        ))
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
        return self._keys(key)

    def _refresh_all(self):
        create_task(self._data_source_registry.refresh_all())

    def _create_snapshot(self):
        add_snapshot_dialog = ConfigDialog(
            u'Create snapshot',
            create_add_snapshot_dialog_config()
        )
        connect_signal(add_snapshot_dialog, 'cancel', lambda _: self._view_manager.close_dialog())
        connect_signal(add_snapshot_dialog, 'ok', self._dispatch_create_snapshot, uuid1())
        self._view_manager.open_dialog(add_snapshot_dialog)

    def _dispatch_create_snapshot(self, _, config_values: tuple[ConfigValue, ...], uuid: UUID):
        snapshot = snapshot_from_add_config_values(uuid, tuple(AssetSnapshot(
            uuid=asset.uuid,
            name=asset.name,
            amount=asset.amount,
        ) for asset in self._store.get_state().assets), config_values)
        self._store.dispatch(Action(ADD_SNAPSHOT, snapshot))
        create_task(self._data_source_registry.refresh_snapshot(snapshot))
        self._view_manager.close_dialog()

    def _move_asset_up(self, asset: Asset):
        self._store.dispatch(Action(MOVE_ASSET_UP, asset))

    def _move_asset_down(self, asset: Asset):
        self._store.dispatch(Action(MOVE_ASSET_DOWN, asset))

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
