"""
Description: This module contains the constants used mainly for pattern detections - but can be used elsewhere.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.pybase.loop_list import ExtendedDictionary


class PPR:  # PatternProcesses
    UPDATE_PATTERN_INTRADAY = 'Update_Pattern_Intraday'
    UPDATE_PATTERN_DAILY = 'Update_Pattern_Daily'
    UPDATE_WAVE_INTRADAY_CRYPTO = 'Update_Wave_Intraday_Crypto'
    UPDATE_WAVE_INTRADAY_SHARES = 'Update_Wave_Intraday_Shares'
    UPDATE_WAVE_INTRADAY_CCY = 'Update_Wave_Intraday_Currencies'
    UPDATE_WAVE_DAILY = 'Update_Wave_Daily'
    DELETE_DUPLICATE_RECORDS_IN_TABLES = 'Delete_Duplicate_Records_in_Tables'
    UPDATE_EQUITY_DATA = 'Update_Equity_Data'
    UPDATE_STOCK_DATA_DAILY_CRYPTO = 'Update_Stock_Data_Daily_Crypto'
    UPDATE_STOCK_DATA_DAILY_SHARES = 'Update_Stock_Data_Daily_Shares'
    UPDATE_STOCK_DATA_DAILY_CCY = 'Update_Stock_Data_Daily_Currencies'
    UPDATE_HEATMAP_IN_WAVE_TAB = 'Update_Heatmap_in_Wave_Tab'
    UPDATE_CLASS_METRICS_FOR_PREDICTOR_AND_LABEL = 'Update_Class_Metrics_For_Predictor_and_Label'
    UPDATE_TRADE_POLICY_METRIC = 'Update_Trade_Policy_Metric'
    UPDATE_TRADE_RECORDS = 'Update_Trade_Records'
    UPDATE_PREDICTORS = 'Update_Predictors'


class TFOP:
    GRADIENT_DESCENT_MANUAL = 'Gradient_Descent_Manual'
    GRADIENT_DESCENT = 'Gradient_Descent'
    GRADIENT_DESCENT_OPTIMIZER = 'Gradient_Descent_Optimizer'
    MOMENTUM_OPTIMIZER = 'Momentum_Optimizer'


class POC:  # PatternObservationColumns
    # All pct values are with respective to the off set value = buy price
    LIMIT_PCT = 'Limit_Percentage'
    STOP_LOSS_PCT = 'Stop_Loss_PCT'
    CURRENT_TICK_PCT = 'Current_Tick_Percentage'  # regarding to length of pattern
    CURRENT_VALUE_HIGH_PCT = 'Current_Value_High_Percentage'
    CURRENT_VALUE_LOW_PCT = 'Current_Value_Low_Percentage'
    CURRENT_VALUE_OPEN_PCT = 'Current_Value_Open_Percentage'
    CURRENT_VALUE_CLOSE_PCT = 'Current_Value_Close_Percentage'
    CURRENT_VOLUME_BUY_PCT = 'Current_Volume_Buy_Percentage'
    CURRENT_VOLUME_LAST_PCT = 'Current_Volume_Last_Percentage'
    BEFORE_PATTERN_MAX_PCT = 'Before_Pattern_Max_Percentage'
    BEFORE_PATTERN_MIN_PCT = 'Before_Pattern_Min_Percentage'
    PATTERN_MAX_PCT = 'Pattern_Max_Percentage'
    PATTERN_MIN_PCT = 'Pattern_Min_Percentage'
    AFTER_BUY_MAX_PCT = 'After_Buy_Max_Percentage'  # until current value !!!
    AFTER_BUY_MIN_PCT = 'After_Buy_Min_Percentage'  # until current value !!!
    FC_TICKS_TO_POSITIVE_HALF_PCT = 'Forecast_Ticks_To_Positive_Half_Percentage'  # regarding to length of pattern
    FC_TICKS_TO_POSITIVE_FULL_PCT = 'Forecast_Ticks_To_Positive_Full_Percentage'  # regarding to length of pattern
    FC_TICKS_TO_NEGATIVE_HALF_PCT = 'Forecast_Ticks_To_Negative_Half_Percentage'  # regarding to length of pattern
    FC_TICKS_TO_NEGATIVE_FULL_PCT = 'Forecast_Ticks_To_Negative_Full_Percentage'  # regarding to length of pattern

    @staticmethod
    def get_observation_space_columns():
        return [POC.LIMIT_PCT,
                POC.STOP_LOSS_PCT,
                POC.CURRENT_TICK_PCT,
                POC.CURRENT_VALUE_HIGH_PCT, POC.CURRENT_VALUE_LOW_PCT,
                POC.CURRENT_VALUE_OPEN_PCT, POC.CURRENT_VALUE_CLOSE_PCT,
                POC.CURRENT_VOLUME_BUY_PCT, POC.CURRENT_VOLUME_LAST_PCT,
                POC.BEFORE_PATTERN_MAX_PCT, POC.BEFORE_PATTERN_MIN_PCT,
                POC.PATTERN_MAX_PCT, POC.PATTERN_MIN_PCT,
                POC.AFTER_BUY_MAX_PCT, POC.AFTER_BUY_MIN_PCT,
                DC.FC_HALF_POSITIVE_PCT, DC.FC_FULL_POSITIVE_PCT,
                DC.FC_HALF_NEGATIVE_PCT, DC.FC_FULL_NEGATIVE_PCT,
                POC.FC_TICKS_TO_POSITIVE_HALF_PCT, POC.FC_TICKS_TO_POSITIVE_FULL_PCT,
                POC.FC_TICKS_TO_NEGATIVE_HALF_PCT, POC.FC_TICKS_TO_NEGATIVE_FULL_PCT]


class WPC:  # WavePredictionColumns
    # All pct values are with respective to the total value and total timestamp range
    W1_VALUE_RANGE_PCT = 'W1_Value_Range_PCT'
    W2_VALUE_RANGE_PCT = 'W2_Value_Range_PCT'
    W3_VALUE_RANGE_PCT = 'W3_Value_Range_PCT'
    W4_VALUE_RANGE_PCT = 'W4_Value_Range_PCT'
    W5_VALUE_RANGE_PCT = 'W5_Value_Range_PCT'
    W1_TS_RANGE_PCT = 'W1_Timestamp_Range_PCT'
    W2_TS_RANGE_PCT = 'W2_Timestamp_Range_PCT'
    W3_TS_RANGE_PCT = 'W3_Timestamp_Range_PCT'
    W4_TS_RANGE_PCT = 'W4_Timestamp_Range_PCT'
    W5_TS_RANGE_PCT = 'W5_Timestamp_Range_PCT'

    @staticmethod
    def get_wave_prediction_columns():
        return [WPC.W1_VALUE_RANGE_PCT, WPC.W2_VALUE_RANGE_PCT,
                WPC.W3_VALUE_RANGE_PCT, WPC.W4_VALUE_RANGE_PCT, WPC.W5_VALUE_RANGE_PCT,
                WPC.W1_TS_RANGE_PCT, WPC.W2_TS_RANGE_PCT,
                WPC.W3_TS_RANGE_PCT, WPC.W4_TS_RANGE_PCT, WPC.W5_TS_RANGE_PCT,
                DC.WAVE_END_FLAG, DC.WAVE_MAX_RETR_PCT, DC.WAVE_MAX_RETR_TS_PCT]

    
class TPA:  # TradePolicyAction
    SELL = 'Sell'
    STOP_LOSS_UP = 'Stop_Loss_upwards'
    STOP_LOSS_DOWN = 'Stop_Loss_downwards'
    WAIT = 'WAIT'
    LIMIT_UP = 'Limit_upwards'
    LIMIT_DOWN = 'Limit_downwards'


class SVW:  # stocks views
    V_WAVE = 'v_wave'

class STBL:  # stocks tables
    EQUITY = 'Equity'
    STOCKS = 'Stocks'
    COMPANY = 'Company'
    PATTERN = 'Pattern'
    PROCESS = 'Process'
    TRADE = 'Trade'
    WAVE = 'Wave'
    ASSET = 'Asset'
    METRIC = 'Metric'
    TRADE_POLICY_METRIC = 'TradePolicyMetric'

    @staticmethod
    def get_all():
        return [STBL.EQUITY, STBL.STOCKS, STBL.COMPANY, STBL.PATTERN, STBL.TRADE,
                STBL.WAVE, STBL.ASSET, STBL.METRIC, STBL.TRADE_POLICY_METRIC, STBL.PROCESS]

    @staticmethod
    def get_as_options():
        return [{'label': table, 'value': table} for table in STBL.get_all()]

    @staticmethod
    def get_for_model_statistics():
        return [STBL.PATTERN, STBL.TRADE]


class BLR:  # BlackListReason
    SIMILAR_AVAILABLE = 'Similar trade available'
    BUY_TRIGGER_CONDITIONS = 'Buy trigger conditions violated'
    TRADE_STRATEGY_CONDITIONS = 'Trade strategy conditions violated'
    NO_BEST_STRATEGY = 'No best strategy found'


class PDP:  # Pattern Detection Process
    UPDATE_TRADE_DATA = 'Update_Trade_Data'
    UPDATE_PATTERN_DATA = 'Update_Pattern_Data'
    ALL = 'All'


class PRED:  # Predictors
    TOUCH_POINT = 'Touch_Point'
    BEFORE_BREAKOUT = 'Before_Breakout'
    AFTER_BREAKOUT = 'After_Breakout'
    FOR_TRADE = 'For_Trade'
    BREAKOUT_LEVEL = 'Breakout_Level'

    @staticmethod
    def get_as_options():
        return [{'label': chart_mode, 'value': chart_mode} for chart_mode in CHM.get_all()]

    @staticmethod
    def get_for_pattern_all():
        return [PRED.TOUCH_POINT, PRED.BEFORE_BREAKOUT, PRED.AFTER_BREAKOUT]

    @staticmethod
    def get_for_trade_all():
        return [PRED.FOR_TRADE]


class DTRG:  # Date Ranges
    ALL = 'All'
    TODAY = 'Today'
    CURRENT_WEEK = 'Current week'
    CURRENT_MONTH = 'Current month'
    LAST_WEEK_WEEK = 'Last week'
    LAST_MONTH = 'Last month'
    LAST_YEAR = 'Breakout_Level'

    @staticmethod
    def get_as_options_for_log_tab():
        return [{'label': date_range, 'value': date_range} for date_range in DTRG.get_for_log_tab()]

    @staticmethod
    def get_as_options_for_db_tab():
        return [{'label': date_range, 'value': date_range} for date_range in DTRG.get_for_db_tab()]

    @staticmethod
    def get_for_log_tab():
        return [DTRG.ALL, DTRG.TODAY, DTRG.CURRENT_WEEK]

    @staticmethod
    def get_for_db_tab():
        return [DTRG.ALL, DTRG.TODAY, DTRG.CURRENT_WEEK]


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
    MY_TRADES = 'My Trades'
    AREA = 'Area'
    BAR = 'Bar'
    LINE = 'Line'
    HEAT_MAP = 'Heatmap'
    MOOD_CHART = 'Mood Chart'
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
    STACK_GROUP = 'Stackgroup'
    CONFUSION = 'Confusion Matrix'
    ROC = 'ROC Curve'

    @staticmethod
    def get_as_options():
        li = CHT.get_all()
        return [{'label': chart_type, 'value': chart_type} for chart_type in li]

    @staticmethod
    def get_all():
        li = [CHT.SCATTER, CHT.MY_TRADES, CHT.AREA_WINNER_LOSER, CHT.PREDICTOR_PIE,
              CHT.BAR, CHT.LINE, CHT.AREA, CHT.HEAT_MAP, CHT.TABLE, CHT.CONTOUR, CHT.PIE, CHT.D3_SCATTER,
              CHT.D3_LINE, CHT.D3_SURFACE, CHT.BOX, CHT.VIOLINE, CHT.HISTOGRAM, CHT.D2_CONTOUR_HISTOGRAM,
              CHT.POLAR_SCATTER]
        return li

    @staticmethod
    def get_chart_types_for_trade_statistics():
        return [CHT.MY_TRADES, CHT.AREA_WINNER_LOSER, CHT.SCATTER, CHT.PREDICTOR, CHT.PIE]

    @staticmethod
    def get_chart_types_for_pattern_statistics():
        return [CHT.AREA_WINNER_LOSER, CHT.SCATTER, CHT.PREDICTOR, CHT.PIE]

    @staticmethod
    def get_chart_types_for_asset_statistics():
        return [CHT.STACK_GROUP, CHT.LINE, CHT.PIE]

    @staticmethod
    def get_chart_types_for_models_statistics():
        return [CHT.CONFUSION, CHT.ROC]


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


class INDI:  # Indicators
    NONE = 'None'
    BOLLINGER = 'Bollinger Band'
    PATTERN = 'Pattern'

    @staticmethod
    def get_id(key: str):
        return {INDI.BOLLINGER: 10, INDI.PATTERN: 90}.get(key, 0)

    @staticmethod
    def get_as_options():
        return [{'label': indicator, 'value': indicator} for indicator in INDI.get_all()]

    @staticmethod
    def get_all() -> list:
        return [INDI.NONE, INDI.BOLLINGER, INDI.PATTERN]


class FWST:   # Fibonacci Wave Structure
    S_M_L = 'Short_medium_long'
    S_L_S = 'Short_long_short'
    L_M_S = 'Long_medium_short'
    NONE = 'None'

    @staticmethod
    def get_id(key: str):
        return {FWST.L_M_S: 1, FWST.S_L_S: 2, FWST.S_M_L: 3}.get(key, 0)


class EQUITY_TYPE:
    NONE = 'None'
    SHARE = 'Shares'
    COMMODITY = 'Commodity'
    CRYPTO = 'Crypto_Currencies'
    CURRENCY = 'Currencies'
    CASH = 'CASH'

    @staticmethod
    def get_id(key: str):
        return {EQUITY_TYPE.SHARE: 1, EQUITY_TYPE.COMMODITY: 10, EQUITY_TYPE.CURRENCY: 15,
                EQUITY_TYPE.CRYPTO: 20, EQUITY_TYPE.CASH: 30}.get(key)


class OT:  # order type
    EXCHANGE_MARKET = 'exchange market'
    EXCHANGE_LIMIT = 'exchange _limit'
    EXCHANGE_STOP = 'exchange stop'
    EXCHANGE_TRAILING_STOP = 'exchange trailing-stop'

    def get_id(key: str):
        return {OT.EXCHANGE_MARKET: 1, OT.EXCHANGE_LIMIT: 2, OT.EXCHANGE_STOP: 3, OT.EXCHANGE_TRAILING_STOP: 4}.get(key)


class OS:  # Order side
    BUY = 'buy'
    SELL = 'sell'

    def get_id(key: str):
        return {OS.BUY: 1, OS.SELL: -1}.get(key)


class MT:  # Model Types
    ALL = 'All'
    LOGISTIC_REGRESSION = 'Logistic Regression'
    K_NEAREST_NEIGHBORS = 'k-Nearest Neigbors'
    LINEAR_REGRESSION = 'Linear Regression'
    SVM = 'Support Vektor Machine'
    DECISION_TREE = 'Decision Tree'
    RANDOM_FOREST = 'Random Forest'
    NN = 'Neural Network'
    OPTIMIZER = 'Optimizer'
    MLP_CLASSIFIER = 'MLP Classifier'

    @staticmethod
    def get_all():
        return [MT.LOGISTIC_REGRESSION, MT.K_NEAREST_NEIGHBORS, MT.LINEAR_REGRESSION,
                MT.SVM, MT.DECISION_TREE,
                MT.RANDOM_FOREST, MT.NN, MT.MLP_CLASSIFIER]

    @staticmethod
    def get_all_classifiers(with_optimizer=False):
        base_list = [MT.LOGISTIC_REGRESSION, MT.K_NEAREST_NEIGHBORS, MT.SVM, MT.DECISION_TREE,
                     MT.RANDOM_FOREST, MT.MLP_CLASSIFIER]
        if with_optimizer:
            base_list.append(MT.OPTIMIZER)
        return base_list

    @staticmethod
    def get_all_cv_classifiers():  # cv=cross-validation
        return [MT.K_NEAREST_NEIGHBORS, MT.SVM, MT.DECISION_TREE, MT.RANDOM_FOREST]

    @staticmethod
    def get_all_regressions():
        return [MT.LINEAR_REGRESSION]

    @staticmethod
    def get_all_for_statistics():
        return sorted(MT.get_all_classifiers(True))


class MTC:  # Metrics
    ALL = 'All'
    PRECISION = 'Precision'
    RECALL = 'Recall'
    F1_SCORE = 'F1 Score'
    ROC_AUC = 'ROC AUC'

    @staticmethod
    def get_all():
        return [MTC.PRECISION, MTC.RECALL, MTC.F1_SCORE, MTC.ROC_AUC]

    @staticmethod
    def get_all_for_statistics():
        return sorted(MTC.get_all())


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
    def is_pattern_type_any_triangle(pattern_type: str) -> bool:
        return pattern_type in FT.get_triangle_types()

    @staticmethod
    def get_triangle_types() -> list:
        return [FT.TRIANGLE, FT.TRIANGLE_DOWN, FT.TRIANGLE_UP, FT.TRIANGLE_BOTTOM, FT.TRIANGLE_TOP]

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


class WPDT:  # WavePeakDateType
    DAILY_DATE = 'Daily_Date'
    INTRADAY_DATE = 'Intraday_Date'
    INTRADAY_15_TS = 'Intraday_15_Timestamp'
    INTRADAY_30_TS = 'Intraday_30_Timestamp'

    @staticmethod
    def get_period_for_wave_period_key(wave_period_key: str):
        return {WPDT.DAILY_DATE: PRD.DAILY}.get(wave_period_key, PRD.INTRADAY)

    @staticmethod
    def get_types_for_period(period: str) -> list:
        if period == PRD.DAILY:
            return [WPDT.DAILY_DATE, WPDT.INTRADAY_DATE]
        elif period == PRD.INTRADAY:
            return [WPDT.INTRADAY_30_TS]
        return [WPDT.DAILY_DATE, WPDT.INTRADAY_DATE, WPDT.INTRADAY_30_TS]


class PRD:  # Periods
    WEEKLY = 'WEEKLY'
    DAILY = 'DAILY'
    INTRADAY = 'INTRADAY'
    ALL = 'ALL'

    @staticmethod
    def get_id(period: str):
        return PRD.get_value_key_dict().get(period)

    @staticmethod
    def get_period(period_id: int):
        return ExtendedDictionary.get_key_for_value(PRD.get_value_key_dict(), period_id)

    @staticmethod
    def get_value_key_dict() -> dict:
        return {PRD.INTRADAY: 0, PRD.DAILY: 1, PRD.WEEKLY: 2, PRD.ALL: 10}

    @staticmethod
    def hallo():
        return 'Hallo'



class ITV:  # Interval
    HOURLY = 'HOURLY'
    MINUTELY = 'MINUTELY'
    NONE = 'NONE'


class LOGT:  # Log Types (corresponds with the columns in the overview table for logs
    DATE_RANGE = 'date_range'
    ERRORS = 'errors'
    PROCESSES = 'processes'
    SCHEDULER = 'scheduler'
    MESSAGE_LOG = 'message_log'
    PATTERNS = 'patterns'
    WAVES = 'waves'
    TRADES = 'trades'

    @staticmethod
    def get_log_types_for_processing():
        return [LOGT.ERRORS, LOGT.PROCESSES, LOGT.SCHEDULER, LOGT.MESSAGE_LOG, LOGT.PATTERNS, LOGT.WAVES, LOGT.TRADES]

    @staticmethod
    def get_first_log_type_for_processing():
        return LOGT.get_log_types_for_processing()[0]


class WAVEST:  # Waves Types (corresponds with the columns in the overview table for waves
    INDICES = 'indices'
    INTRADAY_ASC = 'intraday_ascending'
    INTRADAY_DESC = 'intraday_descending'
    DAILY_ASC = 'daily_ascending'
    DAILY_DESC = 'daily_descending'

    @staticmethod
    def get_waves_types():
        return [WAVEST.INDICES, WAVEST.INTRADAY_ASC, WAVEST.DAILY_ASC, WAVEST.INTRADAY_DESC, WAVEST.DAILY_DESC]

    @staticmethod
    def get_waves_types_for_processing(period_list: list):
        if len(period_list) in [0, 2] or period_list[0] == PRD.DAILY:
            return [WAVEST.DAILY_ASC, WAVEST.INTRADAY_ASC, WAVEST.DAILY_DESC, WAVEST.INTRADAY_DESC]
        elif period_list[0] == PRD.INTRADAY:
            return [WAVEST.INTRADAY_ASC, WAVEST.INTRADAY_DESC]

    @staticmethod
    def get_waves_types_for_period(period: str):
        if period == PRD.INTRADAY:
            return [WAVEST.INTRADAY_DESC, WAVEST.INTRADAY_ASC]
        return [WAVEST.DAILY_DESC, WAVEST.DAILY_ASC]

    @staticmethod
    def get_period_for_wave_type(wave_type: str):
        return PRD.INTRADAY if wave_type in [WAVEST.INTRADAY_ASC, WAVEST.INTRADAY_DESC] else PRD.DAILY

    @staticmethod
    def get_direction_for_wave_type(wave_type: str):
        return FD.DESC if wave_type in [WAVEST.DAILY_DESC, WAVEST.INTRADAY_DESC] else FD.ASC

    @staticmethod
    def get_period_and_direction_for_wave_type(wave_type: str):
        return WAVEST.get_period_for_wave_type(wave_type), WAVEST.get_direction_for_wave_type(wave_type)

class LOGDC:  # Log data columns
    DATE = 'Date'
    TIME = 'Time'
    PROCESS = 'Process'
    PROCESS_STEP = 'Process Step'
    COMMENT = 'Comment'
    # These are artificial columns
    STRATEGY = 'Strategy'
    PATTERN = 'Pattern'
    SYMBOL = 'Symbol'
    TRADE_TYPE = 'Trade type'
    RESULT = 'Result'
    START = 'Start'
    END = 'End'


class SCORING:
    ALL = 'all'
    BEST = 'best'


class TRC:  # Trade Clients
    BITFINEX = 'Bitfinex'
    IBKR = 'InteractiveBroker'


class OPS:  # Outputsize
    COMPACT = 'compact'
    FULL = 'full'


class PT:  # PredictorType
    TOUCH_POINTS = 'touch_points'
    BEFORE_BREAKOUT = 'before_breakout'
    AFTER_BREAKOUT = 'after_breakout'

    def get_id(key: str):
        return {PT.TOUCH_POINTS: 1, PT.BEFORE_BREAKOUT: 2, PT.AFTER_BREAKOUT: 3}.get(key)


class PAT:  # PredictionAnnotationType
    BEFORE_BREAKOUT = 'Prediction before breakout'
    BEFORE_BREAKOUT_DETAILS = '...details'
    AFTER_BREAKOUT = 'Prediction after breakout'
    RETRACEMENT = 'Prediction retracement'


class INDICES:
    DOW_JONES = 'Dow Jones'
    NASDAQ100 = 'Nasdaq 100'
    NASDAQ = 'Nasdaq (all)'
    SP500 = 'S&P 500'
    FOREX = 'Forex'
    MIXED = 'Mixed'
    CRYPTO_CCY = 'Crypto Currencies'
    ALL_DATABASE = 'All in database'
    ALL = 'All'
    INDICES = 'Indices'
    NONE = 'None'
    UNDEFINED = 'Undefined'
    SHARES_GENERAL = 'Shares'

    @staticmethod
    def get_index_list_for_waves_tab():
        return [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100, INDICES.FOREX]

    @staticmethod
    def get_index_list_for_index_configuration():
        return [INDICES.CRYPTO_CCY, INDICES.DOW_JONES, INDICES.NASDAQ100, INDICES.FOREX]

    @staticmethod
    def get_ticker_for_index(index: str):
        if index == INDICES.DOW_JONES:
            return 'DJI'
        elif index == INDICES.NASDAQ100:
            return 'NDX'
        elif index == INDICES.CRYPTO_CCY:
            return 'BTCUSD'
        elif index == INDICES.FOREX:
            return 'USDEUR'
        return ''


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


class TRT:  # Trade types
    UNKNOWN = ''
    LONG = 'long'
    SHORT = 'short'
    NONE = 'none'
    NOT_LONG = 'not long'
    NOT_SHORT = 'not short'


class FCC:  # Formation Condition Columns
    BREAKOUT_WITH_BUY_SIGNAL = 'breakout had a buy signal'
    PREVIOUS_PERIOD_CHECK_OK = 'previous _period check OK'  # eg. CN.LOW
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
    BUY_SELL_LIMIT = 'buy & sell at _limit'
    BUY_ADJUST_STOP_LOSS = 'buy & adjust stop loss'
    BUY_SELL_STOP_LOSS = 'buy & sell at stop loss'
    ACTIVATE_BREAKOUT = 'activate breakout for touch'
    BACK_TESTING = 'back testing'


class EST:  # EquityStatus
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class RST:  # ReplayStatus
    REPLAY = 'replay'
    STOP = 'stop'
    CANCEL = 'cancel'


class PTS:  # PatternTradeStatus
    NEW = 'new'
    IN_EXECUTION = 'in execution'
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
    BOLLINGER_BAND = 'Bollinger Band'

    @staticmethod
    def get_id(key: str):
        return {TBT.EXPECTED_WIN: 10, TBT.TOUCH_POINT: 20,  TBT.BOLLINGER_BAND: 30}.get(key)


class PDR:  # Pattern Deletion Reasons
    PATTERN_VANISHED = 'Pattern_vanished'
    WRONG_BREAKOUT = 'Wrong_breakout'
    BUYING_PROBLEM = 'Buying_problem'
    SELL_PROBLEM = 'Sell_problem'
    BUYING_PRECONDITION_PROBLEM = 'Buying_precondition_problem'
    TRADE_FINISHED = 'Trade_finished'
    SMA_PROBLEM = 'Simple_moving_average_problem'
    TRADE_CANCELLED = 'Trade manually cancelled'

    def get_id(key: str):
        return {PDR.PATTERN_VANISHED: 10, PDR.WRONG_BREAKOUT: 20, PDR.BUYING_PROBLEM: 25, PDR.TRADE_FINISHED: 40}.get(key)


class ST:  # Sell Trigger
    LIMIT = 'Limit'
    STOP_LOSS = 'Stop_loss'
    CANCEL = 'Cancellation'
    PATTERN_VANISHED = 'Pattern_vanished'
    PATTERN_END = 'Pattern_end'
    FORECAST_TICKS = 'Forecast_ticks_reached'

    def get_id(key: str):
        return {ST.LIMIT: 10, ST.STOP_LOSS: 20, ST.CANCEL: 25, ST.PATTERN_END: 40, ST.PATTERN_END: 50}.get(key)


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
    BEGIN_PREVIOUS = 'Begin previous _period'
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
    FIRST_LIMIT_REACHED = 'First _limit reached'
    STOP_LOSS_MAX_REACHED = 'Max stop loss reached (bound of original range)'


class DC:  # Data Columns
    ROWID = 'rowid'
    # for Stocks
    EQUITY_INDEX = 'Equity_Index'  # Index is a keyword for SQLite
    SYMBOL = 'Symbol'
    TIMESTAMP = 'Timestamp'
    DATE = 'Date'
    TIME = 'Time'
    OPEN = 'Open'
    HIGH = 'High'
    LOW = 'Low'
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
    EQUITY_TYPE = 'Equity_Type'  # Share, Commodities, Crypto Currency, Cash
    EQUITY_TYPE_ID = 'Equity_Type_ID'  # Share, Commodities, Crypto Currency, Cash
    EQUITY_ID = 'Equity_ID'  # e.g. USD, AAPL, ...
    EQUITY_NAME = 'Equity_Name'  # e.g. USD, Apple, ...
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
    TRADE_TYPE = 'Trade_Type'  # long, short, .... see TRT
    APEX_VALUE = 'APEX_Value'
    APEX_TS = 'APEX_Timestamp'
    # and additional for Trades
    TRADE_ID = 'Trade_ID'
    TRADE_STATUS = 'Trade_Status'
    TRADE_IS_SIMULATION = 'Trade_Simulation'
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

    # Additional Wave Columns
    WAVE_TYPE = 'Wave_Type'
    WAVE_TYPE_ID = 'Wave_Type_ID'
    WAVE_STRUCTURE = 'Wave_Structure'
    WAVE_STRUCTURE_ID = 'Wave_Structure_ID'
    W1_BEGIN_TS = 'W1_Begin_Timestamp'
    W1_BEGIN_DT = 'W1_Begin_Datetime'
    W1_BEGIN_VALUE = 'W1_Begin_Value'
    W2_BEGIN_TS = 'W2_Begin_Timestamp'
    W2_BEGIN_DT = 'W2_Begin_Datetime'
    W2_BEGIN_VALUE = 'W2_Begin_Value'
    W3_BEGIN_TS = 'W3_Begin_Timestamp'
    W3_BEGIN_DT = 'W3_Begin_Datetime'
    W3_BEGIN_VALUE = 'W3_Begin_Value'
    W4_BEGIN_TS = 'W4_Begin_Timestamp'
    W4_BEGIN_DT = 'W4_Begin_Datetime'
    W4_BEGIN_VALUE = 'W4_Begin_Value'
    W5_BEGIN_TS = 'W5_Begin_Timestamp'
    W5_BEGIN_DT = 'W5_Begin_Datetime'
    W5_BEGIN_VALUE = 'W5_Begin_Value'
    WAVE_END_TS = 'Wave_End_Timestamp'
    WAVE_END_DT = 'Wave_End_Datetime'
    WAVE_END_DATE = 'Wave_End_Date'  # this is NOT a real column - it's computed.
    WAVE_END_VALUE = 'Wave_End_Value'
    W1_RANGE = 'W1_Range'
    W2_RANGE = 'W2_Range'
    W3_RANGE = 'W3_Range'
    W4_RANGE = 'W4_Range'
    W5_RANGE = 'W5_Range'
    PARENT_WAVE_OID = 'Parent_Wave_OID'
    WAVE_IN_PARENT = 'Wave_in_parent'
    WAVE_END_FLAG = 'Wave_End_Flag'
    WAVE_MAX_RETR_PCT = 'Wave_Max_Retr_PCT'
    WAVE_MAX_RETR_TS_PCT = 'Wave_Max_Retr_Timestamp_PCT'

    FC_TS = 'FC_Timestamp'
    FC_DT = 'FC_Datetime'

    FC_C_WAVE_END_FLAG = 'FC_C_Wave_End_Flag'
    FC_C_WAVE_MAX_RETR_PCT = 'FC_C_Wave_Max_Retr_PCT'
    FC_C_WAVE_MAX_RETR_TS_PCT = 'FC_C_Wave_Max_Retr_Timestamp_PCT'

    FC_R_WAVE_END_FLAG = 'FC_R_Wave_End_Flag'
    FC_R_WAVE_MAX_RETR_PCT = 'FC_R_Wave_Max_Retr_PCT'
    FC_R_WAVE_MAX_RETR_TS_PCT = 'FC_R_Wave_Max_Retr_Timestamp_PCT'

    # Additional Asset Columns
    VALIDITY_DT = 'Validity_Datetime'
    VALIDITY_TS = 'Validity_Timestamp'
    LOCATION = 'Location'
    QUANTITY = 'Quantity'
    VALUE_PER_UNIT = 'Value_Unit'
    VALUE_TOTAL = 'Value_Total'
    CURRENCY = 'Currency'

    @staticmethod
    def get_columns_for_agent_environment():
        return [DC.TS_PATTERN_TICK_FIRST, DC.TS_PATTERN_TICK_LAST,
                DC.PATTERN_RANGE_BEGIN_DT, DC.PATTERN_RANGE_END_DT,
                DC.EXPECTED_WIN,
                DC.TRADE_BOX_OFF_SET, DC.TRADE_BOX_LIMIT_ORIG, DC.TRADE_BOX_STOP_LOSS_ORIG,
                DC.FC_HALF_POSITIVE_PCT, DC.FC_FULL_POSITIVE_PCT, DC.FC_HALF_NEGATIVE_PCT, DC.FC_FULL_NEGATIVE_PCT,
                DC.FC_TICKS_TO_POSITIVE_HALF, DC.FC_TICKS_TO_POSITIVE_FULL,
                DC.FC_TICKS_TO_NEGATIVE_HALF, DC.FC_TICKS_TO_NEGATIVE_FULL,
                DC.BUY_DT, DC.BUY_PRICE,
                DC.TRADE_REACHED_PRICE_PCT, DC.TRADE_RESULT_AMOUNT, DC.TRADE_RESULT_PCT]


class MDC:  # Metric data column
    VALID_DT = 'Valid_Date'
    MODEL = 'Model'
    TABLE = 'Table'
    PREDICTOR = 'Predictor'
    LABEL = 'Label'
    PATTERN_TYPE = 'Pattern_Type'
    VALUE = 'Value'
    PRECISION = 'Precision'
    RECALL = 'RECALL'
    F1_SCORE = 'F1_Score'
    ROC_AUC = 'ROC_AUC'


class TPMDC:  # Trade Policy Metric data column
    VALID_DT = 'Valid_Date'
    POLICY = 'Policy'
    EPISODES = 'Episodes'
    PERIOD = 'Period'
    AGGREGATION = 'Aggregation'
    TRADE_MEAN_AGGREGATION = 'Trade_Mean_Aggregation'
    PATTERN_TYPE = 'Pattern_Type'
    NUMBER_TRADES = 'Number_Trades'
    REWARD_PCT_TOTAL = 'Reward_percentage_total'
    REWARD_PCT_AVG = 'Reward_percentage_avg'


class EDC:  # Equity data column
    EQUITY_KEY = 'Key'
    EQUITY_NAME = 'Name'
    EQUITY_TYPE = 'Equity_Type'
    EXCHANGE = 'Exchange'
    VALID_FROM_DT = 'Valid_From_Date'
    VALID_TO_DT = 'Valid_To_Date'
    EQUITY_STATUS = 'Status'


class PRDC:  # Process data column
    PROCESS = 'Process'
    TRIGGER = 'Trigger'
    START_DT = 'Start_Date'
    START_TIME = 'Start_Time'
    END_DT = 'End_Date'
    END_TIME = 'End_Time'
    RUNTIME_SECONDS = 'Runtime_Seconds'
    COMMENT = 'Comment'


class JDC:  # Jobs data column
    NAME = 'Name'
    PERIOD = 'Period'
    WEEKDAYS = 'Weekdays'
    START_TIMES = 'Start times'
    NEXT_START_TIME = 'Next start'
    LAST_RUN = 'Last start'
    LAST_RUN_TIME = 'Runtime (sec.)'
    PROCESSED = 'pro/ins/upd/del'

    @staticmethod
    def get_all():
        return [JDC.NAME, JDC.PERIOD, JDC.WEEKDAYS, JDC.START_TIMES,
                JDC.NEXT_START_TIME, JDC.LAST_RUN, JDC.LAST_RUN_TIME, JDC.PROCESSED]

    @staticmethod
    def get_columns_for_job_table():
        return [JDC.NAME, JDC.START_TIMES, JDC.NEXT_START_TIME, JDC.LAST_RUN, JDC.LAST_RUN_TIME,
                JDC.PROCESSED, JDC.WEEKDAYS]
