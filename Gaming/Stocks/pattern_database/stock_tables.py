"""
Description: This module contains the configuration tables for stock database
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""


from sertl_analytics.datafetcher.database_fetcher import MyTable, MyTableColumn, CDT
from sertl_analytics.constants.pattern_constants import DC, PRD, STBL, MDC, PRED, EDC, TPMDC, PRDC
from sertl_analytics.mydates import MyDate


class PredictionFeatureTable:
    @staticmethod
    def is_label_column_for_regression(label_column: str):
        return False   # label_column[-4:] == '_PCT'


class ProcessTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.PROCESS

    def _add_columns_(self):
        self._columns.append(MyTableColumn(PRDC.PROCESS, CDT.STRING, 50))
        self._columns.append(MyTableColumn(PRDC.TRIGGER, CDT.STRING, 50))
        self._columns.append(MyTableColumn(PRDC.START_DT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.START_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.END_DT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.END_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(PRDC.RUNTIME_SECONDS, CDT.INTEGER))
        self._columns.append(MyTableColumn(PRDC.COMMENT, CDT.STRING, 200))


class EquityTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.EQUITY

    def __get_column_date__(self):
        return EDC.VALID_TO_DT

    def _add_columns_(self):
        self._columns.append(MyTableColumn(EDC.EQUITY_KEY, CDT.STRING, 10))
        self._columns.append(MyTableColumn(EDC.EQUITY_NAME, CDT.STRING, 50))
        self._columns.append(MyTableColumn(EDC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(EDC.EXCHANGE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(EDC.VALID_FROM_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(EDC.VALID_TO_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(EDC.EQUITY_STATUS, CDT.STRING, 20))


class MetricTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.METRIC

    def _add_columns_(self):
        self._columns.append(MyTableColumn(MDC.VALID_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(MDC.MODEL, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.TABLE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.PREDICTOR, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.LABEL, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.PATTERN_TYPE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(MDC.VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.PRECISION, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.RECALL, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.F1_SCORE, CDT.FLOAT))
        self._columns.append(MyTableColumn(MDC.ROC_AUC, CDT.FLOAT))

    def __get_key_column_name_list__(self):
        return [MDC.VALID_DT, MDC.TABLE, MDC.PREDICTOR, MDC.LABEL, MDC.PATTERN_TYPE, [MDC.VALUE]]


class TradePolicyMetricTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.TRADE_POLICY_METRIC

    def _add_columns_(self):
        self._columns.append(MyTableColumn(TPMDC.VALID_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(TPMDC.POLICY, CDT.STRING, 50))
        self._columns.append(MyTableColumn(TPMDC.EPISODES, CDT.INTEGER))
        self._columns.append(MyTableColumn(TPMDC.PERIOD, CDT.STRING, 50))
        self._columns.append(MyTableColumn(TPMDC.AGGREGATION, CDT.INTEGER))
        self._columns.append(MyTableColumn(TPMDC.TRADE_MEAN_AGGREGATION, CDT.INTEGER))
        self._columns.append(MyTableColumn(TPMDC.PATTERN_TYPE, CDT.STRING, 50))
        self._columns.append(MyTableColumn(TPMDC.NUMBER_TRADES, CDT.INTEGER))
        self._columns.append(MyTableColumn(TPMDC.REWARD_PCT_TOTAL, CDT.FLOAT))
        self._columns.append(MyTableColumn(TPMDC.REWARD_PCT_AVG, CDT.FLOAT))


class AssetTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.ASSET

    def __get_column_date__(self):
        return ''

    def __get_column_time_stamp__(self):
        return DC.VALIDITY_TS

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.VALIDITY_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.VALIDITY_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.LOCATION, CDT.STRING, 50))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.EQUITY_ID, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.EQUITY_NAME, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.QUANTITY, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.VALUE_PER_UNIT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.VALUE_TOTAL, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.CURRENCY, CDT.STRING, 10))

    @staticmethod
    def get_columns_for_statistics_category() -> list:
        return [DC.LOCATION, DC.EQUITY_TYPE, DC.EQUITY_NAME]

    @staticmethod
    def get_columns_for_statistics_x_variable() -> list:
        return [DC.VALIDITY_DT]

    @staticmethod
    def get_columns_for_statistics_y_variable() -> list:
        return [DC.VALUE_TOTAL]

    @staticmethod
    def get_columns_for_statistics_text_variable() -> list:
        return [DC.LOCATION, DC.EQUITY_TYPE, DC.VALUE_TOTAL]


class WaveTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.WAVE

    def __get_column_date__(self):
        return ''

    def __get_column_time_stamp__(self):
        return DC.WAVE_END_TS

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.EQUITY_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PERIOD_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.PERIOD_AGGREGATION, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TICKER_ID, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.TICKER_NAME, CDT.STRING, 50))
        self._columns.append(MyTableColumn(DC.WAVE_TYPE, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.WAVE_TYPE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.WAVE_STRUCTURE, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.WAVE_STRUCTURE_ID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W1_BEGIN_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W1_BEGIN_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.W1_BEGIN_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W2_BEGIN_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W2_BEGIN_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.W2_BEGIN_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W3_BEGIN_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W3_BEGIN_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.W3_BEGIN_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W4_BEGIN_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W4_BEGIN_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.W4_BEGIN_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W5_BEGIN_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.W5_BEGIN_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.W5_BEGIN_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.WAVE_END_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.WAVE_END_DT, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.WAVE_END_VALUE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W1_RANGE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W2_RANGE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W3_RANGE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W4_RANGE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.W5_RANGE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.PARENT_WAVE_OID, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.WAVE_IN_PARENT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.WAVE_END_FLAG, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.WAVE_MAX_RETR_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.WAVE_MAX_RETR_TS_PCT, CDT.FLOAT))

        self._columns.append(MyTableColumn(DC.FC_TS, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_DT, CDT.STRING, 20))

        self._columns.append(MyTableColumn(DC.FC_C_WAVE_END_FLAG, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.FC_C_WAVE_MAX_RETR_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_C_WAVE_MAX_RETR_TS_PCT, CDT.FLOAT))

        self._columns.append(MyTableColumn(DC.FC_R_WAVE_END_FLAG, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_R_WAVE_MAX_RETR_PCT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FC_R_WAVE_MAX_RETR_TS_PCT, CDT.FLOAT))

    def __get_key_column_name_list__(self):
        return [DC.EQUITY_TYPE_ID, DC.PERIOD_ID, DC.TICKER_ID, DC.WAVE_TYPE_ID, DC.WAVE_STRUCTURE_ID,
                DC.W1_BEGIN_TS, DC.W2_BEGIN_TS, DC.W3_BEGIN_TS, DC.W4_BEGIN_TS, DC.W5_BEGIN_TS, DC.WAVE_END_TS]

    def get_query_for_wave_counter(self, period: str, limit: int=0) -> str:
        ts_from = self.__get_from_time_stamp__(period, limit)
        return "Select Ticker_ID, count(*) FROM {} WHERE Period = '{}' and W1_Begin_Timestamp >= {} " \
               "GROUP BY Ticker_ID".format(self._name, period, ts_from)

    def get_query_for_recommender_records(self, limit: int):
        ts_from_daily = self.__get_from_time_stamp__(PRD.DAILY, limit)
        ts_from_intraday = self.__get_from_time_stamp__(PRD.INTRADAY)
        where_intraday = "Period = '{}' and W1_Begin_Timestamp >= {}".format(PRD.INTRADAY, ts_from_intraday)
        where_daily = "Period = '{}' and W1_Begin_Timestamp >= {}".format(PRD.DAILY, ts_from_daily)
        return "Select * FROM {} WHERE ({}) OR ({})".format(self._name, where_daily, where_intraday)

    @staticmethod
    def __get_from_time_stamp__(period: str, limit: int=0):
        limit = 2 if period == PRD.INTRADAY else limit  # to get only the waves of the last 2 days for intraday
        return MyDate.time_stamp_now() - (60 * 60 * 24 * limit)


class TradeTable(MyTable, PredictionFeatureTable):
    def __init__(self):
        MyTable.__init__(self)
        self._feature_columns_for_trades = self.__get_feature_columns_for_trades__()
        self._label_columns_for_trades = self.__get_label_columns_for_trades__()
        self._query_for_feature_and_label_data_for_trades = self.__get_query_for_feature_and_label_data_for_trades__()

    @property
    def id_columns(self) -> list:
        return [DC.ID, DC.PATTERN_TYPE]

    @property
    def feature_columns_for_trades(self):
        return self._feature_columns_for_trades

    @property
    def label_columns_for_trades(self):
        return self._label_columns_for_trades

    @property
    def query_for_feature_and_label_data_for_trades(self) -> str:
        return self._query_for_feature_and_label_data_for_trades

    @staticmethod
    def _get_name_():
        return STBL.TRADE

    def __get_column_date__(self):
        return ''

    def __get_column_time_stamp__(self):
        return DC.TS_PATTERN_TICK_LAST

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.ID, CDT.STRING, 200))
        self._columns.append(MyTableColumn(DC.PATTERN_ID, CDT.STRING, 100))  # foreign key
        self._columns.append(MyTableColumn(DC.TRADE_MEAN_AGGREGATION, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.TRADE_PROCESS, CDT.STRING, 20))
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
        self._columns.append(MyTableColumn(DC.PATTERN_RANGE_BEGIN_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_RANGE_BEGIN_TIME, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.PATTERN_RANGE_END_DT, CDT.DATE))
        self._columns.append(MyTableColumn(DC.PATTERN_RANGE_END_TIME, CDT.STRING, 10))
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

        self._columns.append(MyTableColumn(DC.TRADE_RESULT_AMOUNT, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.TRADE_RESULT_PCT, CDT.FLOAT))

        self._columns.append(MyTableColumn(DC.TRADE_RESULT, CDT.STRING, 10))
        self._columns.append(MyTableColumn(DC.TRADE_RESULT_ID, CDT.INTEGER))

    @staticmethod
    def __get_feature_columns_for_trades__():
        return [DC.BUY_TRIGGER_ID, DC.TRADE_STRATEGY_ID, DC.TRADE_BOX_TYPE_ID]

    @staticmethod
    def get_query_for_trading_optimizer():
        return "SELECT {}, {}, {}, {}, {}, {}, {} FROM trade WHERE {}='DAILY'".format(
            DC.ID, DC.TICKER_ID, DC.PATTERN_TYPE, DC.BUY_TRIGGER, DC.TRADE_STRATEGY,
            DC.TRADE_RESULT_PCT, DC.PATTERN_ID, DC.PERIOD
        )

    @staticmethod
    def get_feature_columns_for_trades_statistics():
        return [DC.BUY_TRIGGER, DC.TRADE_STRATEGY, DC.TRADE_BOX_TYPE, DC.TRADE_MEAN_AGGREGATION]

    @staticmethod
    def __get_label_columns_for_trades__():
        return [DC.TRADE_REACHED_PRICE_PCT, DC.TRADE_RESULT_ID]

    @staticmethod
    def get_label_columns_for_trades_statistics():
        return [DC.TRADE_REACHED_PRICE_PCT, DC.TRADE_RESULT_ID]

    @staticmethod
    def get_label_columns_for_predictor_for_statistics(predictor: str):
        if predictor == PRED.FOR_TRADE:
            return TradeTable.get_label_columns_for_trades_statistics()
        return TradeTable.get_label_columns_for_trades_statistics()

    @staticmethod
    def get_columns_for_replay() -> list:
        return [DC.TICKER_ID, DC.TICKER_NAME, DC.BUY_TRIGGER, DC.TRADE_STRATEGY, DC.PATTERN_TYPE,
                DC.PATTERN_RANGE_BEGIN_DT, DC.PATTERN_RANGE_BEGIN_TIME,
                DC.PATTERN_RANGE_END_DT, DC.PATTERN_RANGE_END_TIME, DC.TRADE_RESULT, DC.TRADE_RESULT_PCT,
                DC.PERIOD, DC.PERIOD_AGGREGATION, DC.ID]

    @staticmethod
    def get_columns_for_online_trades() -> list:
        return [DC.TRADE_STATUS, DC.TRADE_IS_SIMULATION, DC.TICKER_ID, DC.FC_SUMMARY_AFTER_BREAKOUT,
                DC.TRADE_STRATEGY, DC.PATTERN_TYPE,
                DC.BOUGHT_AT, DC.ACTUAL, DC.LIMIT, DC.STOP,
                DC.TRADE_RESULT_PCT,
                DC.PATTERN_RANGE_BEGIN_DT,
                DC.PATTERN_RANGE_BEGIN_TIME,
                DC.PATTERN_RANGE_END_DT,
                DC.PATTERN_RANGE_END_TIME,
                DC.PERIOD, DC.PERIOD_AGGREGATION, DC.ID]

    @staticmethod
    def get_columns_for_statistics() -> list:
        return [DC.TICKER_ID, DC.TICKER_NAME, DC.BUY_TRIGGER, DC.TRADE_STRATEGY, DC.PATTERN_TYPE,
                DC.PATTERN_RANGE_BEGIN_DT, DC.PATTERN_RANGE_END_DT, DC.TRADE_BOX_TYPE, DC.SELL_TRIGGER, DC.TRADE_RESULT]

    @staticmethod
    def get_columns_for_statistics_category(with_trade_process=False) -> list:
        if with_trade_process:
            return [DC.PATTERN_TYPE, DC.TRADE_STRATEGY, DC.TRADE_PROCESS]
        return [DC.PATTERN_TYPE, DC.TRADE_STRATEGY, DC.BUY_TRIGGER, DC.SELL_TRIGGER, DC.TRADE_BOX_TYPE]

    @staticmethod
    def get_columns_for_statistics_x_variable() -> list:
        return [DC.TRADE_MEAN_AGGREGATION, DC.PATTERN_RANGE_BEGIN_DT,
                DC.FC_FULL_POSITIVE_PCT, DC.FC_FULL_NEGATIVE_PCT,
                DC.FC_TICKS_TO_POSITIVE_FULL, DC.FC_TICKS_TO_NEGATIVE_FULL,
                DC.FC_BREAKOUT_DIRECTION, DC.FC_FALSE_BREAKOUT_ID]

    @staticmethod
    def get_columns_for_statistics_y_variable() -> list:
        return [DC.TRADE_REACHED_PRICE_PCT, DC.TRADE_RESULT_PCT]

    @staticmethod
    def get_table_style_cell_conditional() -> list:
        # ['Status', 'Simul', 'Ticker', 'FC after Breakout', 'Strategy', 'Type', 'ID']
        return [{'if': {'column_id': c}, 'textAlign': 'left'}
                for c in [DC.TRADE_STATUS, DC.TRADE_IS_SIMULATION, DC.TICKER_ID,
                          DC.FC_SUMMARY_AFTER_BREAKOUT, DC.TRADE_STRATEGY, DC.PATTERN_TYPE, DC.ID]]

    @staticmethod
    def get_table_style_data_conditional():
        column_id = DC.TRADE_RESULT_PCT
        filter_green = '{{{}}}  > 0'.format(DC.TRADE_RESULT_PCT)
        filter_red = '{{{}}}  < 0'.format(DC.TRADE_RESULT_PCT)
        return [
            {'if': {'column_id': column_id, 'filter': filter_green}, 'backgroundColor': 'green', 'color': 'white'},
            {'if': {'column_id': column_id, 'filter': filter_red}, 'backgroundColor': 'red', 'color': 'white'},
        ]

    @staticmethod
    def get_columns_for_statistics_text_variable() -> list:
        return [DC.TRADE_STRATEGY, DC.PATTERN_TYPE, DC.BUY_TRIGGER, DC.SELL_TRIGGER, DC.TRADE_RESULT]

    def __get_query_for_feature_and_label_data_for_trades__(self) -> str:
        return "SELECT {} FROM {} WHERE Trade_Result_ID != 0".format(
            self.__get_concatenated_feature_label_columns_for_trades__(), self._name)

    def __get_concatenated_feature_label_columns_for_trades__(self):
        return ', '.join(self.id_columns + self._feature_columns_for_trades + self._label_columns_for_trades)


class PatternTable(MyTable, PredictionFeatureTable):
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

    @property
    def id_columns(self) -> list:
        return [DC.ID, DC.PATTERN_TYPE]

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

    @staticmethod
    def get_columns_for_replay() -> list:
        return [DC.TICKER_ID, DC.TICKER_NAME, DC.PATTERN_TYPE, DC.PATTERN_BEGIN_DT, DC.PATTERN_END_DT,
                DC.BREAKOUT_DT, DC.BREAKOUT_DIRECTION, DC.EXPECTED_WIN, DC.EXPECTED_WIN_REACHED,
                DC.PERIOD, DC.PERIOD_AGGREGATION, DC.ID]

    @staticmethod
    def get_columns_for_statistics() -> list:
        return [DC.TICKER_ID, DC.TICKER_NAME, DC.PATTERN_TYPE, DC.PATTERN_BEGIN_DT, DC.PATTERN_END_DT,
                DC.BREAKOUT_DT, DC.BREAKOUT_DIRECTION, DC.EXPECTED_WIN, DC.EXPECTED_WIN_REACHED]

    @staticmethod
    def get_columns_for_statistics_category() -> list:
        return [DC.PATTERN_TYPE]

    @staticmethod
    def get_columns_for_statistics_x_variable() -> list:
        return [DC.PATTERN_BEGIN_DT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT,
                DC.SLOPE_LOWER_PCT, DC.SLOPE_UPPER_PCT, DC.SLOPE_REGRESSION_PCT, DC.SLOPE_BREAKOUT_PCT,
                DC.VOLUME_CHANGE_AT_BREAKOUT_PCT, DC.SLOPE_VOLUME_REGRESSION_PCT,
                DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT]

    @staticmethod
    def get_columns_for_statistics_y_variable() -> list:
        return [DC.EXPECTED_WIN, DC.EXPECTED_WIN_REACHED, DC.FC_FULL_POSITIVE_PCT,
                DC.FC_FULL_NEGATIVE_PCT, DC.FC_FALSE_BREAKOUT_ID]

    @staticmethod
    def get_columns_for_statistics_text_variable() -> list:
        return [DC.PATTERN_TYPE, DC.BREAKOUT_DIRECTION]

    def __get_column_date__(self):
        return ''

    def __get_column_time_stamp__(self):
        return DC.TS_PATTERN_TICK_LAST

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

        self._columns.append(MyTableColumn(DC.TRADE_TYPE, CDT.STRING, 10))  # new since 10.11.2018

    @staticmethod
    def _get_name_():
        return STBL.PATTERN

    def __get_query_for_feature_and_label_data_touch_points__(self) -> str:
        return "SELECT {} FROM {}".format(self.__get_concatenated_feature_label_columns_touch_points__(), self._name)

    def __get_query_for_feature_and_label_data_before_breakout__(self) -> str:
        return "SELECT {} FROM {}".format(self.__get_concatenated_feature_label_columns_before_breakout__(), self._name)

    def __get_query_for_feature_and_label_data_after_breakout__(self):
        return "SELECT {} FROM {}".format(self.__get_concatenated_feature_label_columns_after_breakout__(), self._name)

    def __get_concatenated_feature_label_columns_touch_points__(self):
        return ', '.join(self.id_columns + self._feature_columns_touch_points + self._label_columns_touch_points)

    def __get_concatenated_feature_label_columns_before_breakout__(self):
        return ', '.join(self.id_columns + self._feature_columns_before_breakout + self._label_columns_before_breakout)

    def __get_concatenated_feature_label_columns_after_breakout__(self):
        return ', '.join(self.id_columns + self._feature_columns_after_breakout + self._label_columns_after_breakout)

    @staticmethod
    def get_feature_columns_after_breakout_for_statistics():
        return PatternTable.__get_feature_columns_after_breakout__(True)

    @staticmethod
    def get_feature_columns_before_breakout_for_statistics():
        return PatternTable.__get_feature_columns_before_breakout__(True)

    @staticmethod
    def get_feature_columns_touch_points_for_statistics():
        return PatternTable.__get_feature_columns_before_breakout__(True)

    @staticmethod
    def __get_feature_columns_after_breakout__(for_statistics=False):
        return [DC.TICKS_TILL_PATTERN_FORMED, DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT,
                DC.SLOPE_UPPER_PCT, DC.SLOPE_LOWER_PCT, DC.SLOPE_REGRESSION_PCT,
                DC.SLOPE_BREAKOUT_PCT,
                DC.SLOPE_VOLUME_REGRESSION_PCT,
                DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT,
                DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM,
                DC.BREAKOUT_DIRECTION if for_statistics else DC.BREAKOUT_DIRECTION_ID,
                DC.VOLUME_CHANGE_AT_BREAKOUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_TOP_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_TOP_OUT_PCT,
                DC.PREVIOUS_PERIOD_HALF_BOTTOM_OUT_PCT, DC.PREVIOUS_PERIOD_FULL_BOTTOM_OUT_PCT,
                DC.AVAILABLE_FIBONACCI_TYPE if for_statistics else DC.AVAILABLE_FIBONACCI_TYPE_ID]

    @staticmethod
    def __get_feature_columns_before_breakout__(for_statistics=False):
        base_list = PatternTable.__get_feature_columns_after_breakout__(for_statistics)
        del base_list[base_list.index(DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT)]
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_TOP)]
        del base_list[base_list.index(DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM)]
        if for_statistics:
            del base_list[base_list.index(DC.BREAKOUT_DIRECTION)]
        else:
            del base_list[base_list.index(DC.BREAKOUT_DIRECTION_ID)]
        del base_list[base_list.index(DC.VOLUME_CHANGE_AT_BREAKOUT_PCT)]
        del base_list[base_list.index(DC.SLOPE_BREAKOUT_PCT)]
        del base_list[base_list.index(DC.SLOPE_VOLUME_REGRESSION_AFTER_PATTERN_FORMED_PCT)]
        return base_list

    @staticmethod
    def __get_feature_columns_touch_points__(for_statistics=False):
        base_list = PatternTable.__get_feature_columns_before_breakout__(for_statistics)
        return base_list

    @staticmethod
    def get_label_columns_after_breakout_for_statistics():
        return PatternTable.__get_label_columns_after_breakout__(True)

    @staticmethod
    def get_label_columns_before_breakout_for_statistics():
        return PatternTable.__get_label_columns_before_breakout__(True)

    @staticmethod
    def get_label_columns_touch_points_for_statistics():
        return PatternTable.__get_label_columns_touch_points__(True)

    @staticmethod
    def get_label_columns_for_predictor_for_statistics(predictor: str):
        if predictor == PRED.TOUCH_POINT:
            return PatternTable.__get_label_columns_touch_points__(True)
        elif predictor == PRED.BEFORE_BREAKOUT:
            return PatternTable.__get_label_columns_before_breakout__(True)
        return PatternTable.__get_label_columns_after_breakout__(True)

    @staticmethod
    def __get_label_columns_after_breakout__(for_statistics=False):
        # return [DC.FALSE_BREAKOUT]
        return [DC.NEXT_PERIOD_HALF_POSITIVE_PCT, DC.NEXT_PERIOD_FULL_POSITIVE_PCT,
                DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, DC.NEXT_PERIOD_FULL_NEGATIVE_PCT,
                DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL,
                DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL,
                DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_before_breakout__(for_statistics=False):
        return [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, DC.BREAKOUT_DIRECTION_ID, DC.FALSE_BREAKOUT]

    @staticmethod
    def __get_label_columns_touch_points__(for_statistics=False):
        return [DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM]


class StocksTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.STOCKS

    @property
    def id_columns(self) -> list:
        return [DC.PERIOD, DC.PERIOD_AGGREGATION, DC.SYMBOL, DC.TIMESTAMP]

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.PERIOD, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.PERIOD_AGGREGATION, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.SYMBOL, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.TIMESTAMP, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.DATE, CDT.DATE))
        self._columns.append(MyTableColumn(DC.TIME, CDT.TIME))
        self._columns.append(MyTableColumn(DC.OPEN, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.HIGH, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.LOW, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.CLOSE, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.VOLUME, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.BIG_MOVE, CDT.BOOLEAN, default=False))
        self._columns.append(MyTableColumn(DC.DIRECTION, CDT.INTEGER, default=0)) # 1 = up, -1 = down, 0 = no big move

    def get_query_for_unique_record(self, symbol: str, time_stamp: int, period: str, aggregation: int):
        return "SELECT * from {} WHERE {}='{}' and {}={} and {}='{}' and {}={}".format(
            self._name, DC.SYMBOL, symbol, DC.TIMESTAMP, time_stamp, DC.PERIOD, period,
            DC.PERIOD_AGGREGATION, aggregation)

    def get_distinct_symbol_query(self, symbol_input: str = '', like_input: str = '') -> str:
        query = 'SELECT DISTINCT Symbol from {}'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        return query.format(self._name)

    @staticmethod
    def get_process_type_for_update(period: str, aggregation: int, dt_now_time_stamp, last_loaded_time_stamp):
        delta_time_stamp = dt_now_time_stamp - last_loaded_time_stamp
        delta_time_stamp_min = int(delta_time_stamp / 60)
        delta_time_stamp_days = int(delta_time_stamp_min / (24 * 60))
        if period == PRD.DAILY:
            if delta_time_stamp_days < 2:
                return 'NONE'
            elif delta_time_stamp_days < 50:
                return 'COMPACT'
            else:
                return 'FULL'
        else:
            if delta_time_stamp_min < aggregation:
                return 'NONE'
            else:
                return 'FULL'


class CompanyTable(MyTable):
    @staticmethod
    def _get_name_():
        return STBL.COMPANY

    def _add_columns_(self):
        self._columns.append(MyTableColumn(DC.SYMBOL, CDT.STRING, 20))
        self._columns.append(MyTableColumn(DC.NAME, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.TO_BE_LOADED, CDT.BOOLEAN, default=False))
        self._columns.append(MyTableColumn(DC.SECTOR, CDT.STRING, 100))
        self._columns.append(MyTableColumn(DC.YEAR, CDT.INTEGER))
        self._columns.append(MyTableColumn(DC.REVENUES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.EXPENSES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.EMPLOYEES, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.SAVINGS, CDT.FLOAT))
        self._columns.append(MyTableColumn(DC.FORECAST_GROWTH, CDT.FLOAT))

    @staticmethod
    def get_select_query(symbol_input='', like_input='') -> str:
        query = 'SELECT * FROM Company'
        if symbol_input != '':
            query += ' WHERE Symbol = "' + symbol_input + '"'
        elif like_input != '':
            query += ' WHERE Symbol like "%' + like_input + '"'
        query += ' ORDER BY Symbol'
        return query

    @staticmethod
    def get_alternate_name(ticker: str, name: str):
        dic_alternate = {'GOOG': 'Alphabeth', 'LBTYK': 'Liberty', 'FOX': 'Twenty-First Century'}
        return dic_alternate[ticker] if ticker in dic_alternate else name

    @staticmethod
    def get_insert_dict_for_company(symbol: str, name: str, to_be_loaded: bool) -> dict:
        return {'Symbol': symbol, 'Name': name, 'ToBeLoaded': to_be_loaded, 'Sector': '', 'Year': 2018, 'Revenues': 0,
                'Expenses': 0, 'Employees': 0, 'Savings': 0, 'ForcastGrowth': 0}

