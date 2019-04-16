"""
Description: This module contains the html header tab table for the log tab
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.constants.pattern_constants import LOGT
from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS, MyHTML
from salesman_dash.header_tables.my_tab_header_table import MyHTMLTabHeaderTable


class MyHTMLTabLogHeaderTable(MyHTMLTabHeaderTable):
    def __init__(self):
        self._column_number = len(self.__get_table_header_dict__())
        MyHTMLTable.__init__(self, 3, self._column_number)

    def _init_cells_(self):
        column_number = 0
        table_header_dict = self.__get_table_header_dict__()
        today_label_div = MyHTML.div('my_log_today_label_div', 'Today', True)
        all_label_div = MyHTML.div('my_log_all_label_div', 'All', True)
        for log_type, title in table_header_dict.items():
            column_number += 1
            label_div = MyHTML.div('my_log_{}_label_div'.format(log_type), title, True)
            today_value_div = MyHTML.div('my_log_{}_today_value_div'.format(log_type), '0', bold=False)
            all_value_div = MyHTML.div('my_log_{}_all_value_div'.format(log_type), '0', bold=False)
            self.set_value(1, column_number, label_div)
            if log_type == LOGT.DATE_RANGE:
                self.set_value(2, 1, today_label_div)
                self.set_value(3, 1, all_label_div)
            else:
                self.set_value(2, column_number, today_value_div)
                self.set_value(3, column_number, all_value_div)

    @staticmethod
    def get_title_for_log_type(log_type: str):
        table_header_dict = MyHTMLTabLogHeaderTable.__get_table_header_dict__()
        return table_header_dict.get(log_type)

    @staticmethod
    def get_types_for_processing_as_options():
        header_dict = MyHTMLTabLogHeaderTable.__get_table_header_dict__()
        log_types = LOGT.get_log_types_for_processing()
        return [{'label': header_dict[log_type], 'value': log_type} for log_type in log_types]

    @staticmethod
    def __get_table_header_dict__():
        return {LOGT.DATE_RANGE: 'Date range',
                LOGT.ERRORS: 'Errors',
                LOGT.PROCESSES: 'Processes',
                LOGT.SCHEDULER: 'Scheduler',
                LOGT.MESSAGE_LOG: 'Salesman log',
                LOGT.PATTERNS: 'Pattern',
                LOGT.WAVES: 'Waves',
                LOGT.TRADES: 'Trades (add/buy)'}

    def _get_cell_style_(self, row: int, col: int):
        base_width = int(100/self._column_number)
        width_list = ['{}%'.format(base_width) for k in range(0, self._column_number)]
        width = width_list[col - 1]
        bg_color = COLORS[2]['background'] if row == 1 or col == 1 else COLORS[1]['background']
        color = COLORS[2]['text']
        text_align = 'left' if col == 1 else 'center'
        v_align = 'top'
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}

