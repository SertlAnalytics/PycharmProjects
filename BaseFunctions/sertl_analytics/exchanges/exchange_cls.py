"""
Description: This module contains all classes for exchange tradings, like Order, Ticket, ...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Reference: https://docs.bitfinex.com/v1/reference
Date: 2018-08-28
"""

class Balance:
    def __init__(self, balance_type: str, equity: str, amount: float, amount_available: float):
        self.type = balance_type  # 'trading', 'deposit' or 'exchange'
        self.equity = equity  # currency or equity symbol
        self.amount = amount
        self.amount_available = amount_available



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
        self.bid = bid
        self.ask = ask
        self.last_price = last_price
        self.low = low
        self.high = high
        self.vol = vol
        self.time_stamp = ts

    def print(self):
        return 'Bid: {}, Ask: {}, Last: {}, Low: {}, High: {}, Volume: {}, Time: {}'.format(
            self.bid, self.ask, self.last_price, self.low, self.high, self.vol, self.time_stamp
        )


class Order:
    def __init__(self, symbol: str, amount: float, price: float, side: str, order_type: str):
        self.symbol = symbol
        self.amount = amount
        self.price = price
        self.side = side
        self.type = order_type

    def print(self):
        return 'Symbol: {}, Amount: {}, Price={}, Side={}, Type={}'.format(
            self.symbol, self.amount, self.price, self.side, self.type
        )


class OrderBook:
    def __init__(self, bids, bids_price: float, bids_amount, bids_ts,
                 asks, asks_price: float, asks_amount: float, asks_ts: float):
        self.bids = bids  # array
        self.bids_price = bids_price
        self.bids_amount = bids_amount
        self.bids_ts = bids_ts
        self.asks = asks  # array
        self.asks_price = asks_price
        self.asks_amount = asks_amount
        self.asks_ts = asks_ts