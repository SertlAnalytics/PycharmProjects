"""
Description: This module contains  a test case for class variables compared with instance variables
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-03-25
"""


import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import sys


def name_decorator(func):
    def function_wrapper(*args, **kwargs):
        __name__ = 'test'
        return func(*args, **kwargs)
    return function_wrapper


class Test:
    def __init__(self):
        self.name = 'MyTest'

    @name_decorator
    def my_function(self):
        print('Function name={}'.format(__name__))
        # modules = sys.modules[__name__]
        # name = sys._getframe(1).f_code.co_name
        # trace = sys.gettrace()
        print('Hallo: {}'.format(__name__))


def print_function_name(func):
    print(func.__name__)


test = Test()
# print_function_name(test.my_function)
test.my_function()

