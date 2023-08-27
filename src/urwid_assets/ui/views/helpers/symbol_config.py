from dataclasses import replace
from uuid import UUID

from injector import singleton, inject

from urwid_assets.lib.redux.store import Store
from urwid_assets.selectors.selectors import select_symbols
from urwid_assets.state.saved.symbols.symbols import Symbol
from urwid_assets.state.state import State
from urwid_assets.ui.widgets.dialogs.config_dialog.config_field import ChoiceConfigField, ConfigFieldChoice


def apply_symbol(symbol_config: ChoiceConfigField,
                 symbol: UUID) -> ChoiceConfigField:
    return replace(symbol_config, value=symbol)


def _create_symbol_choice(symbol: Symbol) -> ConfigFieldChoice:
    return ConfigFieldChoice(
        value=symbol.uuid,
        display_text=symbol.name,
        sub_fields=tuple(),
    )


@singleton
class SymbolConfigFactory:
    @inject
    def __init__(self, store: Store[State]):
        self._store = store

    def create_symbol_config(self, name: str, display_name: str) -> ChoiceConfigField:
        symbols = select_symbols(self._store.get_state())
        return ChoiceConfigField(
            name=name,
            display_name=display_name,
            value=symbols[0].uuid,
            choices=tuple(_create_symbol_choice(symbol) for symbol in symbols)
        )
