"""
Description: This module contains different functions for Bokeh.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""

import numpy as np

from bokeh.plotting import figure
from bokeh.io import output_file, show


class MyBokehClass:
    def __init__(self):
        pass

    @staticmethod
    def create_simple_line_graph():
        # prepare some data
        x = [1, 2, 3, 4, 5]
        y = [6, 7, 8, 9, 10]

        # prepare the output file
        output_file("Line.html")

        # create a figure object
        f = figure()

        # create line plot
        f.line(x, y)

        # write the plot in the figure object
        show(f)


my_class = MyBokehClass()
my_class.create_simple_line_graph()