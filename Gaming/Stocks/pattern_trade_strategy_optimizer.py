"""
Description: This module contains the PatternTradeStrategyOptimizer classes
They are used for getting the correct trade strategy for a dedicated trade.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import DC
from pattern import Pattern
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade import PatternTrade, PatternTradeApi


class TradeCandidateController:
    """
        controls which trade is put into the trade process - this process is handled by PatternTradeHandler
    """
    def __init__(self, exchange_config: ExchangeConfiguration):
        self.exchange_config = exchange_config
        self._pattern_id_optimal_strategy_list = []  # this list contains verified strategies for a pattern

    def get_optimal_trade_strategy_for_pattern(self, pattern: Pattern):
        for nn_entry in pattern.nearest_neighbor_entry_list:
            print(nn_entry.get_details)
        return False

