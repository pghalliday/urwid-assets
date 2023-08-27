from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ConfigField, StringConfigField


def create_passphrase_dialog_config() -> tuple[ConfigField, ...]:
    return (StringConfigField(
        name='passphrase',
        display_name=u'Passphrase',
        value=u'',
        secret=True
    ),)
