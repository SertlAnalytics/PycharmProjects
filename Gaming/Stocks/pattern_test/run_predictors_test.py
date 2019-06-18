"""
Description: This module contains the test cases for the pattern master_predictor optimizer
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-12

Pattern:
feature_columns=Ticks_Till_Pattern_Formed,Slope_Upper_PCT,Slope_Lower_PCT,Slope_Regression_PCT,Slope_Volume_Regression_PCT,Previous_Period_Half_Top_Out_PCT,Previous_Period_Full_Top_Out_PCT,Previous_Period_Half_Bottom_Out_PCT,Previous_Period_Full_Bottom_Out_PCT,Available_Fibonacci_Type_ID
label_columns=Touch_Points_Till_Breakout_Top,Touch_Points_Till_Breakout_Bottom

26,-2.0,-1.0,-1.0,-190.0,0.0,0.0,40.0,70.0,0
20,-1.0,-1.0,-1.0,10.0,50.0,50.0,0.0,20.0,0
"""

from pattern_predictor_optimizer import PatternPredictorOptimizer
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.constants.pattern_constants import FT, PRED, STBL, MT, DC


sys_config = SystemConfiguration()

master_predictor_list = [
    sys_config.master_predictor_for_trades,
    sys_config.master_predictor_touch_points,
    sys_config.master_predictor_before_breakout,
    sys_config.master_predictor_after_breakout
]

for master_predictor in master_predictor_list:
    patter_type_list = FT.get_all()
    for pattern_type in patter_type_list:
        print('Processing: {} - {}'.format(master_predictor.__class__.__name__, pattern_type))
        feature_columns = master_predictor.get_feature_columns(pattern_type)
        x_data = [1 for col in feature_columns]
        prediction_dict = master_predictor.predict_for_label_columns(pattern_type, x_data)
        print('{}: {}'.format(pattern_type, prediction_dict))