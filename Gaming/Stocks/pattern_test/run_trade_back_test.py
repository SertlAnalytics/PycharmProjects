"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.datafetcher.financial_data_fetcher import ApiPeriod
from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC
from pattern_system_configuration import SystemConfiguration, debugger
from pattern_detection_controller import PatternDetectionController
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade_handler import PatternTradeHandler
from pattern_test.trade_test_cases import TradeTestCase, TradeTestCaseFactory


class TradeBackTest:
    def __init__(self):
        self.sys_config = SystemConfiguration()
        self.exchange_config = ExchangeConfiguration()
        self.__adjust_sys_config__()
        self.__adjust_exchange_config__()

    def __adjust_exchange_config__(self):
        self.exchange_config.buy_order_value_max = 100
        self.exchange_config.is_simulation = True
        # self.exchange_config.trade_strategy_dict = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP],
        #                             BT.TOUCH_POINT: [TSTR.LIMIT]}

    def __adjust_sys_config__(self):
        self.sys_config.config.for_back_testing = True
        self.sys_config.config.get_data_from_db = True
        self.sys_config.config.api_period = ApiPeriod.DAILY
        self.sys_config.config.api_period_aggregation = 1
        self.sys_config.config.plot_data = False
        self.sys_config.prediction_mode_active = True
        self.sys_config.config.save_pattern_features = False
        self.sys_config.config.save_trade_data = False

    def get_pattern_list_for_back_testing(self, symbol: str, and_clause: str):
        self.sys_config.config.pattern_type_list = FT.get_all()
        pattern_controller = PatternDetectionController(self.sys_config)
        detector = pattern_controller.get_detector_for_dash(self.sys_config, symbol, and_clause)
        return detector.get_pattern_list_for_back_testing()

    def run_test_case(self, tc: TradeTestCase):
        self.exchange_config.trade_strategy_dict = {tc.buy_trigger: [tc.trade_strategy]}
        self.sys_config.config.pattern_type_list = [tc.pattern_type]
        self.sys_config.config.use_own_dic({tc.symbol: tc.symbol})
        self.sys_config.config.and_clause = tc.and_clause

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

    @staticmethod
    def __print_frame_information__(trigger: str, strategy: str, expected=''):
        if expected == '':
            print('\n************* TEST CASE: {} / {} END *************\n'.format(trigger, strategy))
        else:
            print('\n\n************* TEST CASE: {} / {} EXPECTED: {} *************\n'.format(trigger, strategy, expected))


back_test = TradeBackTest()
# ******** START **********
buy_trigger = BT.BREAKOUT
trade_strategy = TSTR.SMA
process = TTC.BACK_TESTING
# ******** END **********

symbol = 'ETH_USD'
and_clause = "Date BETWEEN '2017-11-01' AND '2018-09-05'"
pattern_list_all = back_test.get_pattern_list_for_back_testing(symbol, and_clause)
# pattern_list_all = back_test.get_all_finished_patterns_for_a_equity('MMM', "Date BETWEEN '2017-11-25' AND '2019-07-30'")
for pattern in pattern_list_all:
    test_case = TradeTestCaseFactory.get_test_case_from_pattern(pattern, buy_trigger, trade_strategy, process)
    test_case.symbol = symbol
    back_test.run_test_case(test_case)




