"""
Description: This module contains test cases for the Fibonacci wave predictions
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-02-20
"""

from pattern_database.stock_database import StockDatabase
from fibonacci.fibonacci_predictor import FibonacciPredictor
from sertl_analytics.constants.pattern_constants import PRED, STBL, FT, DC, MT, MDC, WPC


label = DC.WAVE_END_FLAG
# label = DC.WAVE_MAX_RETR_PCT
# label = DC.WAVE_MAX_RETR_TS_PCT
fib_prediction = FibonacciPredictor(StockDatabase(), 5)
# fib_prediction.train_models(label)
# fib_prediction.perform_cross_validation(label)





