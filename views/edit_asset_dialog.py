from decimal import Decimal
from uuid import UUID

from urwid import Edit, Text, Divider, Columns, Button, Pile
from urwid.numedit import FloatEdit

from lib.widgets.view import View
from state.models import Asset


class EditAssetDialog(View):
    signals = [
        'apply',
        'cancel',
    ]
    _uuid: UUID
    _name: Edit
    _amount: FloatEdit
    _price_source: Edit

    def __init__(self,
                 title: str,
                 uuid: UUID,
                 name: str,
                 amount: Decimal,
                 price_source: str,
                 ) -> None:
        self._uuid = uuid
        self._name = Edit(u'Name: ', name)
        self._amount = FloatEdit(u'Amount: ', amount)
        self._price_source = Edit(u'Price source: ', price_source)
        super().__init__(Pile([
            Text(title),
            Divider(u'-'),
            self._name,
            self._amount,
            self._price_source,
            Divider(u'-'),
            Columns([
                Text(u''),
                Button(u'Cancel', self._cancel),
                Button(u'Apply', self._apply),
            ]),
        ]))

    def _apply(self, _):
        self._emit('apply', Asset(
            self._uuid,
            self._name.get_edit_text(),
            self._amount.value(),
            self._price_source.get_edit_text()
        ))

    def _cancel(self, _):
        self._emit('cancel')
