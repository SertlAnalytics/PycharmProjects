"""
Description: This module is the test module for the factory classes for Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-21
"""
from sertl_analytics.constants.salesman_constants import SLDC
from sertl_analytics.mydates import MyDate
from factories.salesman_sale_factory import SalesmanSaleFactory
from salesman_sale_list  import SalesmanSaleList
from salesman_sale import SalesmanSale
from salesman_system_configuration import SystemConfigurationForTest
from salesman_tutti.tutti import Tutti
from testing.test_data import SaleTestDataFactory, TCKEY


class SalesmanSaleFactoryTest(SalesmanSaleFactory):
    def __init__(self, delete_old_test_cases=True):
        self._delete_old_test_cases = delete_old_test_cases
        self.sys_config = SystemConfigurationForTest()
        self._tutti = Tutti(self.sys_config)
        SalesmanSaleFactory.__init__(self, self.sys_config, self._tutti.salesman_spacy)
        if self._delete_old_test_cases:
            self.delete_all_test_cases_in_db()

    def test_write_sales_after_checks_to_db(self):
        sales, sale_master = self.__get_sales_and_master_sale_for_test_run__()
        self.write_sales_after_checks_to_db(sales, sale_master, enforce_writing=True)
        self.print_test_results()
        print('\nTest: Does the child sale disappear in v_sale when End_Date is set in relation?')
        self.update_sale_relation_end_date(sales[1].sale_id, sale_master.sale_id, MyDate.today_str())
        self.print_test_results(['V_SALE', 'SALE_RELATION'])
        print('\nTest: Is the relation set back to active after loading again?')
        self.write_sales_after_checks_to_db(sales, sale_master, enforce_writing=True)
        self.print_test_results()
        print('\nTest: Do we get new versions for master and child_01?')
        sales, sale_master = self.__get_sales_and_master_sale_for_test_run__()  # we have to start with new ones ...
        sale_master.set_value(SLDC.TITLE, 'New title for Master')
        sales[1].set_value(SLDC.TITLE, 'New title for child_02')
        self.write_sales_after_checks_to_db(sales, sale_master, enforce_writing=True)
        self.print_test_results()

    def test_database_updater_check_status_of_sales_in_database(self):
        sales, sale_master = self.__get_sales_and_master_sale_for_test_run__()
        self.write_sales_after_checks_to_db(sales, sale_master, enforce_writing=True)
        self.print_test_results()
        self.check_status_of_sales_in_database()
        self.print_test_results()
        self.check_status_of_sales_in_database()
        self.print_test_results()

    def test_sale_list(self):
        if self._delete_old_test_cases:
            sales, sale_master = self.__get_sales_and_master_sale_for_test_run__()
            self.write_sales_after_checks_to_db(sales, sale_master, enforce_writing=True)
            self.print_test_results()
        sale_master = self.get_sale_from_db_by_sale_id('T_M_01')
        sales = self.get_similar_sales_for_master_sale_from_db(sale_master)
        sale_list = SalesmanSaleList(self.sys_config, sales, sale_master)
        result_rows = sale_list.get_sales_as_search_result_rows()
        print(result_rows)

    def print_test_results(self, key_list=None):
        key_list = ['SALE', 'V_SALE', 'SALE_RELATION'] if key_list is None else key_list
        query_dict = {
            'SALE': "SELECT Sale_ID, Version, Last_Check_Date, Sale_State, Title FROM Sale WHERE Sale_ID LIKE 'T_%';",
            'V_SALE': "SELECT Sale_ID, Version, Master_id, Sale_State, Title FROM v_sale WHERE Sale_ID LIKE 'T_%';",
            'SALE_RELATION': "SELECT * FROM Sale_Relation WHERE Child_ID LIKE 'T_%' OR Master_ID LIKE 'T_%';"
        }
        for key, query in query_dict.items():
            if key in key_list:
                df = self._access_layer_sale.select_data_by_query(query)
                print('\n{}: {}'.format(key, df.head(10)))

    def __get_sales_and_master_sale_for_test_run__(self):
        test_data_dict = SaleTestDataFactory.get_test_data_dict_for_master_child_test()
        for data_dict in test_data_dict.values():
            data_dict[SLDC.VERSION] = self._access_layer_sale.get_next_version_for_sale_id(data_dict[SLDC.SALE_ID])

        sales_dict = {key: self.__get_sale_by_data_dict__(dd, is_from_db=True) for key, dd in
                      test_data_dict.items()}
        sale_master = sales_dict[TCKEY.MASTER]
        sales = [sales_dict[TCKEY.CHILD_01], sales_dict[TCKEY.CHILD_02]]
        return sales, sale_master


factory = SalesmanSaleFactoryTest()  # the previous test cases are all removed...
# factory.test_write_sales_after_checks_to_db()
# factory.test_database_updater_check_status_of_sales_in_database()
factory.test_sale_list()


