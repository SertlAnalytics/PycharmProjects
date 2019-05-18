"""
Description: This module contains the element ids dash tab for recommendations from various sources, e.g. bitfinex, Nasdaq...
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-11-14
"""

from salesman_dash.input_tables.my_online_sale_table import MyHTMLSearchOnlineInputTable
from salesman_dash.my_dash_tab_dd_for_search import SearchTabDropDownHandler, SRDD


class MyDashTabElements4Search:
    def __init__(self, dd_handler: SearchTabDropDownHandler, search_table: MyHTMLSearchOnlineInputTable):
        self.my_search_result_grid_table = 'my_search_result_grid_table'
        self.my_search_result_grid_table_div = '{}_div'.format(self.my_search_result_grid_table)
        self.my_search_result_entry_link = 'my_search_result_entry_link'
        self.my_search_result_graph_div = 'my_search_result_graph_div'
        self.my_search_div = 'my_search_div'
        self.my_search_result_grid_table = 'my_search_result_grid_table'
        self.my_search_result_entry_markdown = 'my_search_result_entry_markdown'
        self.my_search_result_grid_table_div = '{}_div'.format(self.my_search_result_grid_table)
        self.my_search_online_input_table = 'my_search_online_input_table'
        self.my_search_online_input_table_div = '{}_div'.format(self.my_search_online_input_table)
        self.my_search_test_markdown = 'my_search_test_markdown'
        self.my_search_input_markdown = 'my_search_input_markdown'
        # add elements from drop down handler
        self.my_search_source_dd = dd_handler.my_search_source_dd
        self.my_search_region_dd = dd_handler.my_search_region_dd
        self.my_search_category_dd = dd_handler.my_search_category_dd
        self.my_search_sub_category_dd = dd_handler.my_search_sub_category_dd
        self.my_search_entities_dd = dd_handler.my_search_entities_dd
        # refresh button
        self.my_search_refresh_button = 'my_search_refresh_button'
        # add elements from online search table
        self.my_search_input = search_table.my_search_input
        self.my_search_button = search_table.my_search_button
        self.my_search_db_dd = search_table.my_search_db_dd
        self.my_search_db_button = search_table.my_search_db_button
        self.my_search_file_dd = search_table.my_search_file_dd
        self.my_search_file_button = search_table.my_search_file_button


