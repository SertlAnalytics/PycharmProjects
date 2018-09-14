"""
Description: This module contains the PatternTrade class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-10
"""

import numpy as np
from sertl_analytics.constants.pattern_constants import TSTR, BT, ST, FD, DC, TBT, PTS, OS, TR, OT, SVC
from sertl_analytics.mydates import MyDate
from pattern import Pattern
from sertl_analytics.exchanges.exchange_cls import OrderStatus, Ticker
from pattern_data_dictionary import PatternDataDictionary
from pattern_trade_box import FibonacciTradingBox, ExpectedWinTradingBox, TouchPointTradingBox, TradingBoxApi
from pattern_trade_box import ForecastHalfLengthTradingBox, ForecastFullLengthTradingBox


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

    def is_ticker_breakout(self, ticker: Ticker):
        if not self._is_breakout_active:
            return False
        if self.buy_trigger == BT.BREAKOUT:
            upper_value = self.pattern.get_upper_value(ticker.time_stamp)
            is_breakout = ticker.last_price >= upper_value
        else:
            lower_value = self.pattern.get_lower_value(ticker.time_stamp)
            is_breakout = ticker.last_price > lower_value  # ToDo eventual some % of the height...
        self._breakout_counter += 1 if is_breakout else 0
        return self._breakout_counter >= self._counter_required  # we need a second confirmation

    def is_ticker_wrong_breakout(self, ticker: Ticker):
        lower_value = self.pattern.get_lower_value(ticker.time_stamp)
        is_wrong_breakout = ticker.last_price <= lower_value
        self._wrong_breakout_counter += 1 if is_wrong_breakout else 0
        return self._wrong_breakout_counter >= self._counter_required  # we need a second confirmation

    def verify_touch_point(self, ticker: Ticker):
        self._is_breakout_active = self.pattern.is_value_in_category(ticker.last_price, ticker.time_stamp, SVC.L_on)

    def save_trade(self):
        if not self.sys_config.config.save_trade_data:
            return
        if self.data_dict_obj.is_data_dict_ready_for_trade_table():
            trade_dict = self.data_dict_obj.get_data_dict_for_trade_table()
            self.sys_config.db_stock.delete_existing_trade(trade_dict[DC.ID])  # we need always the most actual version
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

    def adjust_to_next_ticker_last_price(self, last_price: float) -> bool:
        return self._trade_box.adjust_to_next_ticker_last_price(last_price)

    def __get_trade_box__(self, off_set_price: float, buy_price: float):
        api = TradingBoxApi()
        api.data_dict = self.pattern.data_dict_obj.data_dict
        api.off_set_value = off_set_price
        api.buy_price = buy_price
        api.trade_strategy = self.trade_strategy
        if self.trade_box_type == TBT.EXPECTED_WIN:
            return ExpectedWinTradingBox(api)
        elif self.trade_box_type == TBT.FORECAST_HALF_LENGTH:
            return ForecastHalfLengthTradingBox(api)
        elif self.trade_box_type == TBT.FORECAST_FULL_LENGTH:
            return ForecastFullLengthTradingBox(api)
        elif self.trade_box_type == TBT.TOUCH_POINT:
            return TouchPointTradingBox(api)
        elif self.trade_box_type == TBT.FIBONACCI:
            return FibonacciTradingBox(api)
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
        off_set_value = self.pattern.get_upper_value(ticker.time_stamp)
        buy_price = ticker.last_price
        self._trade_box = self.__get_trade_box__(off_set_value, buy_price)
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
