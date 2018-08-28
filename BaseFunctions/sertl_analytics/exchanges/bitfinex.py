"""
Description: This module is the base class for our dash - deferred classes required.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Original, i.e. copied from: https://github.com/scottjbarr/bitfinex/blob/develop/bitfinex/client.py
Date: 2018-06-17
"""


from __future__ import absolute_import
import requests
import json
import base64
import hmac
import hashlib
import time
from sertl_analytics.exchanges.exchange_abc import ExInterface
from sertl_analytics.exchanges.exchange_cls import Order, OrderBook, Balance, Ticker


class MyBitfinexTest:
    def __init__(self):
        self.a = 'a'
        self.b = 'b'

    def print_text(self, text: str):
        print(text)

    def print_another_text(self, text, str):
        print(text)


class BitfinexFactory:
    @staticmethod
    def get_balance_by_json_dict(json: dict) -> Balance:
        # {'type': 'exchange', 'currency': 'usd', 'amount': '12.743', 'available': '12.743'}
        return Balance(json['type'], json['currency'], float(json['amount']), float(json['available']))

    @staticmethod
    def get_ticker_by_json_dict(json: dict) -> Ticker:
        # {'mid': 7052.45, 'bid': 7052.4, 'ask': 7052.5, 'last_price': 7051.3, 'timestamp': 1535469615.659593}
        return Ticker(json['bid'], json['ask'], json['last_price'], 0, 0, 0, json['timestamp'])


class BuyMarketOrder(Order):
    def __init__(self, symbol: str, amount: float):
        Order.__init__(self, symbol, amount, 0.00, 'buy', 'exchange market')


class SellMarketOrder(Order):
    def __init__(self, symbol: str, amount: float):
        Order.__init__(self, symbol, amount, 0.00, 'sell', 'exchange market')


