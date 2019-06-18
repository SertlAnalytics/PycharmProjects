"""
Description: This class is responsible for the automated daily update of the stock database.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-10
"""

from sertl_analytics.constants.pattern_constants import BT, TSTR, FT, DC, PRD, TRT, EQUITY_TYPE, TRC, LOGT
from sertl_analytics.constants.pattern_constants import INDICES, EDC, EST, FD
from sertl_analytics.constants.pattern_constants import TPMDC
from sertl_analytics.mydates import MyDate
from sertl_analytics.myfile import MyFile
from sertl_analytics.my_text import MyText
from fibonacci.fibonacci_wave import FibonacciWave
from pattern_system_configuration import SystemConfiguration
from pattern_detection_controller import PatternDetectionController
from pattern_database.stock_tables_data_dictionary import AssetDataDictionary
from sertl_analytics.exchanges.exchange_cls import Balance
from pattern_database.stock_access_layer import AccessLayer4Asset, AccessLayer4Stock, AccessLayer4Equity
from pattern_database.stock_access_layer import AccessLayer4Wave
from pattern_database.stock_access_layer import AccessLayer4TradePolicyMetric
from pattern_reinforcement.trade_policy import TradePolicyFactory
from pattern_reinforcement.trade_policy_handler import TradePolicyHandler
from pattern_database.stock_wave_entity import WaveEntity
from pattern_scheduling.pattern_job_result import StockDatabaseUpdateJobResult
from sertl_analytics.myfilelog import FileLogLine
from time import sleep
import numpy as np


