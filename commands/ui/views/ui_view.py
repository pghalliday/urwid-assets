from asyncio import create_task

from injector import inject, singleton
from urwid import connect_signal, ExitMainLoop

from commands.ui.ui_types import ShowLogPanel
from commands.ui.views.helpers.passphrase_dialog_config import create_passphrase_dialog_config
from commands.ui.views.layout_view import LayoutView
from commands.ui.views.log_view import LogView
from commands.ui.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue, StringConfigValue
from commands.ui.widgets.views.columns_view import ColumnsView, Column
from commands.ui.widgets.views.view_manager import ViewManager
from commands.ui.widgets.views.view_wrap import ViewWrap
from encryption.encryption import Encryption, DecryptionFailure
from lib.data_sources.data_source_registry import DataSourceRegistry


@singleton
class UIView(ViewWrap):
    @inject
    def __init__(
            self,
            view_manager: ViewManager,
            encryption: Encryption,
            data_source_registry: DataSourceRegistry,
            layout_view: LayoutView,
            log_view: LogView,
            show_log_panel: ShowLogPanel,
    ) -> None:
        self._view_manager = view_manager
        self._encryption = encryption
        self._data_source_registry = data_source_registry
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
        passphrase_dialog = ConfigDialog(title=u'Enter passphrase',
                                         config_fields=create_passphrase_dialog_config(),
                                         message=error_message)
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
            create_task(self._data_source_registry.refresh_all())
        except DecryptionFailure:
            self._prompt_for_passphrase(u'Error: Failed to export data file')
            return
        self._view_manager.set_screen(self._layout_view)