class MyBitfinex(ExInterface):
    def __init__(self, api_key: str, api_secret_key: str):
        self.base_currency = 'usd'
        self.http_timeout = 5.0 # HTTP request timeout in seconds
        self.url = 'https://api.bitfinex.com/v1'
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.symbols = self.get_symbols()

    @property
    def nonce(self):
        return str(time.time() * 1000000)

    def delete_order(self, order_id: int):
        payload_additional = {"order_id": order_id}
        json_resp = self.__get_json__('/order/cancel', payload_additional)
        try:
            json_resp['avg_execution_price']
        except:
            return json_resp['message']
        return json_resp

    def delete_all_orders(self):
        return self.__get_json__('/order/cancel/all')

    def create_order(self, order: Order):
        payload_additional = {
            'symbol': order.symbol, 'amount': str(order.amount), 'price': str(order.price),
            'exchange': 'bitfinex', 'side': order.side, 'type': order.type
        }
        json_resp = self.__get_json__('/order/new', payload_additional)
        try:
            json_resp['order_id']
        except:
            return json_resp['message']
        return json_resp

    def sell_all(self, symbol: str):
        balance = self.__get_balance_for_symbol__(symbol)
        if balance:
            print('Could sell {} from {}. Do you really want...'.format(balance.amount_available,
                                                                        balance.equity))
            order_sell_all = SellMarketOrder(symbol, balance.amount_available)
            # self.create_order(order_sell_all)
        else:
            print('No amounts available for {}'.format(symbol))

    def buy_available(self, symbol: str):
        balance = self.__get_balance_for_symbol__(self.base_currency)
        ticker = self.get_ticker(symbol)
        if balance:
            amount = balance.amount / ticker.ask
            order_buy_all = BuyMarketOrder(symbol, amount)
            print('Could buy {} of {}. Do you really want...'.format(amount, symbol))
            # self.create_order(order_buy_all)
        else:
            print('No {} balance available'.format(self.base_currency))

    def __get_balance_for_symbol__(self, symbol: str) -> Balance:
        balance_dict_list = self.get_balances()
        for balance_dict in balance_dict_list:
            if balance_dict['currency'] == symbol:
                return BitfinexFactory.get_balance_by_json_dict(balance_dict)
        return None

    def get_order(self, order_id: int):
        payload_additional = {"order_id": order_id}
        json_resp = self.__get_json__('/order/status', payload_additional)
        try:
            json_resp['avg_execution_price']
        except:
            return json_resp['message']
        return json_resp

    def get_active_orders(self):
        return self.__get_json__('/orders')

    def get_active_positions(self):
        return self.__get_json__('/positions')

    def get_past_trades(self, symbol: str, from_time_stamp: float):
        payload_additional = {"symbol": symbol, "timestamp": from_time_stamp}
        return self.__get_json__('/positions', payload_additional)

    def get_balances(self):
        json_resp = self.__get_json__('/balances')
        return [list_entries for list_entries in json_resp if list_entries['amount'] != '0.0']

    def get_summary(self):  # Returns a 30-day summary of your trading volume and return on margin funding.
        return self.__get_json__('/summary')

    def get_history(self, since_ts: int, until_ts, limit: int):
        raise NotImplementedError

    def get_symbols(self):
        return self.__get_requests_result__(self.__get_full_url__('symbols'))

    def get_ticker(self, symbol: str):
        data = self.__get_requests_result__(self.__get_full_url__('ticker/{}'.format(symbol)))
        data_converted = self.__convert_to_floats__(data)
        return BitfinexFactory.get_ticker_by_json_dict(data_converted)

    def get_order_book(self, symbol: str, parameter_dict: dict=None):
        """
        curl "https://api.bitfinex.com/v1/book/btcusd"
        {"bids":[{"price":"561.1101","amount":"0.985","timestamp":"1395557729.0"}],"asks":[{"price":"562.9999","amount":"0.985","timestamp":"1395557711.0"}]}
        The 'bids' and 'asks' arrays will have multiple bid and ask dicts.
        Optional parameters
        limit_bids (int): Optional. Limit the number of bids returned. May be 0 in which case the array of bids is empty. Default is 50.
        limit_asks (int): Optional. Limit the number of asks returned. May be 0 in which case the array of asks is empty. Default is 50.
        eg.
        curl "https://api.bitfinex.com/v1/book/btcusd?limit_bids=1&limit_asks=0"
        {"bids":[{"price":"561.1101","amount":"0.985","timestamp":"1395557729.0"}],"asks":[]}
        """
        data = self.__get_requests_result__(self.__get_full_url__('book/{}'.format(symbol), parameters=parameter_dict))

        for type_ in data.keys():
            for list_ in data[type_]:
                for key, value in list_.items():
                    list_[key] = float(value)
        return data

    def __get_json__(self, path: str, payload_additional: dict = None):
        payload = {
            'request': '/v1{}'.format(path),  # like /order/cancel
            'nonce': self.nonce
        }
        if payload_additional:
            for key, values in payload_additional.items():
                payload[key] = values

        signed_payload = self.__get_signed_payload__(payload)
        r = requests.post(self.url + path, headers=signed_payload, verify=True)
        return r.json()

    def __get_signed_payload__(self, payload: dict):
        j = json.dumps(payload)
        data = base64.standard_b64encode(j.encode('utf8'))
        h = hmac.new(self.api_secret_key.encode('utf8'), data, hashlib.sha384)
        signature = h.hexdigest()
        return {
            "X-BFX-APIKEY": self.api_key,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": data
        }

    @staticmethod
    def __convert_to_floats__(data_dict: dict):
        return {key: float(value) for key, value in data_dict.items()}

    def __get_requests_result__(self, url: str):
        return requests.get(url, timeout=self.http_timeout).json()

    def __get_full_url__(self, path: str, parameters: dict=None):
        url = '{}/{}'.format(self.url, path)
        if parameters:
            url = '{}?{}'.format(url, self.__build_parameters__(parameters))
        return url

    @staticmethod
    def __build_parameters__(parameters: dict):
        # sort the keys so we can test easily in Python 3.3 (dicts are not ordered)
        keys_sorted = list(parameters.keys())
        keys_sorted.sort()
        return '&'.join(['{}={}'.format(k, parameters[k]) for k in keys_sorted])