"""
Description: This module contains the dash replay handler class. Handles the replay of a trade or a pattern.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-07
"""

from pattern_system_configuration import SystemConfiguration
from pattern_dash.my_dash_components import DccGraphApi
from pattern_trade_handler import PatternTradeHandler
from pattern_trade import PatternTrade
from pattern_database.stock_database import StockDatabaseDataFrame
from sertl_analytics.constants.pattern_constants import DC, TP, PRD, RST
from pattern_wave_tick import WaveTick
from pattern_test.trade_test_cases import TradeTestCaseFactory
from pattern_test.trade_test import TradeTest
from pattern_data_container import PatternData
from sertl_analytics.mydates import MyDate


class ReplayHandler:
    def __init__(self, trade_process: str, sys_config: SystemConfiguration):
        self.sys_config = sys_config.get_semi_deep_copy()
        self.trade_process = trade_process
        if self.trade_process == TP.ONLINE:
            self.sys_config = sys_config
        else:
            self.sys_config.data_provider.from_db = False
            self.sys_config.data_provider.period = PRD.DAILY
            self.sys_config.data_provider.aggregation = 1
        self.sys_config.runtime_config.actual_trade_process = self.trade_process
        self.trade_handler = PatternTradeHandler(self.sys_config)
        self.trade_test_api = None
        self.trade_test = None
        self.detector = None
        self.test_case = None
        self.test_case_wave_tick_list_index = -1
        self.graph_api = None
        self.graph = None

    @property
    def replay_status(self):
        if len(self.trade_handler.pattern_trade_dict) == 0:
            return RST.CANCEL
        else:
            for pattern_trade in self.trade_handler.pattern_trade_dict.values():
                if pattern_trade.is_wrong_breakout:
                    return RST.STOP
        return RST.REPLAY

    @property
    def graph_id(self):
        if self.trade_process == TP.TRADE_REPLAY:
            return 'my_graph_trade_replay'
        if self.trade_process == TP.PATTERN_REPLAY:
            return 'my_graph_pattern_replay'
        return 'my_graph_trade_online'

    @property
    def graph_title(self):
        return '{}: {}-{}-{}-{}'.format(self.trade_test_api.symbol,
                                        self.trade_test_api.buy_trigger, self.trade_test_api.trade_strategy,
                                        self.trade_test_api.pattern_type, self.sys_config.period)

    @property
    def pattern_trade(self) -> PatternTrade:
        if self.graph_api is not None:
            return self.graph_api.pattern_trade

    def set_trade_test_api_by_selected_trade_row(self, selected_row):
        self.trade_test_api = TradeTestCaseFactory.get_trade_test_api_by_selected_trade_row(
            selected_row, self.trade_process)
        if self.trade_process in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY]:
            self.trade_test_api.from_db = True
            self.trade_test_api.period = selected_row[DC.PERIOD]
            self.trade_test_api.period_aggregation = selected_row[DC.PERIOD_AGGREGATION]
        else:
            self.trade_test_api.from_db = False
            self.trade_test_api.period = self.sys_config.period
            # print('set_trade_test_api_by_selected_trade_row: _period = {}'.format(self.sys_config._period))
            self.trade_test_api.period_aggregation = self.sys_config.period_aggregation
            self.trade_test_api.trade_id = selected_row[DC.ID]
            self.trade_test_api.pattern_id = ''

    def is_another_wave_tick_available(self):
        if len(self.trade_handler.pattern_trade_dict) == 0:  # trade was removed...
            return False
        return self.get_remaining_tick_number() > 0

    def get_remaining_tick_number(self):
        if self.test_case is None:
            return 0
        return len(self.test_case.wave_tick_list) - 1 - self.test_case_wave_tick_list_index

    def get_next_wave_tick(self) -> WaveTick:
        self.test_case_wave_tick_list_index += 1
        wave_tick = self.test_case.wave_tick_list[self.test_case_wave_tick_list_index]
        time_stamp = wave_tick.time_stamp
        date_time = MyDate.get_date_time_from_epoch_seconds(time_stamp)
        value = wave_tick.close
        print('{}: {}-new value pair to check: [{} ({}), {}]'.format(
            self.trade_process, self.trade_test_api.symbol, date_time, time_stamp, value))
        return wave_tick

    def set_trade_test(self):
        self.trade_test = TradeTest(self.trade_test_api, self.sys_config)

    def set_detector(self):
        self.detector = self.trade_test.get_pattern_detector_for_replay(self.trade_test_api)

    def set_pattern_to_api(self):
        self.trade_test_api.pattern = self.detector.get_pattern_for_replay()

    def set_tick_list_to_api(self):
        api = self.trade_test_api
        stock_db_df_obj = StockDatabaseDataFrame(self.sys_config.db_stock, api.symbol, api.and_clause_unlimited)
        # print('api._symbol={}, api.and_clause_unlimited={}, stock_db_df_obj.df_data.shape={}'.format(
        #     api._symbol, api.and_clause_unlimited, stock_db_df_obj.df_data.shape))
        pattern_data = PatternData(self.sys_config.config, stock_db_df_obj.df_data)
        self.trade_test_api.tick_list_for_replay = pattern_data.tick_list

    def set_test_case(self):
        self.test_case = TradeTestCaseFactory.get_test_case_from_pattern(self.trade_test_api)

    def add_pattern_list_for_trade(self):
        self.trade_handler.add_pattern_list_for_trade([self.trade_test_api.pattern])

    def set_graph_api(self):
        self.graph_api = DccGraphApi(self.graph_id, self.graph_title)
        if self.trade_process in [TP.TRADE_REPLAY, TP.PATTERN_REPLAY]:
            self.graph_api.pattern_trade = self.trade_handler.pattern_trade_for_replay
            self.graph_api.ticker_id = self.trade_test_api.symbol
            self.graph_api.df = self.detector.pdh.pattern_data.df
        else:
            self.set_selected_trade_to_api()
            # print('set_graph_api: trade_id={}, pattern_trade.id={}'.format(self.trade_test_api.trade_id,
            #                                                                self.graph_api.pattern_trade.id))
            self.graph_api.ticker_id = self.trade_test_api.symbol
            self.graph_api.df = self.graph_api.pattern_trade.get_data_frame_for_replay()  # ToDo - old (this) or new
            # self.graph_api._df = self.detector.pdh.pattern_data._df
        self.graph_api.period = self.trade_test_api.period

    def set_selected_trade_to_api(self):
        self.graph_api.pattern_trade = self.trade_handler.get_pattern_trade_by_id(self.trade_test_api.trade_id)

    def check_actual_trades_for_replay(self, wave_tick: WaveTick):
        if self.graph_api is not None:
            self.trade_handler.check_actual_trades_for_replay(wave_tick)
            self.graph_api.df = self.trade_handler.get_pattern_trade_data_frame_for_replay()

    def refresh_api_df_from_pattern_trade(self):
        # self.set_selected_trade_to_api()
        self.graph_api.df = self.graph_api.pattern_trade.get_data_frame_for_replay()