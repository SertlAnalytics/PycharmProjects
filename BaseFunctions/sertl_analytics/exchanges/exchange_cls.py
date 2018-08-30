"""
Description: This module contains all classes for exchange tradings, like Order, Ticket, ...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Reference: https://docs.bitfinex.com/v1/reference
Date: 2018-08-28
"""

from sertl_analytics.mydates import MyDate


class ExchangeConfiguration:
    def __init__(self):
        self.is_simulation = True
        self.hodl_dict = {}  # currency in upper characters
        self.buy_order_value_max = 0
        self.__set_values__()

    def __set_values__(self):
        pass


class Balance:
    def __init__(self, balance_type: str, asset: str, amount: float, amount_available: float):
        self.type = balance_type  # 'trading', 'deposit' or 'exchange'
        self.asset = asset.upper()  # currency or equity symbol
        self.amount = amount
        self.amount_available = amount_available

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
    def __init__(self, bid: float, ask: float, last_price: float, low: float, high: float, vol: float, ts: float):
        self.bid = round(bid, 4)
        self.ask = round(ask, 4)
        self.last_price = round(last_price, 4)
        self.low = round(low, 4)
        self.high = round(high, 4)
        self.vol = vol
        self.time_stamp = round(ts)

    def print_ticker(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('Bid: {}, Ask: {}, Last: {}, Low: {}, High: {}, Volume: {}, Time: {}'.format(
            self.bid, self.ask, self.last_price, self.low, self.high, self.vol, self.time_stamp
        ))


class Order:
    def __init__(self, symbol: str, amount: float, price: float, side: str, order_type: str):
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.side = side
        self.type = order_type
        self.actual_ticker = None
        self.actual_money_available = 0
        self.actual_balance_symbol = None

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


class OrderStatus:
    def __init__(self, order_id: int, symbol: str, exchange: str, price: float, avg_execution_price: float,
                 side: str, order_type: str, executed_amount: float, original_amount: float,
                 remaining_amount: float, is_cancelled: bool, time_stamp: float):
        self.order_id = order_id
        self.symbol = symbol        # The symbol name the order belongs to
        self.exchange = exchange    # “bitfinex”
        self.price = price          # The price the order was issued at (can be null for market orders)
        self.avg_execution_price = avg_execution_price  # The average price at which this order as been executed so far.
                                                        # 0 if the order has not been executed at all
        self.side = side            # Either “buy” or “sell”
        self.type = order_type      # Either “market” / “limit” / “stop” / “trailing-stop'
        self.time_stamp = round(time_stamp)  # The timestamp the order was submitted
        self.is_live = False        # Could the order still be filled?
        self.is_cancelled = is_cancelled   # Has the order been cancelled?
        self.is_hidden = False      # Is the order hidden?
        self.oco_order = None       # If the order is an OCO order, the ID of the linked order. or null
        self.was_forced = False     # For margin only true if it was forced by the system
        self.executed_amount = executed_amount # How much of the order has been executed so far in its history?
        self.remaining_amount = remaining_amount # How much is still remaining to be submitted?
        self.original_amount = original_amount # What was the order originally submitted for?


    def print_order_status(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print('Order_Id: {}\nSymbol: {}\nExchange: {}\nPrice: {}\nSide: {}\nType: {}\n' \
               'Is_cancelled: {}\nExecuted_amount: {}\nDateTime: {}\nTimestamp: {}'.format(
            self.order_id, self.symbol, self.exchange, self.price, self.side, self.type, self.is_cancelled,
            self.executed_amount, MyDate.get_date_time_from_epoch_seconds(self.time_stamp), self.time_stamp
        ))


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