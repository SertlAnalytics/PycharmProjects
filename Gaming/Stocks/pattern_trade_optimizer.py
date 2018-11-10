"""
Description: This module contains the trade optimizer functions
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, DC
from pattern_database.stock_database import StockDatabase
import numpy as np
import statistics
import math


class TradeStrategyOptimizer:
    def __init__(self, db_stock: StockDatabase):
        self.db_stock = db_stock
        self.df_trades = self.db_stock.get_trade_records_for_trading_optimizer_dataframe()
        self.expected_relation_pos_neg = 1.8
        self._pattern_type_pos_neg_result_dict = self.__get_pattern_type_pos_neg_result_relation_as_dict__()
        self._optimal_pattern_type_dict_for_long_trading = self.__get_optimal_pattern_type_dict_for_long_trading__()
        self._optimal_pattern_type_list_for_long_trading = \
            [pattern_type for pattern_type in self._optimal_pattern_type_dict_for_long_trading]

    @property
    def pattern_type_pos_neg_result_dict(self) -> dict:
        return self._pattern_type_pos_neg_result_dict

    @property
    def optimal_pattern_type_dict_for_long_trading(self) -> dict:
        return self._optimal_pattern_type_dict_for_long_trading

    @property
    def optimal_pattern_type_list_for_long_trading(self) -> list:
        return self._optimal_pattern_type_list_for_long_trading

    def get_trade_able_pattern_from_pattern_list(self, pattern_list: list) -> list:
        return [pattern for pattern in pattern_list
                if pattern.pattern_type in self._optimal_pattern_type_list_for_long_trading]

    def get_optimal_strategy_for_pattern_id_list(self, pattern_id_list: list, buy_trigger: str, strategy_list: list):
        """
        For each pattern we get the nearest neighbors pattern which are checked in this module.
        The check is done as follows:
        a) check all trades for these patterns
        b) take the trade strategy which was the best on average for these patterns
        :param pattern_id_list: pattern_id of these patterns
        :param buy_trigger: buy_trigger for the actual trade
        :param strategy_list: possible strategies
        :return: best strategy for the nearest neighbors pattern, assuming it will be best for the source pattern as well
        """
        strategy_result_list_dict = {strategy: [] for strategy in strategy_list}
        strategy_opt = ''
        result_pct_opt = -math.inf
        for pattern_id in pattern_id_list:
            df_pattern_id = self.df_trades.loc[np.logical_and(
                    self.df_trades[DC.PATTERN_ID] == pattern_id,
                    self.df_trades[DC.BUY_TRIGGER] == buy_trigger)]
            for index, rows in df_pattern_id.iterrows():
                strategy = rows[DC.TRADE_STRATEGY]
                if strategy in strategy_list:
                    strategy_result_list_dict[strategy].append(float(rows[DC.TRADE_RESULT_PCT]))
        for strategy, strategy_result_list in strategy_result_list_dict.items():
            if len(strategy_result_list) > 0 and statistics.mean(strategy_result_list) > result_pct_opt:
                strategy_opt = strategy
                result_pct_opt = statistics.mean(strategy_result_list)
        print('Best trade strategy: {} - expected: {:0.2f}%'.format(strategy_opt, result_pct_opt))
        return strategy_opt, result_pct_opt

    def __get_optimal_pattern_type_dict_for_long_trading__(self):
        opt_dict = {}
        for pattern_type in FT.get_long_trade_able_types():
            if self._pattern_type_pos_neg_result_dict[pattern_type] > self.expected_relation_pos_neg:
                opt_dict[pattern_type] = self._pattern_type_pos_neg_result_dict[pattern_type]
        return opt_dict

    def __get_pattern_type_pos_neg_result_relation_as_dict__(self):
        pattern_type_pos_neg_relation_dict = {}
        for pattern_type in FT.get_all():
            pattern_type_pos_neg_relation_dict[pattern_type] = 1  # default
            df_pos = self.df_trades.loc[np.logical_and(
                    self.df_trades[DC.PATTERN_TYPE] == pattern_type,
                    self.df_trades[DC.TRADE_RESULT_PCT] > 1)]
            df_neg = self.df_trades.loc[np.logical_and(
                self.df_trades[DC.PATTERN_TYPE] == pattern_type,
                self.df_trades[DC.TRADE_RESULT_PCT] < -1)]
            if df_neg.shape[0] < 10:  # not enough data
                if df_pos.shape[0] > 20:
                    pattern_type_pos_neg_relation_dict[pattern_type] = 3
            else:
                pattern_type_pos_neg_relation_dict[pattern_type] = round(df_pos.shape[0]/df_neg.shape[0], 1)
        return pattern_type_pos_neg_relation_dict

