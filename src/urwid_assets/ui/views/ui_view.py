from asyncio import create_task

from injector import inject, singleton, ClassAssistedBuilder
from urwid import connect_signal, ExitMainLoop

from urwid_assets.cli.ui import ShowLogPanel
from urwid_assets.encryption.encryption import Encryption, DecryptionFailure
from urwid_assets.lib.data_sources.data_source_registry import DataSourceRegistry
from urwid_assets.ui.views.helpers.passphrase_dialog_config import create_passphrase_dialog_config
from urwid_assets.ui.views.layout_view import LayoutView
from urwid_assets.ui.views.log_view import LogView
from urwid_assets.ui.widgets.dialogs.config_dialog.config_dialog import ConfigDialog
from urwid_assets.ui.widgets.dialogs.config_dialog.config_value import ConfigValue, StringConfigValue
from urwid_assets.ui.widgets.views.columns_view import ColumnsView, Column
from urwid_assets.ui.widgets.views.view_manager import ViewManager
from urwid_assets.ui.widgets.views.view_wrap import ViewWrap


@singleton
class UIView(ViewWrap):
    @inject
    def __init__(
            self,
            view_manager: ViewManager,
            encryption: Encryption,
            data_source_registry: DataSourceRegistry,
            config_dialog_builder: ClassAssistedBuilder[ConfigDialog],
            layout_view: LayoutView,
            log_view: LogView,
            show_log_panel: ShowLogPanel,
    ) -> None:
        self._view_manager = view_manager
        self._encryption = encryption
        self._data_source_registry = data_source_registry
        self._config_dialog_builder = config_dialog_builder
        self._layout_view = layout_view
        self._prompt_for_passphrase()
        if show_log_panel:
            super().__init__(ColumnsView((
                Column(9, self._view_manager),
                Column(3, log_view),
            )))
        else:
            super().__init__(self._view_manager)

    def _prompt_for_passphrase(self, error_message: str | None = None):
        passphrase_dialog = self._config_dialog_builder.build(
            title=u'Enter passphrase',
            config_fields=create_passphrase_dialog_config(),
            message=error_message
        )
        connect_signal(passphrase_dialog, 'cancel', self._exit)
        connect_signal(passphrase_dialog, 'ok', self._init_passphrase)
        self._view_manager.open_dialog(passphrase_dialog)

    def _exit(self, _):
        raise ExitMainLoop()

    def _init_passphrase(self, _, values: tuple[ConfigValue, ...]):
        self._view_manager.close_dialog()
        passphrase_value = values[0]
        assert isinstance(passphrase_value, StringConfigValue)
        passphrase = passphrase_value.value
        try:
            self._encryption.init_passphrase(passphrase)
            create_task(self._data_source_registry.refresh_rates())
        except DecryptionFailure:
            self._prompt_for_passphrase(u'Error: Failed to decrypt data file')
            return
        self._view_manager.set_screen(self._layout_view)
