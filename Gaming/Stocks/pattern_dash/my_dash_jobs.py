"""
Description: This module contains all the scheduled jobs
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-22
"""

from pattern_scheduling.pattern_job import MyPatternJob
from sertl_analytics.constants.pattern_constants import PRD, INDICES, FT, PPR
from sertl_analytics.constants.my_constants import MYPR
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_database_updater import StockDatabaseUpdater
from pattern_predictor_optimizer import PatternPredictorOptimizer
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.mydates import MyDate


class MyDashPatternJob(MyPatternJob):
    def __init__(self, weekdays: list, start_times: list, db_updater: StockDatabaseUpdater):
        MyPatternJob.__init__(self, period=PRD.DAILY, weekdays=weekdays, start_times=start_times)
        self._db_updater = db_updater


class MyDashTradePolicyUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._db_updater.update_trade_policy_metric_for_today(FT.get_long_trade_able_types())

    @property
    def process_name(self):
        return PPR.UPDATE_TRADE_POLICY_METRIC


class MyDashPredictorOptimizerJob(MyDashPatternJob):
    def __perform_task__(self):
        sys_config = SystemConfiguration()
        predictor_optimizer = PatternPredictorOptimizer(sys_config.db_stock)
        pattern_type_list = [FT.ALL] + sys_config.trade_strategy_optimizer.optimal_pattern_type_list_for_long_trading
        predictor_optimizer.calculate_class_metrics_for_predictor_and_label_for_today(pattern_type_list)

    @property
    def process_name(self):
        return PPR.UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL


class MyDashDeleteDuplicatesJob(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        db_stock.delete_duplicate_records(db_stock.trade_table)
        db_stock.delete_duplicate_records(db_stock.pattern_table)
        db_stock.delete_duplicate_records(db_stock.wave_table)

    @property
    def process_name(self):
        return PPR.DELETE_DUPLICATE_RECORDS_IN_TABLES


class MyDashStockDataUpdateJobForCrypto(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        exchange_config = BitfinexConfiguration()
        db_stock.update_crypto_currencies(PRD.DAILY, symbol_list=exchange_config.ticker_id_list)

    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_CRYPTO


class MyDashStockDataUpdateJobForShares(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        db_stock.update_stock_data_by_index(INDICES.INDICES, PRD.DAILY)
        db_stock.update_stock_data_by_index(INDICES.DOW_JONES, PRD.DAILY)
        db_stock.update_stock_data_for_symbol('MRAM')
        db_stock.update_stock_data_for_symbol('FCEL')
        db_stock.update_stock_data_for_symbol('TSLA')
        db_stock.update_stock_data_for_symbol('GE')
        db_stock.update_stock_data_by_index(INDICES.NASDAQ100, PRD.DAILY)
        db_stock.update_stock_data_by_index(INDICES.Q_FSE, PRD.DAILY)
        self._db_updater.calculate_index_list([INDICES.NASDAQ100, INDICES.Q_FSE])

    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_SHARES


class MyDashStockDataUpdateJobForCurrencies(MyDashPatternJob):
    def __perform_task__(self):
        db_stock = StockDatabase()
        db_stock.update_stock_data_by_index(INDICES.FOREX, PRD.DAILY)

    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_CCY


class MyEquityUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        result_obj = self._db_updater.update_equity_records()
        self.process.increment_deleted_records(result_obj.number_deleted_records)
        self.process.increment_inserted_records(result_obj.number_saved_records)

    @property
    def process_name(self):
        return PPR.UPDATE_EQUITY_DATA


class MyDailyWaveUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        index_list = [INDICES.CRYPTO_CCY, INDICES.FOREX, INDICES.DOW_JONES, INDICES.NASDAQ100]
        for index in index_list:
            if index == INDICES.CRYPTO_CCY or MyDate.is_tuesday_till_saturday():
                self._db_updater.update_wave_data_by_index_for_daily_period(index, 400)
        self.process.increment_updated_records(
            self._db_updater.add_wave_end_data_to_wave_records(
                symbol='', ts_start=0, ts_end=0, scheduled_job=True)
        )
        self.process.increment_deleted_records(
            self._db_updater.delete_inconsistent_wave_records(scheduled_job=True)
        )

    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_DAILY


class MyIntradayWaveUpdateJob(MyDashPatternJob):
    @property
    def index_list(self):
        return [INDICES.CRYPTO_CCY, INDICES.FOREX, INDICES.DOW_JONES, INDICES.NASDAQ100]

    @property
    def period_aggregation(self):
        return 30

    def __perform_task__(self):
        for index in self.index_list:
            self._db_updater.update_wave_data_by_index_for_intraday(index, self.period_aggregation)
        self.process.increment_updated_records(
            self._db_updater.add_wave_end_data_to_wave_records(symbol='', ts_start=0, ts_end=0, scheduled_job=True)
        )
        self.process.increment_deleted_records(
            self._db_updater.delete_inconsistent_wave_records(scheduled_job=True)
        )


class MyIntradayWaveUpdateJobForCrypto(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.CRYPTO_CCY]

    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_CRYPTO

    @property
    def period_aggregation(self):
        return 15  # we use the same aggregation as normal for cryptos


class MyIntradayWaveUpdateJobForShares(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.DOW_JONES, INDICES.NASDAQ100]

    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_SHARES


class MyIntradayWaveUpdateJobForCurrencies(MyIntradayWaveUpdateJob):
    @property
    def index_list(self):
        return [INDICES.FOREX]

    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_CCY


class MyPatternUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._db_updater.update_pattern_data_by_index_for_daily_period(INDICES.CRYPTO_CCY)
        if MyDate.is_tuesday_till_saturday():
            self._db_updater.update_pattern_data_by_index_for_daily_period(INDICES.FOREX)
            self._db_updater.update_pattern_data_by_index_for_daily_period(INDICES.INDICES)
            self._db_updater.update_pattern_data_by_index_for_daily_period(INDICES.DOW_JONES)
            self._db_updater.update_pattern_data_by_index_for_daily_period(INDICES.NASDAQ100)

    @property
    def process_name(self):
        return PPR.UPDATE_PATTERN_DAILY


class MyTradeRecordsUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._db_updater.update_trade_records(4, 16)

    @property
    def process_name(self):
        return PPR.UPDATE_TRADE_RECORDS


class MyWaitingTransactionsUpdateJob(MyDashPatternJob):
    def __perform_task__(self):
        self._db_updater.handle_transaction_problems()

    @property
    def process_name(self):
        return PPR.HANDLE_TRANSACTION_PROBLEMS


class MyDashOptimizeLogFilesJob(MyDashPatternJob):
    def __perform_task__(self):
        self._file_log.process_optimize_log_files()

    @property
    def process_name(self):
        return MYPR.OPTIMIZE_LOG_FILES

