import urwid
import data
from decimal import Decimal

COLUMN_WEIGHTS: list[int] = [2, 1, 1, 1]

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


class ColumnLabel(urwid.Columns):
    def __init__(self, text: str) -> None:
        super().__init__([
            (2, urwid.Text(u'| ')),
            urwid.Text(text),
            (2, urwid.Text(u' |')),
        ])


class Field(urwid.WidgetWrap):
    def __init__(self, text: str) -> None:
        super().__init__(
            urwid.AttrMap(urwid.Button(text),
                          None, focus_map='reversed')
        )


class ColumnLayout(urwid.Columns):
    def __init__(self, fields: list[urwid.Widget]) -> None:
        super().__init__(columns(fields))


class Row(ColumnLayout):
    def __init__(self, asset: data.Asset) -> None:
        super().__init__([
            Field(asset.name),
            Field(format_amount(asset.amount)),
        ])


class Table(urwid.ListBox):
    def __init__(self, current: list[data.Asset]) -> None:
        super().__init__(urwid.SimpleFocusListWalker([Row(asset) for asset in current]))


class ColumnLabels(ColumnLayout):
    def __init__(self) -> None:
        super().__init__([
            ColumnLabel(u'Name'),
            ColumnLabel(u'Amount'),
            ColumnLabel(u'Unit Price'),
            ColumnLabel(u'Value'),
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
    def __init__(self, assets: data.Assets) -> None:
        super().__init__(
            Table(assets.current),
            Header(),
            Footer()
        )
