"""
Description: This module contains the PatternTradeCandidates classes
They are used for getting the correct candidates for the trades.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import DC
from pattern import Pattern
from sertl_analytics.exchanges.exchange_cls import ExchangeConfiguration
from pattern_trade import PatternTrade, PatternTradeApi


class TradeCandidate:
    def __init__(self, pattern_trade: PatternTrade):
        self._pattern_trade = pattern_trade
        self._forecast_pct = self.pattern_trade.data_dict_obj.get(DC.FC_TRADE_REACHED_PRICE_PCT)
        self._forecast_result_id = self.pattern_trade.data_dict_obj.get(DC.FC_TRADE_RESULT_ID)
        self._ranking_quotient = self._forecast_pct * self._forecast_result_id

    @property
    def pattern_trade(self) -> PatternTrade:
        return self._pattern_trade

    @property
    def is_candidate_for_real_trading(self):
        return self._ranking_quotient > 0

    @property
    def ticker_id(self):
        return self.pattern_trade.pattern.ticker_id

    @property
    def pattern_id(self):
        return self.pattern_trade.pattern.id

    @property
    def trade_id(self):
        return self.pattern_trade.id

    @property
    def ranking_quotient(self):
        return self._ranking_quotient

    def __eq__(self, other):
        return self._ranking_quotient == other.ranking_quotient

    def __lt__(self, other):
        return self._ranking_quotient < other.ranking_quotient


class TradeCandidateCollection:
    """
        controls the trade candidates for one equity. The rule is that only one pattern per entity will be processed
        we try to get the one with the highest success probability for real exchange_config the others for that pattern run
        in simulation mode
    """
    def __init__(self, exchange_config: ExchangeConfiguration, symbol: str):
        self.exchange_config = exchange_config
        self.symbol = symbol
        self.candidates_by_pattern_id_dict = {}  # contains for each pattern_id the related trade candidates

    def add_trade_candidate(self, trade_candidate: TradeCandidate):
        if trade_candidate.pattern_id not in self.candidates_by_pattern_id_dict:
            self.candidates_by_pattern_id_dict[trade_candidate.pattern_id] = [trade_candidate]
        else:
            self.candidates_by_pattern_id_dict[trade_candidate.pattern_id].append(trade_candidate)

    def get_trade_candidate_list(self) -> list:
        if len(self.candidates_by_pattern_id_dict) == 0:
            return []
        self.__sort_candidates_by_pattern_id_dict_by_ranking__()
        pattern_id_for_best_trade = self.__get_pattern_id_for_best_trade__()
        trade_candidate_list_for_best_trade = self.candidates_by_pattern_id_dict[pattern_id_for_best_trade]
        del self.candidates_by_pattern_id_dict[pattern_id_for_best_trade]  # this is now regarded as processed
        return trade_candidate_list_for_best_trade

    def __get_pattern_id_for_best_trade__(self):
        best_trade_candidates_by_pattern_id = [lists[0] for lists in self.candidates_by_pattern_id_dict.values()]
        best_trade_candidates_by_pattern_id = sorted(best_trade_candidates_by_pattern_id, reverse=True)
        best_trade_candidate = best_trade_candidates_by_pattern_id[0]
        return best_trade_candidate.pattern_id

    def __sort_candidates_by_pattern_id_dict_by_ranking__(self):
        for pattern_id in self.candidates_by_pattern_id_dict:
            self.candidates_by_pattern_id_dict[pattern_id] = sorted(self.candidates_by_pattern_id_dict[pattern_id],
                                                                    reverse=True)


class TradeCandidateController:
    """
        controls which trade is put into the trade process - this process is handled by PatternTradeHandler
    """
    def __init__(self, exchange_config: ExchangeConfiguration):
        self.exchange_config = exchange_config
        self._actual_pattern_id_list = []  # this list contains all pattern_ids for actual trade candidates
        self._black_pattern_id_readable_list = []
        self._black_buy_pattern_id_readable_list = []
        self._black_buy_and_strategy_pattern_id_readable_list = []
        self._trade_candidates_for_ticker_id_dict = {}  # with ticker_id as key and TradeCandidateCollection as value

    @property
    def actual_pattern_id_list(self):
        return self._actual_pattern_id_list

    def add_new_pattern_list(self, pattern_list: list):
        self._actual_pattern_id_list = []
        self._trade_candidates_for_ticker_id_dict = {}
        for pattern in pattern_list:
            if pattern.ticker_id not in ['NEOUSD']:  # ToDo currently we have some data sourcing issues with that...
                self._actual_pattern_id_list.append(pattern.id)
                self.__add_pattern_to_candidates_after_check__(pattern)

    def is_pattern_id_in_actual_pattern_id_list(self, pattern_id: str) -> bool:
        return pattern_id in self._actual_pattern_id_list

    def __add_pattern_to_candidates_after_check__(self, pattern: Pattern):
        if pattern.id_readable in self._black_pattern_id_readable_list:
            print('Already in black list: {}'.format(pattern.id_readable))
            return  # already checked against some conditions
        if pattern.are_pre_conditions_for_a_trade_fulfilled():
            self.__add_pattern_to_trade_candidate_list__(pattern)
        else:
            self.__add_to_black_pattern_id_list__(pattern.id_readable)

    def __add_pattern_to_trade_candidate_list__(self, pattern: Pattern):
        for buy_trigger, trade_strategies in self.exchange_config.trade_strategy_dict.items():
            key_buy = self.__get_key_for_black_buy_pattern_id_readable_list(pattern, buy_trigger)
            print('Add_to_candidate_list: Checking buy trigger: {}'.format(key_buy))
            if key_buy in self._black_buy_pattern_id_readable_list:
                print('Already in black_buy_trigger_list: {}'.format(key_buy))
            else:
                if pattern.are_conditions_for_buy_trigger_fulfilled(buy_trigger):
                    self.__add_pattern_to_trade_candidate_list_for_buy_trigger__(pattern, buy_trigger, trade_strategies)
                else:
                    self.__add_to_black_buy_pattern_id_readable_list__(key_buy)

    def __add_pattern_to_trade_candidate_list_for_buy_trigger__(
            self, pattern: Pattern, buy_trigger: str, trade_strategies: list):
        for trade_strategy in trade_strategies:
            key_buy_and_strategy = self.__get_key_for_black_buy_and_strategy_pattern_id_readable_list(
                pattern, buy_trigger, trade_strategy)
            print('Add_to_candidate_list: Checking trade strategy: {}'.format(key_buy_and_strategy))
            if key_buy_and_strategy in self._black_buy_and_strategy_pattern_id_readable_list:
                print('Already in black_buy_trigger_trade_strategy_pattern_id_list: {}'.format(key_buy_and_strategy))
            else:
                if pattern.are_conditions_for_trade_strategy_fulfilled(trade_strategy):
                    trade_api = PatternTradeApi(pattern, buy_trigger, trade_strategy)
                    trade_api.bitfinex_config = self.exchange_config
                    self.__add_trade_candidate_entry_to_ticker_id_dict__(TradeCandidate(PatternTrade(trade_api)))
                else:
                    self.__add_to_black_buy_strategy_pattern_id_readable_list__(key_buy_and_strategy)

    @staticmethod
    def __get_key_for_black_buy_pattern_id_readable_list(pattern: Pattern, buy_trigger: str):
        return '{}_{}'.format(buy_trigger, pattern.id_readable)

    @staticmethod
    def __get_key_for_black_buy_and_strategy_pattern_id_readable_list(
            pattern: Pattern, buy_trigger: str, trade_strategy: str):
        return '{}_{}_{}'.format(buy_trigger, trade_strategy, pattern.id_readable)

    def __add_to_black_pattern_id_list__(self, pattern_id_readable: str):
        if pattern_id_readable not in self._black_pattern_id_readable_list:
            self._black_pattern_id_readable_list.append(pattern_id_readable)
            print('Added to black_pattern_id_readable_list: {}'.format(pattern_id_readable))

    def add_pattern_trade_to_black_buy_trigger_list(self, pattern_trade: PatternTrade):
        buy_trigger = pattern_trade.buy_trigger
        key = self.__get_key_for_black_buy_pattern_id_readable_list(pattern_trade.pattern, buy_trigger)
        self.__add_to_black_buy_pattern_id_readable_list__(key)

    def __add_to_black_buy_pattern_id_readable_list__(self, buy_trigger_key: str):
        if buy_trigger_key not in self._black_buy_pattern_id_readable_list:
            self._black_buy_pattern_id_readable_list.append(buy_trigger_key)
            print('Added to black_buy_trigger_pattern_id_readable list: {}'.format(buy_trigger_key))

    def __add_to_black_buy_strategy_pattern_id_readable_list__(self, buy_and_strategy_key: str):
        if buy_and_strategy_key not in self._black_buy_and_strategy_pattern_id_readable_list:
            self._black_buy_and_strategy_pattern_id_readable_list.append(buy_and_strategy_key)
            print('Added to black_buy_and_strategy_pattern_id_readable_list: {}'.format(buy_and_strategy_key))

    def __add_trade_candidate_entry_to_ticker_id_dict__(self, trade_candidate: TradeCandidate):
        ticker_id = trade_candidate.ticker_id
        if ticker_id not in self._trade_candidates_for_ticker_id_dict:
            self._trade_candidates_for_ticker_id_dict[ticker_id] = TradeCandidateCollection(self.exchange_config,
                                                                                            ticker_id)
        self._trade_candidates_for_ticker_id_dict[ticker_id].add_trade_candidate(trade_candidate)
        print('Added to trade_candidates_for_ticker_id_dict {}: {}'.format(ticker_id, trade_candidate.trade_id))

    def get_pattern_trade_candidates_for_processing(self) -> list:
        return_list = []
        for candidate_collection in self._trade_candidates_for_ticker_id_dict.values():
            candidate_list = candidate_collection.get_trade_candidate_list()
            for trade_candidate in candidate_list:
                return_list.append(trade_candidate)
        return return_list