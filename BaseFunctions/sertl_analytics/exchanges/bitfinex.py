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
from sertl_analytics.exchanges.exchange_cls import Order, OrderStatus, OrderBook, Balance, Ticker, ExchangeConfiguration
from sertl_analytics.mydates import MyDate


class OT:
    EXCHANGE_MARKET = 'exchange market'
    EXCHANGE_LIMIT = 'exchange limit'
    EXCHANGE_STOP = 'exchange stop'
    EXCHANGE_TRAILING_STOP = 'exchange trailing - stop'


class OS:
    BUY = 'buy'
    SELL = 'sell'


class TP:  # trading pairs - they are all put to lowercase when sent to Bitfinex
    BCH_USD = 'BCHUSD'
    BTC_USD = 'BTCUSD'
    EOS_USD = 'EOSUSD'
    ETH_USD = 'ETHUSD'
    IOT_USD = 'IOTUSD'
    LTC_USD = 'LTCUSD'
    NEO_USD = 'NEOUSD'


class SYM:
    BCH = 'BCH'
    BTC = 'BTC'
    EOS = 'EOS'
    ETH = 'ETH'
    IOT = 'IOT'
    LTC = 'LTC'
    NEO = 'NEO'


class BitfinexConfiguration(ExchangeConfiguration):
    def __set_values__(self):
        self.is_simulation = True
        self.hodl_dict = {'IOT': 7000}  # currency in upper characters
        self.buy_order_value_max = 100


class BitfinexFactory:
    @staticmethod
    def get_balance_by_json_dict(json: dict) -> Balance:
        # {'type': 'exchange', 'currency': 'usd', 'amount': '12.743', 'available': '12.743'}
        return Balance(json['type'], json['currency'], float(json['amount']), float(json['available']))

    @staticmethod
    def get_ticker_by_json_dict(json: dict) -> Ticker:
        # {'mid': 7052.45, 'bid': 7052.4, 'ask': 7052.5, 'last_price': 7051.3, 'timestamp': 1535469615.659593}
        return Ticker(float(json['bid']), float(json['ask']), float(json['last_price']),
                      0, 0, 0, float(json['timestamp']))

    @staticmethod
    def get_order_status_by_json_dict(order_id: int, json: dict) -> OrderStatus:
        return OrderStatus(order_id, json['symbol'], json['exchange'], float(json['price']),
                           float(json['avg_execution_price']), json['side'], json['type'],
                           float(json['executed_amount']), float(json['original_amount']),
                           float(json['remaining_amount']), json['is_cancelled'], float(json['timestamp']))

    @staticmethod
    def get_order_status_list_by_json_dict_list(json_dict_list: list) -> list:
        order_list = []
        for json_dict in json_dict_list:
            order_id = json_dict['id']
            order_list.append(BitfinexFactory.get_order_status_by_json_dict(order_id, json_dict))
        return order_list

    @staticmethod
    def get_order_status_by_order_for_simulation(order: Order):  # it is used for simulations
        order_id = MyDate.get_epoch_seconds_from_datetime()
        return OrderStatus(order_id, order.symbol, 'simulation', order.price, order.price,
                           order.side, order.type, order.amount, order.amount, 0, False, order_id)


class BitfinexOrder(Order):
    @property
    def trading_pair(self):
        return self.symbol

    @property
    def crypto(self):
        return self.symbol[:-3].upper()

    @property
    def currency(self):
        return self.symbol[-3:].upper()


class BuyMarketOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float):
        Order.__init__(self, symbol, amount, 1.00, OS.BUY, OT.EXCHANGE_MARKET)


class BuyLimitOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, limit: float):
        Order.__init__(self, symbol, amount, limit, OS.BUY, OT.EXCHANGE_LIMIT)


class BuyStopOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, stop_price: float):
        Order.__init__(self, symbol, amount, stop_price, OS.BUY, OT.EXCHANGE_STOP)


class SellMarketOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float):
        Order.__init__(self, symbol, amount, 1.00, OS.SELL, OT.EXCHANGE_MARKET)


class SellLimitOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, limit: float):
        Order.__init__(self, symbol, amount, limit, OS.SELL, OT.EXCHANGE_LIMIT)


class SellStopLossOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, stop_price: float):
        Order.__init__(self, symbol, amount, stop_price, OS.SELL, OT.EXCHANGE_STOP)


class SellTrailingStopOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, price_distance: float):
        Order.__init__(self, symbol, amount, price_distance, OS.SELL, OT.EXCHANGE_TRAILING_STOP)

    def __init__(self, exchange_config: BitfinexConfiguration):
        self.trading_config = trading_config
        self.is_simulation = self.trading_config.is_simulation
        self.hodl_dict = self.trading_config.hodl_dict


