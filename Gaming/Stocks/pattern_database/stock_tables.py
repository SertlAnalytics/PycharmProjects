"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyTable, MyTableColumn, CDT
from sertl_analytics.constants.pattern_constants import DC


class PredictionFeatureTable:
    @staticmethod
    def is_label_column_for_regression(label_column: str):
        return label_column[-4:] == '_PCT'


class TradeTable(MyTable, PredictionFeatureTable):
    def __init__(self):
        MyTable.__init__(self)
        self._feature_columns_for_trades = self.__get_feature_columns_for_trades__()
        self._label_columns_for_trades = self.__get_label_columns_for_trades__()
        self._query_for_feature_and_label_data_for_trades = self.__get_query_for_feature_and_label_data_for_trades__()

    @property
    def feature_columns_for_trades(self):
        return self._feature_columns_for_trades

    @property
    def label_columns_for_trades(self):
        return self._label_columns_for_trades

    @property
    def query_for_feature_and_label_data_for_trades(self):
        return self._query_for_feature_and_label_data_for_trades

    @staticmethod
    def _get_name_():
        return 'Trade'

    @staticmethod
    def get_query_for_unique_record_by_id(id: str) -> str:
        return "SELECT * FROM Trade where ID='{}'".format(id)

    @staticmethod
    def get_query_for_records(where_clause='') -> str:
        return "SELECT * FROM Trade".format(id)

    @staticmethod
    def get_query_for_delete_by_id(trade_id: str) -> str:
        return "DELETE FROM Trade where ID='{}'".format(trade_id)

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.ID, CDT.STRING, 100))

        self._columns.append(MyTableColumn(DC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.PERIOD_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD_AGGREGATION , CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKER_ID, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.TICKER_NAME, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE_ID, CDT.INTEGER)) # 1x = Channel, 2x = Triangle, 3x = TKE, 4x = HS
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_FIRST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_LAST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_END_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_END_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.EXPECTED_WIN, CDT.FLOAT))

        self._columns.append(MyTableColumn(DC.TRADE_READY_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TRADE_STRATEGY, CDT.STRING, 50))
        self._columns.append(MyTableColumn(DC.TRADE_STRATEGY_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_TYPE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_HEIGHT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_OFF_SET, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_MAX_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_LIMIT_ORIG, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_STOP_LOSS_ORIG, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_LIMIT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_STOP_LOSS, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_BOX_STD, CDT.FLOAT))

        self._columns.append(MyTableColumn(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_TOP, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TILL_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_BREAKOUT_DIRECTION, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.FC_BREAKOUT_DIRECTION_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_FALSE_BREAKOUT_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_HALF_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_FULL_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_HALF_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_FULL_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_POSITIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_POSITIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_NEGATIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_NEGATIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_BUY_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.FC_BUY_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.FC_SELL_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.FC_SELL_TIME, CDT.STRING, 10))

        self._columns.append(MyTableColumn(DC.BUY_ORDER_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.BUY_ORDER_TPYE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.BUY_ORDER_TPYE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.BUY_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.BUY_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BUY_AMOUNT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BUY_PRICE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BUY_TOTAL_COSTS, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BUY_TRIGGER, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.BUY_TRIGGER_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.BUY_COMMENT, CDT.STRING, 100))

        self._columns.append(MyTableColumn(DC.SELL_ORDER_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.SELL_ORDER_TPYE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.SELL_ORDER_TPYE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.SELL_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.SELL_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.SELL_AMOUNT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SELL_PRICE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SELL_TOTAL_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SELL_COMMENT, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.SELL_TRIGGER, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.SELL_TRIGGER_ID, CDT.INTEGER))

        self._columns.append(MyTableColumn(DC.TRADE_REACHED_PRICE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_REACHED_PRICE_PCT, CDT.INTEGER))

        self._columns.append(MyTableColumn(DC.TRADE_RESULT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.TRADE_RESULT_ID, CDT.INTEGER))

    @staticmethod
    def __get_feature_columns_for_trades__():
        return [DC.BUY_TRIGGER_ID, DC.TRADE_STRATEGY_ID, DC.TRADE_BOX_TYPE_ID,
                DC.EQUITY_TYPE_ID, DC.PERIOD_ID, DC.PERIOD_AGGREGATION, DC.PATTERN_TYPE_ID]

    @staticmethod
    def __get_label_columns_for_trades__():
        return [DC.TRADE_REACHED_PRICE_PCT, DC.TRADE_RESULT_ID]

    def __get_query_for_feature_and_label_data_for_trades__(self) -> str:
        return "SELECT {} FROM Trade WHERE Trade_Result_ID != 0".format(
            self.__get_concatenated_feature_label_columns_for_trades__())

    def __get_concatenated_feature_label_columns_for_trades__(self):
        return ', '.join(self._feature_columns_for_trades + self._label_columns_for_trades)


