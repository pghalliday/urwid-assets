from dataclasses import dataclass
from decimal import Decimal

from injector import inject, singleton
from urwid import Widget, Text, WidgetWrap, AttrMap, Pile, Button, connect_signal, Columns, ListBox, \
    SimpleFocusListWalker, Divider, Frame, Edit
from urwid.numedit import FloatEdit

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
    signals = [
        'apply',
        'cancel',
    ]

    def __init__(self, name: str, amount: Decimal, price_source: str) -> None:
        self.name_edit = Edit(u'Name: ', name)
        self.amount_edit = FloatEdit(u'Amount: ', amount)
        self.price_source_edit = Edit(u'Price source: ', price_source)
        super().__init__(ListBox(SimpleFocusListWalker([
            Text(u'Edit Asset'),
            Divider(u'-'),
            self.name_edit,
            self.amount_edit,
            self.price_source_edit,
            Divider(u'-'),
            Columns([
                BlankField(),
                Button(u'Cancel', self.cancel),
                Button(u'Apply', self.apply),
            ]),
        ])))

    def apply(self, _):
        self._emit('apply',
                   self.name_edit.get_edit_text(),
                   Decimal(self.amount_edit.value()),
                   self.price_source_edit.get_edit_text())

    def cancel(self, _):
        self._emit('cancel')


class Field(Columns):
    def __init__(self, text: str) -> None:
        self.text_widget = Text(text)
        super().__init__([
            (2, Text(u'| ')),
            self.text_widget,
            (2, Text(u' |')),
        ])

    def set_text(self, text: str):
        self.text_widget.set_text(text)


class SelectableText(Text):
    _selectable = True

    signals = ['edit']

    def keypress(self, _, key: str) -> str | None:
        if key in ('e', 'E'):
            self._emit('edit')
        else:
            return key


class SelectableField(Columns):
    signals = ['edit']

    def __init__(self, text: str) -> None:
        self.selectable_text = SelectableText(text)
        super().__init__([
            (2, Text(u'| ')),
            self.selectable_text,
            (2, Text(u' |')),
        ])
        connect_signal(self.selectable_text, 'edit', self.edit)

    def set_text(self, text: str):
        self.selectable_text.set_text(text)

    def edit(self, _) -> None:
        self._emit('edit')


class ColumnLayout(Columns):
    def __init__(self, fields: list[Widget]) -> None:
        super().__init__(columns(fields))


class Row(WidgetWrap):
    def __init__(self,
                 asset: Asset,
                 ui_controller: UIController,
                 data_controller: DataController) -> None:
        self.name_field = SelectableField(asset.name)
        self.amount_field = Field(format_amount(asset.amount))
        super().__init__(AttrMap(ColumnLayout([
            self.name_field,
            self.amount_field,
            Field(LOADING_TEXT),
            Field(LOADING_TEXT),
        ]), None, focus_map='reversed'))
        connect_signal(self.name_field, 'edit', self.edit)
        self.asset = asset
        self.ui_controller = ui_controller
        self.data_controller = data_controller

    def edit(self, _) -> None:
        dialog = AssetEditDialog(
            self.asset.name,
            self.asset.amount,
            self.asset.price_source,
        )
        connect_signal(dialog, 'apply', self.apply_edit)
        connect_signal(dialog, 'cancel', self.cancel_edit)
        self.ui_controller.open_dialog(dialog)

    def apply_edit(self, _, name: str, amount: Decimal, price_source: str):
        self.name_field.set_text(name)
        self.amount_field.set_text(format_amount(amount))
        self.data_controller.update_current_asset(self.asset,
                                                  name,
                                                  amount,
                                                  price_source)
        self.ui_controller.close_dialog()

    def cancel_edit(self, _):
        self.ui_controller.close_dialog()


@singleton
@inject
@dataclass
class RowFactory:
    ui_controller: UIController
    data_controller: DataController

    def create(self, asset):
        return Row(asset, self.ui_controller, self.data_controller)


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


class Instructions(Columns):
    def __init__(self) -> None:
        super().__init__([
            Field(u'e - edit asset'),
            Field(u'q - exit'),
        ])


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
