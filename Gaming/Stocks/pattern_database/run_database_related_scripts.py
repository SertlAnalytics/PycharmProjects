"""
Description: This module tests/handles some database related methods.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-07-22
"""
from sertl_analytics.constants.pattern_constants import PRD, FT
from pattern_database.stock_database_updater import StockDatabaseUpdater
from pattern_predictor_optimizer import PatternPredictorOptimizer
from sertl_analytics.exchanges.bitfinex import BitfinexConfiguration
from pattern_system_configuration import SystemConfiguration

sys_config = SystemConfiguration()
stock_db = sys_config.db_stock
predictor_optimizer = PatternPredictorOptimizer(stock_db)

feature_columns_before_breakout = sys_config.pattern_table.get_feature_columns_before_breakout_for_statistics()
print('\nfeature_columns_before_breakout={}'.format(', '.join(feature_columns_before_breakout)))

label_columns_before_breakout = sys_config.pattern_table.get_label_columns_before_breakout_for_statistics()
print('\nlabel_columns_before_breakout={}'.format(', '.join(label_columns_before_breakout)))

feature_columns_after_breakout = sys_config.pattern_table.get_feature_columns_after_breakout_for_statistics()
print('\nfeature_columns_after_breakout={}'.format(', '.join(feature_columns_after_breakout)))

label_columns_after_breakout = sys_config.pattern_table.get_label_columns_after_breakout_for_statistics()
print('\nlabel_columns_after_breakout={}'.format(', '.join(label_columns_after_breakout)))

feature_columns_touch_points = sys_config.pattern_table.get_feature_columns_touch_points_for_statistics()
print('\nfeature_columns_touch_points={}'.format(', '.join(feature_columns_touch_points)))

label_columns_touch_points = sys_config.pattern_table.get_label_columns_touch_points_for_statistics()
print('\nlabel_columns_touch_points={}'.format(', '.join(label_columns_touch_points)))