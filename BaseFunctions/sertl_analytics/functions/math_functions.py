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
    return p