"""
Description: This job updates the trade records for all pattern without that trade type.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.constants.pattern_constants import BT, TSTR, FT, DC, PRD, TRT
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from pattern_detection_controller import PatternDetectionController
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList


class StockDatabaseUpdater:
    def __init__(self):
        self.sys_config = SystemConfiguration()
        self.db_stock = self.sys_config.db_stock
        self.pattern_controller = PatternDetectionController(self.sys_config)

    def update_trade_records(self, mean: int, sma_number: int, trade_strategies: dict=None):
        self.sys_config.init_detection_process_for_automated_trade_update(mean, sma_number)
        if trade_strategies is None:
            trade_strategies = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.LIMIT_FIX, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP]}
        for pattern_type in FT.get_long_trade_able_types():
            where_clause = "pattern_type = '{}' and period = 'DAILY' and trade_type in ('', 'long')".format(pattern_type)
            df_pattern_for_pattern_type = self.db_stock.get_pattern_records_as_dataframe(where_clause)
            pattern_id_dict = {row[DC.ID]: row[DC.TRADE_TYPE] for index, row in df_pattern_for_pattern_type.iterrows()}
            # pattern_id_list = ['20_1_1_LTCUSD_20_2016-11-02_00:00_2016-12-04_00:00']
            counter = 0
            for pattern_id, trade_type in pattern_id_dict.items():
                counter += 1
                run_detail = '{} ({:03d} of {:03d}): {}'.format(pattern_type, counter, len(pattern_id_dict), pattern_id)
                result_dict = self.db_stock.get_missing_trade_strategies_for_pattern_id(
                    pattern_id, trade_strategies, mean, sma_number)
                for buy_trigger, trade_strategy_list in result_dict.items():
                    if len(trade_strategy_list) == 0:
                        print('{}: OK'.format(run_detail))
                    else:
                        print('{}: processing...'.format(run_detail))
                        self.sys_config.config.pattern_ids_to_find = [pattern_id]
                        self.sys_config.exchange_config.trade_strategy_dict = {buy_trigger: trade_strategy_list}
                        pattern_controller = PatternDetectionController(self.sys_config)
                        pattern_controller.run_pattern_detector()
                if trade_type == '':
                    self.db_stock.update_trade_type_for_pattern(pattern_id, TRT.LONG)

    def update_wave_data_by_index_for_daily_period(self, index: str, limit: int):
        print('Update wave data for index: {} ({}days)'.format(index, limit))
        ticker_dic = IndicesComponentList.get_ticker_name_dic(index)
        for ticker in ticker_dic:
            self.update_wave_records_for_daily_period(ticker, limit)

    def update_wave_records_for_daily_period(self, ticker_id: str, limit: int):
        self.sys_config.config.save_wave_data = True
        self.sys_config.data_provider.period = PRD.DAILY
        self.sys_config.data_provider.from_db = True
        date_start = MyDate.adjust_by_days(MyDate.get_datetime_object().date(), -limit)
        and_clause = "Date > '{}'".format(date_start)
        detector = self.pattern_controller.get_detector_for_fibonacci(self.sys_config, ticker_id, and_clause, limit)
        detector.save_wave_data()

    def update_wave_data_by_index_for_intraday(self, index: str, aggregation: int=30):
        print('Update wave data for index: {} ({}min)'.format(index, aggregation))
        ticker_dic = IndicesComponentList.get_ticker_name_dic(index)
        for ticker in ticker_dic:
            self.update_wave_records_for_intraday(ticker, aggregation)

    def update_wave_records_for_intraday(self, ticker_id: str, aggregation: int):
        self.sys_config.config.save_wave_data = True
        self.sys_config.data_provider.period = PRD.INTRADAY
        self.sys_config.data_provider.aggregation = aggregation
        self.sys_config.data_provider.from_db = False
        detector = self.pattern_controller.get_detector_for_fibonacci(self.sys_config, ticker_id)
        detector.save_wave_data()

