"""
Description: This module tests the breakout prediction on accuracy - whether is can be used for prediction
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-01-14
"""

from pattern_predictor_breakout import BreakoutPredictor, MT


breakout_predictor = BreakoutPredictor(
    len_learning_range=10,
    train_model=True,
    number_symbols=10,
    manipulation_type=MT.ONE_ROW_MIXED_NOT_SCALED,
    breakout_level_threshold=0
)

