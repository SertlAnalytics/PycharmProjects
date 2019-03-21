"""
https://github.com/Crypto-toolbox/btfxwss
Snapshots (data structure): https://docs.bitfinex.com/v1/reference#ws-auth-order-snapshots
"""

import os
from sertl_analytics.exchanges.interactive_broker import MyIBKR, IBKRConfiguration
from sertl_analytics.exchanges.bitfinex import Ticker, Balance
from sertl_analytics.exchanges.interactive_broker import IBKRBuyMarketOrder, IBKRBuyLimitOrder, IBKRBuyStopOrder
from sertl_analytics.exchanges.interactive_broker import IBKRSellMarketOrder, IBKRSellStopLossOrder, IBKRSellTrailingStopOrder
from sertl_analytics.constants.pattern_constants import CN, TP, PRD
from pattern_wave_tick import WaveTick, WaveTickList
from sertl_analytics.exchanges.exchange_abc import MyExchangeTest


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


class MyIBKRTradeClient:
    """
    We use Alphavantage as data provider. Interactive Broker TWS is used for trading....
    """
    def __init__(self, exchange_config: IBKRConfiguration):
        self.exchange_config = exchange_config
        self.exchange_config.print_actual_mode()
        self._api_key = os.environ['alphavantage_apikey']
        self._api_key_secret = os.environ['alphavantage_apikey']
        self._ibkr = MyIBKR(self.exchange_config)
        self._trading_pairs = self._ibkr.trading_pairs

    @property
    def ibkr(self):
        return self._ibkr

    def get_ticker(self, symbol: str) -> Ticker:
        return self._ibkr.get_ticker(symbol)

    def get_current_wave_tick(self, symbol: str, period: str, aggregation: int) -> WaveTick:
        wave_tick_list = self.get_latest_tickers_as_wave_tick_list(symbol, period, aggregation)
        return wave_tick_list.tick_list[-1]

    def get_candles(self, symbol: str, period: str, aggregation: int, section='hist', limit=200):
        return self._ibkr.get_candles(symbol, period, aggregation, section, limit)

    def get_latest_tickers_as_wave_tick_list(self, symbol: str, period: str, aggregation: int, limit=2) -> WaveTickList:
        df = self.get_candles(symbol, period, aggregation, 'hist', limit)
        df[CN.TIMESTAMP] = df.index
        df[CN.POSITION] = 0
        return WaveTickList(df)

    def get_last_ticker(self, symbol: str, period: str, aggregation: int):
        return self.get_candles(symbol, period, aggregation, 'last')

    def get_balance(self, symbol: str) -> Balance:
        return self._ibkr.get_balance_for_symbol(symbol)

    def print_active_orders(self):
        self._ibkr.print_active_orders()

    def get_active_orders(self):
        return self._ibkr.get_active_orders()

    def print_active_balances(self, prefix=''):
        self._ibkr.print_active_balances(prefix)

    def get_balances(self):
        return self._ibkr.get_balances()

    def get_balances_with_current_values(self):
        default_currency = self._ibkr.exchange_config.default_currency
        balances = self._ibkr.get_balances()
        for balance in balances:
            if balance.asset == default_currency:
                balance.current_value = balance.amount
            else:
                ticker = self.get_ticker('{}{}'.format(balance.asset, default_currency))
                balance.current_value = round(ticker.last_price * balance.amount, 2)
        return balances

    def print_order_status(self, order_id: int):
        self._ibkr.print_order_status(order_id)

    def delete_order(self, order_id: int, is_trade_simulation: bool):
        self._ibkr.delete_order(order_id, is_trade_simulation)

    def update_order(self, order_id: int, price_new: float, is_order_simulation: bool):
        self._ibkr.update_order(order_id, price_new, is_order_simulation)

    def delete_all_orders(self):
        self._ibkr.delete_all_orders()

    def buy_available(self, trading_pair: str, last_price=0.0, is_order_simulation=False):
        self.print_active_balances('Before "Buy available {}"'.format(trading_pair))
        order_status = self._ibkr.buy_available(trading_pair, last_price, is_order_simulation)
        self.print_active_balances('After "Buy available {}"'.format(trading_pair))
        return order_status

    def sell_all(self, trading_pair: str):
        self.print_active_balances('Before "Sell all {}"'.format(trading_pair))
        order_status = self._ibkr.sell_all(trading_pair)
        self.print_active_balances('After "Sell all {}"'.format(trading_pair))
        return order_status

    def sell_all_assets(self):
        self.print_active_balances('Before "Sell all assets"')
        order_status_list = self._ibkr.sell_all_assets()
        self.print_active_balances('After "Sell all assets"')
        return order_status_list

    def create_buy_market_order(self, trading_pair: str, amount: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRBuyMarketOrder(trading_pair, amount), is_order_simulation)

    def create_buy_stop_order(self, trading_pair: str, amount: float, buy_stop_price: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRBuyStopOrder(trading_pair, amount, buy_stop_price), is_order_simulation)

    def create_buy_limit_order(self, trading_pair: str, amount: float, limit_price: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRBuyLimitOrder(trading_pair, amount, limit_price), is_order_simulation)

    def create_sell_market_order(self, trading_pair: str, amount: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRSellMarketOrder(trading_pair, amount), is_order_simulation)

    def create_sell_stop_loss_order(self, trading_pair: str, amount: float, stop_price: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRSellStopLossOrder(trading_pair, amount, stop_price), is_order_simulation)

    def create_sell_trailing_stop_order(self, trading_pair: str, amount: float, distance: float, is_order_simulation: bool):
        return self._ibkr.create_order(IBKRSellTrailingStopOrder(trading_pair, amount, distance), is_order_simulation)


class MyIBKRTest(MyExchangeTest):
    @staticmethod
    def __get_exchange__():
        trade_client = MyIBKRTradeClient(IBKRConfiguration())
        return trade_client.ibkr

    @staticmethod
    def __get_symbol__():
        return 'AAPL'

    @staticmethod
    def __get_order_id__():
        return ''

    def __get_test_list_for_get_candles__(self):
        return [
            [[self._symbol, PRD.DAILY, 1, '', 0], [self._symbol, 100]],
            [[self._symbol, PRD.DAILY, 1, '', 150], [self._symbol, 100]],
            [[self._symbol, PRD.INTRADAY, 15, '', 0], [self._symbol, 100]],
            [[self._symbol, PRD.INTRADAY, 30, '', 0], [self._symbol, 100]],
        ]
