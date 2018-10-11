"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import Indices, FT
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_data_container import PatternDataHandler
from pattern_configuration import PatternConfiguration, RuntimeConfiguration
from pattern_configuration import PatternDebugger
from pattern_database import stock_database
from copy import deepcopy
# from bitfinex import Bitfinex
from pattern_predictor import PatternPredictorBeforeBreakout, PatternPredictorAfterBreakout, \
    PatternPredictorTouchPoints, PatternPredictorForTrades
import numpy as np


class PatternMasterPredictor:
    def __init__(self, config: PatternConfiguration):
        self.config = config
        self.pattern_table = stock_database.PatternTable()
        self.trade_table = stock_database.TradeTable()
        self.db_stock = stock_database.StockDatabase()
        self.predictor_dict = {}
        self.__init_predictor_dict__()

    def get_feature_columns(self, pattern_type: str):
        predictor = self.predictor_dict[pattern_type]
        return predictor.feature_columns

    def predict_for_label_columns(self, pattern_type: str, x_input: np.array):
        predictor = self.predictor_dict[pattern_type]
        return predictor.predict_for_label_columns(x_input)

    def init_without_condition_list(self, ticker_id: str):
        self.__init_predictor_dict__(self.__get_skip_condition_list__(ticker_id))

    def __init_predictor_dict__(self, skip_condition_list=None):
        for pattern_type in FT.get_all():
            self.predictor_dict[pattern_type] = \
                self.__get_predictor_for_pattern_type__(pattern_type, skip_condition_list)

    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        pass

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        pass


class PatternMasterPredictorTouchPoints(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorTouchPoints(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorBeforeBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorBeforeBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorAfterBreakout(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_pattern]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorAfterBreakout(self.db_stock, pattern_type, skip_condition_list)


class PatternMasterPredictorForTrades(PatternMasterPredictor):
    def __get_skip_condition_list__(self, ticker_id: str) -> list:
        return ["Ticker_ID = '{}'".format(ticker_id), self.config.and_clause_for_trade]

    def __get_predictor_for_pattern_type__(self, pattern_type: str, skip_condition_list: list):
        return PatternPredictorForTrades(self.db_stock, pattern_type, skip_condition_list)


class SystemConfiguration:
    def __init__(self, for_semi_deep_copy=False):
        if for_semi_deep_copy:
            return
        self.trading = BitfinexConfiguration()
        self.config = PatternConfiguration()
        self.runtime = RuntimeConfiguration()
        # self.bitfinex = Bitfinex()
        self.crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        self.pdh = PatternDataHandler(self.config)
        self.pattern_table = stock_database.PatternTable()
        self.trade_table = stock_database.TradeTable()
        self.db_stock = stock_database.StockDatabase()
        self.master_predictor_touch_points = PatternMasterPredictorTouchPoints(self.config)
        self.master_predictor_before_breakout = PatternMasterPredictorBeforeBreakout(self.config)
        self.master_predictor_after_breakout = PatternMasterPredictorAfterBreakout(self.config)
        self.master_predictor_for_trades = PatternMasterPredictorForTrades(self.config)

    def init_predictors_without_condition_list(self, ticker_id: str):
        self.master_predictor_touch_points.init_without_condition_list(ticker_id)
        self.master_predictor_before_breakout.init_without_condition_list(ticker_id)
        self.master_predictor_after_breakout.init_without_condition_list(ticker_id)
        self.master_predictor_for_trades.init_without_condition_list(ticker_id)

    def get_semi_deep_copy(self):
        """
        This function is necessary since db_stock can't be deeply copied - I don't know the reason...
        All other components don't make any problems. But nevertheless with this function we have control
        about which part has to be deeply copied and which can be used by reference.
        """
        sys_config_copy = SystemConfiguration(True)
        sys_config_copy.config = deepcopy(self.config)
        sys_config_copy.runtime = deepcopy(self.runtime)
        # sys_config_copy.bitfinex = self.bitfinex
        sys_config_copy.crypto_ccy_dic = self.crypto_ccy_dic
        sys_config_copy.pdh = self.pdh
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.db_stock = self.db_stock
        sys_config_copy.trade_table = self.trade_table
        sys_config_copy.pattern_table = self.pattern_table
        sys_config_copy.master_predictor_touch_points = self.master_predictor_touch_points
        sys_config_copy.master_predictor_before_breakout = self.master_predictor_before_breakout
        sys_config_copy.master_predictor_after_breakout = self.master_predictor_after_breakout
        sys_config_copy.master_predictor_for_trades = self.master_predictor_for_trades
        return sys_config_copy


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