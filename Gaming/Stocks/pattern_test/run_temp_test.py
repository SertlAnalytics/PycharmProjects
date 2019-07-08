import pandas as pd
from sertl_analytics.constants.pattern_constants import CN
import numpy as np


def get_data_series_for_value(value=0.0):
    f_upper = 2.0
    h_upper = 2.1
    f_lower = -2.0
    h_lower = -2.1
    v_array = np.array([f_upper, h_upper, f_lower, h_lower, value, value, value, value]).reshape([1, 8])
    df = pd.DataFrame(v_array, columns=[CN.F_UPPER, CN.H_UPPER, CN.F_LOWER, CN.H_LOWER,
                                        CN.HIGH, CN.LOW, CN.OPEN, CN.CLOSE])
    return df.iloc[0]

def get_data_series_for_value_by_dict(value=0.0):
    f_upper = 2.0
    h_upper = 2.1
    f_lower = -2.0
    h_lower = -2.1
    data_dict = {CN.F_UPPER: f_upper, CN.H_UPPER: h_upper, CN.F_LOWER: f_lower, CN.H_LOWER: h_lower,
                                        CN.HIGH: value, CN.LOW: value, CN.OPEN: value, CN.CLOSE: value}
    return pd.Series(data_dict)

data_series_by_df = get_data_series_for_value()
data_series_by_dict = get_data_series_for_value_by_dict()

print('type(data_series_by_df) = {}, {}'.format(type(data_series_by_df), data_series_by_df))
print('')
print('type(data_series_by_dict) = {}, {}'.format(type(data_series_by_dict), data_series_by_dict))