class StockDatabaseUpdater:
    def __init__(self, sys_config=None):
        self.sys_config = SystemConfiguration() if sys_config is None else sys_config
        self.db_stock = self.sys_config.db_stock
        self.pattern_controller = PatternDetectionController(self.sys_config)

    def add_wave_end_data_to_wave_records(self, symbol='', ts_start=0, ts_end=0, scheduled_job=False) -> int:
        """
        Some attributes have to be calculated AFTER the waves completes:
        DC.WAVE_END_FLAG, DC.WAVE_MAX_RETR_PCT, DC.WAVE_MAX_RETR_TS_PCT
        """
        print('Add wave end data to wave records..')
        access_layer_wave = AccessLayer4Wave(self.db_stock)
        access_layer_stocks = AccessLayer4Stock(self.db_stock)
        df_wave_to_process = access_layer_wave.get_wave_data_frame_without_end_data(symbol, ts_start, ts_end)
        ts_start_stocks = ts_start if ts_end == 0 else ts_end
        df_stocks = access_layer_stocks.get_stocks_data_frame_for_wave_completing(symbol=symbol, ts_start=ts_start_stocks)
        tolerance = 0.01
        update_counter = 0
        ts_now = MyDate.time_stamp_now()
        for wave_index, wave_row in df_wave_to_process.iterrows():
            wave_entity = WaveEntity(wave_row)
            ts_start, ts_end = wave_entity.get_ts_start_end_for_check_period()
            ts_start_dt = MyDate.get_date_from_epoch_seconds(ts_start)
            ts_end_dt = MyDate.get_date_from_epoch_seconds(ts_end)
            wave_end_value, wave_value_range = wave_entity.wave_end_value, wave_entity.wave_value_range
            if ts_end < ts_now:
                wave_end_reached = 1
                max_retracement = 0
                max_retracement_ts = ts_start
                max_retracement_dt = ts_start_dt
                df_filtered_stocks = df_stocks[np.logical_and(
                    df_stocks[DC.SYMBOL] == wave_entity.symbol,
                    np.logical_and(df_stocks[DC.TIMESTAMP] > ts_start, df_stocks[DC.TIMESTAMP] <= ts_end))]
                for index_stocks, row_stocks in df_filtered_stocks.iterrows():
                    row_low, row_high, row_ts = row_stocks[DC.LOW], row_stocks[DC.HIGH], row_stocks[DC.TIMESTAMP]
                    if wave_entity.wave_type == FD.ASC:
                        if wave_end_value < row_high * (1 - tolerance):
                            wave_end_reached = 0
                            break
                        else:
                            retracement = wave_end_value - row_low
                    else:
                        if wave_end_value > row_low * (1 + tolerance):
                            wave_end_reached = 0
                            break
                        else:
                            retracement = row_high - wave_end_value
                    if retracement > max_retracement:
                        max_retracement = round(retracement, 2)
                        max_retracement_ts = row_ts
                        max_retracement_dt = row_stocks[DC.DATE]
                max_retracement_pct = round(max_retracement / wave_value_range * 100, 2)
                max_retracement_ts_pct = round((max_retracement_ts - ts_start) / wave_entity.wave_ts_range * 100, 2)
                data_dict = {DC.WAVE_END_FLAG: wave_end_reached,
                             DC.WAVE_MAX_RETR_PCT: max_retracement_pct,
                             DC.WAVE_MAX_RETR_TS_PCT: max_retracement_ts_pct}
                access_layer_wave.update_record(wave_entity.row_id, data_dict)
                update_counter += 1
        if scheduled_job:
            self.sys_config.file_log.log_scheduler_process(
                log_message='Updated: {}/{}'.format(update_counter, df_wave_to_process.shape[0]),
                process='Update wave records',
                process_step='add_wave_end_data')
        return update_counter

    def add_wave_prediction_data_to_wave_records(self, symbol='', ts_start=0, ts_end=0, scheduled_job=False):
        """
        This job calculates the prediction data for all kind of waves (daily and intraday
        """
        print('Add prediction data to wave records..')
        access_layer_wave = AccessLayer4Wave(self.db_stock)
        df_wave_to_process = access_layer_wave.get_wave_data_without_prediction_data(symbol, ts_start, ts_end)
        update_counter = 0
        for wave_index, wave_row in df_wave_to_process.iterrows():
            wave_entity = WaveEntity(wave_row)
            x_data = wave_entity.data_list_for_prediction_x_data
            prediction_dict = self.sys_config.fibonacci_predictor.get_prediction_as_dict(x_data)
            data_dict = {}
            FibonacciWave.update_dict_by_prediction_dict(prediction_dict, data_dict)
            access_layer_wave.update_record(wave_entity.row_id, data_dict)
            update_counter += 1

        if scheduled_job:
            self.sys_config.file_log.log_scheduler_process(
                log_message='Updated: {}/{}'.format(update_counter, df_wave_to_process.shape[0]),
                process='Update wave records',
                process_step='add_wave_prediction')

    def update_equity_records(self) -> StockDatabaseUpdateJobResult:
        result_obj = StockDatabaseUpdateJobResult()
        access_layer = AccessLayer4Equity(self.db_stock)
        dt_today = MyDate.get_date_from_datetime()
        # dt_today = MyDate.adjust_by_days(dt_today, 40)
        dt_valid_until = MyDate.adjust_by_days(dt_today, 30)
        dt_today_str = str(dt_today)
        dt_valid_until_str = str(dt_valid_until)
        exchange_equity_type_dict = self.__get_equity_dict__()
        result_obj.number_processed_records = len(exchange_equity_type_dict)
        for exchange, equity_type in exchange_equity_type_dict.items():
            value_dict = access_layer.get_index_dict(exchange)
            if not access_layer.are_any_records_available_for_date(dt_today, exchange, equity_type):
                result_obj.number_deleted_records += access_layer.delete_existing_equities(equity_type, exchange)
                sleep(2)
                self.__update_equity_records_for_equity_type__(
                    access_layer, dt_today_str, dt_valid_until_str, exchange, equity_type)
                result_obj.number_saved_records += 1
        return result_obj

    @staticmethod
    def __get_equity_dict__():
        return {
            TRC.BITFINEX: EQUITY_TYPE.CRYPTO,
            INDICES.DOW_JONES: EQUITY_TYPE.SHARE,
            INDICES.NASDAQ100: EQUITY_TYPE.SHARE,
            INDICES.FOREX: EQUITY_TYPE.CURRENCY
        }

    def __update_equity_records_for_equity_type__(
            self, access_layer: AccessLayer4Equity, dt_today_str: str, dt_valid_until_str: str,
            exchange: str, equity_type: str):
        # a) get symbol - name dictionaries
        if equity_type == EQUITY_TYPE.SHARE:
            index = exchange
        elif equity_type == EQUITY_TYPE.CURRENCY:
            index = INDICES.FOREX
        else:
            index = INDICES.CRYPTO_CCY
        source_data_dict = self.sys_config.index_config.get_ticker_dict_for_index(index)

        # b) get existing records
        existing_data_dict = access_layer.get_existing_equities_as_data_dict(equity_type, exchange)

        # b) none available => get new ones
        for key, value in source_data_dict.items():
            if key in existing_data_dict:
                pass
            else:
                data_dict = {EDC.EQUITY_KEY: key, EDC.EQUITY_NAME: value,
                             EDC.VALID_FROM_DT: dt_today_str, EDC.VALID_TO_DT: dt_valid_until_str,
                             EDC.EXCHANGE: exchange, EDC.EQUITY_TYPE: equity_type, EDC.EQUITY_STATUS: EST.ACTIVE}
                self.db_stock.insert_equity_data([data_dict])

    def update_trade_records(self, mean: int, sma_number: int, trade_strategies: dict=None, pattern_end_date=str):
        if pattern_end_date == '':
            pattern_end_date = str(MyDate.adjust_by_days(None, -90))  # only the ones which are 3 month back
        self.sys_config.init_detection_process_for_automated_trade_update(mean, sma_number)
        if trade_strategies is None:
            trade_strategies = {BT.BREAKOUT: [TSTR.LIMIT, TSTR.LIMIT_FIX, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP]}
        for pattern_type in FT.get_long_trade_able_types():
            where_clause = "pattern_type = '{}' and period = 'DAILY' and trade_type in ('', 'long')".format(pattern_type)
            if pattern_end_date != '':
                where_clause += " AND {} > '{}'".format(DC.PATTERN_END_DT, pattern_end_date)
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

    def update_pattern_data_by_index_for_daily_period(self, index: str):
        print('Update pattern data for index: {}'.format(index))
        self.sys_config.init_detection_process_for_automated_pattern_update()
        self.sys_config.data_provider.use_index(index)
        pattern_controller = PatternDetectionController(self.sys_config)
        pattern_controller.run_pattern_detector()

    def update_wave_data_by_index_for_daily_period(self, index: str, limit: int):
        ticker_dic = self.__get_configured_ticker_dict_for_index__(index)
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
        ticker_dic = self.__get_configured_ticker_dict_for_index__(index)
        for ticker in ticker_dic:
            try:
                self.update_wave_records_for_intraday(ticker, aggregation)
            except:
                self.sys_config.file_log.log_error()

    def __get_configured_ticker_dict_for_index__(self, index):
        if index == INDICES.CRYPTO_CCY:
            ticker_dic = self.sys_config.index_config.get_ticker_dict_for_index(
                index, self.sys_config.exchange_config.ticker_id_list)
        else:
            ticker_dic = self.sys_config.index_config.get_ticker_dict_for_index(index)
        return ticker_dic

    def update_wave_records_for_intraday(self, ticker_id: str, aggregation: int):
        self.sys_config.config.save_wave_data = True
        self.sys_config.data_provider.period = PRD.INTRADAY
        self.sys_config.data_provider.aggregation = aggregation
        self.sys_config.data_provider.from_db = False
        detector = self.pattern_controller.get_detector_for_fibonacci(self.sys_config, ticker_id)
        detector.save_wave_data()

    def update_trade_policy_metric_for_today(self, pattern_type_list: list):
        print("\nSTARTING 'update_trade_policy_metric_for_today' for {}...".format(pattern_type_list))
        access_layer = AccessLayer4TradePolicyMetric(self.db_stock)
        dt_today_str = str(MyDate.get_date_from_datetime())
        check_dict = {TPMDC.VALID_DT: dt_today_str}
        if access_layer.are_any_records_available(check_dict):
            print("END 'update_trade_policy_metric_for_today': No updates for today\n")
            # return
        policy_list = TradePolicyFactory.get_trade_policies_for_metric_calculation()
        period_list = [PRD.DAILY]
        mean_aggregation_list = [4, 8, 16]
        for pattern_type in pattern_type_list:
            for period in period_list:
                for mean_aggregation in mean_aggregation_list:
                    policy_handler = TradePolicyHandler(pattern_type=pattern_type, period=period,
                                                        mean_aggregation=mean_aggregation)
                    for policy in policy_list:
                        rewards, entity_counter = policy_handler.run_policy(policy, False)
                        insert_dict = {TPMDC.VALID_DT: dt_today_str,
                                       TPMDC.POLICY: policy.policy_name,
                                       TPMDC.EPISODES: 1,
                                       TPMDC.PERIOD: period,
                                       TPMDC.AGGREGATION: 1,
                                       TPMDC.TRADE_MEAN_AGGREGATION: mean_aggregation,
                                       TPMDC.PATTERN_TYPE: pattern_type,
                                       TPMDC.NUMBER_TRADES: entity_counter,
                                       TPMDC.REWARD_PCT_TOTAL: round(rewards, 2),
                                       TPMDC.REWARD_PCT_AVG: round(rewards/entity_counter, 2),
                                       }
                        access_layer.insert_data([insert_dict])
        print("END 'update_trade_policy_metric_for_today'\n")

    def handle_transaction_problems(self):
        print("\nSTARTING 'handle_transaction_problems'")
        line_to_keep_list = []
        file_path = self.sys_config.file_log.get_file_path_for_log_type(LOGT.TRANSACTIONS)
        file_with_transactions = MyFile(file_path)
        lines_as_list = file_with_transactions.get_lines_as_list()
        for line in lines_as_list:
            log_line = FileLogLine(line)
            # line_to_keep_list.append(line)
            if log_line.is_valid:
                table_name = log_line.process
                data_str_dict_list_as_string = log_line.step
                data_str_dict_list_as_string = data_str_dict_list_as_string.replace('#', ',')
                data_str_dict_list = MyText.get_list_from_text(data_str_dict_list_as_string)
                data_dict_list = [MyText.get_dict_from_text(dict_str) for dict_str in data_str_dict_list]
                print('Handle_transaction_problem for table {}: {}'.format(table_name, data_dict_list))
                self.db_stock.correct_data_types_withing_data_dict_list(table_name, data_dict_list)
                data_dict_list = self.db_stock.remove_existing_entries_from_data_dict_list(table_name, data_dict_list)
                if len(data_dict_list) > 0:
                    inserted = self.db_stock.insert_data_into_table(table_name, data_dict_list)
                    if inserted <= 0:
                        line_to_keep_list.append(line)
            else:
                print('{}: Line not valid in log file: {}'.format(file_path, line))
        file_with_transactions.replace_file_when_changed(line_to_keep_list)
        print("END 'handle_transaction_problems'\n")

    def fill_asset_gaps(self, ts_last: int, ts_to: int, ts_interval: int):
        access_layer_stocks = AccessLayer4Stock(self.db_stock)
        last_asset_query = 'SELECT * FROM asset WHERE Validity_Timestamp={}'.format(ts_to)
        df_last_asset = AccessLayer4Asset(self.db_stock).select_data_by_query(last_asset_query)
        ts_actual = ts_last + ts_interval
        while ts_actual < ts_to:
            dt_saving = str(MyDate.get_date_time_from_epoch_seconds(ts_actual))
            for index, asset_row in df_last_asset.iterrows():
                equity_type = asset_row[DC.EQUITY_TYPE]
                asset = asset_row[DC.EQUITY_NAME]
                amount = asset_row[DC.QUANTITY]
                value_total = asset_row[DC.VALUE_TOTAL]
                balance = Balance('exchange', asset, amount, amount)
                if equity_type == EQUITY_TYPE.CASH:
                    balance.current_value = value_total
                else:
                    if equity_type == EQUITY_TYPE.CRYPTO:
                        asset = asset + 'USD'
                    current_price = access_layer_stocks.get_actual_price_for_symbol(asset, ts_actual)
                    balance.current_value = value_total if current_price == 0 else round(amount * current_price, 2)
                data_dict = AssetDataDictionary().get_data_dict_for_target_table_for_balance(
                    balance, ts_actual, dt_saving)
                self.db_stock.insert_asset_entry(data_dict)
            ts_actual += ts_interval

