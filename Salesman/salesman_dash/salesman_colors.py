"""
Description: This module contains the pattern plotting classes - central for stock data plotting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from salesman_tutti.tutti import Tutti
from sertl_analytics.mydash.my_dash_color_handler import DashColorHandler


class SalesmanColorHandler(DashColorHandler):
    @staticmethod
    def get_colors_for_pattern_trade(tutti: Tutti):
        if tutti is None:
            return 'salmon', 'orangered', 'lightgreen', 'green'  # for watching, buying, selling, after_selling
        else:
            return 'salmon', 'orangered', 'lightgreen', 'red' # for watching, buying, selling, after_selling
