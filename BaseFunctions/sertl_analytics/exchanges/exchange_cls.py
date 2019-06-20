"""
Description: This module contains all classes for exchange tradings, like Order, Ticket, ...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Reference: https://docs.bitfinex.com/v1/reference
Date: 2018-08-28
"""

from sertl_analytics.mydates import MyDate
from sertl_analytics.mystring import MyString
from sertl_analytics.mymath import MyMath
from sertl_analytics.constants.pattern_constants import BT, TSTR, TP


class SmallProfitHandler:
    def __init__(self, min_profit_pct: float, start_profit_pct: float, active=False):
        self._min_profit_pct = min_profit_pct
        self._start_profit_pct = start_profit_pct
        self._active = active

    def can_small_profit_can_be_taken(self, current_pct: float):
        if self._active:
            return False
        return False


class ExchangeConfiguration:
    buy_order_value_max = 100
    automatic_trading_on = False
    small_profit_taking_active = False

    def __init__(self):
        self.exchange_name = self.get_exchange_name()
        self.default_currency = 'USD'
        self.delete_vanished_patterns_from_trade_dict = True
        self.hodl_dict = {}  # currency in upper characters
        self.buy_fee_pct = 0.25
        self.sell_fee_pct = 0.25
        self.ticker_refresh_rate_in_seconds = 5
        self.small_profit_taking_parameters = [1.0, 0.8]  # 1. param: this limit reached => stop loss at 2. param,
        # 2. param: when this stop loss is enabled
        self.cache_ticker_seconds = 30  # keep ticker in the cache
        self.cache_balance_seconds = 300  # keep balances in the cache (it's overwriten when changes happen)
        self.check_ticker_after_timer_intervals = 4  # currently the timer intervall is set to 5 sec, i.e. check each 20 sec.
        self.finish_vanished_trades = False  # True <=> if a pattern is vanished after buying sell the position (market)
        self.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP],
                                    BT.TOUCH_POINT: [TSTR.LIMIT]}
        self.default_trade_strategy_dict = {BT.BREAKOUT: TSTR.TRAILING_STOP, BT.TOUCH_POINT: TSTR.LIMIT}
        self.fibonacci_indicators = {}
        self.bollinger_band_indicators = {}
        self.massive_breakout_pct = 10  # = 10%
        self.ticker_id_list = self.__get_ticker_id_list__()
        self.ticker_id_excluded_from_trade_list = []  # in case we have some issues the datas...
        self.__set_exchange_default_values__()

    def get_exchange_name(self):
        return 'N.N.'

    def deactivate_automatic_trading(self):
        ExchangeConfiguration.automatic_trading_on = False
        self.print_actual_mode(mode_was_changed=True)

    def activate_automatic_trading(self):
        ExchangeConfiguration.automatic_trading_on = True
        self.print_actual_mode(mode_was_changed=True)

    @staticmethod
    def __get_ticker_id_list__() -> list:
        return []  # we want to track only these symbols...

    def __set_exchange_default_values__(self):
        pass

    def print_actual_mode(self, mode_was_changed=False):
        mode = '{}'.format('TRADING (!!!)' if self.automatic_trading_on else 'SIMULATION')
        text = '{} is running {}in {} mode.'.format(self.exchange_name, 'now ' if mode_was_changed else '', mode)
        print(MyString.surround(text))

    def get_fibonacci_indicators(self):
        li = []
        for key, key_list in self.fibonacci_indicators.items():
            for numbers in key_list:
                li.append([key, numbers])
        return li

    def get_bollinger_band_indicators(self):
        li = []
        for key, key_list in self.bollinger_band_indicators.items():
            for numbers in key_list:
                li.append([key, numbers])
        return li


