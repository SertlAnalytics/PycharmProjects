"""
Description: This module contains the test cases for Bitfinex trading tests
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import FT, BT, TSTR, TTC


class TradeTestCase:
    def __init__(self):
        self.pattern_type = ''
        self.buy_trigger = ''
        self.trade_strategy = ''
        self.test_process = ''
        self.symbol = ''
        self.and_clause = ''
        self.value_list = []


class BitfinexTestCaseFactory:
    @staticmethod
    def get_test_case(pattern_type: str, buy_trigger, trade_strategy: str, test_process: str) -> TradeTestCase:
        tc = TradeTestCase()
        tc.pattern_type = pattern_type
        tc.buy_trigger = buy_trigger
        tc.trade_strategy = trade_strategy
        tc.test_process = test_process
        BitfinexTestCaseFactory.__fill_test_data_for_pattern_type__(tc)
        return tc

    @staticmethod
    def __fill_test_data_for_pattern_type__(tc: TradeTestCase):
        if tc.pattern_type == FT.TRIANGLE_DOWN:
            BitfinexTestCaseFactory.fill_test_data_for_triangle_down(tc)
        elif tc.pattern_type == FT.FIBONACCI_DESC:
            BitfinexTestCaseFactory.fill_test_data_for_fibonacci_desc(tc)

    @staticmethod
    def fill_test_data_for_triangle_down(tc: TradeTestCase):
        tc.symbol = 'ETH_USD'
        tc.and_clause = "Date BETWEEN '2018-03-01' AND '2018-07-05'"
        base_list = [
            [BT.BREAKOUT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [470, 484, 485, 600]],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [470, 480, 470, 300]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450]],
            [BT.BREAKOUT, TSTR.SMA, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_ADJUST_STOP_LOSS, BitfinexTestCaseFactory.get_sma_values(470, 20000, 0.1, 800)],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_SELL_STOP_LOSS, BitfinexTestCaseFactory.get_sma_values(470, 20000, 0.1, 500)],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [388, 380, 370]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.ACTIVATE_BREAKOUT, [388, 405, 410]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [388, 405, 410, 420]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [388, 380, 370]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450, 400]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [388, 380, 370]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [388, 405, 410, 420, 430, 440, 450]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [388, 405, 410, 430, 440, 450, 400]],
        ]
        BitfinexTestCaseFactory.fill_value_list_from_base_list(base_list, tc)

    @staticmethod
    def get_sma_values(start_value: float, times: int, increment: float, end_value: float):
        return_list = [start_value]
        value = start_value
        for k in range(0, times):
            value += increment
            return_list.append(value)
        return_list.append(end_value)
        return return_list

    @staticmethod
    def fill_test_data_for_fibonacci_desc(tc: TradeTestCase):
        tc.symbol = 'ETH_USD'
        tc.and_clause = "Date BETWEEN '2018-03-01' AND '2018-06-29'"
        base_list = [
            [BT.BREAKOUT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [470, 484, 485, 600]],
            [BT.BREAKOUT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [470, 480, 470, 300]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550]],
            [BT.BREAKOUT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [470, 480, 490, 520, 530, 550]],
            [BT.BREAKOUT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [470, 480, 500, 550, 450]],
            [BT.BREAKOUT, TSTR.SMA, TTC.FALSE_BREAKOUT, [470, 380, 370]],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_ADJUST_STOP_LOSS, [470, 484, 485, 600]],
            [BT.BREAKOUT, TSTR.SMA, TTC.BUY_SELL_STOP_LOSS, [470, 490, 495, 490, 5050, 510, 530, 300]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.ACTIVATE_BREAKOUT, [406, 410]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.FALSE_BREAKOUT, [406, 410, 400, 399]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_LIMIT, [406, 410, 412, 471, 609, 610]],
            [BT.TOUCH_POINT, TSTR.LIMIT, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.FALSE_BREAKOUT, [406, 410, 400, 399]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_ADJUST_STOP_LOSS, [406, 410, 412, 471, 609, 610, 700]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STOP, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.FALSE_BREAKOUT, [406, 410, 400, 399]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_ADJUST_STOP_LOSS, [406, 410, 412, 471, 609, 610, 700]],
            [BT.TOUCH_POINT, TSTR.TRAILING_STEPPED_STOP, TTC.BUY_SELL_STOP_LOSS, [406, 410, 412, 471, 609, 500]],
        ]
        BitfinexTestCaseFactory.fill_value_list_from_base_list(base_list, tc)

    @staticmethod
    def fill_value_list_from_base_list(base_list, tc):
        for entries in base_list:
            if entries[0] == tc.buy_trigger and entries[1] == tc.trade_strategy and entries[2] == tc.test_process:
                tc.value_list = entries[3]