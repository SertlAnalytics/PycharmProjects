"""
Description: This module contains the PatternProcess and PatternProcessManager classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.pattern_constants import PPR, STBL
from sertl_analytics.mydates import MyDate
from pattern_database.stock_database import StockDatabase
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


class PatternProcess:
    def __init__(self, db_stock: StockDatabase):
        self._db_stock = db_stock
        self._start_dt = None
        self._end_dt = None
        self._processed_records = 0
        self._deleted_records = 0
        self._updated_records = 0
        self._inserted_records = 0
        self._child_process_names = self.__get_child_process_names__()
        self._child_processes = []
        self._triggered_by_process_names = []
        self._process_result = None
        self._table_record_number_before_start = 0
        self._table_record_number_after_end = 0
        self._table_names = self.__get_table_names__()

    @property
    def process_name(self):
        return PPR.RUN_UNDEFINED_PROCESS

    @property
    def process_result(self):
        return self._process_result

    @process_result.setter
    def process_result(self, value):
        self._process_result = value

    def was_triggered_by_another_process(self):
        return len(self._triggered_by_process_names) > 0

    def set_child_processes(self, process_dict: dict):
        self._child_processes = [process_dict.get(process_name) for process_name in self._child_process_names]

    def add_to_triggered_by_process_names(self, process_name: str):
        if process_name not in self._triggered_by_process_names:
            self._triggered_by_process_names.append(process_name)

    def process_decorator(self, func):
        # if a function use this decorator there must be a parameter in the signature called "process"
        def function_wrapper(*args, **kwargs):
            self.__start_process__()
            self.process_result = func(*args, **kwargs, process=self)
            self.__end_process__()
            return self.process_result
        return function_wrapper

    def __start_process__(self):
        print('Start process: {}'.format(self.process_name))
        self._start_dt = MyDate.get_datetime_object()
        self._end_dt = None
        self._processed_records = 0
        self._updated_records = 0
        self._deleted_records = 0
        self._inserted_records = 0
        self._table_record_number_before_start = self.__get_table_record_numbers__()

    def __end_process__(self):
        print('End process: {}'.format(self.process_name))
        self._end_dt = MyDate.get_datetime_object()
        self._table_record_number_after_end = self.__get_table_record_numbers__()
        self.__calculate_insert_delete_numbers__()
        self._triggered_by_process_names = []  # done for this dependencies
        self.__trigger_child_processes__()
        PatternLog.log_message(self.get_statistics(), 'End Process', self.process_name)  # ToDo - get rid of this log...

    def __get_table_record_numbers__(self):
        counter = 0
        for table_name in self._table_names:
            counter += self._db_stock.get_number_of_records_for_table(table_name)
        return counter

    def __calculate_insert_delete_numbers__(self):
        change_since_start = self._table_record_number_after_end - self._table_record_number_before_start
        if change_since_start > 0:
            self.increment_inserted_records(change_since_start)
        else:
            self.increment_deleted_records(change_since_start)

    def __trigger_child_processes__(self):
        for child_process in self._child_processes:
            print('__trigger_child_processes__: child_process={}, triggered_by_name={}'.format(
                child_process.process_name, self.process_name
            ))
            child_process.add_to_triggered_by_process_names(self.process_name)

    def increment_processed_records(self, increment=1):
        self._processed_records += increment

    def increment_deleted_records(self, increment=1):
        self._deleted_records += increment

    def increment_updated_records(self, increment=1):
        self._updated_records += increment

    def increment_inserted_records(self, increment=1):
        self._inserted_records += increment

    def get_record_numbers(self) -> list:
        return [self._processed_records, self._inserted_records, self._updated_records, self._deleted_records]

    def get_record_numbers_as_string(self) -> list:
        return [str(number) for number in self.get_record_numbers()]

    def get_statistics(self):
        record_numbers = self.get_record_numbers()
        if max(record_numbers) == 0:
            return ''
        prefix_list = ['processed', 'inserted', 'updated', 'deleted']
        prefix_value_list = ['{}: {}'.format(prefix_list[idx], n) for idx, n in enumerate(record_numbers) if n > 0]
        return ', '.join(prefix_value_list)

    @staticmethod
    def __get_child_process_names__():
        return []

    @staticmethod
    def __get_table_names__():
        return []


class ProcessRunUndefinedProcess(PatternProcess):
    @property
    def process_name(self):
        return PPR.RUN_UNDEFINED_PROCESS


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
    @property
    def process_name(self):
        return PPR.UPDATE_STOCK_DATA_DAILY

    @staticmethod
    def __get_table_names__():
        return [STBL.STOCKS]


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


class PatternProcessManager:
    def __init__(self):
        self._db_stock = StockDatabase()
        self._process_dict = self.__get_process_dict__()
        self.__set_child_processes__()
        self._default_process = self._process_dict[PPR.RUN_UNDEFINED_PROCESS]

    def get_process_by_name(self, process_name: str) -> PatternProcess:
        return self._process_dict.get(process_name, self._default_process)

    def print_statistics(self):
        for key, process in self._process_dict.items():
            statistics = process.get_statistics()
            if statistics != '':
                print('Statistics for {}: {}'.format(key, statistics))

    def __get_process_dict__(self) -> dict:
        return {
            PPR.DELETE_DUPLICATE_RECORDS_IN_TABLES: ProcessDeleteDuplicateRecordsInTables(self._db_stock),
            PPR.UPDATE_EQUITY_DATA: ProcessUpdateEquityData(self._db_stock),
            PPR.UPDATE_PATTERN_INTRADAY: ProcessUpdatePatternIntraday(self._db_stock),
            PPR.UPDATE_PATTERN_DAILY: ProcessUpdatePatternDaily(self._db_stock),
            PPR.UPDATE_WAVE_INTRADAY_CRYPTO: ProcessUpdateWaveIntradayCrypto(self._db_stock),
            PPR.UPDATE_WAVE_INTRADAY_SHARES: ProcessUpdateWaveIntradayShares(self._db_stock),
            PPR.UPDATE_WAVE_INTRADAY_CCY: ProcessUpdateWaveIntradayCurrencies(self._db_stock),
            PPR.UPDATE_WAVE_DAILY: ProcessUpdateWaveDaily(self._db_stock),
            PPR.UPDATE_HEATMAP_IN_WAVE_TAB: ProcessUpdateHeatMapInWaveTab(self._db_stock),
            PPR.UPDATE_TRADE_RECORDS: ProcessUpdateTradeRecords(self._db_stock),
            PPR.UPDATE_STOCK_DATA_DAILY: ProcessUpdateStockDataDaily(self._db_stock),
            PPR.UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL:
                ProcessUpdateClassMetricForPredictorAndLabel(self._db_stock),
            PPR.UPDATE_TRADE_POLICY_METRIC: ProcessUpdateTradePolicyMetric(self._db_stock),
            PPR.RUN_UNDEFINED_PROCESS: ProcessRunUndefinedProcess(self._db_stock)
        }

    def __set_child_processes__(self):
        for process in self._process_dict.values():
            process.set_child_processes(self._process_dict)