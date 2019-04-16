"""
Description: This module contains the html tab header table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import MyHTML
from sertl_analytics.mydash.my_dash_components import MyHTMLTable, COLORS


class MyHTMLInputTable(MyHTMLTable):
    def __init__(self):
        MyHTMLTable.__init__(self, 2, 3)

    def _get_cell_style_(self, row: int, col: int):
        width = ['20%', '60%', '20%'][col - 1]
        bg_color = COLORS[2]['background']
        color = COLORS[2]['text']
        text_align = ['left', 'left', 'left'][col - 1]
        v_align = ['top', 'top', 'top'][col - 1]
        return {'width': width, 'background-color': bg_color, 'color': color, 'text-align': text_align,
                'vertical-align': v_align, 'padding': self.padding_cell}


class MyHTMLSaleOnlineInputTable(MyHTMLInputTable):
    @property
    def my_sales_title_label_div(self):
        return 'my_sales_title_label_div'

    @property
    def my_sales_description_label_div(self):
        return 'my_sales_description_label_div'

    @property
    def my_sales_title_input(self):
        return 'my_sales_title_input'

    @property
    def my_sales_description_input(self):
        return 'my_sales_description_input'

    @property
    def my_sales_online_search_button(self):
        return 'my_sales_online_search_button'

    def _init_cells_(self):
        self.set_value(1, 1, 'Title')
        self.set_value(2, 1, 'Description')

        title_label_div = MyHTML.div(self.my_sales_title_label_div, 'Title:', True)
        description_label_div = MyHTML.div(self.my_sales_description_label_div, 'Description:', True)

        title_input = MyHTML.div_with_input(element_id=self.my_sales_title_input,
                                            placeholder='Please enter title...', size=500, height=27)

        description_input = MyHTML.div_with_textarea(element_id=self.my_sales_description_input,
                                                     placeholder='Please enter description...', size=500, height=100)

        button_search = MyHTML.div_with_html_button_submit(self.my_sales_online_search_button, 'Search', hidden='')

        self.set_value(1, 1, title_label_div)
        self.set_value(1, 2, title_input)
        self.set_value(2, 1, description_label_div)
        self.set_value(2, 2, description_input)
        self.set_value(2, 3, button_search)


