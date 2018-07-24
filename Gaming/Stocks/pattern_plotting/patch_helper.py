"""
Description: This module contains the pattern patch helper class
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np


class PatchHelper:
    @staticmethod
    def get_id_for_polygon(patch) -> str:
        return_string = ''
        if PatchHelper.get_patch_type(patch) == 'Polygon':
            xy = patch.get_xy().round(2)
            xy_reshaped = xy.reshape(xy.size)
            for elements in xy_reshaped:
                return_string = return_string + ('' if return_string == '' else '-') + str(elements)
        return return_string

    @staticmethod
    def is_xy_close_to_polygon(x: float, y: float, patch, tolerance_range) -> bool:
        if x is None:
            return False
        if PatchHelper.get_patch_type(patch) == 'Polygon':
            xy = patch.get_xy().round(2)
            for k in range(0, xy.shape[0] - 1):
                x_01, x_02 = xy[k, 0], xy[k+1, 0]
                if x_01 <= x <= x_02:
                    y_01, y_02 = xy[k, 1], xy[k + 1, 1]
                    np_array = np.polyfit(np.array([x_01, x_02]), np.array([y_01, y_02]), 1)
                    linear_function = np.poly1d([np_array[0], np_array[1]])
                    distance = abs(y - linear_function(x))
                    if distance < tolerance_range:
                        return True
        return False

    @staticmethod
    def get_patch_type(patch):
        return patch.__class__.__name__
