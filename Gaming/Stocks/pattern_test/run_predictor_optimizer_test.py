"""
Description: This module contains the test cases for the pattern predictor optimizer
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-12-12

Pattern:
feature_columns=Ticks_Till_Pattern_Formed,Slope_Upper_PCT,Slope_Lower_PCT,Slope_Regression_PCT,Slope_Volume_Regression_PCT,Previous_Period_Half_Top_Out_PCT,Previous_Period_Full_Top_Out_PCT,Previous_Period_Half_Bottom_Out_PCT,Previous_Period_Full_Bottom_Out_PCT,Available_Fibonacci_Type_ID
label_columns=Touch_Points_Till_Breakout_Top,Touch_Points_Till_Breakout_Bottom

26,-2.0,-1.0,-1.0,-190.0,0.0,0.0,40.0,70.0,0
20,-1.0,-1.0,-1.0,10.0,50.0,50.0,0.0,20.0,0
"""

from pattern_predictor import PatternPredictorOptimizer
from pattern_system_configuration import SystemConfiguration
from sertl_analytics.constants.pattern_constants import FT, PRED, STBL, MT

sys_config = SystemConfiguration()
optimizer = PatternPredictorOptimizer(sys_config.config, sys_config.db_stock)
x_lists = [[26,-2.0,-1.0,-1.0,-190.0,0.0,0.0,40.0,70.0,0], [20,-1.0,-1.0,-1.0,10.0,50.0,50.0,0.0,20.0,0]]
label_list = ['Touch_Points_Till_Breakout_Top' , 'Touch_Points_Till_Breakout_Bottom']
for x_list in x_lists:
    for label in label_list:
        prediction = optimizer.predict(STBL.PATTERN, PRED.TOUCH_POINT, label, x_list)
        print('optimal prediction for {}: {}'.format(label, prediction))




