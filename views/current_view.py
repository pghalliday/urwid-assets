from dataclasses import dataclass
from decimal import Decimal

from injector import inject, singleton
from urwid import Widget, Text, WidgetWrap, AttrMap, Filler, Pile, Button, connect_signal, Columns, ListBox, \
    SimpleFocusListWalker, Divider, Frame

from controllers.data_controller import DataController
from controllers.ui_controller import UIController
from models.models import Asset

COLUMN_WEIGHTS: list[int] = [2, 1, 1, 1]
LOADING_TEXT: str = u'Loading...'

ColumnTuple = tuple[str, int, Widget]


def get_field(fields: list[Widget], index: int) -> Widget:
    try:
        return fields[index]
    except IndexError:
        return BlankField()


def column_tuple(weight: int, field: Widget) -> ColumnTuple:
    return 'weight', weight, field


def columns(fields: list[Widget]) -> list[ColumnTuple]:
    return [column_tuple(weight, get_field(fields, index))
            for index, weight in enumerate(COLUMN_WEIGHTS)]


def format_amount(amount: Decimal) -> str:
    return '{}'.format(amount)


class BlankField(Text):
    def __init__(self) -> None:
        super().__init__(u'')


class AssetEditDialog(WidgetWrap):
    name: str
    amount: Decimal
    price_source: str
    signals = [
        'apply',
        'cancel',
    ]

    def __init__(self, name: str, amount: Decimal, price_source: str) -> None:
        super().__init__(AttrMap(Filler(Pile([
            Text(name),
            Text(format_amount(amount)),
            Text(price_source),
            Button(u'Cancel', self.cancel),
            Button(u'Apply', self.apply),
        ])), 'popup-bg'))

    def apply(self, _):
        self._emit('apply')

    def cancel(self, _):
        self._emit('cancel')


class AssetSelector(Button):
    def __init__(self, text: str, asset: Asset, ui_controller: UIController) -> None:
        super().__init__(text, self.edit_asset)
        self.asset = asset
        self.ui_controller = ui_controller

    def edit_asset(self, _) -> None:
        dialog = AssetEditDialog(
            self.asset.name,
            self.asset.amount,
            self.asset.price_source,
        )
        connect_signal(dialog, 'apply', self.apply_edit)
        connect_signal(dialog, 'cancel', self.cancel_edit)
        self.ui_controller.open_dialog(dialog)

    def apply_edit(self, _):
        self.ui_controller.close_dialog()

    def cancel_edit(self, _):
        self.ui_controller.close_dialog()


@singleton
@inject
@dataclass
class AssetSelectorFactory:
    ui_controller: UIController

    def create(self, text: str, asset: Asset):
        return AssetSelector(text, asset, self.ui_controller)


class Field(Columns):
    def __init__(self, text: str) -> None:
        super().__init__([
            (2, Text(u'| ')),
            Text(text),
            (2, Text(u' |')),
        ])


class ColumnLayout(Columns):
    def __init__(self, fields: list[Widget]) -> None:
        super().__init__(columns(fields))


class Row(WidgetWrap):
    def __init__(self, asset: Asset, asset_selector_factory: AssetSelectorFactory) -> None:
        super().__init__(AttrMap(ColumnLayout([
            asset_selector_factory.create(asset.name, asset),
            Field(format_amount(asset.amount)),
            Field(LOADING_TEXT),
            Field(LOADING_TEXT),
        ]), None, focus_map='reversed'))


@singleton
@inject
@dataclass
class RowFactory:
    asset_selector_factory: AssetSelectorFactory

    def create(self, asset):
        return Row(asset, self.asset_selector_factory)


class Table(ListBox):
    @inject
    def __init__(self, data_controller: DataController, row_factory: RowFactory) -> None:
        super().__init__(SimpleFocusListWalker(
            [row_factory.create(asset)
             for asset
             in data_controller.get_current()]
        ))


class ColumnLabels(ColumnLayout):
    def __init__(self) -> None:
        super().__init__([
            Field(u'Name'),
            Field(u'Amount'),
            Field(u'Unit Price'),
            Field(u'Value'),
        ])


class Header(Pile):
    def __init__(self) -> None:
        super().__init__([
            ColumnLabels(),
            Divider(u'-'),
        ])


class Instructions(Text):
    def __init__(self) -> None:
        super().__init__(u'q - exit')


class Footer(Pile):
    def __init__(self) -> None:
        super().__init__([
            Divider(u'-'),
            Instructions(),
        ])


class CurrentView(Frame):
    @singleton
    @inject
    def __init__(self, table: Table, header: Header, footer: Footer) -> None:
        super().__init__(
            table,
            header,
            footer,
        )
