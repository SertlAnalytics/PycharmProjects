"""
Description: This module contains the constants used mainly for pattern detections - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

class CM:  # coverage mode
    COVERING = 'covering'
    COVERED_BY = 'covered_by'
    NONE = 'NONE'


class DIR:
    UP = 'UP'
    DOWN = 'DOWN'


class FR:  # Fibonnaci Retracements
    R_100 = 1.000
    R_764 = 0.764
    R_618 = 0.618
    R_500 = 0.500
    R_382 = 0.382
    R_236 = 0.236
    R_000 = 0.000


class FT:
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    TRIANGLE_TOP = 'Triangle top'
    TRIANGLE_BOTTOM = 'Triangle bottom'
    TRIANGLE_UP = 'Triangle up'
    TRIANGLE_DOWN = 'Triangle down'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp
    CHANNEL_UP = 'Channel up'
    CHANNEL_DOWN = 'Channel down'
    TKE_DOWN = 'TKE down'  # Trend correction extrema
    TKE_UP = 'TKE up'  # Trend correction extrema
    HEAD_SHOULDER = 'Head-Shoulder'
    HEAD_SHOULDER_BOTTOM = 'Head-Shoulder-Bottom'
    ALL = 'All'

    @staticmethod
    def get_all():
        return [FT.TRIANGLE, FT.TRIANGLE_TOP, FT.TRIANGLE_BOTTOM, FT.TRIANGLE_UP, FT.TRIANGLE_DOWN, FT.CHANNEL,
                FT.CHANNEL_UP, FT.CHANNEL_DOWN, FT.TKE_UP, FT.TKE_DOWN, FT.HEAD_SHOULDER, FT.HEAD_SHOULDER_BOTTOM]

    @staticmethod
    def get_type_id(pattern_type: str):
        type_dict = {FT.CHANNEL: 10, FT.CHANNEL_UP: 11, FT.CHANNEL_DOWN: 12,
                     FT.TRIANGLE: 20, FT.TRIANGLE_UP: 21, FT.TRIANGLE_DOWN: 22,
                     FT.TRIANGLE_TOP: 23, FT.TRIANGLE_BOTTOM: 24,
                     FT.TKE_UP: 31, FT.TKE_DOWN: 32,
                     FT.HEAD_SHOULDER: 43, FT.HEAD_SHOULDER_BOTTOM: 44}
        return type_dict.get(pattern_type, 0)


class Indices:
    DOW_JONES = 'Dow Jones'
    NASDAQ100 = 'Nasdaq 100'
    NASDAQ = 'Nasdaq (all)'
    SP500 = 'S&P 500'
    MIXED = 'Mixed'
    CRYPTO_CCY = 'Crypto Currencies'
    ALL_DATABASE = 'All in database'
    ALL = 'All'


class FD:
    NONE = 'NONE'
    HOR = 'horizontal'
    ASC = 'ascending'
    DESC = 'descending'


class TT:  # Tick types
    NONE = 'NONE'
    DOJI = 'Doji'


class FCC:  # Formation Condition Columns
    BREAKOUT_WITH_BUY_SIGNAL = 'breakout had a buy signal'
    PREVIOUS_PERIOD_CHECK_OK = 'previous period check OK'  # eg. CN.LOW
    COMBINED_PARTS_APPLICABLE = 'combined parts are formation applicable'


class CN:  # Column Names
    PERIOD = 'Period'
    AGGREGATION = 'Aggregation'
    SYMBOL = 'Symbol'
    DIRECTION = 'Direction'
    BIG_MOVE = 'BigMove'
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
    CLOSE = 'Close'
    MEAN_HL = 'MeanHL'
    VOL = 'Volume'
    DATE = 'Date'
    TIME = 'Time'
    DATETIME = 'Datetime'
    TIMESTAMP = 'Timestamp'
    DATEASNUM = 'DateAsNumber'
    POSITION = 'Position'
    TICKS_BREAK_HIGH_BEFORE = 'BREAK_HIGH_BEFORE'
    TICKS_BREAK_HIGH_AFTER = 'BREAK_HIGH_AFTER'
    TICKS_BREAK_LOW_BEFORE = 'BREAK_LOW_BEFORE'
    TICKS_BREAK_LOW_AFTER = 'BREAK_LOW_AFTER'
    GLOBAL_MIN = 'G_MIN'
    GLOBAL_MAX = 'G_MAX'
    LOCAL_MIN = 'L_MIN'
    LOCAL_MAX = 'L_MAX'
    F_UPPER = 'F_UPPER'
    F_LOWER = 'F_LOWER'
    H_UPPER = 'H_UPPER'
    H_LOWER = 'H_LOWER'
    IS_MIN = 'Is_MIN'
    IS_MAX = 'Is_MAX'


class ValueCategories:
    pass


class SVC(ValueCategories):  # Stock value categories:
    U_out = 'Upper_out'
    U_in = 'Upper_in'
    U_on = 'Upper_on'
    M_in = 'Middle_in'
    L_in = 'Low_in'
    L_on = 'Low_on'
    L_out = 'Low_out'
    H_in = 'Helper_in'
    H_on = 'Helper_on'
    H_U_out = 'Helper_Upper_out'
    H_U_in = 'Helper_Upper_in'
    H_U_on = 'Helper_Upper_on'
    H_M_in = 'Helper_Middle_in'
    H_L_in = 'Helper_Low_in'
    H_L_on = 'Helper_Low_on'
    H_L_out = 'Helper_Low_out'

    NONE = 'NONE'


class CT:  # Constraint types
    F_UPPER = 'f_upper_percentage'
    F_LOWER = 'f_lower_percentage'
    F_REGRESSION = 'f_regression_percentage'
    REL_HEIGHTS = 'relation_height_end_start'
    ALL_IN = 'All_In'
    COUNT = 'Count'
    SERIES = 'Series'


class PSC:  # Pattern Statistics Columns
    C_BOUND_UPPER_VALUE = 'conf.bound_upper_value'  # eg. CN.HIGH
    C_BOUND_LOWER_VALUE = 'conf.bound_lower_value'  # eg. CN.LOW
    C_CHECK_PREVIOUS_PERIOD = 'conf.check_previous_period'
    C_BREAKOUT_OVER_CONGESTION = 'conf.breakout_over_congestion_range'
    C_TOLERANCE_PCT = 'conf.tolerance in %'
    C_BREAKOUT_RANGE_PCT = 'conf.breakout range in %'
    C_AND_CLAUSE = 'conf.and clause'

    CON_PREVIOUS_PERIOD_CHECK_OK = FCC.PREVIOUS_PERIOD_CHECK_OK
    CON_COMBINED_PARTS_APPLICABLE = FCC.COMBINED_PARTS_APPLICABLE
    CON_BREAKOUT_WITH_BUY_SIGNAL = FCC.BREAKOUT_WITH_BUY_SIGNAL

    NUMBER = 'Number'
    STATUS = 'Status'
    TICKER = 'Ticker'
    NAME = 'Name'
    PATTERN = 'Pattern'
    BEGIN_PREVIOUS = 'Begin previous period'
    BEGIN = 'Begin'
    END = 'End'
    LOWER = 'Lower'
    UPPER = 'Upper'
    SLOPE_UPPER = 'Slope_upper'
    SLOPE_LOWER = 'Slope_lower'
    SLOPE_RELATION = 'Slope_relation'
    TICKS = 'Ticks'
    BREAKOUT_DATE = 'Breakout date'
    BREAKOUT_DIRECTION = 'Breakout direction'
    VOLUME_CHANGE = 'Volume change'
    EXPECTED = 'Expected'
    RESULT = 'Result'
    EXT = 'Extended'
    VAL = 'Validated'
    BOUGHT_AT = 'Bought at'
    SOLD_AT = 'Sold at'
    BOUGHT_ON = 'Bought on'
    SOLD_ON = 'Sold on'
    T_NEEDED = 'Ticks needed'
    LIMIT = 'Limit'
    STOP_LOSS_AT = 'Stop loss at'
    STOP_LOSS_TRIGGERED = 'Stop loss triggered'
    RESULT_DF_MAX = 'Result DF max.'
    RESULT_DF_MIN = 'Result DF min.'
    FIRST_LIMIT_REACHED = 'First limit reached'
    STOP_LOSS_MAX_REACHED = 'Max stop loss reached (bound of original range)'


class PFC:  # Pattern Feature Columns
    TICKER_ID = 'Ticker_Id'
    TICKER_NAME = 'Ticker_Name'
    PATTERN_TYPE = 'Pattern_Type'
    PATTERN_TYPE_ID = 'Pattern_Type_ID'
    TS_PATTERN_TICK_FIRST = 'Timestamp_Pattern_Tick_First'
    TS_PATTERN_TICK_LAST = 'Timestamp_Pattern_Tick_Last'
    TS_BREAKOUT = 'Timestamp_Breakout'
    TICKS_TILL_PATTERN_FORMED = 'Ticks_Till_Pattern_Formed'
    TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT = 'Ticks_From_Pattern_Formed_Till_Breakout'
    DT_BEGIN = 'Begin_Date'
    TIME_BEGIN = 'Begin_Time'
    DT_END = 'End_Date'
    TIME_END = 'END_Time'
    TOLERANCE_PCT = 'Tolerance in %'
    BREAKOUT_RANGE_MIN_PCT = 'Breakout range in %'
    BEGIN_LOW = 'Value_Begin_Low'
    BEGIN_HIGH = 'Value_Begin_High'
    END_LOW = 'Value_End_Low'
    END_HIGH = 'Value_End_High'
    SLOPE_UPPER = 'Slope_Upper'
    SLOPE_LOWER = 'Slope_Lower'
    SLOPE_REGRESSION = 'Slope_Regression'
    SLOPE_BREAKOUT = 'Slope_Breakout'
    TOUCH_POINTS_TILL_BREAKOUT_HIGH = 'Touch_Points_High_Till_Breakout'
    TOUCH_POINTS_TILL_BREAKOUT_LOW= 'Touch_Points_Low_Till_Breakout'
    BREAKOUT_DIRECTION = 'Breakout_direction'
    VOLUME_CHANGE_AT_BREAKOUT_PCT = 'Volume_Change_At_Breakout_in_Percentage'
    SLOPE_VOLUME_REGRESSION = 'Slope_Volume_Regression'
    SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED = 'Slope_Volume_Regression_After_Pattern_Formed'
    PREVIOUS_PERIOD_HALF_UPPER_PCT = 'Max_Value_Percentage_Previous_Period_Half'
    PREVIOUS_PERIOD_FULL_UPPER_PCT = 'Max_Value_Percentage_Previous_Period_Full'
    PREVIOUS_PERIOD_HALF_LOWER_PCT = 'Min_Value_Percentage_Previous_Period_Half'
    PREVIOUS_PERIOD_FULL_LOWER_PCT = 'Min_Value_Percentage_Previous_Period_Full'
    NEXT_PERIOD_HALF_POSITIVE_PCT = 'Next_Period_Half_Positive_Percentage'
    NEXT_PERIOD_FULL_POSITIVE_PCT= 'Next_Period_Full_Positive_Percentage'
    NEXT_PERIOD_HALF_NEGATIVE_PCT= 'Next_Period_Half_Negative_Percentage'
    NEXT_PERIOD_FULL_NEGATIVE_PCT= 'Next_Period_Full_Negative_Percentage'
    TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF = 'Ticks_From_Breakout_Till_Positive_Half'
    TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL = 'Ticks_From_Breakout_Till_Positive_Full'
    TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF = 'Ticks_From_Breakout_Till_Negative_Half'
    TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL = 'Ticks_From_Breakout_Till_Negative_Full'
    AVAILABLE_FIBONACCI_END = 'Available_Fibonacci_End'  # 0 = No, 1 = Min, 2 = Max
    EXPECTED_WIN = 'Expected_Win'
    FALSE_BREAKOUT = 'False_Breakout'
    EXPECTED_WIN_REACHED = 'Expected_Win_Reached'

    @staticmethod
    def get_all():
        return_list = [PFC.TICKER_ID]
        return_list.append(PFC.TICKER_NAME)
        return_list.append(PFC.PATTERN_TYPE)
        return_list.append(PFC.TS_PATTERN_TICK_FIRST)
        return_list.append(PFC.TS_PATTERN_TICK_LAST)
        return_list.append(PFC.TS_BREAKOUT)
        return_list.append(PFC.TICKS_TILL_PATTERN_FORMED)
        return_list.append(PFC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT)
        return_list.append(PFC.DT_BEGIN)
        return_list.append(PFC.DT_END)
        return_list.append(PFC.TOLERANCE_PCT)
        return_list.append(PFC.BREAKOUT_RANGE_MIN_PCT)
        return_list.append(PFC.BEGIN_LOW)
        return_list.append(PFC.BEGIN_HIGH)
        return_list.append(PFC.END_LOW)
        return_list.append(PFC.END_HIGH)
        return_list.append(PFC.SLOPE_UPPER)
        return_list.append(PFC.SLOPE_LOWER)
        return_list.append(PFC.SLOPE_REGRESSION)
        return_list.append(PFC.SLOPE_BREAKOUT)
        return_list.append(PFC.TOUCH_POINTS_TILL_BREAKOUT_HIGH)
        return_list.append(PFC.TOUCH_POINTS_TILL_BREAKOUT_LOW)
        return_list.append(PFC.BREAKOUT_DIRECTION)
        return_list.append(PFC.VOLUME_CHANGE_AT_BREAKOUT_PCT)
        return_list.append(PFC.SLOPE_VOLUME_REGRESSION)
        return_list.append(PFC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED)
        return_list.append(PFC.MAX_VALUE_PREVIOUS_PERIOD_HALF_PCT)
        return_list.append(PFC.MAX_VALUE_PREVIOUS_PERIOD_FULL_PCT)
        return_list.append(PFC.MIN_VALUE_PREVIOUS_PERIOD_HALF_PCT)
        return_list.append(PFC.MIN_VALUE_PREVIOUS_PERIOD_FULL_PCT)
        return_list.append(PFC.MAX_VALUE_NEXT_PERIOD_HALF_PCT)
        return_list.append(PFC.MAX_VALUE_NEXT_PERIOD_FULL_PCT)
        return_list.append(PFC.MIN_VALUE_NEXT_PERIOD_HALF_PCT)
        return_list.append(PFC.MIN_VALUE_NEXT_PERIOD_FULL_PCT)
        return_list.append(PFC.TICKS_FROM_BREAKOUT_TILL_MAX_HALF)
        return_list.append(PFC.TICKS_FROM_BREAKOUT_TILL_MIN_HALF)
        return_list.append(PFC.TICKS_FROM_BREAKOUT_TILL_MAX_FULL)
        return_list.append(PFC.TICKS_FROM_BREAKOUT_TILL_MIN_HALF)
        return_list.append(PFC.AVAILABLE_FIBONACCI_END)
        return_list.append(PFC.EXPECTED_WIN)
        return_list.append(PFC.FALSE_BREAKOUT)
        return_list.append(PFC.EXPECTED_WIN_REACHED)
        return return_list
