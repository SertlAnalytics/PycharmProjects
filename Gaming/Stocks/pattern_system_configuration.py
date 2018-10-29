"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import Indices, EQUITY_TYPE, PRD
from sertl_analytics.pybase.loop_list import LL
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_data_container import PatternDataHandler
from pattern_configuration import PatternConfiguration, RuntimeConfiguration
from pattern_configuration import PatternDebugger
from pattern_database.stock_database import StockDatabase, PatternTable, TradeTable
from copy import deepcopy
# from bitfinex import Bitfinex
from pattern_predictor import PatternMasterPredictorBeforeBreakout, PatternMasterPredictorAfterBreakout
from pattern_predictor import PatternMasterPredictorTouchPoints, PatternMasterPredictorForTrades
from pattern_predictor import PatternMasterPredictorHandler
import numpy as np
from pattern_data_provider import PatternDataProviderApi, PatternDataProvider


class SystemConfiguration:
    def __init__(self, data_provider_api: PatternDataProviderApi, for_semi_deep_copy=False):
        self.data_provider_api = data_provider_api
        self.config = PatternConfiguration(self.data_provider_api)
        self.runtime = RuntimeConfiguration()
        self.trading = BitfinexConfiguration()
        self.pdh = None  # for the pattern data handler - for a dedicated ticker_id later
        if for_semi_deep_copy:
            return
        self.crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        # self.pdh = PatternDataHandler(self.config)
        self.pattern_table = PatternTable()
        self.trade_table = TradeTable()
        self.db_stock = StockDatabase()
        self.data_provider = self.get_data_provider_by_api()
        self.master_predictor_handler = PatternMasterPredictorHandler(self.config)

    @property
    def master_predictor_touch_points(self):
        return self.master_predictor_handler.master_predictor_touch_points

    @property
    def master_predictor_before_breakout(self):
        return self.master_predictor_handler.master_predictor_before_breakout

    @property
    def master_predictor_after_breakout(self):
        return self.master_predictor_handler.master_predictor_after_breakout

    @property
    def master_predictor_for_trades(self):
        return self.master_predictor_handler.master_predictor_for_trades

    def init_predictors_without_condition_list(self, ticker_id: str):
        self.master_predictor_handler.init_predictors_without_condition_list(ticker_id)

    def init_pattern_data_handler_for_ticker_id(self, ticker_id: str, and_clause: str, limit=300) -> bool:
        df_data = self.data_provider.get_df_for_ticker(ticker_id, and_clause, limit)
        if df_data is None:
            return False
        self.pdh = PatternDataHandler(self.config, df_data)
        return True

    def get_data_provider_by_api(self) -> PatternDataProvider:
        return PatternDataProvider(self.db_stock, self.crypto_ccy_dic, self.data_provider_api)

    def update_data_provider_api(self, from_db: bool=None, period: str=None, aggregation: int=None):
        if from_db is not None:
            self.data_provider_api.from_db = from_db
        if period is not None:
            self.data_provider_api.period = period
        if aggregation is not None:
            self.data_provider_api.period_aggregation = aggregation

    def get_semi_deep_copy_for_new_pattern_data_provider_api(self, data_provider_api: PatternDataProviderApi=None):
        """
        This function is necessary since db_stock can't be deeply copied - I don't know the reason...
        All other components don't make any problems. But nevertheless with this function we have control
        about which part has to be deeply copied and which can be used by reference.
        """
        if data_provider_api is None:
            data_provider_api = deepcopy(self.config.data_provider_api)
        sys_config_copy = SystemConfiguration(data_provider_api, True)
        sys_config_copy.config.ticker_dic = self.config.ticker_dic
        sys_config_copy.crypto_ccy_dic = self.crypto_ccy_dic
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.db_stock = self.db_stock
        sys_config_copy.trade_table = self.trade_table
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.data_provider = sys_config_copy.get_data_provider_by_api()
        sys_config_copy.master_predictor_handler = self.master_predictor_handler
        return sys_config_copy

    def update_runtime_parameters_by_dict_values(self, entry_dic: dict):
        self.runtime.actual_ticker = entry_dic[LL.TICKER]
        if self.runtime.actual_ticker in self.crypto_ccy_dic:
            self.runtime.actual_ticker_equity_type = EQUITY_TYPE.CRYPTO
            if self.config.api_period == PRD.INTRADAY:
                self.runtime.actual_expected_win_pct = 1
            else:
                self.runtime.actual_expected_win_pct = 1
        else:
            self.runtime.actual_ticker_equity_type = EQUITY_TYPE.SHARE
            self.runtime.actual_expected_win_pct = 1
        self.runtime.actual_and_clause = entry_dic[LL.AND_CLAUSE]
        self.runtime.actual_number = entry_dic[LL.NUMBER]
        if self.db_stock is not None:
            self.runtime.actual_ticker_name = self.db_stock.get_name_for_symbol(entry_dic[LL.TICKER])
        if self.runtime.actual_ticker_name == '':
            self.runtime.actual_ticker_name = self.config.ticker_dic[entry_dic[LL.TICKER]]


debugger = PatternDebugger()

# Todo Signals and expected win & connection to Bitfinex
"""
ToDo list:
a) Signals - later: With support from KI
- Breakout (differ between false breakout and real breakout
- pullback: within a range (opposite from "expected" breakout) and Fibonacci compliant, i.e. 5th wave completed
b) Expected win for all these case
c) Channel Pattern: sometimes (???) there are only 2 hits on the entrance side and 3 or more on the opposite (breakout)
side - so I think we have to go back with the f_params to the left side as well...
d) Connection to Bitfinex (from 01.09.2018): https://www.bitfinex.com/posts/267
e) Correlation: Please check BCH_USD and EOS - both had TKEs together....
"""