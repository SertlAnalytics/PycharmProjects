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
import pandas as pd
from sertl_analytics.constants.pattern_constants import OS, OT, TSTR, BT
from sertl_analytics.exchanges.exchange_abc import ExchangeInterface
from sertl_analytics.exchanges.exchange_cls import Order, OrderApi, OrderStatus, OrderStatusApi
from sertl_analytics.exchanges.exchange_cls import OrderBook, Balance, Ticker
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from sertl_analytics.datafetcher.financial_data_fetcher import BitfinexCryptoFetcher
from sertl_analytics.datafetcher.data_fetcher_cache import DataFetcherCacheKey
from sertl_analytics.mydates import MyDate
from sertl_analytics.mystring import MyString
from sertl_analytics.mycache import MyCacheObjectApi, MyCacheObject, MyCache


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
        self.buy_fee_pct = 0.25
        self.sell_fee_pct = 0.25
        self.ticker_refresh_rate_in_seconds = 5
        self.cache_ticker_seconds = 30  # keep ticker in the Bitfinex cache
        self.cache_balance_seconds = 300  # keep balances in the Bitfinex cache (it's overwriten when changes happen)
        self.check_ticker_after_timer_intervals = 4  # currently the timer intervall is set to 5 sec, i.e. check each 20 sec.
        self.finish_vanished_trades = False  # True <=> if a pattern is vanished after buying sell the position (market)
        self.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP],
                                    BT.TOUCH_POINT: [TSTR.LIMIT]}
        self.default_trade_strategy_dict = {BT.BREAKOUT: TSTR.TRAILING_STOP,
                                    BT.TOUCH_POINT: TSTR.LIMIT}

    def print_actual_mode(self):
        text = 'Bitfinex running in {} mode.'.format('SIMULATION' if self.is_simulation else 'TRADING (!!!)')
        print(MyString.surround(text))


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


class BitfinexOrderStatus(OrderStatus):
    @property
    def value_total(self):
        amount = self.original_amount if self.executed_amount == 0 else self.executed_amount
        if self.side == OS.BUY:
            return round(self.price * amount + self.fee_amount, 2)
        else:
            return round(self.price * amount - self.fee_amount, 2)


class BuyMarketOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float):
        api = OrderApi(symbol, amount)
        api.price = 1.00
        api.side = OS.BUY
        api.type = OT.EXCHANGE_MARKET
        Order.__init__(self, api)


class BuyLimitOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, limit: float):
        api = OrderApi(symbol, amount, price=limit)
        api.side = OS.BUY
        api.type = OT.EXCHANGE_LIMIT
        Order.__init__(self, api)


class BuyStopOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, stop_price: float):
        api = OrderApi(symbol, amount, price=stop_price)
        api.side = OS.BUY
        api.type = OT.EXCHANGE_STOP
        Order.__init__(self, api)


class SellMarketOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float):
        api = OrderApi(symbol, amount)
        api.price = 1.00
        api.side = OS.SELL
        api.type = OT.EXCHANGE_MARKET
        Order.__init__(self, api)


class SellLimitOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, limit: float):
        api = OrderApi(symbol, amount, price=limit)
        api.side = OS.SELL
        api.type = OT.EXCHANGE_LIMIT
        Order.__init__(self, api)


class SellStopLossOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, stop_price: float):
        api = OrderApi(symbol, amount, price=stop_price)
        api.side = OS.SELL
        api.type = OT.EXCHANGE_STOP
        Order.__init__(self, api)


class SellTrailingStopOrder(BitfinexOrder):
    def __init__(self, symbol: str, amount: float, price_distance: float):
        api = OrderApi(symbol, amount, price=price_distance)
        api.side = OS.SELL
        api.type = OT.EXCHANGE_TRAILING_STOP
        Order.__init__(self, api)


