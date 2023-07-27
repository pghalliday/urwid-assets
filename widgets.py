from decimal import Decimal

import urwid

import data
from ui_manager import UIManager

COLUMN_WEIGHTS: list[int] = [2, 1, 1, 1]
LOADING_TEXT: str = u'Loading...'

ColumnTuple = tuple[str, int, urwid.Widget]


def get_field(fields: list[urwid.Widget], index: int) -> urwid.Widget:
    try:
        return fields[index]
    except IndexError:
        return BlankField()


def column_tuple(weight: int, field: urwid.Widget) -> ColumnTuple:
    return 'weight', weight, field


def columns(fields: list[urwid.Widget]) -> list[ColumnTuple]:
    return [column_tuple(weight, get_field(fields, index))
            for index, weight in enumerate(COLUMN_WEIGHTS)]


def format_amount(amount: Decimal) -> str:
    return '{}'.format(amount)


class BlankField(urwid.Text):
    def __init__(self) -> None:
        super().__init__(u'')


class AssetEditPopUp(urwid.WidgetWrap):
    signals = [
        'apply',
        'cancel',
    ]

    def __init__(self, name: str, amount: Decimal, price_source: str) -> None:
        super().__init__(urwid.AttrMap(urwid.Filler(urwid.Pile([
            urwid.Text(name),
            urwid.Text(format_amount(amount)),
            urwid.Text(price_source),
            urwid.Button(u'Cancel', self.cancel),
            urwid.Button(u'Apply', self.apply),
        ])), 'popup-bg'))

    def apply(self, _):
        self._emit('apply')

    def cancel(self, _):
        self._emit('cancel')


class AssetSelector(urwid.PopUpLauncher):
    def __init__(self, text: str, asset: data.Asset) -> None:
        super().__init__(urwid.Button(text, self.edit_asset))
        self.asset = asset

    def edit_asset(self, _) -> None:
        self.open_pop_up()

    def create_pop_up(self):
        pop_up = AssetEditPopUp(
            self.asset.name,
            self.asset.amount,
            self.asset.price_source,
        )
        urwid.connect_signal(pop_up, 'apply', self.apply_edit)
        urwid.connect_signal(pop_up, 'cancel', self.cancel_edit)
        return pop_up

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 0, 'overlay_width': 32, 'overlay_height': 5}

    def apply_edit(self, _):
        self.close_pop_up()

    def cancel_edit(self, _):
        self.close_pop_up()


class Field(urwid.Columns):
    def __init__(self, text: str) -> None:
        super().__init__([
            (2, urwid.Text(u'| ')),
            urwid.Text(text),
            (2, urwid.Text(u' |')),
        ])


class ColumnLayout(urwid.Columns):
    def __init__(self, fields: list[urwid.Widget]) -> None:
        super().__init__(columns(fields))


class Row(urwid.WidgetWrap):
    def __init__(self, asset: data.Asset) -> None:
        super().__init__(urwid.AttrMap(ColumnLayout([
            AssetSelector(asset.name, asset),
            Field(format_amount(asset.amount)),
            Field(LOADING_TEXT),
            Field(LOADING_TEXT),
        ]), None, focus_map='reversed'))


class Table(urwid.ListBox):
    def __init__(self, current: list[data.Asset]) -> None:
        super().__init__(urwid.SimpleFocusListWalker(
            [Row(asset) for asset in current]
        ))


class ColumnLabels(ColumnLayout):
    def __init__(self) -> None:
        super().__init__([
            Field(u'Name'),
            Field(u'Amount'),
            Field(u'Unit Price'),
            Field(u'Value'),
        ])


class Header(urwid.Pile):
    def __init__(self) -> None:
        super().__init__([
            ColumnLabels(),
            urwid.Divider(u'-'),
        ])


class Instructions(urwid.Text):
    def __init__(self) -> None:
        super().__init__(u'q - exit')


class Footer(urwid.Pile):
    def __init__(self) -> None:
        super().__init__([
            urwid.Divider(u'-'),
            Instructions(),
        ])


class Layout(urwid.Frame):
    def __init__(self, current: list[data.Asset], ui_manager: UIManager) -> None:
        super().__init__(
            Table(current),
            Header(),
            Footer()
        )
