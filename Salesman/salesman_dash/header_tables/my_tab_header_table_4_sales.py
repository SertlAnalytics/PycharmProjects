"""
Description: This module contains the html tab header table for the tab sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-10-03
"""

from sertl_analytics.mydash.my_dash_components import MyHTML, MyDCC
from salesman_dash.header_tables.my_tab_header_table import MyHTMLTabHeaderTable


class MyHTMLTabSalesHeaderTable(MyHTMLTabHeaderTable):
    @property
    def my_sales_position_label_div(self):
        return 'my_sales_position_label_div'

    @property
    def my_sales_position_div(self):
        return 'my_sales_position_div'

    @property
    def my_sales_markdown(self):
        return 'my_sales_markdown'

    @property
    def my_sales_news_markdown(self):
        return 'my_sales_news_markdown'

    def _init_cells_(self):
        ticker_label_div = MyHTML.div(self.my_sales_position_label_div, 'Position:', True)
        ticker_div = MyHTML.div(self.my_sales_position_div, '', False)

        self.set_value(1, 1, MyHTML.div_embedded([ticker_label_div, MyHTML.span(' '), ticker_div]))
        self.set_value(1, 2, MyDCC.markdown(self.my_sales_markdown))
        self.set_value(1, 3, MyDCC.markdown(self.my_sales_news_markdown))

