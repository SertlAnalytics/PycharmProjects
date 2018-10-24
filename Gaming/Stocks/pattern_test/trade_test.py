"""
Description: This module contains the trade test classes which are uses for single test and back testing
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-21
"""

from sertl_analytics.constants.pattern_constants import FT, TP, BT, PRD, DC
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController
from pattern_detector import PatternDetector
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade_handler import PatternTradeHandler
from pattern_test.trade_test_cases import TradeTestCase, TradeTestCaseFactory, TradeTestApi


class TradeTest:
    def __init__(self, api: TradeTestApi, sys_config=None, exchange_config=None):
        self.api = api
        self.trade_process = api.test_process
        self.sys_config = sys_config if sys_config else SystemConfiguration()
        self.exchange_config = exchange_config if exchange_config else ExchangeConfiguration()
        self.__adjust_sys_config__()
        self.__adjust_exchange_config__()

    def __adjust_exchange_config__(self):
        self.exchange_config.buy_order_value_max = 100
        self.exchange_config.is_simulation = True

    def __adjust_sys_config__(self):
        self.sys_config.runtime.actual_trade_process = self.trade_process
        if self.trade_process == TP.BACK_TESTING:
            self.sys_config.config.pattern_type_list = FT.get_long_trade_able_types()
        self.sys_config.config.get_data_from_db = self.api.get_data_from_db
        self.sys_config.config.api_period = self.api.period
        self.sys_config.config.api_period_aggregation = self.api.period_aggregation
        self.sys_config.config.plot_data = False
        self.sys_config.prediction_mode_active = True
        self.sys_config.config.save_pattern_data = False
        self.sys_config.config.save_trade_data = False

    def run_back_testing(self, api: TradeTestApi):
        self.sys_config.init_predictors_without_condition_list(api.symbol)
        tc_list = self.__get_test_case_list__(api)  # we need this list since the config will be changed for each entry
        for tc in tc_list:
            self.run_test_case(tc)

    def run_test_case(self, tc: TradeTestCase):
        self.exchange_config.trade_strategy_dict = {tc.buy_trigger: [tc.trade_strategy]}
        self.sys_config.config.pattern_type_list = [tc.pattern_type]
        self.sys_config.config.use_own_dic({tc.symbol: tc.symbol})
        self.sys_config.config.and_clause = tc.and_clause
        self.sys_config.config.with_trade_part = False if tc.buy_trigger == BT.TOUCH_POINT else True

        pattern_controller = PatternDetectionController(self.sys_config)
        detector = pattern_controller.get_detector_for_dash(self.sys_config, tc.symbol, tc.and_clause)
        pattern_list = detector.get_pattern_list_for_buy_trigger(tc.buy_trigger)
        trade_handler = PatternTradeHandler(self.sys_config, self.exchange_config)  # we need a new one for each
        trade_handler.add_pattern_list_for_trade(pattern_list)
        self.__print_frame_information__(tc.buy_trigger, tc.trade_strategy, tc.test_process)
        for wave_tick in tc.wave_tick_list:
            trade_handler.check_actual_trades(wave_tick)  # wave_tick
        trade_handler.enforce_sell_at_end(tc.wave_tick_list[-1])
        self.__print_frame_information__(tc.buy_trigger, tc.trade_strategy)

    def __get_test_case_list__(self, api):
        test_case_list = []
        pattern_list_all = self.__get_pattern_list_for_back_testing__(api)
        for pattern in pattern_list_all:
            api.pattern = pattern
            tc = TradeTestCaseFactory.get_test_case_from_pattern(api)
            test_case_list.append(tc)
        return test_case_list

    def __get_pattern_list_for_back_testing__(self, api: TradeTestApi):
        pattern_controller = PatternDetectionController(self.sys_config)
        detector = pattern_controller.get_detector_for_dash(self.sys_config, api.symbol, api.and_clause)
        return detector.get_pattern_list_for_back_testing()

    def get_pattern_detector_for_replay(self, api: TradeTestApi) -> PatternDetector:
        self.__adjust_sys_config_for_replay__(api)
        pattern_controller = PatternDetectionController(self.sys_config)
        return pattern_controller.get_detector_for_dash(self.sys_config, api.symbol, api.and_clause)

    def __adjust_sys_config_for_replay__(self, api: TradeTestApi):
        self.exchange_config.trade_strategy_dict = {api.buy_trigger: [api.trade_strategy]}
        self.sys_config.config.pattern_type_list = [api.pattern_type]
        self.sys_config.config.use_own_dic({api.symbol: api.symbol})
        self.sys_config.config.and_clause = api.and_clause
        self.sys_config.config.with_trade_part = False

    @staticmethod
    def __print_frame_information__(trigger: str, strategy: str, expected=''):
        if expected == '':
            print('\n************* TEST CASE: {} / {} END *************\n'.format(trigger, strategy))
        else:
            print('\n\n************* TEST CASE: {} / {} EXPECTED: {} *************\n'.format(trigger, strategy, expected))

