"""
Description: This module contains the tab header table for the dash application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS, MyHTML, MyDCC


class MyHTMLTabHeaderTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 1, 3)

    def _init_cells_(self):
        self.set_value(1, 1, '')
        self.set_value(1, 2, '')
        self.set_value(1, 3, '')

    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '60%', '20%'][col - 1]
        bg_color = COLORS[2]['background']
        color = COLORS[2]['text']
        text_align = ['left', 'center', 'left'][col - 1]
        v_align = ['top', 'top', 'top'][col - 1]
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}

