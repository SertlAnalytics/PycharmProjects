"""
Description: This module contains the test cases for the fibonacci wave handler
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from fibonacci.fibonacci_wave_handler import FibonacciWaveHandler
from sertl_analytics.constants.pattern_constants import WAVEST, DC, PRD, INDICES


index_selected = INDICES.DOW_JONES
wave_type_selected = WAVEST.INTRADAY_DESC
wave_handler = FibonacciWaveHandler(100)
a = wave_handler.get_waves_numbers_with_dates_for_wave_type_and_index_for_days(wave_type_selected, index_selected)
print('{} - {}: \n{}'.format(index_selected, wave_type_selected, a))
