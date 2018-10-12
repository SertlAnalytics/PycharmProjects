"""
Description: This module contains the drop down classes for Dash.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from pattern_database.stock_tables import TradeTable, PatternTable
from sertl_analytics.constants.pattern_constants import DC, CHT, FT, PRED
from pattern_dash.my_dash_components import DropDownHandler


class DDT:  # Drop Down Types
    CHART_TYPE = 'Chart_Type'
    PREDICTOR = 'Predictor'
    CATEGORY = 'Category'
    X_VARIABLE = 'x_variable'
    Y_VARIABLE = 'y_variable'
    CHART_TEXT_VARIABLE = 'Chart_text_variable'
    PATTERN_TYPE = 'Pattern_Type'


class StatisticsDropDownHandler(DropDownHandler):
    def __get_div_text__(self, drop_down_type: str):
        value_dict = {
            DDT.CHART_TYPE: 'Chart Type',
            DDT.CATEGORY: 'Category',
            DDT.PREDICTOR: 'Predictor',
            DDT.X_VARIABLE: 'x-variable',
            DDT.Y_VARIABLE: 'y-variable',
            DDT.CHART_TEXT_VARIABLE: 'Chart Text',
            DDT.PATTERN_TYPE: 'Pattern Type'
        }
        return value_dict.get(drop_down_type, None)

    def __get_element_id__(self, drop_down_type: str):
        pass

    def __get_default_value__(self, drop_down_type: str) -> str:
        pass

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            DDT.CHART_TYPE: 190,
            DDT.PREDICTOR: 150,
            DDT.CATEGORY: 150,
            DDT.X_VARIABLE: 260,
            DDT.Y_VARIABLE: 220,
            DDT.CHART_TEXT_VARIABLE: 140,
            DDT.PATTERN_TYPE: 200
        }
        return value_dict.get(drop_down_type, 200)

    def __get_drop_down_value_dict__(self) -> dict:
        pass

    def __get_for_multi__(self, drop_down_type: str):
        return False


class TradeStatisticsDropDownHandler(StatisticsDropDownHandler):
    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            DDT.CHART_TYPE: 'my_trade_statistics_chart_type_selection',
            DDT.PREDICTOR: 'my_trade_statistics_predictor_selection',
            DDT.CATEGORY: 'my_trade_statistics_category_selection',
            DDT.X_VARIABLE: 'my_trade_statistics_x_variable_selection',
            DDT.Y_VARIABLE: 'my_trade_statistics_y_variable_selection',
            DDT.CHART_TEXT_VARIABLE: 'my_trade_statistics_text_variable_selection',
            DDT.PATTERN_TYPE: 'my_trade_statistics_pattern_type_selection'
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str) -> str:
        default_dict = {
            DDT.CHART_TYPE: CHT.AREA_WINNER_LOSER,
            DDT.PREDICTOR: PRED.FOR_TRADE,
            DDT.CATEGORY: DC.PATTERN_TYPE,
            DDT.X_VARIABLE: DC.PATTERN_RANGE_BEGIN_DT,
            DDT.Y_VARIABLE: DC.TRADE_RESULT,
            DDT.CHART_TEXT_VARIABLE: DC.TRADE_STRATEGY,
            DDT.PATTERN_TYPE: FT.ALL
        }
        return default_dict.get(drop_down_type, None)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            DDT.CHART_TYPE: CHT.get_for_trade_statistics(),
            DDT.PREDICTOR: PRED.get_for_trade_all(),
            DDT.CATEGORY: TradeTable.get_columns_for_statistics_category(),
            DDT.X_VARIABLE: TradeTable.get_columns_for_statistics_x_variable(),
            DDT.Y_VARIABLE: TradeTable.get_columns_for_statistics_y_variable(),
            DDT.CHART_TEXT_VARIABLE: TradeTable.get_columns_for_statistics_text_variable(),
            DDT.PATTERN_TYPE: FT.get_all_for_statistics()
        }

    def __get_for_multi__(self, drop_down_type: str):
        return False if drop_down_type == DDT.PATTERN_TYPE else False


class PatternStatisticsDropDownHandler(StatisticsDropDownHandler):
    def __get_element_id__(self, drop_down_type: str):
        value_dict = {
            DDT.CHART_TYPE: 'my_pattern_statistics_chart_type_selection',
            DDT.PREDICTOR: 'my_pattern_statistics_predictor_selection',
            DDT.CATEGORY: 'my_pattern_statistics_category_selection',
            DDT.X_VARIABLE: 'my_pattern_statistics_x_variable_selection',
            DDT.Y_VARIABLE: 'my_pattern_statistics_y_variable_selection',
            DDT.CHART_TEXT_VARIABLE: 'my_pattern_statistics_text_variable_selection',
            DDT.PATTERN_TYPE: 'my_pattern_statistics_pattern_type_selection'
        }
        return value_dict.get(drop_down_type, None)

    def __get_default_value__(self, drop_down_type: str) -> str:
        default_dict = {
            DDT.CHART_TYPE: CHT.AREA_WINNER_LOSER,
            DDT.PREDICTOR: PRED.TOUCH_POINT,
            DDT.CATEGORY: DC.PATTERN_TYPE,
            DDT.X_VARIABLE: DC.PATTERN_BEGIN_DT,
            DDT.Y_VARIABLE: DC.EXPECTED_WIN_REACHED,
            DDT.CHART_TEXT_VARIABLE: DC.PATTERN_TYPE,
            DDT.PATTERN_TYPE: FT.ALL
        }
        return default_dict.get(drop_down_type, None)

    def __get_drop_down_value_dict__(self) -> dict:
        return {
            DDT.CHART_TYPE: CHT.get_for_pattern_statistics(),
            DDT.PREDICTOR: PRED.get_for_pattern_all(),
            DDT.CATEGORY: PatternTable.get_columns_for_statistics_category(),
            DDT.X_VARIABLE: PatternTable.get_columns_for_statistics_x_variable(),
            DDT.Y_VARIABLE: PatternTable.get_columns_for_statistics_y_variable(),
            DDT.CHART_TEXT_VARIABLE: PatternTable.get_columns_for_statistics_text_variable(),
            DDT.PATTERN_TYPE: FT.get_all_for_statistics()
        }

    def __get_width__(self, drop_down_type: str):
        value_dict = {
            DDT.CHART_TYPE: 190,
            DDT.PREDICTOR: 150,
            DDT.CATEGORY: 220,
            DDT.X_VARIABLE: 260,
            DDT.Y_VARIABLE: 220,
            DDT.CHART_TEXT_VARIABLE: 140,
            DDT.PATTERN_TYPE: 200
        }
        return value_dict.get(drop_down_type, 200)

    def __get_for_multi__(self, drop_down_type: str):
        return False if drop_down_type == DDT.PATTERN_TYPE else False