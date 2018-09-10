"""
Description: This module contains the PatternTradeContainer class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import TSTR, BT, ST, FD, DC, TBT, PTS, OS, TR
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from pattern import Pattern
from pattern_bitfinex import MyBitfinexTradeClient, BitfinexConfiguration
from sertl_analytics.exchanges.exchange_cls import OrderStatus, Ticker
from sertl_analytics.searches.smart_searches import Queue
from pattern_data_dictionary import PatternDataDictionary
from pattern_trading_box import FibonacciTradingBox, ExpectedWinTradingBox, TouchPointTradingBox
from pattern_trading_box import ForecastHalfLengthTradingBox, ForecastFullLengthTradingBox


class PatternTradeApi:
    def __init__(self, pattern: Pattern, buy_trigger: str, box_type: str, trade_strategy: str):
        self.pattern = pattern
        self.buy_trigger = buy_trigger
        self.box_type = box_type
        self.trade_strategy = trade_strategy


class PatternTrade:
    def __init__(self, api: PatternTradeApi):
        self.sys_config = api.pattern.sys_config
        self.buy_trigger = api.buy_trigger
        self.trade_box_type = api.box_type
        self.trade_strategy = api.trade_strategy
        self.pattern = api.pattern
        self._is_simulation = True  # Default
        self.expected_win = self.pattern.data_dict_obj.get(DC.EXPECTED_WIN)
        self.expected_breakout_direction = self.pattern.expected_breakout_direction
        self.id = '{}-{}-{}_{}'.format(self.buy_trigger, self.trade_box_type, self.trade_strategy, self.pattern.id)
        self._order_status_buy = None
        self._order_status_sell = None
        self._status = PTS.NEW
        self._trade_box = None
        self.data_dict_obj = PatternDataDictionary(self.sys_config)
        self.data_dict_obj.inherit_values(self.pattern.data_dict_obj.data_dict)
        self.__add_trade_basis_data_to_data_dict__()
        self.__calculate_prediction_values__()

    @property
    def executed_amount(self):
        return self._order_status_buy.executed_amount

    @property
    def order_status_buy(self):
        return self._order_status_buy

    @property
    def order_status_sell(self):
        return self._order_status_buy

    @property
    def stop_loss_current(self):
        return self._trade_box.stop_loss

    @property
    def limit_current(self):
        return self._trade_box.limit

    @property
    def time_stamp_end(self):
        return self._trade_box.time_stamp_end

    @property
    def trailing_stop_distance(self):
        return self._trade_box.trailing_stop_distance

    @property
    def ticker_id(self):
        return self.pattern.ticker_id.replace('_', '')

    @property
    def status(self):
        return self._status

    def set_time_stamp_end(self):
        self._trade_box.set_time_stamp_end()

    def __get_is_simulation__(self) -> bool:
        return self._is_simulation

    def __set_is_simulation__(self, value: bool):
        self._is_simulation = value

    is_simulation = (__get_is_simulation__, __set_is_simulation__)

    def __calculate_prediction_values__(self):
        predictor = self.sys_config.predictor_for_trades
        x_data = self.__get_x_data_for_prediction__(predictor.feature_columns)
        if x_data is not None:
            prediction_dict = predictor.predict_for_label_columns(x_data)
            self.data_dict_obj.add(DC.FC_TRADE_REACHED_PRICE_PCT, prediction_dict[DC.TRADE_REACHED_PRICE_PCT])
            self.data_dict_obj.add(DC.FC_TRADE_RESULT_ID, prediction_dict[DC.TRADE_RESULT_ID])

    def is_ticker_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            upper_value = self.pattern.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        # elif self.expected_breakout_direction == FD.DESC:
        #     lower_value = self.pattern.get_lower_value(time_stamp)
        #     return ticker.last_price <= lower_value
        return False

    def is_ticker_wrong_breakout(self, ticker: Ticker, time_stamp: int):
        if self.expected_breakout_direction == FD.ASC:
            lower_value = self.pattern.get_lower_value(time_stamp)
            return ticker.last_price <= lower_value
        elif self.expected_breakout_direction == FD.DESC:
            upper_value = self.pattern.get_upper_value(time_stamp)
            return ticker.last_price >= upper_value
        return False

    def save_trade(self):
        if not self.sys_config.config.save_trade_data:
            return
        if self.data_dict_obj.is_data_dict_ready_for_trade_table():
            trade_dict = self.data_dict_obj.get_data_dict_for_trade_table()
            if not self.sys_config.db_stock.is_trade_already_available(trade_dict[DC.ID]):
                self.sys_config.db_stock.insert_trade_data([trade_dict])

    def print_trade(self, prefix = ''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print(self.get_trade_meta_data())
        if self._order_status_buy:
            self._order_status_buy.print_order_status('Buy order')
        if self._order_status_sell:
            self._order_status_sell.print_order_status('Sell order')

    def get_trade_meta_data(self):
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        return '{}: {}'.format(self.id, details)

    def __get_value_dict__(self) -> dict:
        return {'Status': self.status, 'Buy_trigger': self.buy_trigger, 'Trade_box': self.trade_box_type,
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
        self.__add_order_status_buy_to_data_dict__(self._order_status_buy)
        self.__add_order_status_sell_to_data_dict__(self._order_status_sell)  # to initialize those data
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
        self.__add_order_status_sell_to_data_dict__(self._order_status_sell)  # to fill these data finally
        self.print_trade('Details after selling')

    def __set_properties_after_sell__(self):
        self._status = PTS.FINISHED

    def __add_trade_basis_data_to_data_dict__(self):
        self.data_dict_obj.add(DC.ID, self.id)
        self.data_dict_obj.add(DC.TRADE_STRATEGY, self.trade_strategy)
        self.data_dict_obj.add(DC.TRADE_STRATEGY_ID, TSTR.get_id(self.trade_strategy))
        self.data_dict_obj.add(DC.TRADE_BOX_TYPE, self.trade_box_type)
        self.data_dict_obj.add(DC.TRADE_BOX_TYPE_ID, TBT.get_id(self.trade_box_type))
        self.data_dict_obj.add(DC.BUY_TRIGGER, self.buy_trigger)
        self.data_dict_obj.add(DC.BUY_TRIGGER_ID, BT.get_id(self.buy_trigger))

    def __add_order_status_buy_to_data_dict__(self, order_status: OrderStatus):
        self.data_dict_obj.add(DC.BUY_ORDER_ID, order_status.order_id)
        self.data_dict_obj.add(DC.BUY_ORDER_TPYE, order_status.type)
        self.data_dict_obj.add(DC.BUY_ORDER_TPYE_ID, OS.get_id(order_status.type))
        self.data_dict_obj.add(DC.BUY_DT, MyDate.get_date_from_epoch_seconds(order_status.time_stamp))
        self.data_dict_obj.add(DC.BUY_TIME, str(MyDate.get_time_from_epoch_seconds(order_status.time_stamp)))
        self.data_dict_obj.add(DC.BUY_AMOUNT, order_status.executed_amount)
        self.data_dict_obj.add(DC.BUY_PRICE, order_status.avg_execution_price)
        self.data_dict_obj.add(DC.BUY_TOTAL_COSTS, order_status.value_total)
        self.data_dict_obj.add(DC.BUY_TRIGGER, order_status.order_trigger)
        self.data_dict_obj.add(DC.BUY_TRIGGER_ID, BT.get_id(order_status.order_trigger))
        self.data_dict_obj.add(DC.BUY_COMMENT, order_status.order_comment)

    def __add_order_status_sell_to_data_dict__(self, order_status: OrderStatus):
        if order_status:
            self.data_dict_obj.add(DC.TRADE_BOX_HEIGHT, self._trade_box.height)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT, self._trade_box.limit)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS, self._trade_box.stop_loss)

            self.data_dict_obj.add(DC.SELL_ORDER_ID, order_status.order_id)
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE, order_status.type)
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE_ID, OS.get_id(order_status.type))
            self.data_dict_obj.add(DC.SELL_DT, MyDate.get_date_from_epoch_seconds(order_status.time_stamp))
            self.data_dict_obj.add(DC.SELL_TIME, str(MyDate.get_time_from_epoch_seconds(order_status.time_stamp)))
            self.data_dict_obj.add(DC.SELL_AMOUNT, order_status.executed_amount)
            self.data_dict_obj.add(DC.SELL_PRICE, order_status.avg_execution_price)
            self.data_dict_obj.add(DC.SELL_TOTAL_VALUE, order_status.value_total)
            self.data_dict_obj.add(DC.SELL_TRIGGER, order_status.order_trigger)
            self.data_dict_obj.add(DC.SELL_TRIGGER_ID, ST.get_id(order_status.order_trigger))
            self.data_dict_obj.add(DC.SELL_COMMENT, order_status.order_comment)
            if self.data_dict_obj.get(DC.BUY_TOTAL_COSTS) < self.data_dict_obj.get(DC.SELL_TOTAL_VALUE):
                trade_result = TR.WINNER
            else:
                trade_result = TR.LOSER
            self.data_dict_obj.add(DC.TRADE_REACHED_PRICE, self._trade_box.max_ticker_last_price)
            self.data_dict_obj.add(DC.TRADE_REACHED_PRICE_PCT, self._trade_box.max_ticker_last_price_pct)
            self.data_dict_obj.add(DC.TRADE_RESULT, trade_result)
            self.data_dict_obj.add(DC.TRADE_RESULT_ID, TR.get_id(trade_result))
        else:
            self.data_dict_obj.add(DC.TRADE_BOX_HEIGHT, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS, 0)

            self.data_dict_obj.add(DC.SELL_ORDER_ID, '')
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE, '')
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE_ID, 0)
            self.data_dict_obj.add(DC.SELL_DT, None)
            self.data_dict_obj.add(DC.SELL_TIME, '')
            self.data_dict_obj.add(DC.SELL_AMOUNT, 0)
            self.data_dict_obj.add(DC.SELL_PRICE, 0)
            self.data_dict_obj.add(DC.SELL_TOTAL_VALUE, 0)
            self.data_dict_obj.add(DC.SELL_TRIGGER, '')
            self.data_dict_obj.add(DC.SELL_TRIGGER_ID, 0)
            self.data_dict_obj.add(DC.SELL_COMMENT, '')
            self.data_dict_obj.add(DC.TRADE_REACHED_PRICE, 0)
            self.data_dict_obj.add(DC.TRADE_REACHED_PRICE_PCT, 0)
            self.data_dict_obj.add(DC.TRADE_RESULT, '')
            self.data_dict_obj.add(DC.TRADE_RESULT_ID, 0)

    def __get_x_data_for_prediction__(self, feature_columns: list):
        if self.data_dict_obj.is_data_dict_ready_for_columns(feature_columns):
            data_list = self.data_dict_obj.get_data_list_for_columns(feature_columns)
            np_array = np.array(data_list).reshape(1, len(data_list))
            # print('{}: np_array.shape={}'.format(prediction_type, np_array.shape))
            return np_array
        return None


class TradeQueueEntry:
    def __init__(self, pattern_trade: PatternTrade):
        self.pattern_trade = pattern_trade
        self.forecast_pct = self.pattern_trade.data_dict_obj.get(DC.FC_TRADE_REACHED_PRICE_PCT)
        self.forecast_result_id = self.pattern_trade.data_dict_obj.get(DC.FC_TRADE_RESULT_ID)

    def get_simulation_flag(self, simulation_by_config: bool) -> bool:
        if not simulation_by_config:
            if self.forecast_result_id == 1:
                return False
        return True


class TradeQueueController:
    def __init__(self, for_simulation: bool):
        self.for_simulation = for_simulation
        self.actual_pattern_id_list = []  # this list contains all pattern_ids for actual trade candidates
        self.black_pattern_id_list = []
        self.trade_queue = Queue()

    def add_new_pattern_list(self, pattern_list: list):
        self.actual_pattern_id_list = []
        for pattern in pattern_list:
            self.actual_pattern_id_list.append(pattern.id)
            self.__add_pattern_to_queue_after_checks__(pattern)

    def __add_pattern_to_queue_after_checks__(self, pattern: Pattern):
        if pattern.id in self.black_pattern_id_list:
            return  # already checked against some conditions
        if pattern.are_pre_conditions_for_a_trade_fulfilled():
            for strategy in [TSTR.LIMIT, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP]:
                trade_api = PatternTradeApi(pattern, BT.BREAKOUT, TBT.EXPECTED_WIN, strategy)
                trade_queue_entry = TradeQueueEntry(PatternTrade(trade_api))
                self.trade_queue.enqueue(trade_queue_entry)
            pass
        else:
            self.black_pattern_id_list.append(pattern.id)

    def get_pattern_trades_for_processing(self) -> list:
        return_list = []
        while self.trade_queue.size() > 0:
            trade_queue_entry = self.trade_queue.dequeue()
            trade_entry = trade_queue_entry.pattern_trade
            trade_entry.is_simulation = trade_queue_entry.get_simulation_flag(self.for_simulation)
            return_list.append(trade_entry)
        return return_list


class PatternTradeHandler:
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        self.sys_config = sys_config
        self.bitfinex_config = bitfinex_config
        self.bitfinex_trade_client = MyBitfinexTradeClient(bitfinex_config)
        self.stock_db = self.sys_config.db_stock
        self.ticker_id_list = []
        self.pattern_trade_dict = {}
        self.pattern_id_black_list = []
        self._time_stamp_check = 0
        self._date_time_check = None
        self.process = ''
        self.trade_queue_controller = TradeQueueController(self.bitfinex_config.is_simulation)
        self._last_price_for_test = 0

    # def __del__(self):
    #     print('PatternTradeHandler: Destructor...')
    #     self.__create_trailing_stop_order_for_all_executed_trades__()

    @property
    def trade_numbers(self) -> int:
        return len(self.pattern_trade_dict)

    def add_pattern_list_for_trade(self, pattern_list):
        self.trade_queue_controller.add_new_pattern_list(pattern_list)
        self.__process_pattern_queue__()

    def __add_pattern_trade_for_trading__(self, pattern_trade: PatternTrade):
        if pattern_trade.pattern.ticker_id not in self.ticker_id_list:
            self.ticker_id_list.append(pattern_trade.pattern.ticker_id)
        print('Added to trading list{}: {}'.format(' (simulation)' if pattern_trade.is_simulation else ' (REAL)',
                                                   pattern_trade.id))
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
        self.process = 'Ticker'
        self.__adjust_stops_and_limits__()
        self.__handle_sell_triggers__()
        self.__handle_wrong_breakout__()
        self.__handle_buy_breakout__()
        self.__handle_buy_touches__()
        self.__update_ticker_lists__()  # some entries could be deleted
        self.process = ''

    def __process_pattern_queue__(self):
        if self.process != '':
            return
        self.process = 'HandlePatternQueue'
        for pattern_trade in self.trade_queue_controller.get_pattern_trades_for_processing():
            self.__add_pattern_trade_for_trading__(pattern_trade)
        self.__remove_outdated_pattern_trades__()
        self.__set_executed_outdated_pattern_trades_to_end__()
        self.process = ''

    def __remove_outdated_pattern_trades__(self):  # remove trades which doesn't belong to an actual pattern anymore
        deletion_key_list = [key for key, trades in self.__get_pattern_trade_dict_by_status__(PTS.NEW).items()
                             if trades.pattern.id not in self.trade_queue_controller.actual_pattern_id_list]
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list)

    def __set_executed_outdated_pattern_trades_to_end__(self):  # pattern is no longer valid. enforce sell.
        for trades in [trades for trades in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values()
                             if trades.pattern.id not in self.trade_queue_controller.actual_pattern_id_list]:
            trades.set_time_stamp_end()

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
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            self.__print_current_state__('Check sell', pattern_trade, ticker)
            if pattern_trade.stop_loss_current > ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.STOP_LOSS)
            elif pattern_trade.limit_current < ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.LIMIT)
            elif pattern_trade.time_stamp_end < ticker.time_stamp:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.PATTERN_END)

    def __handle_sell_trigger__(self, ticker: Ticker, ticker_id: str, pattern_trade: PatternTrade, sell_trigger: str):
        sell_comment = 'Sell_{} at {:.2f} on {}'.format(sell_trigger, ticker.last_price, self._date_time_check)
        print('Sell: {}'.format(sell_comment))
        order_status = self.bitfinex_trade_client.create_sell_market_order(ticker_id, pattern_trade.executed_amount)
        pattern_trade.set_order_status_sell(order_status, sell_trigger, sell_comment)
        pattern_trade.save_trade()

    def __handle_wrong_breakout__(self):
        deletion_key_list = []
        for key, pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).items():
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            self.__print_current_state__('Check wrong breakout', pattern_trade, ticker)
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
            pattern_trade = self.pattern_trade_dict[key]
            print('Removed from processing list: {}'.format(pattern_trade.get_trade_meta_data()))
            del self.pattern_trade_dict[key]
        self.__update_ticker_lists__()

    def __handle_buy_breakout__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).values():
            ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
            self.__print_current_state__('Check buy breakout', pattern_trade, ticker)
            if pattern_trade.is_ticker_breakout(ticker, self._time_stamp_check):
                self.__handle_buy_breakout_for_pattern_trade__(ticker, pattern_trade)

    def __handle_buy_breakout_for_pattern_trade__(self, ticker: Ticker, pattern_trade: PatternTrade):
        ticker_id = pattern_trade.ticker_id
        buy_comment = '{}-breakout at {:.2f} on {}'.format(ticker_id, ticker.last_price, self._date_time_check)
        print('Handle_buy_breakout_for_pattern_trade: {}'.format(buy_comment))
        order_status = self.bitfinex_trade_client.buy_available(ticker_id, ticker.last_price)
        pattern_trade.set_order_status_buy(order_status, buy_comment, ticker)
        # pattern_trade.save_trade()

    @staticmethod
    def __print_current_state__(scope: str, pattern_trade: PatternTrade, ticker: Ticker):
        if pattern_trade.status == PTS.NEW:
            if scope == 'Check buy breakout':
                breakout_value = pattern_trade.pattern.get_upper_value(ticker.time_stamp)
            else:
                breakout_value = pattern_trade.pattern.get_lower_value(ticker.time_stamp)
            print('{} for {}: ticker.last_price={:.2f}, breakout value={:.2f}'.format(
                scope, ticker.ticker_id, ticker.last_price, breakout_value))
        else:
            print('{} for {}: limit={:.2f}, ticker.last_price={:.2f}, stop_loss={:.2f}, bought_at={:.2f}'.format(
                scope, ticker.ticker_id, pattern_trade.limit_current, ticker.last_price,
                pattern_trade.stop_loss_current, pattern_trade.order_status_buy.avg_execution_price))

    def __handle_buy_touches__(self):
        pass

    def __adjust_stops_and_limits__(self):
        for pattern_trade in self.pattern_trade_dict.values():
            if pattern_trade.status == PTS.EXECUTED:
                ticker = self.__get_ticker_by_ticker_id__(pattern_trade.ticker_id)
                self.__print_current_state__('Adjust limit&stop', pattern_trade, ticker)
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



