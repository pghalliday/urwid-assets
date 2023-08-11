from asyncio import create_task

from injector import inject, singleton
from urwid import connect_signal, ExitMainLoop

from application.application_module import ShowLogPanel
from encryption.encryption import Encryption, DecryptionFailure
from lib.data_sources.data_sources import DataSources
from lib.widgets.dialogs.config_dialog import ConfigDialog, ConfigValue, StringConfigValue
from lib.widgets.views.columns_view import ColumnsView, Column
from lib.widgets.views.view_manager import ViewManager
from lib.widgets.views.view_wrap import ViewWrap
from views.helpers.passphrase_dialog_config import create_passphrase_dialog_config
from views.layout_view import LayoutView
from views.log_view import LogView


@singleton
class ApplicationView(ViewWrap):
    _view_manager: ViewManager
    _encryption: Encryption
    _data_sources: DataSources
    _layout_view: LayoutView

    @inject
    def __init__(
            self,
            view_manager: ViewManager,
            encryption: Encryption,
            data_sources: DataSources,
            layout_view: LayoutView,
            log_view: LogView,
            show_log_panel: ShowLogPanel,
    ) -> None:
        self._view_manager = view_manager
        self._encryption = encryption
        self._data_sources = data_sources
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
            create_task(self._data_sources.refresh_all())
        except DecryptionFailure:
            self._prompt_for_passphrase(u'Error: Failed to decrypt data file')
            return
        self._view_manager.set_screen(self._layout_view)
