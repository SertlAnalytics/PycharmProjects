"""
Description: This module contains the callbacks handler classes for the tab search.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-15
"""

from sertl_analytics.constants.my_constants import MYDSHC
from sertl_analytics.mydash.my_dash_callback import DashCallback, DashCallbackParameter
from salesman_dash.input_tables.my_online_sale_table import MyHTMLSearchOnlineInputTable
from salesman_dash.my_dash_tab_elements import MyDashTabElements4Search
from salesman_sale_factory import SalesmanSaleFactory


class CallbackForSearchInput(DashCallback):
    """
       [Input(self._elements.my_search_button, 'n_clicks'),
         Input(self._elements.my_search_db_button, 'n_clicks'),
         Input(self._elements.my_search_file_button, 'n_clicks'),
         Input(self._elements.my_search_entities_dd, 'value'),
         ],
        [State(self._elements.my_search_source_dd, 'value'),
         State(self._elements.my_search_region_dd, 'value'),
         State(self._elements.my_search_category_dd, 'value'),
         State(self._elements.my_search_sub_category_dd, 'value'),
         State(self._elements.my_search_input, 'value'),
         State(self._elements.my_search_db_dd, 'value'),
         State(self._elements.my_search_file_dd, 'value'),
         ]
    """
    def __init__(self, tab_elements: MyDashTabElements4Search, sale_factory: SalesmanSaleFactory):
        self._tab_elements = tab_elements
        self._sale_factory = sale_factory
        DashCallback.__init__(self)

    def get_selected_db_row_id(self):
        return self.get_parameter_value(self._tab_elements.my_search_db_dd)

    def get_selected_file_row_number(self):
        return self.get_parameter_value(self._tab_elements.my_search_file_dd)

    def get_actual_search_value(self) -> str:
        button_clicked = self.get_clicked_button()
        if button_clicked is None:
            return self.get_parameter_value(self._tab_elements.my_search_input)
        if button_clicked.name == self._tab_elements.my_search_button:
            return self.get_parameter_value(self._tab_elements.my_search_input)
        elif button_clicked.name == self._tab_elements.my_search_db_button:
            sale = self._sale_factory.get_sale_from_db_by_row_id(self.get_selected_db_row_id())
            return sale.title
        elif button_clicked.name == self._tab_elements.my_search_file_button:
            sale = self._sale_factory.get_sale_from_file_by_row_number(self.get_selected_file_row_number())
            return sale.title

    def __get_parameter_list__(self):
        return [
            # Input
            DashCallbackParameter(self._tab_elements.my_search_button, MYDSHC.BUTTON),
            DashCallbackParameter(self._tab_elements.my_search_db_button, MYDSHC.BUTTON),
            DashCallbackParameter(self._tab_elements.my_search_file_button, MYDSHC.BUTTON),
            DashCallbackParameter(self._tab_elements.my_search_entities_dd, MYDSHC.DROP_DOWN),
            # State
            DashCallbackParameter(self._tab_elements.my_search_source_dd, MYDSHC.DROP_DOWN),
            DashCallbackParameter(self._tab_elements.my_search_region_dd, MYDSHC.DROP_DOWN),
            DashCallbackParameter(self._tab_elements.my_search_category_dd, MYDSHC.DROP_DOWN),
            DashCallbackParameter(self._tab_elements.my_search_sub_category_dd, MYDSHC.DROP_DOWN),
            DashCallbackParameter(self._tab_elements.my_search_input, MYDSHC.INPUT),
            DashCallbackParameter(self._tab_elements.my_search_db_dd, MYDSHC.DROP_DOWN),
            DashCallbackParameter(self._tab_elements.my_search_file_dd, MYDSHC.DROP_DOWN),
        ]