class MyBitfinex(ExInterface):
    def __init__(self, api_key: str, api_secret_key: str, exchange_config: BitfinexConfiguration):
        self.exchange_config = exchange_config
        self.base_currency = 'USD'
        self.http_timeout = 5.0 # HTTP request timeout in seconds
        self.url = 'https://api.bitfinex.com/v1'
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self._is_simulation = self.exchange_config.is_simulation
        self._hodl_dict = self.exchange_config.hodl_dict
        self.trading_pairs = self.get_symbols()

    @property
    def nonce(self):
        return str(time.time() * 1000000)

    @property
    def simulation_text(self):
        return ' (simulation)' if self._is_simulation else ''

    def get_available_money(self):
        balance = self.get_balance_for_symbol(self.base_currency)
        return 0 if balance is None else balance.amount_available

    def create_order(self, order: BitfinexOrder, order_type=''):
        self.__init_actual_order_properties__(order)
        if self.__is_enough_balance_available__(order):
            if not self.__is_order_affected_by_hodl_config__(order):
                if self.__is_order_value_compliant__(order):
                    self.__create_order__(order, order_type)

    def delete_order(self, order_id: int):
        prefix = 'Delete order - executed (simulation)' if self._is_simulation else 'Delete order - executed'
        if self._is_simulation:
            order_status = self.get_order(order_id)
        else:
            payload_additional = {"order_id": order_id}
            json_resp = self.__get_json__('/order/cancel', payload_additional)
            try:
                json_resp['avg_execution_price']
            except:
                print('Error deleting order {}: {}'.format(order_id, json_resp['message']))
                return
            order_status = BitfinexFactory.get_order_status_by_json_dict(json_resp['id'], json_resp)
        if order_status:
            order_status.print_order_status(prefix)

    def delete_all_orders(self):
        order_status_list = self.get_active_orders()
        prefix = 'Delete all orders - executed{}'.format(self.simulation_text)
        if self._is_simulation:
            if len(order_status_list) == 0:
                print('\nDelete all orders{} - result: {}'.format(self.simulation_text, 'Nothing to delete.'))
        else:
            json_cancel_all = self.__get_json__('/order/cancel/all')
            print('\nDelete all orders - result: {}'.format(json_cancel_all['result']))
        for order_status in order_status_list:
            order_status.print_order_status(prefix)

    def sell_all(self, trading_pair: str):
        symbol = trading_pair[:-3]
        balance = self.get_balance_for_symbol(symbol)
        if balance:
            self.__sell_all_in_balance__(balance, trading_pair)
        else:
            print('Sell all{} for {}: no amounts available.'.format(self.simulation_text, symbol))

    def sell_all_assets(self):
        balances = self.get_balances()
        for balance in balances:
            trading_pair = '{}{}'.format(balance.asset, self.base_currency).lower()
            if trading_pair in self.trading_pairs:
                self.__sell_all_in_balance__(balance, trading_pair)

    def __sell_all_in_balance__(self, balance: Balance, trading_pair: str):
        order_sell_all = SellMarketOrder(trading_pair, balance.amount_available)
        order_sell_all.actual_balance_symbol = balance
        self.create_order(order_sell_all, 'Sell all')

    def buy_available(self, symbol: str):
        amount_available = min(self.get_available_money(), self.exchange_config.buy_order_value_max)
        if amount_available < 10:
            print('Not enough (>{}$) balance for {} available'.format(10, self.base_currency))
        else:
            ticker = self.get_ticker(symbol)
            # the minus value in the next term is necessary to ensure that this amount is buyable
            amount = round(amount_available / ticker.ask - 0.05, 2)
            order_buy_all = BuyMarketOrder(symbol, amount)
            order_buy_all.actual_money_available = amount_available
            order_buy_all.actual_ticker = ticker
            self.create_order(order_buy_all, 'Buy available')

    def get_balance_for_symbol(self, symbol: str) -> Balance:
        balances = self.get_balances()
        for balance in balances:
            if balance.asset == symbol:
                return balance
        return None

    def get_order(self, order_id: int) -> OrderStatus:
        payload_additional = {'order_id': order_id}
        json_resp = self.__get_json__('/order/status', payload_additional)
        try:
            json_resp['avg_execution_price']
        except:
            print('Error get_order {}: {}'.format(order_id, json_resp['message']))
            return None
        return BitfinexFactory.get_order_status_by_json_dict(order_id, json_resp)

    def get_active_orders(self) -> list:
        return BitfinexFactory.get_order_status_list_by_json_dict_list(self.__get_json__('/orders'))

    def get_active_positions(self):
        return self.__get_json__('/positions')

    def get_past_trades(self, symbol: str, from_time_stamp: float):
        payload_additional = {"symbol": symbol, "timestamp": from_time_stamp}
        return self.__get_json__('/positions', payload_additional)

    def get_balances(self) -> list:
        balance_list = []
        json_resp_list = self.__get_json__('/balances')
        for json_resp in json_resp_list:
            if round(float(json_resp['amount'])) > 0:
                balance_list.append(BitfinexFactory.get_balance_by_json_dict(json_resp))
        return balance_list

    def get_summary(self):  # Returns a 30-day summary of your trading volume and return on margin funding.
        return self.__get_json__('/summary')

    def get_history(self, since_ts: int, until_ts, limit: int):
        raise NotImplementedError

    def get_symbols(self):
        return self.__get_requests_result__(self.__get_full_url__('symbols'))

    def get_ticker(self, symbol: str) -> Ticker:
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

    def print_active_orders(self):
        orders_status_list = self.get_active_orders()
        if len(orders_status_list) > 0:
            print('\nActive orders{}:'.format(self.simulation_text))
        for order_status in orders_status_list:
            order_status.print_order_status()

    def print_active_balances(self, prefix=''):
        prefix = 'Active balances' if prefix == '' else prefix
        balances = self.get_balances()
        if len(balances) > 0:
             print('\n{}{}:'.format(prefix, self.simulation_text))
        for balance in balances:
            balance.print_balance()

    def print_order_status(self, order_id: int):
        order_status = self.get_order(order_id)
        if order_status:
            order_status.print_order_status('Order status{}'.format(self.simulation_text))

    def __create_order__(self, order: Order, trigger: str) -> OrderStatus:
        trigger = 'Normal' if trigger == '' else trigger
        print_prefix = '{}: Order executed{} for {}:'.format(trigger, self.simulation_text, order.symbol)
        if self._is_simulation:
            if order.type == OT.EXCHANGE_MARKET:
                order.price = order.actual_ticker.ask
            order_status = BitfinexFactory.get_order_status_by_order_for_simulation(order)
            order_status.print_order_status(print_prefix)
        else:
            payload_additional = {
                'symbol': order.symbol.lower(), 'amount': str(order.amount), 'price': str(order.price),
                'exchange': 'bitfinex', 'side': order.side, 'type': order.type
            }
            json_resp = self.__get_json__('/order/new', payload_additional)
            try:
                json_resp['order_id']
            except:
                order.print_order('Error create_order: {}'.format(json_resp['message']))
                return
            order_status = BitfinexFactory.get_order_status_by_json_dict(json_resp['order_id'], json_resp)
            order_status.print_order_status(print_prefix)
            time.sleep(2)  # time to execute and update the application

    def __init_actual_order_properties__(self, order: BitfinexOrder):
        if order.actual_ticker is None:
            order.actual_ticker = self.get_ticker(order.symbol)
        if order.actual_money_available == 0:
            order.actual_money_available = self.get_available_money()
        if order.actual_balance_symbol is None:
            order.actual_balance_symbol = self.get_balance_for_symbol(order.crypto)

    def __is_order_affected_by_hodl_config__(self, order: BitfinexOrder):
        if order.side == OS.BUY or order.crypto not in self._hodl_dict:
            return False
        amount_hodl = self._hodl_dict[order.crypto]
        if order.actual_balance_symbol_amount - order.amount < amount_hodl:
            print('\nNot enough balance ({:.2f}) for {} to comply with the HODL amount {} when selling {}.'.format(
                order.actual_balance_symbol_amount, order.crypto, amount_hodl, order.amount))
            return True
        return False

    def __is_order_value_compliant__(self, order: BitfinexOrder):
        return self.__is_buy_order_value_compliant__(order) if order.side == OS.BUY else True

    def __is_buy_order_value_compliant__(self, order):
        price = MyBitfinex.__get_price_for_order__(order)
        order_value = order.amount * price
        if order_value > self.exchange_config.buy_order_value_max:
            print('\nThe order value {:.2f} is over the limit of {:.2f}$:'.format(
                order_value, self.exchange_config.buy_order_value_max), order.get_details())
            return False
        return True

    @staticmethod
    def __is_enough_balance_available__(order: BitfinexOrder):
        if order.side == OS.BUY:
            price = MyBitfinex.__get_price_for_order__(order)
            if order.actual_money_available < order.amount * price:
                print('\nNot enough balance ({:.2f}$) to buy {} of {} at {:.4f}$.'.format(
                    order.actual_money_available, order.amount, order.crypto, price))
                return False
        else:
            if order.actual_balance_symbol_amount < order.amount:
                print('\nNot enough balance ({:.2f}) for {} to sell {:.2f}.'.format(
                    order.actual_balance_symbol_amount, order.crypto, order.amount))
                return True
        return True

    @staticmethod
    def __get_price_for_order__(order: BitfinexOrder):
        return min(order.price, order.actual_ticker.ask) if order.type == OT.EXCHANGE_LIMIT else order.actual_ticker.ask

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