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


class OPTC:  # PredictorOptimizer test cases
    OPTIMAL_PREDICTION = 'optimal prediction'
    VALUE_LIST = 'value list'
    MODEL_TEST = 'model test'


test_case = OPTC.MODEL_TEST
sys_config = SystemConfiguration()
optimizer = PatternPredictorOptimizer(sys_config.db_stock)
x_lists = [[26,-2.0,-1.0,-1.0,-190.0,0.0,0.0,40.0,70.0,0], [20,-1.0,-1.0,-1.0,10.0,50.0,50.0,0.0,20.0,0]]
label_list = ['Touch_Points_Till_Breakout_Top' , 'Touch_Points_Till_Breakout_Bottom']
# label_list = [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, DC.BREAKOUT_DIRECTION_ID, DC.FALSE_BREAKOUT]

predictor_label_dict = {
    PRED.TOUCH_POINT: [DC.TOUCH_POINTS_TILL_BREAKOUT_TOP, DC.TOUCH_POINTS_TILL_BREAKOUT_BOTTOM],
    PRED.BEFORE_BREAKOUT: [DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, DC.BREAKOUT_DIRECTION_ID, DC.FALSE_BREAKOUT],
    PRED.AFTER_BREAKOUT: [DC.NEXT_PERIOD_HALF_POSITIVE_PCT, DC.NEXT_PERIOD_FULL_POSITIVE_PCT,
                DC.NEXT_PERIOD_HALF_NEGATIVE_PCT, DC.NEXT_PERIOD_FULL_NEGATIVE_PCT,
                DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_POSITIVE_FULL,
                DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_HALF, DC.TICKS_FROM_BREAKOUT_TILL_NEGATIVE_FULL,
                DC.FALSE_BREAKOUT]
}

if test_case == OPTC.OPTIMAL_PREDICTION:
    for x_list in x_lists:
        for label in label_list:
            prediction = optimizer.predict(STBL.PATTERN, PRED.TOUCH_POINT, FT.ALL, label, x_list)
            print('optimal prediction for {}: {}'.format(label, prediction))
elif test_case == OPTC.VALUE_LIST:
    for predictor in predictor_label_dict:
        for label in predictor_label_dict[predictor]:
            print('Testing {}: {}'.format(predictor, label))
            sorted_value_list_for_predictor_label = optimizer.get_sorted_value_list_for_predictor_label(
                MT.RANDOM_FOREST, STBL.PATTERN, predictor, label, FT.ALL
            )
            print(sorted_value_list_for_predictor_label)
            break
        break
else:
    optimizer.test_model(
        MT.SVM, STBL.PATTERN, PRED.BEFORE_BREAKOUT, DC.TICKS_FROM_PATTERN_FORMED_TILL_BREAKOUT, FT.ALL)




