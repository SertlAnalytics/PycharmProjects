"""
Description: This module contains plotting examples.
Source: DataCamp - Introduction to Data Visualization with Python - 2018
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-03-11
"""
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


class MyPlotter:
    def __init__(self, x_values, y_values):
        self.x_values = x_values
        self.y_values = y_values

    def plot(self):
        plt.plot(self.x_values, self.y_values)

    def show(self):
        plt.show()