class Balance:
    def __init__(self, balance_type: str, asset: str, amount: float, amount_available: float):
        self.type = balance_type  # 'trading', 'deposit' or 'exchange'
        self.asset = asset.upper()  # currency or equity _symbol
        self.amount = amount
        self.amount_available = amount_available
        self.current_value = 0  # is set later by another call

    def print_balance(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('Type: {}, Asset: {}, Amount: {:.2f}, Amount_available: {:.2f}, Value: {:.2f}$'.format(
            self.type, self.asset, self.amount, self.amount_available, self.current_value
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
                 bid: float, ask: float, last_price: float, low: float, high: float, vol: float, ts: int):
        self.ticker_id = ticker_id
        self.bid = MyMath.round_smart(bid)
        self.ask = MyMath.round_smart(ask)
        self.last_price = MyMath.round_smart(last_price)
        self.low = MyMath.round_smart(low)
        self.high = MyMath.round_smart(high)
        self.vol = MyMath.round_smart(vol)
        self.time_stamp = round(ts)        

    @property
    def date_time_str(self) -> str:
        return str(MyDate.get_date_time_from_epoch_seconds(self.time_stamp))

    def print_ticker(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('{}: Bid: {}, Ask: {}, Last: {}, Low: {}, High: {}, Volume: {}, Time: {} ({})'.format(
            self.ticker_id, self.bid, self.ask, self.last_price, self.low, self.high, self.vol, 
            self.date_time_str, self.time_stamp
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
        self.simulate_transaction = True  # default

    @property
    def side_type(self):
        return '{}_{}'.format(self.side, self.type)

    @property
    def actual_balance_symbol_amount(self):
        if self.actual_symbol_balance:
            return self.actual_symbol_balance.amount
        return 0

    def print_order(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print(self.get_details())

    def get_details(self):
        return 'Symbol: {}, Amount: {}, Price: {}, Side: {}, Type: {}'.format(
            self.symbol, self.amount, self.price, self.side, self.type)


class OrderStatus:
    def __init__(self):
        self.order_id = ''
        self.symbol = ''            # The _symbol name the order belongs to
        self.exchange = ''          # “bitfinex”
        self.price = 0.0            # The price the order was issued at (can be null for market orders)
        self.avg_execution_price = 0.0  # The average price at which this order as been executed so far.
                                        # 0 if the order has not been executed at all
        self.side = ''              # Either “buy” or “sell”
        self.type = ''              # Either “market” / “_limit” / “stop” / “trailing-stop'
        self.time_stamp = 0         # The timestamp the order was submitted
        self.is_live = False        # Could the order still be filled?
        self.is_cancelled = False   # Has the order been cancelled?
        self.is_hidden = False      # Is the order hidden?
        self.oco_order = None       # If the order is an OCO order, the ID of the linked order. or null
        self.was_forced = False     # For margin only true if it was forced by the system
        self.executed_amount = 0.0  # How much of the order has been executed so far in its history?
        self.remaining_amount = 0.0 # How much is still remaining to be submitted?
        self.original_amount = 0.0  # What was the order originally submitted for?
        self.order_trigger = ''     # will be set later
        self.order_comment = ''     # will be set later
        self.trade_strategy = ''    # will be set later
        self._fee_amount = 0

    @property
    def fee_amount(self):
        return self._fee_amount

    def set_fee_amount(self, fee_value: float, as_pct=False):
        amount = self.original_amount if self.executed_amount == 0 else self.executed_amount
        if as_pct:
            self._fee_amount = MyMath.round_smart(self.price * amount * fee_value/100)
        else:
            self._fee_amount = fee_value

    @property
    def value_total(self):
        return MyMath.round_smart(self.price * self.executed_amount + self.fee_amount)

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
        value_dict['Exchange'] = self.exchange
        value_dict['Side'] = self.side
        value_dict['Type'] = self.type
        value_dict['Original_amount'] = self.original_amount
        value_dict['Executed_amount'] = self.executed_amount
        value_dict['Remaining_amount'] = self.remaining_amount
        value_dict['Price'] = self.price
        value_dict['Is_cancelled'] = self.is_cancelled
        value_dict['Fee_amount'] = self.fee_amount
        value_dict['Value_total'] = self.value_total
        value_dict['DateTime'] = MyDate.get_date_time_from_epoch_seconds(self.time_stamp)
        value_dict['Timestamp'] = self.time_stamp
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
