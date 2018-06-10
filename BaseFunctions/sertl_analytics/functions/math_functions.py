import numpy as np

def get_function_parameters(ind_left, value_left, ind_right, value_right):
    """
    Gets the function parameter for the linear function which joins both points on the x-y-diagram
    :param ind_left:
    :param value_left:
    :param ind_right:
    :param value_right:
    :return:
    """
    x = np.array([ind_left, ind_right])
    y = np.array([value_left, value_right])
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    # p[0] = round(p[0], 3)
    # p[1] = round(p[1], 2)
    return p


class ToleranceCalculator:
    @staticmethod
    def are_values_in_tolerance_range(val_1: float, val_2: float, tolerance_pct: float):
        test = abs((val_1 - val_2)/np.mean([val_1, val_2]))
        return True if 0 == val_1 == val_2 else abs((val_1 - val_2)/np.mean([val_1, val_2])) < tolerance_pct

    @staticmethod
    def are_values_in_function_tolerance_range(x: list, y: list, f, tolerance_pct: float):
        for k in range(len(x)):
            y_k = y[k]
            f_k = f(x[k])
            if not ToleranceCalculator.are_values_in_tolerance_range(y_k, f_k, tolerance_pct):
                return False
        return True