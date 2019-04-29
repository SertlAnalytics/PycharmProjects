"""
Description: This module contains the html tab header table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import MyHTML, MyDCC
from salesman_dash.header_tables.my_tab_header_table import MyHTMLTabHeaderTable


class MyHTMLTabSearchHeaderTable(MyHTMLTabHeaderTable):
    @property
    def my_search_online_label_div(self):
        return 'my_search_online_label_div'

    @property
    def my_search_online_value_div(self):
        return 'my_search_online_value_div'

    @property
    def my_search_found_label_div(self):
        return 'my_search_found_label_div'

    @property
    def my_search_found_all_value_div(self):
        return 'my_search_found_all_value_div'

    @property
    def my_search_found_valid_value_div(self):
        return 'my_search_found_valid_value_div'

    @property
    def my_search_markdown(self):
        return 'my_search_markdown'

    @property
    def my_search_news_markdown(self):
        return 'my_search_news_markdown'

    def _init_cells_(self):
        online_label_div = MyHTML.div(self.my_search_online_label_div, 'Online Search', True)
        online_value_div = MyHTML.div(self.my_search_online_value_div, '', False)

        found_label_div = MyHTML.div(self.my_search_found_label_div, 'Found:', True)
        found_valid_value_div = MyHTML.div(self.my_search_found_valid_value_div, '0')
        found_all_value_div = MyHTML.div(self.my_search_found_all_value_div, '0')

        found_div = MyHTML.div_embedded([
            found_label_div, MyHTML.span(' '),
            found_valid_value_div, MyHTML.span('/'), found_all_value_div], inline=True)

        self.set_value(1, 1, MyHTML.div_embedded([online_label_div, MyHTML.span(' '), online_value_div]))
        self.set_value(1, 2, MyDCC.markdown(self.my_search_markdown))
        self.set_value(1, 3, MyHTML.div_embedded([found_div, MyHTML.span(' ')]))

