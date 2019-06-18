"""
Description: This module contains the PatternProcess classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.pattern_constants import PPR, STBL
from sertl_analytics.constants.my_constants import MYPR
from sertl_analytics.processes.my_process import MyProcess
from pattern_logging.pattern_log import PatternLog

"""
    UPDATE_PATTERN_INTRADAY = 'Update_Pattern_Intraday'
    UPDATE_PATTERN_DAILY = 'Update_Pattern_Daily'
    UPDATE_WAVE_INTRADAY_CRYPTO = 'Update_Wave_Intraday_Crypto'
    UPDATE_WAVE_INTRADAY_SHARES = 'Update_Wave_Intraday_Shares'
    UPDATE_WAVE_INTRADAY_CCY = 'Update_Wave_Intraday_Currencies'
    UPDATE_WAVE_DAILY_CRYPTO = 'Update_Wave_Daily_Crypto'
    UPDATE_WAVE_DAILY_SHARES = 'Update_Wave_Daily_Shares'
    UPDATE_WAVE_DAILY_CCY = 'Update_Wave_Daily_Currencies'
    DELETE_DUPLICATE_RECORDS_IN_TABLES = 'Delete_Duplicate_Records_in_Tables'
    UPDATE_STOCK_DATA_DAILY = 'Update_Stock_Data_Daily'
    UPDATE_HEATMAP_IN_WAVE_TAB = 'Update_Heatmap_in_Wave_Tab'
    UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL = 'Update_Class_Metrics_For_Predictor_and_Label'
    UPDATE_TRADE_POLICY_METRIC = 'Update_Trade_Policy_Metric'
    UPDATE_PREDICTORS = 'Update_Predictors'
"""


class PatternProcess(MyProcess):
    def __get_file_log__(self):
        return PatternLog()


class ProcessUpdateEquityData(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_EQUITY_DATA

    @staticmethod
    def __get_table_names__():
        return [STBL.EQUITY]


class ProcessDeleteDuplicateRecordsInTables(PatternProcess):
    @property
    def process_name(self):
        return PPR.DELETE_DUPLICATE_RECORDS_IN_TABLES

    @staticmethod
    def __get_table_names__():
        return [STBL.WAVE, STBL.PATTERN, STBL.TRADE]


class ProcessUpdatePatternIntraday(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_PATTERN_INTRADAY

    @staticmethod
    def __get_table_names__():
        return [STBL.PATTERN]


class ProcessUpdatePatternDaily(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_PATTERN_DAILY

    @staticmethod
    def __get_table_names__():
        return [STBL.PATTERN]


class ProcessUpdateWave(PatternProcess):
    @staticmethod
    def __get_child_process_names__():
        return [PPR.UPDATE_HEATMAP_IN_WAVE_TAB]

    @staticmethod
    def __get_table_names__():
        return [STBL.WAVE]


class ProcessUpdateWaveIntradayCrypto(ProcessUpdateWave):
    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_CRYPTO


class ProcessUpdateWaveIntradayShares(ProcessUpdateWave):
    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_SHARES


class ProcessUpdateWaveIntradayCurrencies(ProcessUpdateWave):
    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_INTRADAY_CCY


class ProcessUpdateWaveDaily(ProcessUpdateWave):
    @property
    def process_name(self):
        return PPR.UPDATE_WAVE_DAILY


class ProcessUpdateHeatMapInWaveTab(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_HEATMAP_IN_WAVE_TAB


class ProcessUpdateStockDataDaily(PatternProcess):
    @staticmethod
    def __get_table_names__():
        return [STBL.STOCKS]


class ProcessHandleTransactionProblems(PatternProcess):
    @property
    def process_name(self):
        return PPR.HANDLE_TRANSACTION_PROBLEMS

    @staticmethod
    def __get_table_names__():
        return STBL.get_all()


class ProcessUpdateStockDataDailyForCrypto(ProcessUpdateStockDataDaily):
    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_CRYPTO


class ProcessUpdateStockDataDailyForShares(ProcessUpdateStockDataDaily):
    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_SHARES


class ProcessUpdateStockDataDailyForCurrencies(ProcessUpdateStockDataDaily):
    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY_CCY


class ProcessUpdateTradeRecords(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_TRADE_RECORDS

    @staticmethod
    def __get_table_names__():
        return [STBL.TRADE]


class ProcessUpdateClassMetricForPredictorAndLabel(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL

    @staticmethod
    def __get_table_names__():
        return [STBL.METRIC]


class ProcessUpdateTradePolicyMetric(PatternProcess):
    @property
    def process_name(self):
        return PPR.UPDATE_TRADE_POLICY_METRIC

    @staticmethod
    def __get_table_names__():
        return [STBL.TRADE_POLICY_METRIC]


class ProcessOptimizeLogFiles(PatternProcess):
    @property
    def process_name(self):
        return MYPR.OPTIMIZE_LOG_FILES

    def __get_table_record_numbers__(self):  # here we have to count the lines within the concerned log files
        return self._file_log.count_rows_for_process_optimize_log_files()


