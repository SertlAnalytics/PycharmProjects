"""
Description: This module contains the constants used mainly for pattern detections - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.pybase.loop_list import ExtendedDictionary


class PDP:  # Pattern Detection Process
    UPDATE_TRADE_DATA = 'Update_Trade_Data'
    UPDATE_PATTERN_DATA = 'Update_Pattern_Data'
    ALL = 'All'


class PRED:  # Predictors
    TOUCH_POINT = 'Touch_Point'
    BEFORE_BREAKOUT = 'Before_Breakout'
    AFTER_BREAKOUT = 'After_Breakout'
    FOR_TRADE = 'For_Trade'

    @staticmethod
    def get_as_options():
        return [{'label': chart_mode, 'value': chart_mode} for chart_mode in CHM.get_all()]

    @staticmethod
    def get_for_pattern_all():
        return [PRED.TOUCH_POINT, PRED.BEFORE_BREAKOUT, PRED.AFTER_BREAKOUT]

    @staticmethod
    def get_for_trade_all():
        return [PRED.FOR_TRADE]


class CHM:  # chart modes
    MARKERS = 'markers'
    LINES = 'lines'

    @staticmethod
    def get_as_options():
        return [{'label': chart_mode, 'value': chart_mode} for chart_mode in CHM.get_all()]

    @staticmethod
    def get_all():
        return [CHM.MARKERS]

    @staticmethod
    def get_mode_for_chart_type(chart_type: str):
        value_dict = {
            CHT.SCATTER: CHM.MARKERS,
            CHT.AREA: CHM.LINES,
        }
        return value_dict.get(chart_type, CHM.MARKERS)


class CHT:  # chart type
    SCATTER = 'Scatter'
    AREA_WINNER_LOSER = 'Area winner and losers'
    PREDICTOR = 'Predictor'
    AREA = 'Area'
    BAR = 'Bar'
    LINE = 'Line'
    HEAT_MAP = 'Heatmap'
    TABLE = 'Table'
    CONTOUR = 'Contour'
    PIE = 'Pie'
    D3_SCATTER = '3D Scatter'
    D3_LINE = '3D Line'
    D3_SURFACE = '3D Surface'
    BOX = 'Box'
    VIOLINE = 'Violine'
    HISTOGRAM = 'Histogram'
    D2_CONTOUR_HISTOGRAM = '2D Contour Histogram'
    POLAR_SCATTER = 'Polar Scatter'

    @staticmethod
    def get_as_options():
        li = CHT.get_all()
        return [{'label': chart_type, 'value': chart_type} for chart_type in li]

    @staticmethod
    def get_all():
        li = [CHT.SCATTER, CHT.AREA_WINNER_LOSER, CHT.PREDICTOR_PIE,
              CHT.BAR, CHT.LINE, CHT.AREA, CHT.HEAT_MAP, CHT.TABLE, CHT.CONTOUR, CHT.PIE, CHT.D3_SCATTER,
              CHT.D3_LINE, CHT.D3_SURFACE, CHT.BOX, CHT.VIOLINE, CHT.HISTOGRAM, CHT.D2_CONTOUR_HISTOGRAM,
              CHT.POLAR_SCATTER]
        return li

    @staticmethod
    def get_for_trade_statistics():
        return [CHT.AREA_WINNER_LOSER, CHT.SCATTER, CHT.PREDICTOR, CHT.PIE]

    @staticmethod
    def get_for_pattern_statistics():
        return [CHT.AREA_WINNER_LOSER, CHT.SCATTER, CHT.PREDICTOR, CHT.PIE]


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


class FWST:   # Fibonacci Wave Structure
    S_M_L = 'Short_medium_long'
    S_L_S = 'Short_long_short'
    L_M_S = 'Long_medium_short'
    NONE = 'None'


class EQUITY_TYPE:
    NONE = 'None'
    SHARE = 'Shares'
    COMMODITY = 'Commodity'
    CRYPTO = 'Crypto_Currencies'

    @staticmethod
    def get_id(key: str):
        return {EQUITY_TYPE.SHARE: 1, EQUITY_TYPE.COMMODITY: 10, EQUITY_TYPE.CRYPTO: 20}.get(key)


class OT:  # order type
    EXCHANGE_MARKET = 'exchange market'
    EXCHANGE_LIMIT = 'exchange limit'
    EXCHANGE_STOP = 'exchange stop'
    EXCHANGE_TRAILING_STOP = 'exchange trailing - stop'

    def get_id(key: str):
        return {OT.EXCHANGE_MARKET: 1, OT.EXCHANGE_LIMIT: 2, OT.EXCHANGE_STOP: 3, OT.EXCHANGE_TRAILING_STOP: 4}.get(key)


class OS:  # Order side
    BUY = 'buy'
    SELL = 'sell'

    def get_id(key: str):
        return {OS.BUY: 1, OS.SELL: -1}.get(key)


class FT:
    ALL = 'ALL'
    NONE = 'NONE'
    TRIANGLE = 'Triangle'
    TRIANGLE_TOP = 'Triangle top'
    TRIANGLE_BOTTOM = 'Triangle bottom'
    TRIANGLE_UP = 'Triangle up'
    TRIANGLE_DOWN = 'Triangle down'
    CHANNEL = 'Channel'  # https://www.investopedia.com/articles/trading/05/020905.asp
    CHANNEL_UP = 'Channel up'
    CHANNEL_DOWN = 'Channel down'
    TKE_BOTTOM = 'TKE bottom'  # Trend correction extrema
    TKE_TOP = 'TKE top'  # Trend correction extrema
    HEAD_SHOULDER = 'Head-Shoulder'
    HEAD_SHOULDER_ASC = 'Head-Shoulder_Ascending'
    HEAD_SHOULDER_BOTTOM = 'Head-Shoulder-Bottom'
    HEAD_SHOULDER_BOTTOM_DESC = 'Head-Shoulder-Bottom_Descending'
    FIBONACCI_ASC = 'Fibonacci_Ascending'
    FIBONACCI_DESC = 'Fibonacci_Descending'

    @staticmethod
    def get_all():
        return [FT.TRIANGLE, FT.TRIANGLE_TOP, FT.TRIANGLE_BOTTOM, FT.TRIANGLE_UP, FT.TRIANGLE_DOWN,
                FT.CHANNEL, FT.CHANNEL_UP, FT.CHANNEL_DOWN,
                FT.TKE_TOP, FT.TKE_BOTTOM,
                FT.FIBONACCI_ASC, FT.FIBONACCI_DESC,
                FT.HEAD_SHOULDER, FT.HEAD_SHOULDER_ASC, FT.HEAD_SHOULDER_BOTTOM, FT.HEAD_SHOULDER_BOTTOM_DESC]

    @staticmethod
    def get_all_for_statistics():
        return [FT.ALL] + sorted(FT.get_all())

    @staticmethod
    def get_long_trade_able_types():
        return [FT.TRIANGLE, FT.TRIANGLE_TOP, FT.TRIANGLE_BOTTOM, FT.TRIANGLE_DOWN,
                FT.CHANNEL, FT.CHANNEL_DOWN,
                FT.TKE_BOTTOM,
                FT.FIBONACCI_DESC,
                FT.HEAD_SHOULDER_BOTTOM, FT.HEAD_SHOULDER_BOTTOM_DESC]

    @staticmethod
    def get_normal_types():
        special_list = FT.get_head_shoulder_types() + FT.get_head_shoulder_bottom_types() + FT.get_fibonacci_types()
        return [entry for entry in FT.get_all() if entry not in special_list]

    @staticmethod
    def get_head_shoulder_types():
        return [FT.HEAD_SHOULDER, FT.HEAD_SHOULDER_ASC]

    @staticmethod
    def get_head_shoulder_bottom_types():
        return [FT.HEAD_SHOULDER_BOTTOM, FT.HEAD_SHOULDER_BOTTOM_DESC]

    @staticmethod
    def get_fibonacci_types():
        return [FT.FIBONACCI_ASC, FT.FIBONACCI_DESC]

    @staticmethod
    def is_pattern_type_any_head_shoulder(pattern_type: str) -> bool:
        return pattern_type in FT.get_head_shoulder_types() + FT.get_head_shoulder_bottom_types()

    @staticmethod
    def is_pattern_type_long_trade_able(pattern_type: str) -> bool:
        return pattern_type in FT.get_long_trade_able_types()

    @staticmethod
    def is_pattern_type_any_fibonacci(pattern_type: str) -> bool:
        return pattern_type in FT.get_fibonacci_types()

    @staticmethod
    def get_id(key: str):
        return FT.get_value_key_dict().get(key, 0)

    @staticmethod
    def get_pattern_type(pattern_type_id: int):
        return ExtendedDictionary.get_key_for_value(FT.get_value_key_dict(), pattern_type_id)

    @staticmethod
    def get_value_key_dict() -> dict:
        return {FT.CHANNEL: 10, FT.CHANNEL_UP: 11, FT.CHANNEL_DOWN: 12,
                FT.TRIANGLE: 20, FT.TRIANGLE_UP: 21, FT.TRIANGLE_DOWN: 22,
                FT.TRIANGLE_TOP: 23, FT.TRIANGLE_BOTTOM: 24,
                FT.TKE_TOP: 31, FT.TKE_BOTTOM: 32,
                FT.HEAD_SHOULDER: 43, FT.HEAD_SHOULDER_BOTTOM: 44,
                FT.HEAD_SHOULDER_ASC: 45, FT.HEAD_SHOULDER_BOTTOM_DESC: 46,
                FT.FIBONACCI_ASC: 55, FT.FIBONACCI_DESC: 56
                }


class PRD:  # Periods
    WEEKLY = 'WEEKLY'
    DAILY = 'DAILY'
    INTRADAY = 'INTRADAY'

    @staticmethod
    def get_id(period: str):
        return PRD.get_value_key_dict().get(period)

    @staticmethod
    def get_period(period_id: int):
        return ExtendedDictionary.get_key_for_value(PRD.get_value_key_dict(), period_id)

    @staticmethod
    def get_value_key_dict() -> dict:
        return {PRD.INTRADAY: 0, PRD.DAILY: 1, PRD.WEEKLY: 2}

    @staticmethod
    def get_seconds_for_period(period: str, aggregation=1):
        if period == PRD.DAILY:
            return 86400
        elif period == PRD.INTRADAY:
            return 60 * aggregation

    @staticmethod
    def get_time_stamp_list_for_time_stamp(time_stamp: int, numbers: int, period: str, aggregation=1):
        period_seconds_part = int(PRD.get_seconds_for_period(period, aggregation)/numbers)
        if period == PRD.DAILY:
            return [(time_stamp + k * period_seconds_part) for k in range(0, numbers)]
        else:
            return [(time_stamp - k * period_seconds_part) for k in range(0, numbers)]

    @staticmethod
    def hallo():
        return 'Hallo'


class OPS:  # Outputsize
    COMPACT = 'compact'
    FULL = 'full'


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

    @staticmethod
    def get_standard_column_names():
        return [CN.OPEN, CN.HIGH, CN.LOW, CN.CLOSE, CN.VOL]


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
    PRE_TOP_PCT = 'Previous_Period_Top_PCT'
    PRE_BOTTOM_PCT = 'Previous_Period_Bottom_PCT'


class TP:  # TradeProcess
    ONLINE = 'Online'
    TEST_SINGLE = 'Test_single'
    BACK_TESTING = 'Back_testing'
    TRADE_REPLAY = 'Trade_replay'
    PATTERN_REPLAY = 'Pattern_replay'
    NONE = 'None'

    @staticmethod
    def get_id(key: str):
        return {TP.ONLINE: 10, TP.TEST_SINGLE: 20, TP.BACK_TESTING: 30, TP.TRADE_REPLAY: 40,
                TP.PATTERN_REPLAY: 50, TP.NONE: 90}.get(key)

    @staticmethod
    def get_as_list():
        return [TP.ONLINE, TP.TRADE_REPLAY, TP.PATTERN_REPLAY]

    @staticmethod
    def get_as_options():
        # li = [TP.TRADE_REPLAY, TP.ONLINE]
        li = [TP.ONLINE, TP.TRADE_REPLAY, TP.PATTERN_REPLAY]
        return [{'label': trade_process.replace('_', ' '), 'value': trade_process} for trade_process in li]


class TSP:  # TradeSubProcess
    WATCHING = 'watching'
    BUYING = 'buying'
    SELLING = 'selling'
    RE_BUYING = 'Re_Buying'
    NONE = 'None'


class BT:  # Buy Trigger
    BREAKOUT = 'Breakout'
    TOUCH_POINT = 'Touch_point'
    FIBONACCI_CLUSTER = 'Fibonacci_cluster'

    @staticmethod
    def get_id(key: str):
        return {BT.BREAKOUT: 10, BT.TOUCH_POINT: 20, BT.FIBONACCI_CLUSTER: 50}.get(key)

    @staticmethod
    def get_as_dict():
        return {BT.BREAKOUT: 10, BT.TOUCH_POINT: 20, BT.FIBONACCI_CLUSTER: 50}

    @staticmethod
    def get_as_list():
        return [BT.BREAKOUT, BT.TOUCH_POINT]

    @staticmethod
    def get_as_options():
        li = [BT.BREAKOUT, BT.TOUCH_POINT]
        return [{'label': buy_trigger.replace('_', ' '), 'value': buy_trigger} for buy_trigger in li]


class TSTR:  # Trading Strategy
    LIMIT = 'Limit'
    LIMIT_FIX = 'Limit_fix'
    TRAILING_STOP = 'Trailing_stop'
    TRAILING_STEPPED_STOP = 'Trailing_stepped_stop'
    SMA = 'Simple_moving_average'

    @staticmethod
    def get_id(key: str):
        return {TSTR.LIMIT: 10, TSTR.LIMIT_FIX: 15, TSTR.TRAILING_STOP: 20,
                TSTR.TRAILING_STEPPED_STOP: 30, TSTR.SMA: 40}.get(key)

    @staticmethod
    def get_as_list():
        return [TSTR.LIMIT, TSTR.LIMIT_FIX, TSTR.TRAILING_STOP, TSTR.TRAILING_STEPPED_STOP, TSTR.SMA]

    @staticmethod
    def get_as_options():
        li = TSTR.get_as_list()
        return [{'label': trade_strategy.replace('_', ' '), 'value': trade_strategy} for trade_strategy in li]


class TTC:  # Trade test cases
    FALSE_BREAKOUT = 'false breakout'
    NO_FALSE_BREAKOUT = 'no false breakout'
    BUY_SELL_LIMIT = 'buy & sell at limit'
    BUY_ADJUST_STOP_LOSS = 'buy & adjust stop loss'
    BUY_SELL_STOP_LOSS = 'buy & sell at stop loss'
    ACTIVATE_BREAKOUT = 'activate breakout for touch'
    BACK_TESTING = 'back testing'


class RST:  # ReplayStatus
    REPLAY = 'replay'
    STOP = 'stop'
    CANCEL = 'cancel'


class PTS:  # PatternTradeStatus
    NEW = 'new'
    EXECUTED = 'executed'
    PENDING = 'pending'
    FINISHED = 'finished'

    @staticmethod
    def get_id(key: str):
        return {PTS.NEW: 10, PTS.EXECUTED: 20, PTS.PENDING: 30, PTS.FINISHED: 50}.get(key)


class PTHP:  # Pattern Trade Handler Processes
    ADJUST_STOPS_AND_LIMITS = 'ADJUST_STOPS_AND_LIMITS'
    HANDLE_SELL_TRIGGERS = 'HANDLE_SELL_TRIGGERS'
    HANDLE_WRONG_BREAKOUT = 'HANDLE_WRONG_BREAKOUT'
    HANDLE_BUY_TRIGGERS = 'HANDLE_BUY_TRIGGERS'
    HANDLE_WATCHING = 'HANDLE_WATCHING'


class TBT:  # TradingBoxType
    EXPECTED_WIN = 'Expected_win'
    TOUCH_POINT = 'Touchpoint'

    @staticmethod
    def get_id(key: str):
        return {TBT.EXPECTED_WIN: 10, TBT.TOUCH_POINT: 20}.get(key)


class PDR:  # Pattern Deletion Reasons
    PATTERN_VANISHED = 'Pattern_vanished'
    WRONG_BREAKOUT = 'Wrong_breakout'
    TRADE_FINISHED = 'Trade_finished'
    SMA_PROBLEM = 'Simple_moving_average_problem'

    def get_id(key: str):
        return {PDR.PATTERN_VANISHED: 10, PDR.WRONG_BREAKOUT: 20, PDR.TRADE_FINISHED: 40}.get(key)


class ST:  # Sell Trigger
    LIMIT = 'Limit'
    STOP_LOSS = 'Stop_loss'
    PATTERN_VANISHED = 'Pattern_vanished'
    PATTERN_END = 'Pattern_end'

    def get_id(key: str):
        return {ST.LIMIT: 10, ST.STOP_LOSS: 20, ST.PATTERN_END: 40, ST.PATTERN_END: 50}.get(key)


class TR:  # Trade Result
    WINNER = 'Winner'
    NEUTRAL = 'Neutral'
    LOSER = 'Loser'

    @staticmethod
    def get_id(key: str):
        return {TR.LOSER: -1, TR.NEUTRAL: 0, TR.WINNER: 1}.get(key)


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
    # for Stocks
    SYMBOL = 'Symbol'
    TIMESTAMP = 'Timestamp'
    DATE = 'Date'
    TIME = 'Time'
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'LOW'
    CLOSE = 'Close'
    VOLUME = 'Volume'
    BIG_MOVE = 'BigMove'
    DIRECTION = 'Direction'
    # for company
    NAME = 'Name'
    TO_BE_LOADED = 'ToBeLoaded'
    SECTOR = 'Sector'
    YEAR = 'Year'
    REVENUES = 'Revenues'
    EXPENSES = 'Expenses'
    EMPLOYEES = 'Employees'
    SAVINGS = 'Savings'
    FORECAST_GROWTH = 'ForcastGrowth'  # writing error...
    # for pattern
    OID = 'oid'  # the default rowid column in each SQLITE table - unless excluded
    ID = 'ID'  # Ticker_ID-Pattern_Type_ID-Pattern_Range_Begin_DT-Pattern_Range_End_DT
    EQUITY_TYPE = 'Equity_Type'  # Share, Commodities, Crypto Currency
    EQUITY_TYPE_ID = 'Equity_Type_ID'  # Share, Commodities, Crypto Currency
    PERIOD = 'Period'  # Daily, Intraday (min)
    PERIOD_ID = 'Period_ID'  # Intraday = 0, Daily = 1, Weekly = 2, Monthly = 3, Intraday (min)
    PERIOD_AGGREGATION = 'Aggregation'
    TICKER_ID = 'Ticker_ID'
    TICKER_NAME = 'Ticker_Name'
    PATTERN_ID = 'Pattern_ID'
    PATTERN_TYPE = 'Pattern_Type'
    PATTERN_TYPE_ID = 'Pattern_Type_ID'
    TS_PATTERN_TICK_FIRST = 'Timestamp_Pattern_Tick_First'
    TS_PATTERN_TICK_LAST = 'Timestamp_Pattern_Tick_Last'
    TS_BREAKOUT = 'Timestamp_Breakout'
    TICKS_TILL_PATTERN_FORMED = 'Ticks_Till_Pattern_Formed'
    TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT = 'Ticks_From_Pattern_Formed_Till_Breakout'
    PATTERN_RANGE_BEGIN_DT = 'Pattern_Range_Begin_Date'
    PATTERN_RANGE_BEGIN_TIME = 'Pattern_Range_Begin_Time'
    PATTERN_BEGIN_DT = 'Pattern_Begin_Date'
    PATTERN_BEGIN_TIME = 'Pattern_Begin_Time'
    BREAKOUT_DT = 'Breakout_Date'
    BREAKOUT_TIME = 'Breakout_Time'
    PATTERN_END_DT = 'Pattern_End_Date'
    PATTERN_END_TIME = 'Pattern_End_Time'
    PATTERN_RANGE_END_DT = 'Pattern_Range_End_Date'
    PATTERN_RANGE_END_TIME = 'Pattern_Range_End_Time'
    PATTERN_TOLERANCE_PCT = 'Patern_Tolerance_PCT'
    BREAKOUT_RANGE_MIN_PCT = 'Breakout_Range_Min_PCT'
    PATTERN_HEIGHT = 'Pattern_Height'
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
    # and additional for Trades
    TRADE_ID = 'Trade_ID'
    TRADE_MEAN_AGGREGATION = 'Trade_Mean_Aggregation'
    TRADE_PROCESS = 'Trade_Process'  #  TP.ONLINE = 'Online', TEST_SINGLE = 'Test_single', BACK_TESTING = 'Back_testing'
    TRADE_READY_ID = 'Trade_Ready_ID'  # for a real trade = 1, 0 else
    TRADE_STRATEGY = 'Trade_Strategy'
    TRADE_STRATEGY_ID = 'Trade_Strategy_ID'
    TRADE_BOX_TYPE = 'Trade_Box_Type'
    TRADE_BOX_TYPE_ID = 'Trade_Box_Type_ID'
    TRADE_BOX_HEIGHT = 'Trade_Box_Height'
    TRADE_BOX_OFF_SET = 'Trade_Box_Offset'
    TRADE_BOX_MAX_VALUE = 'Trade_Box_Max_Value'
    TRADE_BOX_LIMIT_ORIG = 'Trade_Box_Limit_Orig'
    TRADE_BOX_STOP_LOSS_ORIG = 'Trade_Box_Stop_Loss_Orig'
    TRADE_BOX_LIMIT = 'Trade_Box_Limit'
    TRADE_BOX_STOP_LOSS = 'Trade_Box_Stop_Loss'
    TRADE_BOX_STD = 'Trade_Box_STD'  # standard deviation

    BUY_ORDER_ID = 'Buy_Order_ID'
    BUY_ORDER_TPYE = 'Buy_Order_Type'
    BUY_ORDER_TPYE_ID = 'Buy_Order_Type_ID'
    BUY_TIME_STAMP = 'Buy_Time_Stamp'
    BUY_DT = 'Buy_Date'
    BUY_TIME = 'Buy_Time'
    BUY_AMOUNT = 'Buy_Amount'
    BUY_PRICE = 'Buy_Price'
    BUY_TOTAL_COSTS = 'Buy_Total_Costs'
    BUY_TRIGGER = 'Buy_Trigger'
    BUY_TRIGGER_ID = 'Buy_Trigger_ID'
    BUY_COMMENT = 'Buy_Comment'

    FC_TOUCH_POINTS_TILL_BREAKOUT_TOP = 'Forecast_Touch_Points_Till_Breakout_Top'
    FC_TOUCH_POINTS_TILL_BREAKOUT_BOTTOM = 'Forecast_Touch_Points_Till_Breakout_Bottom'
    FC_TICKS_TILL_BREAKOUT = 'Forecast_Ticks_Till_Breakout'
    FC_BREAKOUT_DIRECTION = 'Forecast_Breakout_Direction'
    FC_BREAKOUT_DIRECTION_ID = 'Forecast_Breakout_Direction_ID'
    FC_FALSE_BREAKOUT_ID  = 'Forecast_False_Breakout'
    FC_HALF_POSITIVE_PCT = 'Forecast_Half_Positive_PCT'
    FC_FULL_POSITIVE_PCT = 'Forecast_Full_Positive_PCT'
    FC_HALF_NEGATIVE_PCT = 'Forecast_Half_Negative_PCT'
    FC_FULL_NEGATIVE_PCT = 'Forecast_Full_Negative_PCT'
    FC_TICKS_TO_POSITIVE_HALF = 'Forecast_Ticks_To_Positive_Half'
    FC_TICKS_TO_POSITIVE_FULL = 'Forecast_Ticks_To_Positive_Full'
    FC_TICKS_TO_NEGATIVE_HALF = 'Forecast_Ticks_To_Negative_Half'
    FC_TICKS_TO_NEGATIVE_FULL = 'Forecast_Ticks_To_Negative_Full'
    FC_BUY_DT = 'Forecast_Buy_Date'
    FC_BUY_TIME = 'Forecast_Buy_Time'
    FC_SELL_DT = 'Forecast_Sell_Date'
    FC_SELL_TIME = 'Forecast_Sell_Time'

    SELL_ORDER_ID = 'Sell_Order_ID'
    SELL_ORDER_TPYE = 'Sell_Order_Type'
    SELL_ORDER_TPYE_ID = 'Sell_Order_Type_ID'
    SELL_TIME_STAMP = 'Sell_Time_Stamp'
    SELL_DT = 'Sell_Date'
    SELL_TIME = 'Sell_Time'
    SELL_AMOUNT = 'Sell_Amount'
    SELL_PRICE = 'Sell_Price'
    SELL_TOTAL_VALUE = 'Sell_Total_Value'
    SELL_COMMENT = 'Sell_Comment'
    SELL_TRIGGER = 'Sell_Trigger'
    SELL_TRIGGER_ID = 'Sell_Trigger_ID'

    TRADE_REACHED_PRICE = 'Trade_Reached_Price'
    TRADE_REACHED_PRICE_PCT = 'Trade_Reached_Price_PCT'

    TRADE_RESULT_AMOUNT = 'Trade_Result_Amount'
    TRADE_RESULT_PCT = 'Trade_Result_PCT'

    TRADE_RESULT = 'Trade_Result'
    TRADE_RESULT_ID = 'Trade_Result_ID'

    FC_TRADE_REACHED_PRICE_PCT = 'Forecast_Trade_Reached_Price_PCT'
    FC_TRADE_RESULT_ID = 'Forecast_Trade_Result_ID'