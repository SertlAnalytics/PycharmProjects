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
    def my_sales_id_label_div(self):
        return 'my_sales_id_label_div'

    @property
    def my_sales_id_value_div(self):
        return 'my_sales_value_div'

    @property
    def my_sales_markdown(self):
        return 'my_sales_markdown'

    @property
    def my_sales_found_label_div(self):
        return 'my_sales_found_label_div'

    @property
    def my_sales_found_all_value_div(self):
        return 'my_sales_found_all_value_div'

    @property
    def my_sales_found_valid_value_div(self):
        return 'my_sales_found_valid_value_div'

    def _init_cells_(self):
        id_label_div = MyHTML.div(self.my_sales_id_label_div, 'Sale ID:', True)
        id_value_div = MyHTML.div(self.my_sales_id_value_div, '', False)

        found_label_div = MyHTML.div(self.my_sales_found_label_div, 'Available:', True)
        found_valid_value_div = MyHTML.div(self.my_sales_found_valid_value_div, '0')
        found_all_value_div = MyHTML.div(self.my_sales_found_all_value_div, '0')

        found_div = MyHTML.div_embedded([
            found_label_div, MyHTML.span(' '),
            found_valid_value_div, MyHTML.span('/'), found_all_value_div], inline=True)

        self.set_value(1, 1, MyHTML.div_embedded([id_label_div, MyHTML.span(' '), id_value_div]))
        self.set_value(1, 2, MyDCC.markdown(self.my_sales_markdown))
        self.set_value(1, 3, MyHTML.div_embedded([found_div, MyHTML.span(' ')]))

