"""
Description: This module contains test cases for access layer methods
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from pattern_database.stock_database import StockDatabase
from sertl_analytics.constants.pattern_constants import PRD, WAVEST, INDICES
from fibonacci.fibonacci_wave_data import FibonacciWaveDataHandler


class FWDHTC:  # FibonacciWaveDataHandler TestCase
    RELOAD = 'Reload'
    HEAT_MAP = 'Heatmap'


fibonacci_wave_data_handler = FibonacciWaveDataHandler(StockDatabase())
fibonacci_wave_data_handler.load_data(period=PRD.INTRADAY, aggregation=30)

test_case = FWDHTC.HEAT_MAP

if test_case == FWDHTC.RELOAD:
    fibonacci_wave_data_handler.reload_data_when_outdated()
elif test_case == FWDHTC.HEAT_MAP:
    period = PRD.INTRADAY
    aggregation = 30
    index = INDICES.CRYPTO_CCY
    fibonacci_wave_data_handler.init_tick_key_list_for_retrospection(100, period=period, aggregation=aggregation)
    x_data = fibonacci_wave_data_handler.tick_key_list_for_retrospection
    y_data = WAVEST.get_waves_types_for_processing([fibonacci_wave_data_handler.period_for_retrospection])
    z_data = [fibonacci_wave_data_handler.get_waves_number_list_for_wave_type_and_index(wt, index) for wt in y_data]
    print('__get_data_for_heatmap_figure__: {}: \n{}\n{}'.format(index, x_data, y_data))
    for index_z, z_data_list in enumerate(z_data):
        z_data_list_with_numbers = []
        for index, key in enumerate(x_data):
            if z_data_list[index] > 0:
                z_data_list_with_numbers.append('{}: {}'.format(key, z_data_list[index]))
        print('{}: {}'.format(y_data[index_z], z_data_list_with_numbers))