class FeaturesTable(MyTable, PredictionFeatureTable):
    def __init__(self):
        MyTable.__init__(self)
        self._feature_columns_touch_points = self.__get_feature_columns_touch_points__()
        self._feature_columns_before_breakout = self.__get_feature_columns_before_breakout__()
        self._feature_columns_after_breakout = self.__get_feature_columns_after_breakout__()
        self._label_columns_touch_points = self.__get_label_columns_touch_points__()
        self._label_columns_before_breakout = self.__get_label_columns_before_breakout__()
        self._label_columns_after_breakout = self.__get_label_columns_after_breakout__()
        self._query_for_feature_and_label_data_touch_points = \
            self.__get_query_for_feature_and_label_data_touch_points__()
        self._query_for_feature_and_label_data_before_breakout = \
            self.__get_query_for_feature_and_label_data_before_breakout__()
        self._query_for_feature_and_label_data_after_breakout = \
            self.__get_query_for_feature_and_label_data_after_breakout__()

    @staticmethod
    def get_query_for_unique_record_by_id(id: str) -> str:
        return "SELECT * FROM Features where ID='{}'".format(id)

    @staticmethod
    def get_query_for_records(where_clause='') -> str:
        return "SELECT * FROM Features".format(id)

    @property
    def feature_columns_touch_points(self):
        return self._feature_columns_touch_points

    @property
    def features_columns_before_breakout(self):
        return self._feature_columns_before_breakout

    @property
    def features_columns_after_breakout(self):
        return self._feature_columns_after_breakout

    @property
    def label_columns_touch_points(self):
        return self._label_columns_touch_points

    @property
    def label_columns_before_breakout(self):
        return self._label_columns_before_breakout

    @property
    def label_columns_after_breakout(self):
        return self._label_columns_after_breakout

    @property
    def query_for_feature_and_label_data_touch_points(self):
        return self._query_for_feature_and_label_data_touch_points

    @property
    def query_for_feature_and_label_data_before_breakout(self):
        return self._query_for_feature_and_label_data_before_breakout

    @property
    def query_for_feature_and_label_data_after_breakout(self):
        return self._query_for_feature_and_label_data_after_breakout

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.ID, CDT.STRING, 50))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.PERIOD_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD_AGGREGATION , CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKER_ID, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.TICKER_NAME, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.PATTERN_TYPE_ID, CDT.INTEGER)) # 1x = Channel, 2x = Triangle, 3x = TKE, 4x = HS
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_FIRST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TS_PATTERN_TICK_LAST, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TS_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_TILL_PATTERN_FORMED, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.BREAKOUT_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_END_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_END_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_TOLERANCE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BREAKOUT_RANGE_MIN_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_LOW, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_BEGIN_HIGH, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_END_LOW, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PATTERN_END_HIGH, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_UPPER_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_LOWER_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_REGRESSION_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_BREAKOUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_VOLUME_REGRESSION_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.BREAKOUT_DIRECTION_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_HALF_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_FULL_POSITIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.NEXT_PERIOD_FULL_NEGATIVE_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.AVAILABLE_FIBONACCI_TYPE, CDT.STRING, 10))  # MIN, MAX
        self._columns.append(MyTableColumn(DC.AVAILABLE_FIBONACCI_TYPE_ID, CDT.INTEGER))  # 0=No, -1=MIN, 1 = MAX
        self._columns.append(MyTableColumn(DC.EXPECTED_WIN, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FALSE_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.EXPECTED_WIN_REACHED, CDT.INTEGER))

        self._columns.append(MyTableColumn(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_TOP, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TILL_BREAKOUT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_BREAKOUT_DIRECTION_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_BREAKOUT_DIRECTION, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.FC_FALSE_BREAKOUT_ID, CDT.INTEGER))

        self._columns.append(MyTableColumn(DC.FC_HALF_POSITIVE_PCT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_FULL_POSITIVE_PCT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_HALF_NEGATIVE_PCT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_FULL_NEGATIVE_PCT, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_POSITIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_POSITIVE_FULL, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_NEGATIVE_HALF, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_TICKS_TO_NEGATIVE_FULL, CDT.INTEGER))

    @staticmethod
    def _get_name_():
        return 'Features'

    def __get_query_for_feature_and_label_data_touch_points__(self) -> str:
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_touch_points__())

    def __get_query_for_feature_and_label_data_before_breakout__(self) -> str:
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_before_breakout__())

    def __get_query_for_feature_and_label_data_after_breakout__(self):
        return "SELECT {} FROM Features".format(self.__get_concatenated_feature_label_columns_after_breakout__())

    def __get_concatenated_feature_label_columns_touch_points__(self):
        return ', '.join(self._feature_columns_touch_points + self._label_columns_touch_points)

    def __get_concatenated_feature_label_columns_before_breakout__(self):
        return ', '.join(self._feature_columns_before_breakout + self._label_columns_before_breakout)

    def __get_concatenated_feature_label_columns_after_breakout__(self):
        return ', '.join(self._feature_columns_after_breakout + self._label_columns_after_breakout)

    @staticmethod
    def __get_feature_columns_after_breakout__():
        return [DC.EQUITY_TYPE_ID, DC.PERIOD_ID, DC.PERIOD_AGGREGATION, DC.PATTERN_TYPE_ID,
                DC.TICKS_TILL_PATTERN_FORMED, DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT,
                DC.SLOPE_UPPER_PCT, DC.SLOPE_LOWER_PCT, DC.SLOPE_REGRESSION_PCT,
                DC.SLOPE_BREAKOUT_PCT,
                DC.SLOPE_VOLUME_REGRESSION_PCT,
                DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM,
                DC.BREAKOUT_DIRECTION_ID, DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT,
                DC.AVAILABLE_FIBONACCI_TYPE_ID]

    @staticmethod
    def __get_feature_columns_before_breakout__():
        base_list = FeaturesTable.__get_feature_columns_after_breakout__()
        del base_list[base_list.index(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT)]
        del base_list[base_list.index(DC.BREAKOUT_DIRECTION_ID)]
        del base_list[base_list.index(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT)]
        del base_list[base_list.index(DC.SLOPE_BREAKOUT_PCT)]
        del base_list[base_list.index(DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT)]
        return base_list

    @staticmethod
    def __get_feature_columns_touch_points__():
        base_list = FeaturesTable.__get_feature_columns_before_breakout__()
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP)]
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM)]
        return base_list

    @staticmethod
    def __get_label_columns_after_breakout__():
        return [DC.NEXT_PERIOD_HALF_POSITIVE_PCT, DC.NEXT_PERIOD_FULL_POSITIVE_PCT,
                DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, DC.NEXT_PERIOD_FULL_NEGATIVE_PCT,
                DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL,
                DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL,
                DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_before_breakout__():
        return [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, DC.BREAKOUT_DIRECTION_ID, DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_touch_points__():
        return [DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]

