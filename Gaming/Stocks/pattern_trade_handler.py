"""
Description: This module contains the PatternTradeContainer class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import CN, DIR, FT, TSTR, BT, ST, FD, DC, TBT, PTS
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from pattern import Pattern
from pattern_bitfinex import MyBitfinexTradeClient, BitfinexConfiguration
from sertl_analytics.exchanges.exchange_cls import OrderStatus, Ticker
from pattern_database.stock_database import StockDatabase


class TradingBox:
    def __init__(self, pattern_data_dict: dict, off_set_price: float, trade_strategy: str):
        self.box_type = ''
        self._data_dict = pattern_data_dict
        self._ticker_id = self._data_dict[DC.TICKER_ID]
        self._off_set_price = off_set_price
        self._trade_strategy = trade_strategy
        self._ticker_last_price_list = []
        self._height = 0
        self._distance_bottom = 0
        self._distance_top = 0
        self._stop_loss_orig = 0
        self._stop_loss_current = 0
        self._sell_limit_orig = 0
        self._sell_limit_current = 0
        self._trailing_stop_distance = 0
        self._next_trailing_stop = 0
        self._init_parameters_()
        self.__calculate_stops_and_limits__()

    @property
    def distance_top_bottom(self):
        return self._distance_bottom + self._distance_top

    @property
    def distance_stepping(self):
        return round(self._distance_bottom / 2, 2)

    @property
    def stop_loss(self):
        return self._stop_loss_current

    @property
    def limit(self):
        return self._sell_limit_current

    @property
    def distance_trailing_stop(self):
        return self._trailing_stop_distance

    @property
    def multiplier_positive(self):
        return round(max(100, self._data_dict[DC.FC_HALF_POSITIVE_PCT], self._data_dict[DC.FC_FULL_POSITIVE_PCT])/100, 2)

    @property
    def multiplier_negative(self):
        return round(max(100, self._data_dict[DC.FC_HALF_NEGATIVE_PCT], self._data_dict[DC.FC_FULL_NEGATIVE_PCT])/100, 2)

    def print_box(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        print('{}-box for {}: {}'.format(self.box_type, self._ticker_id, details))

    def __get_value_dict__(self) -> dict:
        return {'Orig_height': self._height,
                'dist_top': '{:.2f} ({:.2f})'.format(self._distance_top, self.multiplier_positive),
                'dist_bottom': '{:.2f} ({:.2f})'.format(self._distance_bottom, self.multiplier_negative),
                'limit': self.limit, 'stop loss': self.stop_loss,
                'dist_stepping': self.distance_stepping,
                'dist_trailing_stop': self.distance_trailing_stop
        }

    def adjust_to_next_ticker_last_price(self, ticker_last_price: float):
        self._ticker_last_price_list.append(ticker_last_price)
        self.__adjust_to_next_ticker_last_price__(ticker_last_price)

    def __adjust_to_next_ticker_last_price__(self, ticker_last_price: float):
        if self._trade_strategy == TSTR.LIMIT:
            pass
        elif self._trade_strategy == TSTR.TRAILING_STOP:
            if self._stop_loss_current < ticker_last_price - self._distance_bottom:
                self._stop_loss_current = ticker_last_price - self._distance_bottom
                self._sell_limit_current = self._stop_loss_current + self.distance_top_bottom
                self.__print_new_adjusted_values__()
        elif self._trade_strategy == TSTR.TRAILING_STEPPED_STOP:
            if self._stop_loss_current < ticker_last_price - self._distance_bottom - self.distance_stepping:
                self._stop_loss_current = ticker_last_price - self.distance_stepping
                self._sell_limit_current = self._stop_loss_current + self.distance_top_bottom
                self.__print_new_adjusted_values__()

    def __print_new_adjusted_values__(self):
        print('..adjusted: new stop_loss={}, new limit={} (top_bottom = {})'.format(
            self._stop_loss_current, self._sell_limit_current, self.distance_top_bottom))

    def _init_parameters_(self):
        pass

    def __calculate_stops_and_limits__(self):
        self._stop_loss_orig = self._off_set_price - self._distance_bottom
        self._stop_loss_current = self._stop_loss_orig
        self._sell_limit_orig = self._off_set_price + self._distance_top
        self._sell_limit_current = self._sell_limit_orig
        self._trailing_stop_distance = self._distance_bottom
        self._next_trailing_stop = self._off_set_price


class ExpectedWinTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.EXPECTED_WIN
        self._height = self._data_dict[DC.EXPECTED_WIN]
        self._distance_bottom = round(self._height * self.multiplier_positive, 2)
        self._distance_top = round(self._height * self.multiplier_negative, 2)


class ForecastHalfLengthTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FORECAST_HALF_LENGTH
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_bottom = round(self._height * self.multiplier_positive, 2)
        self._distance_top = round(self._height * self.multiplier_positive, 2)


class ForecastFullLengthTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FORECAST_FULL_LENGTH
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_bottom = round(self._height * self.multiplier_positive, 2)
        self._distance_top = round(self._height * self.multiplier_positive, 2)


class TouchPointTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.TOUCH_POINT  # ToDo Touch_point
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_bottom = round(self._height/2, 2)
        self._distance_top = round(self._height, 2)


class FibonacciTradingBox(TradingBox):
    def _init_parameters_(self):
        self.box_type = TBT.FIBONACCI  # ToDo Fibonacci
        self._height = self._data_dict[DC.PATTERN_HEIGHT]
        self._distance_bottom = round(self._height, 2)
        self._distance_top = round(self._height, 2)


class PatternTrade:
    def __init__(self, pattern: Pattern, buy_trigger: str, trade_box_type: str, trade_strategy: str):
        self.buy_trigger = buy_trigger
        self.trade_box_type = trade_box_type
        self.trade_strategy = trade_strategy
        self.pattern = pattern
        self.expected_win = self.pattern.data_dict_obj.get(DC.EXPECTED_WIN)
        self.expected_breakout_direction = self.pattern.expected_breakout_direction
        self.id = '{}-{}-{}_{}'.format(buy_trigger, trade_box_type, trade_strategy, pattern.id)
        self._order_status_buy = None
        self._order_status_sell = None
        self._status = PTS.NEW
        self._trade_box = None

    @property
    def executed_amount(self):
        return self._order_status_buy.executed_amount

    @property
    def order_status_buy(self):
        return self._order_status_buy

    @property
    def order_status_sell(self):
        return self._order_status_buy

    def print_trade(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        print('{}: {}'.format(self.id, details))
        if self._order_status_buy:
            self._order_status_buy.print_order_status('Buy order')
        if self._order_status_sell:
            self._order_status_sell.print_order_status('Sell order')

    def __get_value_dict__(self) -> dict:
        return {'Buy_trigger': self.buy_trigger, 'Trade_box': self.trade_box_type,
                'Trade_strategy': self.trade_strategy, 'Pattern_Type': self.pattern.pattern_type,
                'Expected_win': self.expected_win, 'Result': self.get_trade_result_text()
        }

    def get_trade_result_text(self):
        if not self._order_status_sell:
            return '-'
        return '{:0.2f} from {:0.2f}'.format(
            self._order_status_sell.value_total - self._order_status_buy.value_total, self._order_status_buy.value_total
        )

    def adjust_to_next_ticker_last_price(self, last_price: float):
        self._trade_box.adjust_to_next_ticker_last_price(last_price)

    def __get_trade_box__(self, off_set_price: float):
        if self.trade_box_type == TBT.EXPECTED_WIN:
            return ExpectedWinTradingBox(self.pattern.data_dict_obj.data_dict, off_set_price, self.trade_strategy)
        elif self.trade_box_type == TBT.FORECAST_HALF_LENGTH:
            return ForecastHalfLengthTradingBox(self.pattern.data_dict_obj.data_dict, off_set_price, self.trade_strategy)
        elif self.trade_box_type == TBT.FORECAST_FULL_LENGTH:
            return ForecastFullLengthTradingBox(self.pattern.data_dict_obj.data_dict, off_set_price, self.trade_strategy)
        elif self.trade_box_type == TBT.TOUCH_POINT:
            return TouchPointTradingBox(self.pattern.data_dict_obj.data_dict, off_set_price, self.trade_strategy)
        elif self.trade_box_type == TBT.FIBONACCI:
            return FibonacciTradingBox(self.pattern.data_dict_obj.data_dict, off_set_price, self.trade_strategy)
        return None

    def set_order_status_buy(self, order_status: OrderStatus, buy_comment, ticker: Ticker):
        order_status.order_trigger = self.buy_trigger
        order_status.order_comment = buy_comment
        self._order_status_buy = order_status
        self.pattern.data_dict_obj.add_buy_order_status_data_to_pattern_data_dict(order_status, self.trade_strategy)
        self.__set_properties_after_buy__(ticker)
        self.print_trade('Details after buying')

    def __set_properties_after_buy__(self, ticker: Ticker):
        self._status = PTS.EXECUTED
        self._trade_box = self.__get_trade_box__(ticker.last_price)
        self._trade_box.print_box()

    def set_order_status_sell(self, order_status: OrderStatus, sell_trigger: str, sell_comment: str):
        order_status.order_trigger = sell_trigger
        order_status.order_comment = sell_comment
        self._order_status_sell = order_status
        self.pattern.data_dict_obj.add_sell_order_status_data_to_pattern_data_dict(order_status)
        self.__set_properties_after_sell__()
        self.print_trade('Details after selling')

    def __set_properties_after_sell__(self):
        self._status = PTS.FINISHED

    @property
    def stop_loss_current(self):
        return self._trade_box.stop_loss

    @property
    def limit_current(self):
        return self._trade_box.limit

    @property
    def trailing_stop_distance(self):
        return self._trade_box.trailing_stop_distance

    @property
    def ticker_id(self):
        return self.pattern.ticker_id.replace('_', '')

    @property
    def status(self):
        return self._status

    def is_ticker_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            upper_value = self.pattern.function_cont.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        # elif self.expected_breakout_direction == FD.DESC:
        #     lower_value = self.pattern.function_cont.get_lower_value(time_stamp)
        #     return ticker.last_price <= lower_value
        return False

    def is_ticker_wrong_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            lower_value = self.pattern.function_cont.get_lower_value(time_stamp)
            return ticker.last_price <= lower_value
        elif self.expected_breakout_direction == FD.DESC:
            upper_value = self.pattern.function_cont.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        return False


class PatternQueue:
    def __init__(self, pattern_list: list, buy_trigger: str, box_type: str, trade_strategy: str):
        self.pattern_list = pattern_list
        self.buy_trigger = buy_trigger
        self.box_type = box_type
        self.trade_strategy = trade_strategy

    def is_empty(self):
        return len(self.pattern_list) == 0


class PatternTradeHandler:
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        self.sys_config = sys_config
        self.bitfinex_trade_client = MyBitfinexTradeClient(bitfinex_config)
        self.stock_db = self.sys_config.db_stock
        self.ticker_id_list = []
        self.pattern_trade_dict = {}
        self._time_stamp_check = 0
        self._date_time_check = None
        self.process = ''
        self.pattern_queue = None
        self._last_price_for_test = 0

    # def __del__(self):
    #     print('PatternTradeHandler: Destructor...')
    #     self.__create_trailing_stop_order_for_all_executed_trades__()

    @property
    def trade_numbers(self) -> int:
        return len(self.pattern_trade_dict)

    def add_pattern_list_for_trade(self, pattern_list: list, buy_trigger: str, box_type: str, trade_strategy: str):
        self.pattern_queue = PatternQueue(pattern_list, buy_trigger, box_type, trade_strategy)
        self.__process_pattern_queue__()

    def __process_pattern_queue__(self):
        if self.pattern_queue is None or self.pattern_queue.is_empty() or self.process != '':
            return
        queue = self.pattern_queue
        self.process = 'HandlePatternQueue'
        for pattern in queue.pattern_list:
            self.__add_pattern_for_trade__(pattern, queue.buy_trigger, queue.box_type, queue.trade_strategy)
        self.pattern_queue.pattern_list = []
        self.process = ''

    def __add_pattern_for_trade__(self, pattern: Pattern, buy_trigger: str, box_type: str, trade_strategy: str):
        if pattern.expected_breakout_direction != FD.ASC:  # currently we only handle higher curses...
            print('pattern.expected_breakout_direction: {}'.format(pattern.expected_breakout_direction))
            return
        if pattern.ticker_id not in self.ticker_id_list:
            self.ticker_id_list.append(pattern.ticker_id)
        pattern_trade = PatternTrade(pattern, buy_trigger, box_type, trade_strategy)
        print('Added to trade list: {}'.format(pattern_trade.id))
        if pattern_trade.id in self.pattern_trade_dict:
            if self.pattern_trade_dict[pattern_trade.id].status == PTS.NEW:  # replace with new version
                self.pattern_trade_dict[pattern_trade.id] = pattern_trade
        else:
            self.pattern_trade_dict[pattern_trade.id] = pattern_trade

    def check_actual_trades(self, last_price_for_test=None):
        self._last_price_for_test = last_price_for_test
        self._time_stamp_check = MyDate.get_epoch_seconds_from_datetime()
        self._date_time_check = MyDate.get_date_time_from_epoch_seconds(self._time_stamp_check)
        self.__remove_finished_pattern_trades__()
        self.__process_pattern_queue__()  # take care of old patterns in queue
        if self.trade_numbers == 0:
            return
        print('Check_actual_trades: {} trades at {}'.format(self.trade_numbers, self._date_time_check))
        self.process = 'Ticker'
        self.__adjust_stops_and_limits__()
        self.__handle_sell_triggers__()
        self.__handle_wrong_breakout__()
        self.__handle_buy_breakout__()
        self.__handle_buy_touches__()
        self.__update_ticker_lists__()  # some entries could be deleted
        self.process = ''

    def sell_on_fibonacci_cluster_top(self):
        self.bitfinex_trade_client.delete_all_orders()
        self.bitfinex_trade_client.sell_all_assets()
        self.__clear_internal_lists__()

    def __get_ticker_by_ticker_id__(self, ticker_id: str):
        ticker = self.bitfinex_trade_client.get_ticker(ticker_id)
        if self._last_price_for_test:
            ticker.last_price = self._last_price_for_test
        return ticker

    def __get_balance_by_symbol__(self, symbol: str):
        return self.bitfinex_trade_client.get_balance(symbol)

    def __clear_internal_lists__(self):
        self.ticker_id_list = []
        self.pattern_trade_dict = {}

    def __handle_sell_triggers__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values():
            print('handle_sell: status = {}, stop_loss={}, limit={}'.format(pattern_trade.status,
                                                                            pattern_trade.stop_loss_current,
                                                                            pattern_trade.limit_current))
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            if pattern_trade.stop_loss_current > ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.STOP_LOSS)
            elif pattern_trade.limit_current < ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.LIMIT)

    def __handle_sell_trigger__(self, ticker: Ticker, ticker_id: str, pattern_trade: PatternTrade, sell_trigger: str):
        sell_comment = 'Sell_{} at {:.2f} on {}'.format(sell_trigger, ticker.last_price, self._date_time_check)
        print('Sell: {}'.format(sell_comment))
        order_status = self.bitfinex_trade_client.create_sell_market_order(ticker_id, pattern_trade.executed_amount)
        pattern_trade.set_order_status_sell(order_status, sell_trigger, sell_comment)

    def __handle_wrong_breakout__(self):
        deletion_key_list = []
        for key, pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).items():
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            if pattern_trade.is_ticker_wrong_breakout(ticker, self._time_stamp_check):
                deletion_key_list.append(key)
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list)

    def __remove_finished_pattern_trades__(self):
        deletion_key_list = [key for key in self.__get_pattern_trade_dict_by_status__(PTS.FINISHED)]
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list)

    def __delete_entries_from_pattern_trade_dict__(self, deletion_key_list: list):
        if len(deletion_key_list) == 0:
            return
        for key in deletion_key_list:
            del self.pattern_trade_dict[key]
        self.__update_ticker_lists__()

    def __handle_buy_breakout__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).values():
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            if pattern_trade.is_ticker_breakout(ticker, self._time_stamp_check):
                self.__handle_buy_breakout_for_pattern_trade__(ticker, pattern_trade.ticker_id, pattern_trade)

    def __handle_buy_breakout_for_pattern_trade__(self, ticker: Ticker, ticker_id: str, pattern_trade: PatternTrade):
        buy_comment = '{}-breakout at {:.2f} on {}'.format(ticker_id, ticker.last_price, self._date_time_check)
        print('Handle_buy_breakout_for_pattern_trade: {}'.format(buy_comment))
        order_status = self.bitfinex_trade_client.buy_available(ticker_id, ticker.last_price)
        pattern_trade.set_order_status_buy(order_status, buy_comment, ticker)

    def __handle_buy_touches__(self):
        pass

    def __adjust_stops_and_limits__(self):
        for pattern_trade in self.pattern_trade_dict.values():
            if pattern_trade.status == PTS.EXECUTED:
                ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
                pattern_trade.adjust_to_next_ticker_last_price(ticker.last_price)

    def __create_trailing_stop_order_for_all_executed_trades__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values():
            ticker_id = pattern_trade.ticker_id
            amount = pattern_trade.order_status_buy.executed_amount
            distance = pattern_trade.trailing_stop_distance
            pattern_trade.order_status_sell = self.bitfinex_trade_client.create_sell_trailing_stop_order(
                ticker_id, amount, distance)

    def __update_ticker_lists__(self):
        self.ticker_id_list = []
        for pattern_trade in self.pattern_trade_dict.values():
            if pattern_trade.ticker_id not in self.ticker_id_list:
                self.ticker_id_list.append(pattern_trade.ticker_id)

    def __get_pattern_trade_dict_by_status__(self, status: str) -> dict:
        return {key: value for key, value in self.pattern_trade_dict.items() if value.status == status}



