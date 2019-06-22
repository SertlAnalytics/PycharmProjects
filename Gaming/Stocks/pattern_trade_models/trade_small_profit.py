"""
Description: This module is the central class for the calculation for small profit limits
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-18
"""

from sertl_analytics.constants.pattern_constants import DC, FT, PRD, TPA
from pattern_database.stock_database import StockDatabase
from pattern_database.stock_access_layer import AccessLayer4Trade
from pattern_database.stock_trade_entity import TradeEntityCollection, TradeEntity
from pattern_trade_models.trade_environment import TradeEnvironment
from pattern_trade_models.trade_policy import TradePolicy, TradePolicySellCodedTrade
import math


class TradeSmallProfit:
    """
    Description: The intuition behind this class is to use the mean values for the reached max price in pct
    within a trade period for the small profit stop loss
    """
    def __init__(self):
        self._trade_access_layer = AccessLayer4Trade(StockDatabase())
        self.__init_parameters__()

    def __init_parameters__(self):
        self._df_trade_for_calculation = self._trade_access_layer.get_df_for_calculating_small_profit_pct()

        self._df_mean = self._df_trade_for_calculation.groupby(DC.PATTERN_TYPE).mean()
        self._mean_dict = self._df_mean.to_dict('index')

        self._mean_trade_reached_price_pct_dict = {
            key: self._mean_dict[key][DC.TRADE_REACHED_PRICE_PCT] for key in self._mean_dict}
        self._mean_trade_result_pct_dict = {key: self._mean_dict[key][DC.TRADE_RESULT_PCT] for key in self._mean_dict}
        self._mean_trade_reached_price_pct = self._df_trade_for_calculation[DC.TRADE_REACHED_PRICE_PCT].mean()
        self._mean_trade_result_pct = self._df_trade_for_calculation[DC.TRADE_RESULT_PCT].mean()

        # self.print_details_for_mean()

        self._df_std = self._df_trade_for_calculation.groupby(DC.PATTERN_TYPE).std()
        self._std_dict = self._df_std.to_dict('index')
        self._std_trade_reached_price_pct_dict = {
            key: self._std_dict[key][DC.TRADE_REACHED_PRICE_PCT] for key in self._std_dict}
        self._std_trade_result_pct_dict = {key: self._std_dict[key][DC.TRADE_RESULT_PCT] for key in self._std_dict}
        self._std_trade_reached_price_pct = self._df_trade_for_calculation[DC.TRADE_REACHED_PRICE_PCT].std()
        self._std_trade_result_pct = self._df_trade_for_calculation[DC.TRADE_RESULT_PCT].std()

        # self.print_details_for_std()

    def print_details_for_mean(self):
        print('mean_trade_reached_price_pct={:.2f}%, mean_trade_result_pct={:.2f}%'.format(
            self._mean_trade_reached_price_pct, self._mean_trade_result_pct
        ))
        print('self._mean_dict={}'.format(self._mean_dict))

    def print_details_for_std(self):
        print('std_trade_reached_price_pct={:.2f}%, std_trade_result_pct={:.2f}%'.format(
            self._mean_trade_reached_price_pct, self._mean_trade_result_pct
        ))
        print('self._std_dict={}'.format(self._mean_dict))

    @property
    def pattern_types(self) -> list:
        return [key for key in self._mean_dict]

    def get_small_profit_parameter_dict(self, small_profit_distance_from_mean_pct: int):
        pattern_types = list(self.pattern_types)
        pattern_types.append(FT.ALL)
        small_profit_parameter_dict = {}
        for pattern_type in pattern_types:
            upper_pct = round(self.get_mean_trade_reached_price_pct_for_pattern_type(pattern_type), 2)
            lower_pct = round(upper_pct * (100-small_profit_distance_from_mean_pct)/100, 2)
            small_profit_parameter_dict[pattern_type] = [upper_pct, lower_pct]
        return small_profit_parameter_dict

    def get_suggested_small_profit_pct_for_pattern_type(self, pattern_type: str):
        mean_trade_reached_price_pct = self.get_mean_trade_reached_price_pct_for_pattern_type(pattern_type)
        std_trade_reached_price_pct = self.get_std_trade_reached_price_pct_for_pattern_type(pattern_type)
        return mean_trade_reached_price_pct - std_trade_reached_price_pct

    def get_mean_trade_reached_price_pct_for_pattern_type(self, pattern_type: str):
        return self._mean_trade_reached_price_pct_dict.get(pattern_type, self._mean_trade_reached_price_pct)

    def get_std_trade_reached_price_pct_for_pattern_type(self, pattern_type: str):
        return self._std_trade_reached_price_pct_dict.get(pattern_type, self._std_trade_reached_price_pct)

    def get_mean_trade_result_pct_for_pattern_type(self, pattern_type: str):
        return self._mean_trade_result_pct_dict.get(pattern_type, self._mean_trade_result_pct)