class BitfinexFactory:
    @staticmethod
    def get_balance_by_json_dict(json: dict) -> Balance:
        # {'type': 'exchange', 'currency': 'usd', 'amount': '12.743', 'available': '12.743'}
        return Balance(json['type'], json['currency'], float(json['amount']), float(json['available']))

    @staticmethod
    def get_ticker_by_json_dict(ticker_id: str, json: dict) -> Ticker:
        # {'mid': 7052.45, 'bid': 7052.4, 'ask': 7052.5, 'last_price': 7051.3, 'timestamp': 1535469615.659593}
        return Ticker(ticker_id, float(json['bid']), float(json['ask']), float(json['last_price']),
                      0, 0, 0, int(json['timestamp']))

    @staticmethod
    def get_order_status_by_json_dict(config: BitfinexConfiguration, order_id: int, json: dict) -> BitfinexOrderStatus:
        order_status_api = OrderStatusApi()
        order_status_api.order_id = order_id
        order_status_api.symbol = json['symbol']
        order_status_api.exchange = json['exchange']
        order_status_api.price = float(json['price'])
        order_status_api.avg_execution_price = float(json['avg_execution_price'])
        order_status_api.side = json['side']
        order_status_api.type = json['type']
        order_status_api.executed_amount = float(json['executed_amount'])
        order_status_api.original_amount = float(json['original_amount'])
        order_status_api.remaining_amount = float(json['remaining_amount'])
        order_status_api.is_cancelled = json['is_cancelled']
        order_status_api.time_stamp = float(json['timestamp'])
        order_status = BitfinexOrderStatus(order_status_api)
        order_status.set_fee_amount(config.buy_fee_pct if order_status_api.side == OS.BUY else config.sell_fee_pct, True)
        return order_status

    @staticmethod
    def get_order_status_list_by_json_dict_list(exchange_config, json_dict_list: list) -> list:
        order_list = []
        for json_dict in json_dict_list:
            order_id = json_dict['id']
            order_list.append(BitfinexFactory.get_order_status_by_json_dict(exchange_config, order_id, json_dict))
        return order_list

    @staticmethod
    def get_order_status_by_order_for_simulation(config: BitfinexConfiguration, order: Order):  # it is used for simulations
        order_status_api = OrderStatusApi()
        order_status_api.order_id = MyDate.get_epoch_seconds_from_datetime()
        order_status_api.symbol = order.symbol
        order_status_api.exchange = 'simulation'
        order_status_api.price = order.price
        order_status_api.avg_execution_price = order.price
        order_status_api.side = order.side
        order_status_api.type = order.type
        order_status_api.executed_amount = order.amount
        order_status_api.original_amount = order.amount
        order_status_api.remaining_amount = 0
        order_status_api.is_cancelled = False
        order_status_api.time_stamp = order_status_api.order_id
        order_status = BitfinexOrderStatus(order_status_api)
        order_status.set_fee_amount(config.buy_fee_pct if order.side == OS.BUY else config.sell_fee_pct, True)
        return order_status


class BitfinexDataFetcherCacheKey(DataFetcherCacheKey):
    def __init__(self, ticker: str, period: str, aggregation: int, section: str, limit: int):
        DataFetcherCacheKey.__init__(self, ticker, period, aggregation)
        self.section = section
        self.limit = limit

    @property
    def key(self):
        return 'ticker={}_period={}_aggregation={}_section={}_limit={}'.format(
            self.ticker_id, self.period, self.aggregation, self.section, self.limit)


class BitfinexTickerCache(MyCache):
    def __init__(self, cache_seconds: int):
        MyCache.__init__(self)
        self._cache_seconds = cache_seconds

    def add_ticker(self, ticker: Ticker):
        api = MyCacheObjectApi()
        api.valid_until_ts = MyDate.get_epoch_seconds_from_datetime() + self._cache_seconds
        api.key = ticker.ticker_id
        api.object = ticker
        self.add_cache_object(api)


