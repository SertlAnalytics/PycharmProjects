"""
Description: This module contains the trade test classes which are uses for single test and back testing
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-09-21
"""

from sertl_analytics.constants.pattern_constants import FT, TP, BT, PRD
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade_handler import PatternTradeHandler
from pattern_test.trade_test_cases import TradeTestCase, TradeTestCaseFactory, TradeTestApi


class TradeTest:
    def __init__(self, trade_process=TP.NONE):
        self.trade_process = trade_process
        self.sys_config = SystemConfiguration()
        self.exchange_config = ExchangeConfiguration()
        self.__adjust_sys_config__()
        self.__adjust_exchange_config__()

    def __adjust_exchange_config__(self):
        self.exchange_config.buy_order_value_max = 100
        self.exchange_config.is_simulation = True

    def __adjust_sys_config__(self):
        self.sys_config.runtime.actual_trade_process = self.trade_process
        if self.trade_process == TP.BACK_TESTING:
            self.sys_config.config.pattern_type_list = FT.get_long_trade_able_types()
        self.sys_config.config.get_data_from_db = True
        self.sys_config.config.api_period = PRD.DAILY
        self.sys_config.config.api_period_aggregation = 1
        self.sys_config.config.plot_data = False
        self.sys_config.prediction_mode_active = True
        self.sys_config.config.save_pattern_features = False
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
        for value_pair in tc.value_pair_list:
            trade_handler.check_actual_trades(value_pair)
        trade_handler.enforce_sell_at_end(tc.value_pair_list[-1])
        self.__print_frame_information__(tc.buy_trigger, tc.trade_strategy)

    def __get_test_case_list__(self, api):
        test_case_list = []
        pattern_list_all = self.__get_pattern_list_for_back_testing__(api)
        for pattern in pattern_list_all:
            api.pattern = pattern
            tc = TradeTestCaseFactory.get_test_case_from_pattern(api)
            tc.symbol = api.symbol  # sometimes the symbol is changed within the previous process
            test_case_list.append(tc)
        return test_case_list

    def __get_pattern_list_for_back_testing__(self, api: TradeTestApi):
        pattern_controller = PatternDetectionController(self.sys_config)
        detector = pattern_controller.get_detector_for_dash(self.sys_config, api.symbol, api.and_clause)
        return detector.get_pattern_list_for_back_testing()

    @staticmethod
    def __print_frame_information__(trigger: str, strategy: str, expected=''):
        if expected == '':
            print('\n************* TEST CASE: {} / {} END *************\n'.format(trigger, strategy))
        else:
            print('\n\n************* TEST CASE: {} / {} EXPECTED: {} *************\n'.format(trigger, strategy, expected))

