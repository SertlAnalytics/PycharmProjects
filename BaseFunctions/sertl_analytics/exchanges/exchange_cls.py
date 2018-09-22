"""
Description: This module contains all classes for exchange tradings, like Order, Ticket, ...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Reference: https://docs.bitfinex.com/v1/reference
Date: 2018-08-28
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.mystring import MyString
from sertl_analytics.constants.pattern_constants import BT, TSTR, TP


class ExchangeConfiguration:
    def __init__(self):
        self.is_simulation = True
        self.hodl_dict = {}  # currency in upper characters
        self.buy_order_value_max = 0
        self.buy_fee_pct = 0.25
        self.sell_fee_pct = 0.25
        self.ticker_refresh_rate_in_seconds = 5
        self.cache_ticker_seconds = 30  # keep ticker in the cache
        self.cache_balance_seconds = 300  # keep balances in the cache (it's overwriten when changes happen)
        self.check_ticker_after_timer_intervals = 4  # currently the timer intervall is set to 5 sec, i.e. check each 20 sec.
        self.finish_vanished_trades = False  # True <=> if a pattern is vanished after buying sell the position (market)
        self.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP],
                                    BT.TOUCH_POINT: [TSTR.LIMIT]}
        self.default_trade_strategy_dict = {BT.BREAKOUT: TSTR.TRAILING_STOP,
                                    BT.TOUCH_POINT: TSTR.LIMIT}
        self.__set_values__()

    def __set_values__(self):
        pass

    def print_actual_mode(self):
        text = 'Exchange running in {} mode.'.format('SIMULATION' if self.is_simulation else 'TRADING (!!!)')
        print(MyString.surround(text))


class Balance:
    def __init__(self, balance_type: str, asset: str, amount: float, amount_available: float):
        self.type = balance_type  # 'trading', 'deposit' or 'exchange'
        self.asset = asset.upper()  # currency or equity symbol
        self.amount = round(amount, 2)
        self.amount_available = round(amount_available, 2)

    def print_balance(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('Type: {}, Asset: {}, Amount: {:.2f}, Amount_available: {:.2f}'.format(
            self.type, self.asset, self.amount, self.amount_available
        ))


class Ticker:
    """
    Key	Type	Description
    mid	[price]	(bid + ask) / 2
    bid	[price]	Innermost bid
    ask	[price]	Innermost ask
    last_price	[price]	The price at which the last order executed
    low	[price]	Lowest trade price of the last 24 hours
    high	[price]	Highest trade price of the last 24 hours
    volume	[price]	Trading volume of the last 24 hours
    timestamp	[time]	The timestamp at which this information was valid
    """
    def __init__(self, ticker_id: str,
                 bid: float, ask: float, last_price: float, low: float, high: float, vol: float, ts: float):
        self.ticker_id = ticker_id
        self.bid = round(bid, 4)
        self.ask = round(ask, 4)
        self.last_price = round(last_price, 4)
        self.low = round(low, 4)
        self.high = round(high, 4)
        self.vol = round(vol, 2)
        self.time_stamp = round(ts)

    @property
    def date_time_str(self) -> str:
        return str(MyDate.get_date_time_from_epoch_seconds(self.time_stamp))

    def print_ticker(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('{}: Bid: {}, Ask: {}, Last: {}, Low: {}, High: {}, Volume: {}, Time: {}'.format(
            self.ticker_id, self.bid, self.ask, self.last_price, self.low, self.high, self.vol, self.time_stamp
        ))


class OrderApi:
    def __init__(self, symbol: str, amount: float, price: float=0, side: str='', order_type: str=''):
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.side = side
        self.type = order_type
        self.actual_ticker = None
        self.actual_symbol_balance = None
        self.actual_money_balance = None


class Order:
    def __init__(self, api: OrderApi):
        self.symbol = api.symbol
        self.amount = api.amount
        self.price = api.price
        self.side = api.side
        self.type = api.type
        self.actual_ticker = api.actual_ticker
        self.actual_symbol_balance = api.actual_symbol_balance
        self.actual_money_balance = api.actual_money_balance

    @property
    def actual_balance_symbol_amount(self):
        if self.actual_balance_symbol:
            return self.actual_balance_symbol.amount
        return 0

    def print_order(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print(self.get_details())

    def get_details(self):
        return 'Symbol: {}, Amount: {}, Price: {}, Side: {}, Type: {}'.format(
            self.symbol, self.amount, self.price, self.side, self.type)


class OrderStatusApi:
    def __init__(self):
        self.order_id = 0
        self.symbol = ''            # The symbol name the order belongs to
        self.exchange = 'bitfinex'          # “bitfinex”
        self.price = 0              # The price the order was issued at (can be null for market orders)
        self.avg_execution_price = 0  # The average price at which this order as been executed so far.
                                                        # 0 if the order has not been executed at all
        self.side = ''              # Either “buy” or “sell”
        self.type = ''              # Either “market” / “limit” / “stop” / “trailing-stop'
        self.time_stamp = 0         # The timestamp the order was submitted
        self.is_live = False        # Could the order still be filled?
        self.is_cancelled = False   # Has the order been cancelled?
        self.is_hidden = False      # Is the order hidden?
        self.oco_order = None       # If the order is an OCO order, the ID of the linked order. or null
        self.was_forced = False     # For margin only true if it was forced by the system
        self.executed_amount = 0    # How much of the order has been executed so far in its history?
        self.remaining_amount = 0   # How much is still remaining to be submitted?
        self.original_amount = 0    # What was the order originally submitted for?


class OrderStatus:
    def __init__(self, api: OrderStatusApi):
        self.order_id = api.order_id
        self.symbol = api.symbol
        self.exchange = api.exchange
        self.price = api.price
        self.avg_execution_price = api.avg_execution_price
        self.side = api.side
        self.type = api.type
        self.time_stamp = round(api.time_stamp)
        self.is_live = False
        self.is_cancelled = api.is_cancelled
        self.is_hidden = False
        self.oco_order = None
        self.was_forced = False
        self.executed_amount = api.executed_amount
        self.remaining_amount = api.remaining_amount
        self.original_amount = api.original_amount
        self.order_trigger = ''  # will be set later
        self.order_comment = ''  # will be set later
        self.trade_process = '' # will be set later
        self.trade_strategy = ''  # will be set later
        self._fee_amount = 0

    @property
    def fee_amount(self):
        return self._fee_amount

    def set_fee_amount(self, fee_value: float, as_pct=False):
        amount = self.original_amount if self.executed_amount == 0 else self.executed_amount
        if as_pct:
            self._fee_amount = round(self.price * amount * fee_value/100, 2)
        else:
            self._fee_amount = fee_value

    @property
    def value_total(self):
        return round(self.price * self.executed_amount + self.fee_amount, 2)

    def print_order_status(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('\n'.join('{}: {}'.format(key, value) for key, value in self.get_value_dict().items()))

    def print_with_other_order_status(self, other_order_status, columns: list):
        value_dict_self = self.get_value_dict()
        value_dict_other = other_order_status.get_value_dict()
        print('\n{:16}{:^23}{:^23}'.format('', columns[0], columns[1]))
        for key, values in value_dict_self.items():
            print('{:16}{}{:23}{:23}'.format(key, ':  ', str(values), str(value_dict_other[key])))

    def get_value_dict(self) -> dict:
        value_dict = {}
        value_dict['Order_Id'] = self.order_id
        value_dict['Symbol'] = self.symbol
        value_dict['Order_trigger'] = self.order_trigger
        value_dict['Trade_strategy'] = self.trade_strategy
        value_dict['Trade_process'] = self.trade_process
        value_dict['Exchange'] = self.exchange
        value_dict['Side'] = self.side
        value_dict['Type'] = self.type
        # value_dict['Original_amount'] = self.original_amount
        value_dict['Executed_amount'] = self.executed_amount
        value_dict['Price'] = self.price
        # value_dict['Is_cancelled'] = self.is_cancelled
        value_dict['Fee_amount'] = self.fee_amount
        value_dict['Value_total'] = self.value_total
        value_dict['DateTime'] = MyDate.get_date_time_from_epoch_seconds(self.time_stamp)
        # value_dict['Timestamp'] = self.time_stamp
        return value_dict


class OrderBook:
    def __init__(self, bids, bids_price: float, bids_amount, bids_ts,
                 asks, asks_price: float, asks_amount: float, asks_ts: float):
        self.bids = bids  # array
        self.bids_price = bids_price
        self.bids_amount = bids_amount
        self.bids_ts = round(bids_ts)
        self.asks = asks  # array
        self.asks_price = asks_price
        self.asks_amount = asks_amount
        self.asks_ts = round(asks_ts)

    def print_order_book(self, prefix=''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('Bids: {}\nBids_price: {}\nBids_amount: {}\nBids_time: {}' \
              '\nAsks: {}\nAsks_price: {}\nAsks_amount: {}\nAsks_time: {}'.format(
            self.bids, self.bids_price, self.bids_amount, MyDate.get_date_time_from_epoch_seconds(self.bids_ts),
            self.asks, self.asks_price, self.asks_amount, MyDate.get_date_time_from_epoch_seconds(self.asks_ts)
        ))
