from uuid import uuid1

from urwid_assets.state.saved.symbols.symbols import Symbol

USD = Symbol(
    uuid=uuid1(),
    name='USD',
)
GBP = Symbol(
    uuid=uuid1(),
    name='GBP',
)
CAD = Symbol(
    uuid=uuid1(),
    name='CAD',
)
EUR = Symbol(
    uuid=uuid1(),
    name='EUR',
)
AAPL = Symbol(
    uuid=uuid1(),
    name='AAPL',
)
TSLA = Symbol(
    uuid=uuid1(),
    name='TSLA',
)
SPY = Symbol(
    uuid=uuid1(),
    name='SPY',
)
IVV = Symbol(
    uuid=uuid1(),
    name='IVV',
)
BTC = Symbol(
    uuid=uuid1(),
    name='BTC',
)
ETH = Symbol(
    uuid=uuid1(),
    name='ETH',
)
LTC = Symbol(
    uuid=uuid1(),
    name='LTC',
)

SYMBOLS = (USD, GBP, CAD, EUR, AAPL, TSLA, SPY, IVV, BTC, ETH, LTC)