class BitfinexBalanceCache(MyCache):
    def __init__(self, cache_seconds: int):
        MyCache.__init__(self)
        self._cache_seconds = cache_seconds

    def init_by_balance_list(self, balances: list, dedicated_symbol=''):
        api = MyCacheObjectApi()
        api.valid_until_ts = MyDate.get_epoch_seconds_from_datetime() + self._cache_seconds
        for balance in balances:
            api.key = balance.asset
            api.object = balance
            self.add_cache_object(api)
        if dedicated_symbol != '' and self.get_cached_object_by_key(dedicated_symbol) is None:
            api.key = dedicated_symbol
            api.object = Balance('exchange', dedicated_symbol, 0, 0)
            self.add_cache_object(api)


class MyBitfinex(ExchangeInterface):
    def __init__(self, api_key: str, api_secret_key: str, exchange_config: BitfinexConfiguration):
        self.exchange_config = exchange_config
        self._is_simulation_by_config = self.exchange_config.is_simulation
        self.base_currency = self.exchange_config.default_currency
        self.http_timeout = 5.0 # HTTP request timeout in seconds
        self.url = 'https://api.bitfinex.com/v1'
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self._hodl_dict = self.exchange_config.hodl_dict
        self.trading_pairs = self.get_symbols()
        self.ticker_cache = BitfinexTickerCache(self.exchange_config.cache_ticker_seconds)
        self.balance_cache = BitfinexBalanceCache(self.exchange_config.cache_balance_seconds)

    @property
    def nonce(self):
        return str(time.time() * 1000000)

    def get_simulation_text(self, is_simulation=True):
        if is_simulation is None:
            is_simulation = self._is_simulation_by_config
        return ' (simulation)' if is_simulation else ''

    def get_available_money_balance(self) -> Balance:
        return self.get_balance_for_symbol(self.base_currency)

    def get_available_money(self) -> float:
        return self.get_available_money_balance().amount_available

    def create_order(self, order: BitfinexOrder, order_type='', is_simulation=True):
        self.__init_actual_order_properties__(order)
        if is_simulation or self.__is_enough_balance_available__(order):
            if is_simulation or not self.__is_order_affected_by_hodl_config__(order):
                if is_simulation or self.__is_order_value_compliant__(order):
                    return self.__create_order__(order, order_type, is_simulation)

    def delete_order(self, order_id: int, is_simulation=True):
        prefix = 'Delete order - executed (simulation)' if is_simulation else 'Delete order - executed'
        if is_simulation:
            order_status = self.get_order(order_id)
        else:
            payload_additional = {"order_id": order_id}
            json_resp = self.__get_json__('/order/cancel', payload_additional)
            try:
                json_resp['avg_execution_price']
            except:
                print('Error deleting order {}: {}'.format(order_id, json_resp['message']))
                return
            order_status = BitfinexFactory.get_order_status_by_json_dict(self.exchange_config, json_resp['id'], json_resp)
        if order_status:
            order_status.print_order_status(prefix)

    def delete_all_orders(self, is_simulation=True):
        order_status_list = self.get_active_orders()
        if is_simulation:
            if len(order_status_list) == 0:
                print('\nDelete all orders{} - result: {}'.format(self.get_simulation_text(is_simulation),
                                                                  'Nothing to delete.'))
        else:
            json_cancel_all = self.__get_json__('/order/cancel/all')
            print('\nDelete all orders - result: {}'.format(json_cancel_all['result']))

        prefix = 'Delete all orders - executed{}'.format(self.get_simulation_text(is_simulation))
        for order_status in order_status_list:
            order_status.print_order_status(prefix)

    def sell_all(self, trading_pair: str, is_simulation=True):
        symbol = trading_pair[:-3]
        balance = self.get_balance_for_symbol(symbol)
        if balance:
            self.__sell_all_in_balance__(balance, trading_pair, is_simulation)
        else:
            print('Sell all{} for {}: no amounts available.'.format(self.get_simulation_text(is_simulation), symbol))

    def sell_all_assets(self, is_simulation=True):
        order_status_list = []
        balances = self.get_balances()
        for balance in balances:
            trading_pair = '{}{}'.format(balance.asset, self.base_currency).lower()
            if trading_pair in self.trading_pairs:
                order_status_list.append(self.__sell_all_in_balance__(balance, trading_pair, is_simulation))
        return order_status_list

    def __sell_all_in_balance__(self, balance: Balance, trading_pair: str, is_simulation=True):
        order_sell_all = SellMarketOrder(trading_pair, balance.amount_available)
        order_sell_all.actual_balance_symbol = balance
        return self.create_order(order_sell_all, 'Sell all', is_simulation)

    def buy_available(self, symbol: str, last_price=0, is_simulation=True):
        if is_simulation:
            available_money = self.exchange_config.buy_order_value_max
        else:
            available_money = min(self.get_available_money(), self.exchange_config.buy_order_value_max)

        if available_money < 10:
            print('\nNot enough (>{}$) balance for {} available'.format(10, self.base_currency))
        else:
            ticker = self.get_ticker(symbol) if last_price == 0 else None
            last_price = ticker.last_price if ticker else last_price
            # the minus value in the next term is necessary to ensure that this amount is buyable
            amount = round(available_money / last_price - 0.005, 2)  # the part 0.005 is for amount safety
            order_buy_all = BuyMarketOrder(symbol, amount)
            order_buy_all.actual_money_available = available_money
            order_buy_all.actual_ticker = ticker
            return self.create_order(order_buy_all, 'Buy available')

    def get_balance_for_symbol(self, symbol: str) -> Balance:
        balance_from_cache = self.balance_cache.get_cached_object_by_key(symbol)
        if balance_from_cache:
            return balance_from_cache
        self.balance_cache.init_by_balance_list(self.get_balances(), symbol)
        return self.balance_cache.get_cached_object_by_key(symbol)

    def get_order(self, order_id: int) -> BitfinexOrderStatus:
        payload_additional = {'order_id': order_id}
        json_resp = self.__get_json__('/order/status', payload_additional)
        try:
            json_resp['avg_execution_price']
        except:
            print('Error get_order {}: {}'.format(order_id, json_resp['message']))
            return None
        return BitfinexFactory.get_order_status_by_json_dict(self.exchange_config, order_id, json_resp)

    def update_order(self, order_id: int, price_new: float) -> BitfinexOrderStatus:
        old_order_status = self.get_order(order_id)
        if not old_order_status:
            return None
        payload_additional = {
            'order_id': order_id, 'symbol': old_order_status.symbol.lower(),
            'amount': str(old_order_status.original_amount),
            'price': str(price_new), 'exchange': 'bitfinex', 'side': old_order_status.side,
            'type': old_order_status.type
        }
        json_resp = self.__get_json__('/order/cancel/replace', payload_additional)
        try:
            json_resp['avg_execution_price']
        except:
            print('Error update_order {}: {}'.format(order_id, json_resp['message']))
            return None
        return BitfinexFactory.get_order_status_by_json_dict(self.exchange_config, order_id, json_resp)

    def get_active_orders(self) -> list:
        return BitfinexFactory.get_order_status_list_by_json_dict_list(
            self.exchange_config, self.__get_json__('/orders'))

    def get_active_positions(self):
        return self.__get_json__('/positions')

    def get_past_trades(self, symbol: str, from_time_stamp: float):
        payload_additional = {"symbol": symbol, "timestamp": from_time_stamp}
        return self.__get_json__('/positions', payload_additional)

    def get_balances(self) -> list:
        balance_list = []
        json_resp_list = self.__get_json__('/balances')
        for json_resp in json_resp_list:
            if 'error' in json_resp:
                pass
            else:
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
        ticker_from_cache = self.ticker_cache.get_cached_object_by_key(symbol)
        if ticker_from_cache:
            return ticker_from_cache
        data = self.__get_requests_result__(self.__get_full_url__('ticker/{}'.format(symbol)))
        data_converted = self.__convert_to_floats__(data)
        ticker = BitfinexFactory.get_ticker_by_json_dict(symbol, data_converted)
        self.ticker_cache.add_ticker(ticker)
        return ticker

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

    def get_candles(self, symbol: str, period: str, aggregation: int, section='hist',
                    limit=200, ms_start=0, ms_end=0, sort=1):
        data_fetcher_cache_key = BitfinexDataFetcherCacheKey(symbol, period, aggregation, section, limit)
        df_from_cache = self.ticker_cache.get_cached_object_by_key(data_fetcher_cache_key.key)
        if df_from_cache is not None:
            print('df_source from cache: {}'.format(data_fetcher_cache_key.key))
            return df_from_cache
        fetcher = BitfinexCryptoFetcher(symbol, period, aggregation, section, limit)
        self.__add_data_frame_to_cache__(fetcher.df_data, data_fetcher_cache_key)
        return fetcher.df_data

    def __add_data_frame_to_cache__(self, df: pd.DataFrame, data_fetcher_cache_key: BitfinexDataFetcherCacheKey):
        cache_api = MyCacheObjectApi()
        cache_api.key = data_fetcher_cache_key.key
        cache_api.object = df
        cache_api.valid_until_ts = data_fetcher_cache_key.valid_until_ts
        self.ticker_cache.add_cache_object(cache_api)

    def print_active_orders(self):
        orders_status_list = self.get_active_orders()
        if len(orders_status_list) > 0:
            print('\nActive orders{}:'.format(self.get_simulation_text))
        for order_status in orders_status_list:
            order_status.print_order_status()

    def print_active_balances(self, prefix=''):
        prefix = 'Active balances' if prefix == '' else prefix
        balances = self.get_balances()
        if len(balances) > 0:
             print('\n{}{}:'.format(prefix, self.get_simulation_text()))
        for balance in balances:
            balance.print_balance()

    def print_order_status(self, order_id: int, is_simulation: bool):
        order_status = self.get_order(order_id)
        if order_status:
            order_status.print_order_status('Order status{}'.format(self.get_simulation_text(is_simulation)))

    def __create_order__(self, order: Order, trigger: str, is_simulation: bool) -> OrderStatus:
        trigger = 'Normal' if trigger == '' else trigger
        print_prefix = '{}: Order executed{} for {}:'.format(trigger, self.get_simulation_text(is_simulation), order.symbol)
        if is_simulation:
            if order.type == OT.EXCHANGE_MARKET:
                order.price = order.actual_ticker.ask
            order_status = BitfinexFactory.get_order_status_by_order_for_simulation(self.exchange_config, order)
            # order_status.print_order_status(print_prefix)
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
            order_status = BitfinexFactory.get_order_status_by_json_dict(self.exchange_config,
                                                                         json_resp['order_id'], json_resp)
            # order_status.print_order_status(print_prefix)
            time.sleep(2)  # time to execute and update the application
            self.balance_cache.clear()  # the next call has to get the updated balances...
        return order_status

    def __init_actual_order_properties__(self, order: BitfinexOrder):
        if order.actual_ticker is None:
            order.actual_ticker = self.get_ticker(order.symbol)
        if order.actual_money_balance is None:
            order.actual_money_balance = self.get_available_money_balance()
        if order.actual_symbol_balance is None:
            order.actual_symbol_balance = self.get_balance_for_symbol(order.crypto)

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
            money_available = order.actual_money_balance.amount_available
            if money_available < order.amount * price:
                print('\nNot enough balance ({:.2f}$) to buy {} of {} at {:.4f}$.'.format(
                    money_available, order.amount, order.crypto, price))
                return False
        else:
            if order.actual_balance_symbol_amount < order.amount:
                print('\nNot enough balance ({:.2f}) for {} to sell {:.2f}.'.format(
                    order.actual_balance_symbol_amount, order.crypto, order.amount))
                return False
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
        # print('__convert_to_floats__: {}'.format(data_dict))
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