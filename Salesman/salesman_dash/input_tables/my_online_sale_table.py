"""
Description: This module contains the html tab header table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import MyHTML
from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS
from salesman_dash.my_dash_tab_dd_for_search import SearchTabDropDownHandler, SRDD


class MyHTMLInputTable(MyHTMLTable):
    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '60%', '20%'][col - 1]
        bg_color = COLORS[2]['background']
        color = COLORS[2]['text']
        text_align = ['left', 'left', 'left'][col - 1]
        v_align = ['top', 'top', 'top'][col - 1]
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLSearchOnlineInputTable(MyHTMLInputTable):
    def __init__(self, dd_handler: SearchTabDropDownHandler):
        self._dd_handler = dd_handler
        MyHTMLTable.__init__(self, 3, 3)
        self.search_button_n_clicks = 0
        self.search_button_db_n_clicks = 0
        self.search_button_file_n_clicks = 0
        self.search_input_n_blur = 0

    @property
    def my_search_input(self):
        return 'my_search_input'

    @property
    def my_search_db_dd(self):
        return self._dd_handler.my_search_db_dd

    @property
    def my_search_file_dd(self):
        return self._dd_handler.my_search_file_dd

    @property
    def my_search_input_label_div(self):
        return '{}_label_div'.format(self.my_search_input)

    @property
    def my_search_db_label_div(self):
        return '{}_label_div'.format(self.my_search_db_dd)

    @property
    def my_search_file_label_div(self):
        return '{}_label_div'.format(self.my_search_file_dd)

    @property
    def my_search_button(self):
        return 'my_search_button'

    @property
    def my_search_button_db(self):
        return 'my_search_button_db'

    @property
    def my_search_button_file(self):
        return 'my_search_button_file'

    def was_any_button_clicked(self):
        return self.search_button_n_clicks + self.search_button_db_n_clicks + self.search_button_file_n_clicks > 0

    def _init_cells_(self):
        self._init_cells_for_search_by_input__()
        self._init_cells_for_search_by_database_entries__()
        self._init_cells_for_search_by_file_entries__()

    def _init_cells_for_search_by_input__(self):
        input_label_div = MyHTML.div(self.my_search_input_label_div, 'Search input:', True)
        input_field = MyHTML.div_with_textarea(
            element_id=self.my_search_input, placeholder='Please enter search string...', size=650, height=50)
        button_search = MyHTML.div_with_html_button_submit(self.my_search_button, 'Search', hidden='')

        self.set_value(1, 1, input_label_div)
        self.set_value(1, 2, input_field)
        self.set_value(1, 3, button_search)

    def _init_cells_for_search_by_database_entries__(self):
        input_label_div = MyHTML.div(self.my_search_db_label_div, 'Search by database:', True)
        drop_down = MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_DATABASE)),
        button_search = MyHTML.div_with_html_button_submit(self.my_search_button_db, 'Search', hidden='')

        self.set_value(2, 1, input_label_div)
        self.set_value(2, 2, drop_down)
        self.set_value(2, 3, button_search)

    def _init_cells_for_search_by_file_entries__(self):
        input_label_div = MyHTML.div(self.my_search_file_label_div, 'Search by file:', True)
        drop_down = MyHTML.div_with_dcc_drop_down(**self._dd_handler.get_drop_down_parameters(SRDD.SEARCH_FILE)),
        button_search = MyHTML.div_with_html_button_submit(self.my_search_button_file, 'Search', hidden='')

        self.set_value(3, 1, input_label_div)
        self.set_value(3, 2, drop_down)
        self.set_value(3, 3, button_search)



