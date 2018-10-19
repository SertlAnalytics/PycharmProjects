"""
Description: This module contains the drop down classes for the tab trades in Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.constants.pattern_constants import BT, TSTR, TP
from pattern_dash.my_dash_components import DropDownHandler


class TDD:  # Trades Drop Down
    TRADE_TYPE = 'Trade_Type'
    BUY_TRIGGER = 'Buy_Trigger'
    TRADE_STRATEGY = 'Trade_Strategy'


class TradeDropDownHandler(DropDownHandler):
    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            TDD.TRADE_TYPE: 'Trade Type',
            TDD.BUY_TRIGGER: 'Buy Trigger',
            TDD.TRADE_STRATEGY: 'Trade Strategy',
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            TDD.TRADE_TYPE: 'my_trade_type_selection',
            TDD.BUY_TRIGGER: 'my_pattern_buy_trigger_selection',
            TDD.TRADE_STRATEGY: 'my_pattern_trade_strategy_selection',
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str, default_value=None) -> str:
        default_dict = {
            TDD.TRADE_TYPE: TP.ONLINE,
            TDD.BUY_TRIGGER: BT.BREAKOUT,
            TDD.TRADE_STRATEGY: TSTR.TRAILING_STOP,
        }
        return default_dict.get(drop_down_type, None)

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            TDD.TRADE_TYPE: 170,
            TDD.BUY_TRIGGER: 170,
            TDD.TRADE_STRATEGY: 170,
        }
        return value_dict.get(drop_down_type, 200)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            TDD.TRADE_TYPE: TP.get_as_list(),
            TDD.BUY_TRIGGER: BT.get_as_list(),
            TDD.TRADE_STRATEGY: TSTR.get_as_list()
        }

    def __get_for_multi__(self, drop_down_type: str):
        return False
