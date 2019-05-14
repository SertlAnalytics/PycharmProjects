"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_tutti.tutti import Tutti
from time import sleep
from salesman_system_configuration import SystemConfiguration
from salesman_web_parser import OnlineSearchApi
from sertl_analytics.constants.salesman_constants import REGION
from salesman_tutti.tutti_constants import PRSUBCAT, PRCAT

sys_config = SystemConfiguration()
sys_config.with_nlp = True
sys_config.write_to_excel = True
sys_config.load_sm = True
sys_config.write_to_database = False
sys_config.print_details = False
sys_config.plot_results = False

sale_id = '27961855'  # '27993639: Kugelbahn

tutti = Tutti(sys_config)
# tutti.check_my_nth_sale_in_browser_against_database(1)
# tutti.check_my_sales_in_browser_against_database()
# tutti.check_status_of_sales_in_database()
tutti.check_own_sales_in_database_against_similar_sales()
# tutti.check_similar_sales_in_db_against_master_sale_in_db()
# tutti.check_sale_on_platform_against_sale_in_db_by_sale_id(sale_id, write_to_db=True)
tutti.close_excel()

