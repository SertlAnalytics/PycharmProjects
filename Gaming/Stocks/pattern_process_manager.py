"""
Description: This module contains the PatternProcess and PatternProcessManager classes
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-22
"""

from sertl_analytics.constants.pattern_constants import PPR
from sertl_analytics.constants.my_constants import MYPR
from sertl_analytics.processes.my_process import ProcessRunUndefinedProcess
from sertl_analytics.processes.my_process_manager import MyProcessManager
from pattern_database.stock_database import StockDatabase
import pattern_process as ppr


class PatternProcessManager(MyProcessManager):
    def __get_db__(self):
        return StockDatabase()

    def __get_process_dict__(self) -> dict:
        return {
            PPR.DELETE_DUPLICATE_RECORDS_IN_TABLES: ppr.ProcessDeleteDuplicateRecordsInTables(self._db),
            PPR.UPDATE_EQUITY_DATA: ppr.ProcessUpdateEquityData(self._db),
            PPR.UPDATE_PATTERN_INTRADAY: ppr.ProcessUpdatePatternIntraday(self._db),
            PPR.UPDATE_PATTERN_DAILY: ppr.ProcessUpdatePatternDaily(self._db),
            PPR.UPDATE_WAVE_INTRADAY_CRYPTO: ppr.ProcessUpdateWaveIntradayCrypto(self._db),
            PPR.UPDATE_WAVE_INTRADAY_SHARES: ppr.ProcessUpdateWaveIntradayShares(self._db),
            PPR.UPDATE_WAVE_INTRADAY_CCY: ppr.ProcessUpdateWaveIntradayCurrencies(self._db),
            PPR.UPDATE_WAVE_DAILY: ppr.ProcessUpdateWaveDaily(self._db),
            PPR.UPDATE_HEATMAP_IN_WAVE_TAB: ppr.ProcessUpdateHeatMapInWaveTab(self._db),
            PPR.UPDATE_TRADE_RECORDS: ppr.ProcessUpdateTradeRecords(self._db),
            PPR.UPDATE_STOCK_DATA_DAILY_CRYPTO: ppr.ProcessUpdateStockDataDailyForCrypto(self._db),
            PPR.UPDATE_STOCK_DATA_DAILY_CCY: ppr.ProcessUpdateStockDataDailyForCurrencies(self._db),
            PPR.UPDATE_STOCK_DATA_DAILY_SHARES: ppr.ProcessUpdateStockDataDailyForShares(self._db),
            PPR.UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL:
                ppr.ProcessUpdateClassMetricForPredictorAndLabel(self._db),
            PPR.UPDATE_TRADE_POLICY_METRIC: ppr.ProcessUpdateTradePolicyMetric(self._db),
            PPR.HANDLE_TRANSACTION_PROBLEMS: ppr.ProcessHandleTransactionProblems(self._db),
            MYPR.OPTIMIZE_LOG_FILES: ppr.ProcessOptimizeLogFiles(self._db),
            MYPR.RUN_UNDEFINED_PROCESS: ProcessRunUndefinedProcess(self._db)
        }

