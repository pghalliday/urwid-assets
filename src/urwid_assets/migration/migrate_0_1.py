from typing import Any
from uuid import uuid1


class _Name:
    def __init__(self, prefix: str):
        self._index: int = 0
        self._prefix = prefix

    def get(self):
        self._index += 1
        return '%s%s' % (self._prefix, self._index)


def migrate_0_1(serialized: dict[str, Any]) -> dict[str, Any]:
    # Migrate assets to symbols, rates and assets. Bear in mind, we do not know the
    # 'to' symbols for the rates or the names of the symbols, so we will leave them
    # as None or placeholder names. This means that we will have to report errors for
    # unset symbols in the UI so that the user can add the symbols after migration
    # without losing data
    symbols, rates, assets = [], [], []
    symbol_name = _Name('SYM_')
    rate_name = _Name('RATE_')
    for asset in serialized['assets']:
        from_symbol_uuid = str(uuid1())
        to_symbol_uuid = str(uuid1())
        rate_uuid = str(uuid1())
        symbols.append({
            'uuid': from_symbol_uuid,
            'name': symbol_name.get()
        })
        symbols.append({
            'uuid': to_symbol_uuid,
            'name': symbol_name.get()
        })
        rates.append({
            'uuid': rate_uuid,
            'name': rate_name.get(),
            'cost': 1,
            'from_symbol': from_symbol_uuid,
            'to_symbol': to_symbol_uuid,
            'data_source': asset['data_source']['uuid'],
            'endpoint': asset['data_source']['endpoint'],
            'config': asset['data_source']['config'],
        })
        assets.append({
            'uuid': asset['uuid'],
            'name': asset['name'],
            'amount': asset['amount'],
            'symbol': from_symbol_uuid,
        })
    # Snapshot assets no longer record errors as the rate loading
    # has been separated out from assets
    # Rename the price field to rate
    for snapshot in serialized['snapshots']:
        for asset in snapshot['assets']:
            asset['rate'] = asset['price']
            del asset['price']
            del asset['error']
    new_serialized = dict(serialized)
    new_serialized.update({
        'version': 1,
        'symbols': symbols,
        'rates': rates,
        'assets': assets,
    })
    return new_serialized
