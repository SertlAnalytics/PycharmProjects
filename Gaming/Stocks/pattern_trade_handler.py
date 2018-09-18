"""
Description: This module contains the PatternTradeContainer class - central data container for stock data trading
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import TSTR, BT, ST, DC, TBT, PTS, FT, FD, PTHP, PDR
from sertl_analytics.mydates import MyDate
from pattern_system_configuration import SystemConfiguration
from pattern import Pattern
from pattern_bitfinex import MyBitfinexTradeClient, BitfinexConfiguration
from pattern_trade import PatternTrade, PatternTradeApi
from sertl_analytics.exchanges.exchange_cls import Ticker


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
    def ranking_quotient(self):
        return self._ranking_quotient

    def __eq__(self, other):
        return self._ranking_quotient == other.ranking_quotient

    def __lt__(self, other):
        return self._ranking_quotient < other.ranking_quotient


class TradeCandidateCollection:
    """
        controls the trade candidates for one equity. The rule is that only one pattern per entity will be processed
        we try to get the one with the highest success probability for real trading the others for that pattern run
        in simulation mode
    """
    def __init__(self, bitfinex_config: BitfinexConfiguration, symbol: str):
        self.bitfinex_config = bitfinex_config
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
    def __init__(self, bitfinex_config: BitfinexConfiguration):
        self.bitfinex_config = bitfinex_config
        self._actual_pattern_id_list = []  # this list contains all pattern_ids for actual trade candidates
        self._black_pattern_id_readable_list = []
        self._black_buy_trigger_pattern_id_readable_list = []
        self._trade_candidates_for_ticker_id_dict = {}  # with ticker_id as key and TradeCandidateCollection as value

    def add_new_pattern_list(self, pattern_list: list):
        self._actual_pattern_id_list = []
        self._trade_candidates_for_ticker_id_dict = {}
        for pattern in pattern_list:
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

    def __add_pattern_to_trade_candidate_list__(self, pattern):
        for buy_trigger, trade_strategies in self.bitfinex_config.trade_strategy_dict.items():
            key = self.__get_key_for_black_buy_trigger_pattern_id_readable_list(pattern, buy_trigger)
            if key in self._black_buy_trigger_pattern_id_readable_list:
                continue
            if pattern.are_conditions_for_buy_trigger_fulfilled(buy_trigger):
                for trade_strategy in trade_strategies:
                    trade_api = PatternTradeApi(pattern, buy_trigger, TBT.EXPECTED_WIN, trade_strategy)
                    self.__add_trade_candidate_entry_to_ticker_id_dict__(TradeCandidate(PatternTrade(trade_api)))
            else:
                self.__add_to_black_buy_trigger_pattern_id_readable_list__(key)

    @staticmethod
    def __get_key_for_black_buy_trigger_pattern_id_readable_list(pattern: Pattern, buy_trigger: str):
        return '{}_{}'.format(buy_trigger, pattern.id_readable)

    def __add_to_black_pattern_id_list__(self, pattern_id_readable: str):
        if pattern_id_readable not in self._black_pattern_id_readable_list:
            self._black_pattern_id_readable_list.append(pattern_id_readable)
            print('Added to black pattern_id_readable list: {}'.format(pattern_id_readable))

    def add_pattern_trade_to_black_buy_trigger_list(self, pattern_trade: PatternTrade):
        buy_trigger = pattern_trade.buy_trigger
        key = self.__get_key_for_black_buy_trigger_pattern_id_readable_list(pattern_trade.pattern, buy_trigger)
        self.__add_to_black_buy_trigger_pattern_id_readable_list__(key)

    def __add_to_black_buy_trigger_pattern_id_readable_list__(self, buy_trigger_key: str):
        if buy_trigger_key not in self._black_buy_trigger_pattern_id_readable_list:
            self._black_buy_trigger_pattern_id_readable_list.append(buy_trigger_key)
            print('Added to black_buy_trigger_pattern_id_readable list: {}'.format(buy_trigger_key))

    def __add_trade_candidate_entry_to_ticker_id_dict__(self, trade_candidate: TradeCandidate):
        ticker_id = trade_candidate.ticker_id
        if ticker_id not in self._trade_candidates_for_ticker_id_dict:
            self._trade_candidates_for_ticker_id_dict[ticker_id] = TradeCandidateCollection(self.bitfinex_config,
                                                                                            ticker_id)
        self._trade_candidates_for_ticker_id_dict[ticker_id].add_trade_candidate(trade_candidate)

    def get_pattern_trade_candidates_for_processing(self) -> list:
        return_list = []
        for candidate_collection in self._trade_candidates_for_ticker_id_dict.values():
            candidate_list = candidate_collection.get_trade_candidate_list()
            for trade_candidate in candidate_list:
                return_list.append(trade_candidate)
        return return_list


class PatternTradeHandler:
    def __init__(self, sys_config: SystemConfiguration, bitfinex_config: BitfinexConfiguration):
        self.sys_config = sys_config
        self.bitfinex_config = bitfinex_config
        self.bitfinex_trade_client = MyBitfinexTradeClient(bitfinex_config)
        self.stock_db = self.sys_config.db_stock
        self.ticker_id_list = []
        self.pattern_trade_dict = {}
        self.process = ''
        self.trade_candidate_controller = TradeCandidateController(self.bitfinex_config)
        self._last_price_for_test = 0

    # def __del__(self):
    #     print('PatternTradeHandler: Destructor...')
    #     self.__create_trailing_stop_order_for_all_executed_trades__()

    @property
    def trade_numbers(self) -> int:
        return len(self.pattern_trade_dict)

    def add_pattern_list_for_trade(self, pattern_list):
        self.trade_candidate_controller.add_new_pattern_list(pattern_list)
        self.__process_trade_candidates__()

    def check_actual_trades(self, last_price_for_test=None):
        self._last_price_for_test = last_price_for_test
        self.__remove_finished_pattern_trades__()
        self.__process_trade_candidates__()  # take care of old patterns in queue
        if self.trade_numbers == 0:
            return
        self.process = 'Ticker'
        self.__adjust_stops_and_limits__()
        self.__handle_sell_triggers__()
        self.__handle_wrong_breakout__()
        self.__handle_buy_triggers__()
        self.__update_ticker_lists__()  # some entries could be deleted
        self.process = ''

    def __process_trade_candidates__(self):
        if self.process != '':
            return
        self.process = 'HandleTradeCandidates'
        for trade_candidate in self.trade_candidate_controller.get_pattern_trade_candidates_for_processing():
            self.__process_trade_candidate__(trade_candidate)
        self.__remove_outdated_pattern_trades_in_status_new__()
        self.process = ''

    def __process_trade_candidate__(self, trade_candidate: TradeCandidate):
        pattern_trade = trade_candidate.pattern_trade
        pattern_trade.was_candidate_for_real_trading = trade_candidate.is_candidate_for_real_trading
        if not self.bitfinex_config.is_simulation:
            if trade_candidate.is_candidate_for_real_trading:
                pattern_trade.is_simulation = False  # REAL Trading
                print('Trade was initiated by is_candidate_for_real_trading: {}'.format(pattern_trade.id))
            elif pattern_trade.buy_trigger in self.bitfinex_config.default_trade_strategy_dict:
                buy_trigger = pattern_trade.buy_trigger
                if pattern_trade.trade_strategy == self.bitfinex_config.default_trade_strategy_dict(buy_trigger):
                    pattern_trade.is_simulation = False  # REAL Trading
                    print('Trade was initiated by default_trade_strategy: {}'.format(pattern_trade.id))
        self.__add_pattern_trade_to_trade_dict__(pattern_trade)

    @staticmethod
    def __print_details_after_setting_to_real_trade__(self, prefix: str, pattern_trade: PatternTrade):
        print('Trade was initiated by default_trade_strategy for {}'.format(pattern_trade.id))

    def __add_pattern_trade_to_trade_dict__(self, pattern_trade: PatternTrade):
        if pattern_trade.pattern.ticker_id not in self.ticker_id_list:
            self.ticker_id_list.append(pattern_trade.pattern.ticker_id)
        if pattern_trade.id in self.pattern_trade_dict:
            if self.pattern_trade_dict[pattern_trade.id].status == PTS.NEW:  # replace with new version
                self.pattern_trade_dict[pattern_trade.id] = pattern_trade
                self.__print_details_after_adding_to_trade_dict(pattern_trade, 'Replace')
        else:
            self.pattern_trade_dict[pattern_trade.id] = pattern_trade
            self.__print_details_after_adding_to_trade_dict(pattern_trade, 'Add')

    @staticmethod
    def __print_details_after_adding_to_trade_dict(pattern_trade: PatternTrade, scope: str):
        prefix = 'Adding to trading list' if scope == 'Add' else 'Replacing in trading list'
        suffix = ' (simulation)' if pattern_trade.is_simulation else ' (REAL)'
        print('{}{}...: {}'.format(prefix, suffix, pattern_trade.id))

    def __remove_outdated_pattern_trades_in_status_new__(self):
        # remove trades which doesn't belong to an actual pattern anymore
        deletion_key_list = [key for key, trades in self.__get_pattern_trade_dict_by_status__(PTS.NEW).items()
                             if trades.pattern.id not in self.trade_candidate_controller._actual_pattern_id_list]
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list, PDR.PATTERN_VANISHED)

    def sell_on_fibonacci_cluster_top(self):
        self.bitfinex_trade_client.delete_all_orders()
        self.bitfinex_trade_client.sell_all_assets()
        self.__clear_internal_lists__()

    def __get_ticker_for_pattern_trade__(self, pattern_trade: PatternTrade) -> Ticker:
        if self._last_price_for_test:
            return self.__get_ticker_for_pattern_trade_and_test_data__(pattern_trade)
        else:
            return self.bitfinex_trade_client.get_ticker(pattern_trade.ticker_id)

    def __get_ticker_for_pattern_trade_and_test_data__(self, pattern_trade: PatternTrade) -> Ticker:
        val = self._last_price_for_test
        ts = pattern_trade.pattern.part_main.tick_last.time_stamp
        return Ticker(pattern_trade.ticker_id, bid=val, ask=val, last_price=val, low=val, high=val, vol=0, ts=ts)

    def __get_balance_by_symbol__(self, symbol: str):
        return self.bitfinex_trade_client.get_balance(symbol)

    def __clear_internal_lists__(self):
        self.ticker_id_list = []
        self.pattern_trade_dict = {}

    def __handle_sell_triggers__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values():
            ticker = self.__get_ticker_for_pattern_trade__(pattern_trade)
            pattern_trade.print_state_details(PTHP.HANDLE_SELL_TRIGGERS, ticker)
            if pattern_trade.stop_loss_current > ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.STOP_LOSS)
            elif pattern_trade.limit_current < ticker.last_price:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.LIMIT)
            elif pattern_trade.time_stamp_end < ticker.time_stamp:
                self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.PATTERN_END)
            elif not self.trade_candidate_controller.is_pattern_id_in_actual_pattern_id_list(pattern_trade.pattern.id):
                if self.bitfinex_config.finish_vanished_trades:
                    self.__handle_sell_trigger__(ticker, pattern_trade.ticker_id, pattern_trade, ST.PATTERN_VANISHED)

    def __handle_sell_trigger__(self, ticker: Ticker, ticker_id: str, pattern_trade: PatternTrade, sell_trigger: str):
        sell_comment = 'Sell_{} at {:.2f} on {}'.format(sell_trigger, ticker.last_price, ticker.date_time_str)
        print('Sell: {}'.format(sell_comment))
        order_status = self.bitfinex_trade_client.create_sell_market_order(ticker_id, pattern_trade.executed_amount)
        pattern_trade.set_order_status_sell(order_status, sell_trigger, sell_comment)
        pattern_trade.save_trade()

    def __handle_wrong_breakout__(self):
        deletion_key_list = []
        for key, pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).items():
            ticker = self.__get_ticker_for_pattern_trade__(pattern_trade)
            if pattern_trade.is_ticker_wrong_breakout(PTHP.HANDLE_WRONG_BREAKOUT, ticker):
                deletion_key_list.append(key)
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list, PDR.WRONG_BREAKOUT)

    def __remove_finished_pattern_trades__(self):
        deletion_key_list = [key for key in self.__get_pattern_trade_dict_by_status__(PTS.FINISHED)]
        self.__delete_entries_from_pattern_trade_dict__(deletion_key_list, PDR.TRADE_FINISHED)

    def __delete_entries_from_pattern_trade_dict__(self, deletion_key_list: list, deletion_reason: str):
        if len(deletion_key_list) == 0:
            return
        for key in deletion_key_list:
            pattern_trade = self.pattern_trade_dict[key]
            print('Removed from trade_dict ({}): {}'.format(deletion_reason, pattern_trade.get_trade_meta_data()))
            if deletion_reason != PDR.PATTERN_VANISHED:  # they have the trend to reappear
                self.trade_candidate_controller.add_pattern_trade_to_black_buy_trigger_list(pattern_trade)
            del self.pattern_trade_dict[key]
        self.__update_ticker_lists__()

    def __handle_buy_triggers__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.NEW).values():
            ticker = self.__get_ticker_for_pattern_trade__(pattern_trade)
            if pattern_trade.is_breakout_active:
                if pattern_trade.is_ticker_breakout(PTHP.HANDLE_BUY_TRIGGERS, ticker):
                    self.__handle_buy_trigger_for_pattern_trade__(ticker, pattern_trade)
            else:
                pattern_trade.verify_touch_point(ticker)
                if pattern_trade.is_breakout_active:
                    print('Breakout activated for last price={:.2f}'.format(ticker.last_price))

    def __handle_buy_trigger_for_pattern_trade__(self, ticker: Ticker, pattern_trade: PatternTrade):
        ticker_id = pattern_trade.ticker_id
        buy_comment = '{}-{}-{} at {:.2f} on {}'.format(ticker_id,
                                                        pattern_trade.buy_trigger, pattern_trade.trade_strategy,
                                                        ticker.last_price, ticker.date_time_str)
        print('Handle_buy_trigger_for_pattern_trade: {}'.format(buy_comment))
        order_status = self.bitfinex_trade_client.buy_available(ticker_id, ticker.last_price)
        pattern_trade.set_order_status_buy(order_status, buy_comment, ticker)
        pattern_trade.save_trade()

    def __adjust_stops_and_limits__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values():
            ticker = self.__get_ticker_for_pattern_trade__(pattern_trade)
            pattern_trade.adjust_to_next_ticker(ticker)

    def __create_trailing_stop_order_for_all_executed_trades__(self):
        for pattern_trade in self.__get_pattern_trade_dict_by_status__(PTS.EXECUTED).values():
            ticker_id = pattern_trade.ticker_id
            amount = pattern_trade.order_status_buy.executed_amount
            distance = pattern_trade.trailing_stop_distance
            pattern_trade.order_status_sell = self.bitfinex_trade_client.create_sell_trailing_stop_order(
                ticker_id, amount, distance)

    def __update_ticker_lists__(self):
        self.ticker_id_list = []
        for pattern_trade in self.pattern_trade_dict.values():
            if pattern_trade.ticker_id not in self.ticker_id_list:
                self.ticker_id_list.append(pattern_trade.ticker_id)

    def __get_pattern_trade_dict_by_status__(self, status: str) -> dict:
        return {key: value for key, value in self.pattern_trade_dict.items() if value.status == status}



