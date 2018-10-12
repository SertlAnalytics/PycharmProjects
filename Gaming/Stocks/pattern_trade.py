"""
Description: This module contains the PatternTrade class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import TSTR, BT, ST, FD, DC, TBT, PTS, PTHP, TR, OT, SVC, TP, FT, CN
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from sertl_analytics.exchanges.exchange_cls import OrderStatus, Ticker
from pattern_database.stock_tables import TradeTable
from pattern_data_dictionary import PatternDataDictionary
from pattern_trade_box import ExpectedWinTradingBox, TouchPointTradingBox, TradingBoxApi
from pattern_wave_tick import WaveTick, WaveTickList, TickerWaveTickConverter
from sertl_analytics.plotter.my_plot import MyPlotHelper
import math
from textwrap import dedent


class PatternTradeApi:
    def __init__(self, pattern: Pattern, buy_trigger: str, trade_strategy: str):
        self.bitfinex_config = None
        self.pattern = pattern
        self.buy_trigger = buy_trigger
        self.box_type = TBT.TOUCH_POINT if buy_trigger == BT.TOUCH_POINT else TBT.EXPECTED_WIN
        self.trade_strategy = trade_strategy


class PatternTrade:
    def __init__(self, api: PatternTradeApi):
        self.sys_config = api.pattern.sys_config
        self.bitfinex_config = api.bitfinex_config
        self.trade_process = self.sys_config.runtime.actual_trade_process
        self.buy_trigger = api.buy_trigger
        self.trade_box_type = api.box_type
        self.trade_strategy = api.trade_strategy
        self.pattern = api.pattern
        self._wave_tick_list = WaveTickList(self.pattern.part_entry.tick_list)
        if self.trade_process == TP.TRADE_REPLAY:
            self.__initialize_breakout_values_for_tick_list__()
        self._wave_tick_at_start = self._wave_tick_list.tick_list[-1]
        self._wave_tick_at_buying = None
        self._wave_tick_at_selling = None
        self._df_for_replay = self._wave_tick_list.get_tick_list_as_data_frame_for_replay()
        self._ticker_converter = self.__get_ticker_wave_tick_converter__()
        self._ticker_time_stamp_list = []
        self._ticker_dict = {}
        self._is_simulation = True  # Default
        self._is_breakout_active = self.__get_default_value_for_breakout_active__()
        self._counter_required = 2
        self._breakout_counter = 0
        self._wrong_breakout_counter = 0
        self._was_candidate_for_real_trading = False  # default
        self.expected_win = self.pattern.data_dict_obj.get(DC.EXPECTED_WIN)
        self.expected_breakout_direction = self.pattern.expected_breakout_direction
        self._order_status_buy = None
        self._order_status_sell = None
        self._status = PTS.NEW
        self._trade_box = None
        self.data_dict_obj = PatternDataDictionary(self.sys_config)
        self.data_dict_obj.inherit_values(self.pattern.data_dict_obj.data_dict)
        self.__add_trade_basis_data_to_data_dict__()
        self.__calculate_prediction_values__()
        self._xy_for_buying = None
        self._xy_for_selling = None
        self._xy_after_selling = None

    @property
    def id(self):
        return '{}-{}-{}_{}'.format(self.buy_trigger, self.trade_box_type, self.trade_strategy, self.pattern.id_readable)

    @property
    def is_winner(self) -> bool:
        return self.data_dict_obj.get(DC.TRADE_RESULT_ID, 0) == 1

    @property
    def is_breakout_active(self):
        return self._is_breakout_active

    @property
    def counter_required(self):
        return self._counter_required

    @property
    def breakout_counter(self):
        return self._breakout_counter

    @property
    def wrong_breakout_counter(self):
        return self._wrong_breakout_counter

    @property
    def was_candidate_for_real_trading(self):
        return self._was_candidate_for_real_trading

    @was_candidate_for_real_trading.setter
    def was_candidate_for_real_trading(self, value: bool):
        self._was_candidate_for_real_trading = value

    @property
    def executed_amount(self):
        return self._order_status_buy.executed_amount if self._order_status_buy else 0

    @property
    def order_status_buy(self):
        return self._order_status_buy

    @property
    def order_status_sell(self):
        return self._order_status_buy

    @property
    def stop_loss_current(self):
        return self._trade_box.stop_loss if self._trade_box else self.wave_tick_actual.wrong_breakout_value

    @property
    def limit_current(self):
        return self._trade_box.limit if self._trade_box else self.wave_tick_actual.breakout_value

    @property
    def time_stamp_end(self):
        return self._trade_box.time_stamp_end if self._trade_box else 0

    @property
    def trailing_stop_distance(self):
        return self._trade_box.distance_trailing_stop if self._trade_box else 0

    @property
    def ticker_id(self):
        return self.pattern.ticker_id.replace('_', '')

    @property
    def status(self):
        return self._status

    @property
    def is_simulation(self) -> bool:
        return self._is_simulation

    @is_simulation.setter
    def is_simulation(self, value: bool):
        self._is_simulation = value

    @property
    def ticker_actual(self) -> Ticker:
        return self._ticker_dict[self._ticker_time_stamp_list[-1]]

    @property
    def wave_tick_actual(self) -> WaveTick:
        return self._wave_tick_list.tick_list[-1]

    @property
    def current_trade_process(self) -> str:
        if self._status == PTS.NEW:
            return 'buying'
        elif self._status == PTS.EXECUTED:
            return 'selling'
        return 're-buying'

    @property
    def xy_for_buying(self):
        return self._xy_for_buying

    @property
    def xy_for_selling(self):
        return self._xy_for_selling

    @property
    def xy_after_selling(self):
        return self._xy_after_selling

    def get_data_frame_for_replay(self):
        # return self.pattern.df
        if len(self._wave_tick_list.tick_list) > self.pattern.df_length:
            return self._df_for_replay
        else:
            return self._df_for_replay

    def add_ticker(self, ticker: Ticker):
        self._ticker_time_stamp_list.append(ticker.time_stamp)
        self._ticker_dict[ticker.time_stamp] = ticker
        if self._ticker_converter.can_next_ticker_been_added_to_current_wave_tick(ticker.time_stamp):
            self._ticker_converter.add_value_with_timestamp(ticker.last_price, ticker.time_stamp)
            self._wave_tick_list.replace_last_wave_tick(self._ticker_converter.current_wave_tick)
        else:
            self._ticker_converter.reset_variables()
            self._ticker_converter.add_value_with_timestamp(ticker.last_price, ticker.time_stamp)
            self._wave_tick_list.add_wave_tick(self._ticker_converter.current_wave_tick)
        self._df_for_replay = self._wave_tick_list.get_tick_list_as_data_frame_for_replay()
        # self.ticker_actual.print_ticker('Trade: {}: last ticker'.format(self.id))

    def calculate_xy_for_replay(self):
        tick_list_base = self._wave_tick_list.tick_list
        # print('After__initialize_replay_values_for_tick_list__\n')
        # for tick in tick_list_base:
        #     print('datetime={}: tick.breakout_value={}, tick.wrong_breakout_value={}'.format(
        #         MyDate.get_date_time_from_epoch_seconds(tick.time_stamp), tick.breakout_value, tick.wrong_breakout_value))
        # self.__init_wave_tick_values__(tick_list_base)
        if self.status == PTS.NEW:
            self.__initialize_breakout_values_for_tick_list__()
            tick_list = [tick for tick in tick_list_base if tick.position >= self._wave_tick_at_start.position]
            self._xy_for_buying = MyPlotHelper.get_xy_parameter_for_replay_list(tick_list, True)
        elif self.status == PTS.EXECUTED:
            self.__initialize_limit_stop_loss_values_for_tick_list__(tick_list_base)
            tick_list = [tick for tick in tick_list_base if tick.position >= self._wave_tick_at_buying.position-1]
            self._xy_for_selling = MyPlotHelper.get_xy_parameter_for_replay_list(tick_list, False)
        elif self.status == PTS.FINISHED:
            tick_list = [tick for tick in tick_list_base if tick.position >= self._wave_tick_at_selling.position]
            self._xy_after_selling = MyPlotHelper.get_xy_parameter_for_replay_list(tick_list, False)

    def __initialize_limit_stop_loss_values_for_tick_list__(self, tick_list: list):
        for wave_tick in tick_list:
            if wave_tick.limit_value == 0:
                wave_tick.limit_value = self._trade_box.limit
            if wave_tick.stop_loss_value == 0:
                wave_tick.stop_loss_value = self._trade_box.stop_loss
        # for tick in tick_list:
        #     print('tick.limit_value={}, stop_loss_value={}'.format(tick.limit_value, tick.stop_loss_value))

    def get_ticker_for_time_stamp(self, ticker_time_stamp: int):
        return self._ticker_dict[ticker_time_stamp]

    def __get_default_value_for_breakout_active__(self):
        if self.buy_trigger == BT.BREAKOUT:
            return True
        return False # it's not active for touch and fibonacci till confirmation

    def __calculate_prediction_values__(self):
        predictor = self.sys_config.master_predictor_for_trades
        feature_columns = predictor.get_feature_columns(self.pattern.pattern_type)
        x_data = self.__get_x_data_for_prediction__(feature_columns)
        if x_data is not None:
            prediction_dict = predictor.predict_for_label_columns(self.pattern.pattern_type, x_data)
            self.data_dict_obj.add(DC.FC_TRADE_REACHED_PRICE_PCT, prediction_dict[DC.TRADE_REACHED_PRICE_PCT])
            self.data_dict_obj.add(DC.FC_TRADE_RESULT_ID, prediction_dict[DC.TRADE_RESULT_ID])

    def __initialize_breakout_values_for_tick_list__(self):
        vc_b = self.__get_value_category_for_breakout__()
        vc_wb = self.__get_value_category_for_wrong_breakout__()
        for tick in self._wave_tick_list.tick_list:
            l_value_b, u_value_b = self.pattern.value_categorizer.get_value_range_for_category(tick.time_stamp, vc_b)
            l_value_wb, u_value_wb = self.pattern.value_categorizer.get_value_range_for_category(tick.time_stamp, vc_wb)
            tick.breakout_value = round(l_value_b, 4)
            tick.wrong_breakout_value = round(u_value_wb, 4)

    def set_limit_stop_loss_to_replay_values(self):
        last_wave_tick = self._wave_tick_list.last_wave_tick
        if self.limit_current == math.inf or self.limit_current == 0:
            last_wave_tick.limit_value = self._df_for_replay[CN.HIGH].max()
        else:
            last_wave_tick.limit_value = self.limit_current
        if self.stop_loss_current == 0:
            last_wave_tick.stop_loss_value = self.pattern.function_cont.f_lower(last_wave_tick.f_var)
        else:
            last_wave_tick.stop_loss_value = self.stop_loss_current

    def is_actual_ticker_breakout(self, process: str):
        if not self._is_breakout_active:
            return False
        ts = self.ticker_actual.time_stamp
        vc = self.__get_value_category_for_breakout__()
        l_value, u_value = self.pattern.value_categorizer.get_value_range_for_category(ts, vc)
        self.__print_details_for_actual_value_category__('Check breakout', l_value, u_value, vc)
        if l_value < self.ticker_actual.last_price < u_value:
            self._breakout_counter += 1 if self.buy_trigger == BT.BREAKOUT else 2  # touch point => immediate buy
        self._wave_tick_list.last_wave_tick.breakout_value = l_value
        self.print_state_details_for_actual_ticker(process)
        return self._breakout_counter >= self._counter_required  # we need a second confirmation

    def __print_details_for_actual_value_category__(self, process: str, l_value: float, u_value: float, vc: str):
        date_time = MyDate.get_date_time_from_epoch_seconds(self.ticker_actual.time_stamp)
        ticker_id = self.ticker_actual.ticker_id
        print('{}: {}-{} vc={}: [{:.2f}, {:.2f}]: price={}, date_time={}'.format(
            self.trade_process, ticker_id, process, vc, l_value, u_value, self.ticker_actual.last_price, date_time))

    def are_preconditions_for_breakout_buy_fulfilled(self):
        if self.trade_strategy == TSTR.SMA:
            sma = self._wave_tick_list.get_simple_moving_average(self.sys_config.config.simple_moving_average_number)
            time_stamp = self._ticker_time_stamp_list[-1]
            value_categories = [SVC.M_in, SVC.H_M_in]
            for value_category in value_categories:
                if self.pattern.is_value_in_category(sma, time_stamp, value_category, True):
                    return True
        return True

    def __get_value_category_for_breakout__(self):
        if self.pattern.pattern_type in [FT.TKE_BOTTOM, FT.FIBONACCI_DESC]:
            return SVC.H_M_in if self.buy_trigger == BT.TOUCH_POINT else SVC.H_U_out
        else:
            return SVC.M_in if self.buy_trigger == BT.TOUCH_POINT else SVC.U_out

    def is_actual_ticker_wrong_breakout(self, process: str):
        ticker = self.ticker_actual
        vc = self.__get_value_category_for_wrong_breakout__()
        l_value, u_value = self.pattern.value_categorizer.get_value_range_for_category(ticker.time_stamp, vc)
        if ticker.last_price < u_value:
            self._wrong_breakout_counter += 1
        self._wave_tick_list.last_wave_tick.wrong_breakout_value = u_value
        self.print_state_details_for_actual_ticker(process)
        return self._wrong_breakout_counter >= self._counter_required  # we need a second confirmation

    def __get_value_category_for_wrong_breakout__(self):
        if self.pattern.pattern_type in [FT.TKE_BOTTOM, FT.FIBONACCI_DESC]:
            return SVC.H_L_out
        else:
            return SVC.L_out

    def verify_touch_point(self):
        ticker = self.ticker_actual
        last_tick = self.pattern.part_entry.tick_last
        value_tuple_list = [[ticker.last_price, ticker.time_stamp], [last_tick.low, last_tick.time_stamp]]

        vc_b = self.__get_value_category_for_breakout__()
        l_value, u_value = self.pattern.value_categorizer.get_value_range_for_category(ticker.time_stamp, vc_b)
        self.__print_details_for_actual_value_category__('Verify touch-point', l_value, u_value, vc_b)

        for value_tuple in value_tuple_list:
            if value_tuple[0] < l_value:
                self._is_breakout_active = True
                print('Breakout activated for last price={:.2f}'.format(ticker.last_price))
                break

    def print_state_details_for_actual_ticker(self, process: str):
        ticker = self.ticker_actual
        if self.status == PTS.NEW:
            counter_required = self.counter_required
            if self.buy_trigger == BT.BREAKOUT:
                if process == PTHP.HANDLE_WRONG_BREAKOUT:
                    breakout_value = self.pattern.get_lower_value(ticker.time_stamp)
                    counter = self.wrong_breakout_counter
                else:
                    breakout_value = self.pattern.get_upper_value(ticker.time_stamp)
                    counter = self.breakout_counter
            else:
                breakout_value = self.pattern.get_lower_value(ticker.time_stamp)
                if process == PTHP.HANDLE_WRONG_BREAKOUT:
                    counter = self.wrong_breakout_counter
                else:
                    counter = self.breakout_counter
            print('{}: {} for {}-{}-{} ({}/{}): ticker.last_price={:.2f}, breakout value={:.2f}'.format(
                self.trade_process, process, ticker.ticker_id, self.buy_trigger, self.trade_strategy,
                counter, counter_required, ticker.last_price, breakout_value))
        else:
            print('{}: {} for {}-{}-{}: limit={:.2f}, ticker.last_price={:.2f}, stop_loss={:.2f}, bought_at={:.2f}'.format(
                self.trade_process, process, ticker.ticker_id, self.buy_trigger, self.trade_strategy,
                self.limit_current, ticker.last_price, self.stop_loss_current, self.order_status_buy.avg_execution_price))

    def save_trade(self):
        if not self.sys_config.config.save_trade_data:
            return
        if self.data_dict_obj.is_data_dict_ready_for_trade_table():
            trade_dict = self.data_dict_obj.get_data_dict_for_trade_table()
            self.sys_config.db_stock.delete_existing_trade(trade_dict[DC.ID])  # we need always the most actual version
            self.sys_config.db_stock.insert_trade_data([trade_dict])
            self.__save_to_database__()

    def __save_to_database__(self):
        period = self.sys_config.config.api_period
        aggregation = self.sys_config.config.api_period_aggregation
        self.sys_config.db_stock.save_tick_list(self._wave_tick_list.tick_list, self.ticker_id, period, aggregation)

    def print_trade(self, prefix=''):
        if prefix != '':
            print('\n{}:'.format(prefix))
        print(self.get_trade_meta_data())
        if self._order_status_sell:
            self._order_status_buy.print_with_other_order_status(self._order_status_sell, ['buy', 'sell'])
        elif self._order_status_buy:
            self._order_status_buy.print_order_status('Buy order')

    def get_trade_meta_data(self):
        details = '; '.join('{}: {}'.format(key, value) for key, value in self.__get_value_dict__().items())
        return '{}: {}'.format(self.id, details)

    def __get_value_dict__(self) -> dict:
        return {'Status': self.status, 'Buy_trigger': self.buy_trigger, 'Trade_box': self.trade_box_type,
                'Trade_strategy': self.trade_strategy, 'Pattern_Type': self.pattern.pattern_type,
                'Expected_win (per unit):': round(self.expected_win, 4), 'Result (resp. amount)': self.get_trade_result_text()
        }

    def get_trade_result_text(self):
        if not self._order_status_sell:
            return '-'
        return '{:0.2f} from {:0.2f}'.format(
            self._order_status_sell.value_total - self._order_status_buy.value_total, self._order_status_buy.value_total
        )

    def adjust_trade_box_to_actual_ticker(self):
        sma = self.__get_simple_moving_average_value__() if self.trade_strategy == TSTR.SMA else 0
        was_adjusted = self._trade_box.adjust_to_next_ticker_last_price(self.ticker_actual.last_price, sma)
        if was_adjusted:
            self.print_state_details_for_actual_ticker(PTHP.ADJUST_STOPS_AND_LIMITS)

    def __get_simple_moving_average_value__(self) -> float:
        elements = min(self._wave_tick_list.length, self.sys_config.config.simple_moving_average_number)
        return self._wave_tick_list.get_simple_moving_average(elements)

    def __get_ticker_wave_tick_converter__(self) -> TickerWaveTickConverter:
        period = self.sys_config.config.api_period
        aggregation = self.sys_config.config.api_period_aggregation
        wave_tick_last = self._wave_tick_list.tick_list[-1]
        return TickerWaveTickConverter(period, aggregation, wave_tick_last.position, wave_tick_last.time_stamp)

    def __get_trade_box__(self, off_set_price: float, buy_price: float, height=0.0, distance_bottom=0.0):
        api = TradingBoxApi()
        api.data_dict = self.pattern.data_dict_obj.data_dict
        api.off_set_value = off_set_price
        api.buy_price = buy_price
        api.trade_strategy = self.trade_strategy
        api.height = height
        api.distance_bottom = distance_bottom
        if self.trade_box_type == TBT.EXPECTED_WIN:
            return ExpectedWinTradingBox(api)
        elif self.trade_box_type == TBT.TOUCH_POINT:
            return TouchPointTradingBox(api)
        return None

    def set_order_status_buy(self, order_status: OrderStatus, buy_comment, ticker: Ticker):
        order_status.order_trigger = self.buy_trigger
        order_status.trade_strategy = self.trade_strategy
        order_status.order_comment = buy_comment
        self._order_status_buy = order_status
        self.pattern.data_dict_obj.add_buy_order_status_data_to_pattern_data_dict(order_status, self.trade_strategy)
        self.__set_properties_after_buy__(ticker)
        self.__add_order_status_buy_to_data_dict__(self._order_status_buy)
        self.__add_order_status_sell_to_data_dict__(self._order_status_sell)  # to initialize those data
        if self.trade_process != TP.BACK_TESTING:
            self.print_trade('Details after buying')

    def __set_properties_after_buy__(self, ticker: Ticker):
        self._status = PTS.EXECUTED
        self._wave_tick_at_buying = self._wave_tick_list.tick_list[-1]
        buy_price = ticker.last_price
        height = 0
        distance_bottom = 0
        if self.buy_trigger == BT.TOUCH_POINT:
            off_set_value = buy_price
            height = self.pattern.get_upper_value(ticker.time_stamp) - self.pattern.get_lower_value(ticker.time_stamp)
            distance_bottom = buy_price - self.pattern.get_lower_value(ticker.time_stamp)
        else:
            off_set_value = self.pattern.get_upper_value(ticker.time_stamp)
        self._trade_box = self.__get_trade_box__(off_set_value, buy_price, height, distance_bottom)
        self._trade_box.print_box()

    def set_order_status_sell(self, order_status: OrderStatus, sell_trigger: str, sell_comment: str):
        order_status.order_trigger = sell_trigger
        order_status.trade_strategy = self.trade_strategy
        order_status.order_comment = sell_comment
        self._order_status_sell = order_status
        self.pattern.data_dict_obj.add_sell_order_status_data_to_pattern_data_dict(order_status)
        self.__set_properties_after_sell__()
        self.__add_order_status_sell_to_data_dict__(self._order_status_sell)  # to fill these data finally
        self.print_trade('Details after selling')

    def __set_properties_after_sell__(self):
        self._status = PTS.FINISHED
        self._wave_tick_at_selling = self._wave_tick_list.tick_list[-1]

    def get_row_for_dash_data_table(self):
        columns = TradeTable.get_columns_for_replay()
        return {column: self.data_dict_obj.get(column) for column in columns}

    def __add_trade_basis_data_to_data_dict__(self):
        self.data_dict_obj.add(DC.ID, self.id)
        self.data_dict_obj.add(DC.TRADE_PROCESS, self.trade_process)
        self.data_dict_obj.add(DC.TRADE_READY_ID, 1 if self._was_candidate_for_real_trading else 0)
        self.data_dict_obj.add(DC.TRADE_STRATEGY, self.trade_strategy)
        self.data_dict_obj.add(DC.TRADE_STRATEGY_ID, TSTR.get_id(self.trade_strategy))
        self.data_dict_obj.add(DC.TRADE_BOX_TYPE, self.trade_box_type)
        self.data_dict_obj.add(DC.TRADE_BOX_TYPE_ID, TBT.get_id(self.trade_box_type))
        self.data_dict_obj.add(DC.BUY_TRIGGER, self.buy_trigger)
        self.data_dict_obj.add(DC.BUY_TRIGGER_ID, BT.get_id(self.buy_trigger))
        # overwrite some values from pattern (not valid set at that state)
        self.data_dict_obj.add(DC.BREAKOUT_DIRECTION, FD.ASC)
        self.data_dict_obj.add(DC.BREAKOUT_DIRECTION_ID, FD.get_id(FD.ASC))

    def __add_order_status_buy_to_data_dict__(self, order_status: OrderStatus):
        self.data_dict_obj.add(DC.BUY_ORDER_ID, order_status.order_id)
        self.data_dict_obj.add(DC.BUY_ORDER_TPYE, order_status.type)
        self.data_dict_obj.add(DC.BUY_ORDER_TPYE_ID, OT.get_id(order_status.type))
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
            self.data_dict_obj.add(DC.TRADE_BOX_OFF_SET, self._trade_box.off_set_value)
            self.data_dict_obj.add(DC.TRADE_BOX_MAX_VALUE, self._trade_box.max_ticker_last_price)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT_ORIG, self._trade_box.limit_orig)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS_ORIG, self._trade_box.stop_loss_orig)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT, self._trade_box.limit)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS, self._trade_box.stop_loss)
            self.data_dict_obj.add(DC.TRADE_BOX_STD, self._trade_box.std)

            self.data_dict_obj.add(DC.SELL_ORDER_ID, order_status.order_id)
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE, order_status.type)
            self.data_dict_obj.add(DC.SELL_ORDER_TPYE_ID, OT.get_id(order_status.type))
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
            self.data_dict_obj.add(DC.TRADE_BOX_OFF_SET, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_MAX_VALUE, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT_ORIG, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS_ORIG, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_LIMIT, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_STOP_LOSS, 0)
            self.data_dict_obj.add(DC.TRADE_BOX_STD, 0)

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
            # print('{}: np_array.shape={}'.format(prediction_type, np_array.shape)) ToDo
            return np_array
        return None

    def get_markdown_text(self, ticker_refresh: int):
        last_price = self.ticker_actual.last_price
        date_time = self.ticker_actual.date_time_str
        header = '**Last ticker:** {} - **at:** {} (refresh after {} sec.)'.format(last_price, date_time, ticker_refresh)
        process = self.current_trade_process
        limit = self.limit_current
        stop_loss = self.stop_loss_current

        if self._status == PTS.NEW:
            return dedent('''
                {}

                **Process**: {} **Breakout**: {:2.2f} **Wrong breakout**: {:2.2f}
                ''').format(header, process, limit, stop_loss)
        elif self._status == PTS.EXECUTED:
            bought_at = self._order_status_buy.price
            trailing_stop_distance = self.trailing_stop_distance
            return dedent('''
                {}

                **Process**: {} **Bought at**: {:2.2f} **Limit**: {:2.2f} **Stop**: {:2.2f} 
                **Trailing stop distance**: {:2.2f}
                ''').format(header, process, bought_at, limit, stop_loss, trailing_stop_distance)
        else:
            bought_at = self._order_status_buy.price
            return dedent('''
                {}

                **Process**: {} **Breakout**: {:2.2f} **Wrong breakout**: {:2.2f}
                ''').format(header, process, limit, stop_loss)
