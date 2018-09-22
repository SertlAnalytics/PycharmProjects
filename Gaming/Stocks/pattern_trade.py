"""
Description: This module contains the PatternTrade class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import TSTR, BT, ST, FD, DC, TBT, PTS, PTHP, TR, OT, SVC, TP, FT
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from sertl_analytics.exchanges.exchange_cls import OrderStatus, Ticker
from pattern_data_dictionary import PatternDataDictionary
from pattern_trade_box import ExpectedWinTradingBox, TouchPointTradingBox, TradingBoxApi


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
        self.buy_trigger = api.buy_trigger
        self.trade_box_type = api.box_type
        self.trade_strategy = api.trade_strategy
        self.pattern = api.pattern
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

    @property
    def id(self):
        return '{}-{}-{}_{}'.format(self.buy_trigger, self.trade_box_type, self.trade_strategy, self.pattern.id_readable)

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
        return self._trade_box.stop_loss if self._trade_box else 0

    @property
    def limit_current(self):
        return self._trade_box.limit if self._trade_box else 0

    @property
    def time_stamp_end(self):
        return self._trade_box.time_stamp_end if self._trade_box else 0

    @property
    def trailing_stop_distance(self):
        return self._trade_box.trailing_stop_distance if self._trade_box else 0

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

    def __get_default_value_for_breakout_active__(self):
        if self.buy_trigger == BT.BREAKOUT:
            return True
        return False # it's not active for touch and fibonacci till confirmation

    def __calculate_prediction_values__(self):
        predictor = self.sys_config.predictor_for_trades
        x_data = self.__get_x_data_for_prediction__(predictor.feature_columns)
        if x_data is not None:
            prediction_dict = predictor.predict_for_label_columns(x_data)
            self.data_dict_obj.add(DC.FC_TRADE_REACHED_PRICE_PCT, prediction_dict[DC.TRADE_REACHED_PRICE_PCT])
            self.data_dict_obj.add(DC.FC_TRADE_RESULT_ID, prediction_dict[DC.TRADE_RESULT_ID])

    def is_ticker_breakout(self, process: str, ticker: Ticker):
        if not self._is_breakout_active:
            return False
        is_breakout = False  # default
        vc = self.__get_value_category_for_breakout__()
        if self.buy_trigger == BT.BREAKOUT:
            is_breakout = self.pattern.is_value_in_category(ticker.last_price, ticker.time_stamp, vc, True)
        elif self.buy_trigger == BT.TOUCH_POINT:
            is_breakout = self.pattern.is_value_in_category(ticker.last_price, ticker.time_stamp, vc, True)
        if is_breakout:
            self._breakout_counter += 1 if self.buy_trigger == BT.BREAKOUT else 2  # touch point => immediate buy
        self.print_state_details(process, ticker)
        return self._breakout_counter >= self._counter_required  # we need a second confirmation

    def __get_value_category_for_breakout__(self):
        if self.pattern.pattern_type in [FT.TKE_BOTTOM, FT.FIBONACCI_DESC]:
            return SVC.H_M_in if self.buy_trigger == BT.TOUCH_POINT else SVC.H_U_out
        else:
            return SVC.M_in if self.buy_trigger == BT.TOUCH_POINT else SVC.U_out

    def is_ticker_wrong_breakout(self, process: str, ticker: Ticker):
        vc = self.__get_value_category_for_wrong_breakout__()
        is_wrong_breakout = self.pattern.is_value_in_category(ticker.last_price, ticker.time_stamp, vc, True)
        if is_wrong_breakout:
            self._wrong_breakout_counter += 1
        self.print_state_details(process, ticker)
        return self._wrong_breakout_counter >= self._counter_required  # we need a second confirmation

    def __get_value_category_for_wrong_breakout__(self):
        if self.pattern.pattern_type in [FT.TKE_BOTTOM, FT.FIBONACCI_DESC]:
            return SVC.H_L_out
        else:
            return SVC.L_out

    def verify_touch_point(self, ticker: Ticker):
        last_tick = self.pattern.part_main.tick_last
        value_tuple_list = [[ticker.last_price, ticker.time_stamp], [last_tick.low, last_tick.time_stamp]]
        for value_tuple in value_tuple_list:
            if self.pattern.is_value_in_category(value_tuple[0], value_tuple[1], SVC.L_on, True):
                self._is_breakout_active = True
                break

    def print_state_details(self, process: str, ticker: Ticker):
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
            print('{} for {}-{}-{} ({}/{}): ticker.last_price={:.2f}, breakout value={:.2f}'.format(
                process, ticker.ticker_id, self.buy_trigger, self.trade_strategy,
                counter, counter_required, ticker.last_price, breakout_value))
        else:
            print('{} for {}-{}-{}: limit={:.2f}, ticker.last_price={:.2f}, stop_loss={:.2f}, bought_at={:.2f}'.format(
                process, ticker.ticker_id, self.buy_trigger, self.trade_strategy,
                self.limit_current, ticker.last_price,
                self.stop_loss_current, self.order_status_buy.avg_execution_price))

    def save_trade(self):
        if not self.sys_config.config.save_trade_data:
            return
        if self.data_dict_obj.is_data_dict_ready_for_trade_table():
            trade_dict = self.data_dict_obj.get_data_dict_for_trade_table()
            self.sys_config.db_stock.delete_existing_trade(trade_dict[DC.ID])  # we need always the most actual version
            self.sys_config.db_stock.insert_trade_data([trade_dict])

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

    def adjust_to_next_ticker(self, ticker: Ticker):
        was_adjusted = self._trade_box.adjust_to_next_ticker_last_price(ticker.last_price)
        if was_adjusted:
            self.print_state_details(PTHP.ADJUST_STOPS_AND_LIMITS, ticker)

    def __get_trade_box__(self, off_set_price: float, buy_price: float, height=0.0, distance_bottom=0.0):
        api = TradingBoxApi()
        api.data_dict = self.pattern.data_dict_obj.data_dict
        api.off_set_value = off_set_price
        api.buy_price = buy_price
        api.trade_strategy = self.trade_strategy
        api.sma_tick_list = self.pattern.get_simple_moving_average_tick_list_from_part_main()
        api.height = height
        api.distance_bottom = distance_bottom
        api.period = self.sys_config.config.api_period
        api.aggregation = self.sys_config.config.api_period_aggregation
        api.refresh_trigger_in_seconds = self.bitfinex_config.ticker_refresh_rate_in_seconds
        if self.trade_box_type == TBT.EXPECTED_WIN:
            return ExpectedWinTradingBox(api)
        elif self.trade_box_type == TBT.TOUCH_POINT:
            return TouchPointTradingBox(api)
        return None

    def set_order_status_buy(self, order_status: OrderStatus, buy_comment, ticker: Ticker):
        order_status.order_trigger = self.buy_trigger
        order_status.trade_strategy = self.trade_strategy
        order_status.trade_process = self.sys_config.config.trade_process
        order_status.order_comment = buy_comment
        self._order_status_buy = order_status
        self.pattern.data_dict_obj.add_buy_order_status_data_to_pattern_data_dict(order_status, self.trade_strategy)
        self.__set_properties_after_buy__(ticker)
        self.__add_order_status_buy_to_data_dict__(self._order_status_buy)
        self.__add_order_status_sell_to_data_dict__(self._order_status_sell)  # to initialize those data
        if order_status.trade_process != TP.BACK_TESTING:
            self.print_trade('Details after buying')

    def __set_properties_after_buy__(self, ticker: Ticker):
        self._status = PTS.EXECUTED
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

    def __add_trade_basis_data_to_data_dict__(self):
        self.data_dict_obj.add(DC.ID, self.id)
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
            # print('{}: np_array.shape={}'.format(prediction_type, np_array.shape))
            return np_array
        return None
