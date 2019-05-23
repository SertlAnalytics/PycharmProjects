"""
Description: This module contains the test cases for Bitfinex exchange_config tests
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC, DC, PRD
from pattern import Pattern
from sertl_analytics.mydates import MyDate
from pattern_data_provider import PatternDataProvider
from pattern_wave_tick import TickerWaveTickConverter
from pattern_system_configuration import SystemConfiguration


class TradeTestApi:
    def __init__(self):
        self.from_db = True
        self.period = PRD.DAILY
        self.period_aggregation = 1
        self.volume_increase = 10
        self.trade_id = ''
        self.pattern_id = ''
        self.pattern_type = ''
        self.pattern = None
        self.buy_trigger = ''
        self.trade_strategy = ''
        self.test_process = ''
        self.symbol = ''
        self.dt_start = None
        self.dt_end = None
        self.and_clause = ''
        self.and_clause_unlimited = ''
        self.tick_list_for_replay = None  # is used for the whole stock data from the begin of the pattern

    def print_test_api(self):
        print('PatternType={}, buy_trigger={}, trade_strategy={}, test_process={}, _symbol={}, and_clause={}'.format(
            self.pattern_type, self.buy_trigger, self.trade_strategy, self.test_process, self.symbol, self.and_clause
        ))


class TradeTestCase:
    def __init__(self, api: TradeTestApi):
        self.api = api
        self.pattern_type = api.pattern_type
        self.buy_trigger = api.buy_trigger
        self.trade_strategy = api.trade_strategy
        if api.pattern is None:
            self.test_process = api.test_process
        else:
            self.test_process = api.pattern.sys_config.runtime_config.actual_trade_process
        self.symbol = ''
        self.and_clause = ''
        self.time_stamp_start = 0
        self.period_seconds = 0
        self.ticks_per_period = 4
        self.wave_tick_list = []  # [wave_tick]


class TradeTestCaseFactory:
    @staticmethod
    def get_trade_test_api_by_selected_trade_row(row, test_process: str) -> TradeTestApi:
        api = TradeTestApi()
        api.trade_id = row[DC.TRADE_ID] if DC.TRADE_ID in row else row[DC.ID]
        api.pattern_id = row[DC.PATTERN_ID] if DC.PATTERN_ID in row else ''
        api.test_process = test_process  # e.g. TP.TRADE_REPLAY
        api.pattern_type = row[DC.PATTERN_TYPE]
        # api.buy_trigger = row[DC.BUY_TRIGGER]
        api.trade_strategy = row[DC.TRADE_STRATEGY]
        api.symbol = row[DC.TICKER_ID]
        api.dt_start = MyDate.adjust_by_days(row[DC.PATTERN_RANGE_BEGIN_DT], -30)
        api.dt_end = MyDate.adjust_by_days(row[DC.PATTERN_RANGE_END_DT], 30)  # we need this correction for a smooth cont.
        api.and_clause = PatternDataProvider.get_and_clause(api.dt_start, api.dt_end)
        api.and_clause_unlimited = PatternDataProvider.get_and_clause(api.dt_start)
        return api

    @staticmethod
    def get_test_case(api: TradeTestApi) -> TradeTestCase:
        # print('\nget_test_case:')
        # api.print_test_api()
        tc = TradeTestCase(api)
        TradeTestCaseFactory.fill_test_data_for_pattern_type(tc)
        return tc

    @staticmethod
    def get_test_case_from_pattern(api: TradeTestApi) -> TradeTestCase:
        tc = TradeTestCase(api)
        TradeTestCaseFactory.fill_test_data_for_pattern(tc, api.pattern, api.tick_list_for_replay)
        return tc

    @staticmethod
    def fill_test_data_for_pattern(tc: TradeTestCase, pattern: Pattern, tick_list_for_replay=None):
        tc.symbol = pattern.ticker_id
        from_date = MyDate.adjust_by_days(pattern.part_entry.date_first, -20)
        if pattern.part_entry.breakout:
            to_date = pattern.part_entry.breakout.tick_previous.date
        else:
            to_date = pattern.part_entry.pattern_range.tick_last.date
        tc.and_clause = "Date BETWEEN '{}' AND '{}'".format(from_date, to_date)
        tc.wave_tick_list = pattern.get_back_testing_wave_ticks(tick_list_for_replay)

    @staticmethod
    def fill_test_data_for_pattern_type(tc: TradeTestCase):
        if tc.pattern_type == FT.TRIANGLE_DOWN:
            TradeTestCaseFactory.fill_test_data_for_triangle_down(tc)
        elif tc.pattern_type == FT.FIBONACCI_DESC:
            TradeTestCaseFactory.fill_test_data_for_fibonacci_desc(tc)

    @staticmethod
    def fill_test_data_for_triangle_down(tc: TradeTestCase):
        tc.symbol = 'ETHUSD'
        tc.and_clause = "Date BETWEEN '2018-03-01' AND '2018-07-05'"
        tc.time_stamp_start = MyDate.get_epoch_seconds_from_datetime('2018-07-05')
        mv = 459807  # mean volume
        base_list = [
            [BT.BREAKOUT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [470, 484, 485, 600], mv],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [470, 480, 470, 300], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450], mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_ADJUST_STOP_LOSS,
             TradeTestCaseFactory.get_sma_values(470, 20000, 0.1, 800), mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_SELL_STOP_LOSS,
             TradeTestCaseFactory.get_sma_values(470, 20000, 0.1, 500), mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [388, 380, 370], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.ACTIVATE_BREAKOUT, [388, 405, 410], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [388, 405, 410, 420], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [388, 380, 370], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450, 400], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [388, 380, 370], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [388, 405, 410, 430, 440, 450, 400], mv],
        ]
        TradeTestCaseFactory.add_volume_data_to_base_list(base_list, tc.api.volume_increase)
        TradeTestCaseFactory.fill_value_list_from_base_list(base_list, tc)

    @staticmethod
    def add_volume_data_to_base_list(base_list: list, percentage: int):
        return_list = []
        for sub_list in base_list:  # e.g. [BT.BREAKOUT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [470, 380, 370]]
            value_list = sub_list[-2]
            mv = sub_list[-1]
            if len(value_list) < 10:
                sub_list[-1] = [int(mv * ((1 + percentage/100)**k)) for k in range(0, len(value_list))]
            else:  # SMA
                sub_list[-1] = [int(mv + k * (mv * percentage / 100)) for k in range(0, len(value_list))]
            return_list.append(sub_list)
        return return_list

    @staticmethod
    def get_sma_values(start_value: float, times: int, increment: float, end_value: float):
        return_list = [start_value]
        value = start_value
        for k in range(0, times):
            value += increment
            return_list.append(round(value,1))
        return_list.append(round(end_value,1))
        return return_list

    @staticmethod
    def fill_test_data_for_fibonacci_desc(tc: TradeTestCase):
        tc.symbol = 'ETHUSD'
        tc.and_clause = "Date BETWEEN '2018-03-01' AND '2018-06-29'"
        tc.time_stamp_start = MyDate.get_epoch_seconds_from_datetime('2018-06-29')
        mv = 459807  # mean volume
        base_list = [
            [BT.BREAKOUT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [470, 484, 485, 600], mv],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [470, 480, 470, 300], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550], mv],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450], mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.FALSE_BREAKOUT, [470, 380, 370], mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_ADJUST_STOP_LOSS, [470, 484, 485, 600], mv],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_SELL_STOP_LOSS, [470, 490, 495, 490, 5050, 510, 530, 300], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.ACTIVATE_BREAKOUT, [406, 410], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [406, 410, 400, 399], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [406, 410, 412, 471, 609, 610], mv],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [406, 410, 400, 399], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [406, 410, 412, 471, 609, 610, 700], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [406, 410, 400, 399], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [406, 410, 412, 471, 609, 610, 700], mv],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500], mv]
        ]
        TradeTestCaseFactory.add_volume_data_to_base_list(base_list, tc.api.volume_increase)
        TradeTestCaseFactory.fill_value_list_from_base_list(base_list, tc)

    @staticmethod
    def fill_value_list_from_base_list(base_list, tc):
        tc.period_seconds = MyDate.get_seconds_for_period_aggregation(PRD.DAILY, 1)
        tc.ticks_per_period = 4
        seconds_per_step = tc.period_seconds/tc.ticks_per_period
        converter = TickerWaveTickConverter(PRD.DAILY, 1, 0, tc.time_stamp_start)
        for entries in base_list:
            if entries[0] == tc.buy_trigger and entries[1] == tc.trade_strategy and entries[2] == tc.test_process:
                value_list = entries[3]
                volume_list = entries[4]
                for index, value in enumerate(value_list):
                    volume = volume_list[index]
                    converter.add_value_with_timestamp(value, tc.time_stamp_start, volume)
                    tc.wave_tick_list.append(converter.current_wave_tick)
                    tc.time_stamp_start += seconds_per_step
