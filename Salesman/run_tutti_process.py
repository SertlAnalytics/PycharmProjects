"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from tutti import Tutti
from time import sleep
from salesman_system_configuration import SystemConfiguration

sys_config = SystemConfiguration()
sys_config.with_nlp = True
sys_config.write_to_excel = True
sys_config.load_sm = True
sys_config.write_to_database = False

tutti = Tutti(sys_config)
tutti.check_my_nth_sale_against_similar_sales(4)
# tutti.check_my_sales_against_similar_sales('')
# tutti.check_my_virtual_sales_against_similar_sales()
# my_sale_id = '24840384'  # 27912013
# tutti.check_my_sale_on_tutti_by_sale_id_against_sale_in_db(my_sale_id)
# tutti.check_my_sale_on_tutti_by_sale_id_against_similar_sales(my_sale_id)
# tutti.check_my_nth_sale_against_similar_sales(1)
# tutti.check_my_nth_virtual_sale_against_similar_sales(1)
# results = tutti.get_similar_sales_from_online_inputs('Crumpler Tasche', 'Wenig gebraucht')
# print(results)
sleep(2)
