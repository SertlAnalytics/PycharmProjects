"""
https://github.com/Crypto-toolbox/btfxwss
Snapshots (data structure): https://docs.bitfinex.com/v1/reference#ws-auth-order-snapshots
"""

import os
from sertl_analytics.exchanges.bitfinex import MyBitfinex, MyBitfinexTest


# log = logging.getLogger(__name__)
#
# fh = logging.FileHandler('pattern.log')
# fh.setLevel(logging.DEBUG)
# sh = logging.StreamHandler(sys.stdout)
# sh.setLevel(logging.DEBUG)
#
# log.addHandler(sh)
# log.addHandler(fh)
# logging.basicConfig(level=logging.DEBUG, handlers=[fh, sh])


class BTXQ:  # Bitfinex queues types
    ORDERS = 'Orders'
    WALLETS = 'Wallets'
    POSITIONS = 'Positions'
    TRADES = 'Trades'
    ORDERS_CANCELLED = 'Orders_cancelled'
    ORDERS_HISTORICAL = 'Orders_historical'
    TICKET_DATA = 'Ticket_data'
    TRADES_DATA = 'Trades_data'
    ORDER_BOOK_DATA = 'Order_Book_data'
    BALANCE_INFO = 'Balance_info'


class BTXTickerData:
    """
    :param ticker_id:
    :input_stream: ([6696.2, 10.39100737, 6696.3, 28.58829304, -29.8, -0.0044, 6696.2, 18428.0110064, 6789, 6557],
    1535284487.1767092)
    """
    def __init__(self, ticker_id: str, channel_id: int, input_stream: list, ts: float):
        self._ticker_id = ticker_id
        self._channel_id = channel_id  # integer	Channel ID
        self._input_stream = input_stream
        self._bid = self._input_stream[0]  # float Price of last highest bid
        self._ask = self._input_stream[1]  # float	Size of the last highest bid
        self._ask_size = self._input_stream[2]  # float	Size of the last lowest ask
        self._daily_change = self._input_stream[3]  # float	Amount that the last price has changed since yesterday
        self._daily_change_pct = self._input_stream[4]  # float	Amount that the price has changed expressed in pct
        self._last_price = self._input_stream[5]  # float	Price of the last trade
        self._volume = self._input_stream[6]  # float	Daily volume
        self._high = self._input_stream[7]  # float	Daily high
        self._low = self._input_stream[8]  # float	Daily low
        self._ts = ts  # float timestamp


class MyBitfinexTradeClient:
    def __init__(self):
        self._api_key = os.environ['bitfinex_apikey']
        self._api_key_secret = os.environ['bitfinex_apikeysecret']
        self._bitfinex = MyBitfinex(self._api_key, self._api_key_secret)
        self._symbols = self._bitfinex.symbols

    @property
    def bitfinex(self):
        return self._bitfinex

