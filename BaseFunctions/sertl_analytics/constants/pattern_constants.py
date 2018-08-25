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


class EXTREMA:
    MIN = 'MIN'
    MAX = 'MAX'

    @staticmethod
    def get_id(key: str) -> int:
        return int({EXTREMA.MIN: -1, EXTREMA.MAX: 1}.get(key, 0))

class DIR:
    UP = 'UP'
    DOWN = 'DOWN'

    @staticmethod
    def get_id(key: str):
        return {DIR.UP: 1, DIR.DOWN: -1}.get(key)

class FR:  # Fibonnaci Retracements
    R_100 = 1.000
    R_764 = 0.764
    R_618 = 0.618
    R_500 = 0.500
    R_382 = 0.382
    R_236 = 0.236
    R_000 = 0.000


class EQUITY_TYPE:
    NONE = 'None'
    SHARE = 'Shares'
    COMMODITY = 'Commodity'
    CRYPTO = 'Crypto_Currencies'

    @staticmethod
    def get_id(key: str):
        return {EQUITY_TYPE.SHARE: 1, EQUITY_TYPE.COMMODITY: 10, EQUITY_TYPE.CRYPTO: 20}.get(key)


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
    def get_id(key: str):
        return {FT.CHANNEL: 10, FT.CHANNEL_UP: 11, FT.CHANNEL_DOWN: 12,
                FT.TRIANGLE: 20, FT.TRIANGLE_UP: 21, FT.TRIANGLE_DOWN: 22,
                FT.TRIANGLE_TOP: 23, FT.TRIANGLE_BOTTOM: 24,
                FT.TKE_UP: 31, FT.TKE_DOWN: 32,
                FT.HEAD_SHOULDER: 43, FT.HEAD_SHOULDER_BOTTOM: 44}.get(key, 0)


class PT:  # PredictorType
    TOUCH_POINTS = 'touch_points'
    BEFORE_BREAKOUT = 'before_breakout'
    AFTER_BREAKOUT = 'after_breakout'

    def get_id(key: str):
        return {PT.TOUCH_POINTS: 1, PT.BEFORE_BREAKOUT: 2, PT.AFTER_BREAKOUT: 3}.get(key)


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

    def get_id(key: str):
        return {FD.DESC: -1, FD.HOR: 0, FD.ASC: 1}.get(key)


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


class DC:  # Data Columns
    EQUITY_TYPE = 'Equity_Type'  # Share, Commodities, Crypto Currency
    EQUITY_TYPE_ID = 'Equity_Type_ID'  # Share, Commodities, Crypto Currency
    PERIOD = 'Period'  # Daily, Intraday (min)
    PERIOD_ID = 'Period_ID'  # Intraday = 0, Daily = 1, Weekly = 2, Monthly = 3, Intraday (min)
    PERIOD_AGGREGATION = 'Aggregation'
    TICKER_ID = 'Ticker_Id'
    TICKER_NAME = 'Ticker_Name'
    PATTERN_TYPE = 'Pattern_Type'
    PATTERN_TYPE_ID = 'Pattern_Type_ID'
    TS_PATTERN_TICK_FIRST = 'Timestamp_Pattern_Tick_First'
    TS_PATTERN_TICK_LAST = 'Timestamp_Pattern_Tick_Last'
    TS_BREAKOUT = 'Timestamp_Breakout'
    TICKS_TILL_PATTERN_FORMED = 'Ticks_Till_Pattern_Formed'
    TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT = 'Ticks_From_Pattern_Formed_Till_Breakout'
    PATTERN_BEGIN_DT = 'Pattern_Begin_Date'
    PATTERN_BEGIN_TIME = 'Pattern_Begin_Time'
    BREAKOUT_DT = 'Breakout_Date'
    BREAKOUT_TIME = 'Breakout_Time'
    PATTERN_END_DT = 'Pattern_End_Date'
    PATTERN_END_TIME = 'Pattern_End_Time'
    PATTERN_TOLERANCE_PCT = 'Patern_Tolerance_PCT'
    BREAKOUT_RANGE_MIN_PCT = 'Breakout_Range_Min_PCT'
    PATTERN_BEGIN_LOW = 'Pattern_Begin_Low'
    PATTERN_BEGIN_HIGH = 'Pattern_Begin_High'
    PATTERN_END_LOW = 'Pattern_End_Low'
    PATTERN_END_HIGH = 'Pattern_End_High'
    SLOPE_UPPER_PCT = 'Slope_Upper_PCT'
    SLOPE_LOWER_PCT = 'Slope_Lower_PCT'
    SLOPE_REGRESSION_PCT = 'Slope_Regression_PCT'
    SLOPE_VOLUME_REGRESSION_PCT = 'Slope_Volume_Regression_PCT'
    SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT = 'Slope_Volume_Regression_After_Pattern_Formed_PCT'
    SLOPE_BREAKOUT_PCT = 'Slope_Breakout_PCT'
    TOUCH_POINTS_TILL_BREAKOUT_TOP = 'Touch_Points_Till_Breakout_Top'
    TOUCH_POINTS_TILL_BREAKOUT_BOTTOM = 'Touch_Points_Till_Breakout_Bottom'
    BREAKOUT_DIRECTION = 'Breakout_direction'
    BREAKOUT_DIRECTION_ID = 'Breakout_direction_ID'
    VOLUME_CHANGE_AT_BREAKOUT_PCT = 'Volume_Change_At_Breakout_in_PCT'
    PREVIOUS_PERIOD_HALF_TOP_OUT_PCT = 'Previous_Period_Half_Top_Out_PCT'
    PREVIOUS_PERIOD_FULL_TOP_OUT_PCT = 'Previous_Period_Full_Top_Out_PCT'
    PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT = 'Previous_Period_Half_Bottom_Out_PCT'
    PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT = 'Previous_Period_Full_Bottom_Out_PCT'
    NEXT_PERIOD_HALF_POSITIVE_PCT = 'Next_Period_Half_Positive_PCT'
    NEXT_PERIOD_FULL_POSITIVE_PCT= 'Next_Period_Full_Positive_PCT'
    NEXT_PERIOD_HALF_NEGATIVE_PCT= 'Next_Period_Half_Negative_PCT'
    NEXT_PERIOD_FULL_NEGATIVE_PCT= 'Next_Period_Full_Negative_PCT'
    TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF = 'Ticks_From_Breakout_Till_Positive_Half'
    TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL = 'Ticks_From_Breakout_Till_Positive_Full'
    TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF = 'Ticks_From_Breakout_Till_Negative_Half'
    TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL = 'Ticks_From_Breakout_Till_Negative_Full'
    AVAILABLE_FIBONACCI_TYPE = 'Available_Fibonacci_Type'  # '', Min, Max
    AVAILABLE_FIBONACCI_TYPE_ID = 'Available_Fibonacci_Type_ID'  # 0 = No, -1 = Min, 1 = Max
    EXPECTED_WIN = 'Expected_Win'
    FALSE_BREAKOUT = 'False_Breakout'
    EXPECTED_WIN_REACHED = 'Expected_Win_Reached'
