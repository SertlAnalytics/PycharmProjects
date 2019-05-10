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
sys_config.write_to_excel = False
sys_config.load_sm = True
sys_config.write_to_database = False
sys_config.print_details = False

api = OnlineSearchApi('')
api.region_value = sys_config.region_categorizer.get_value_for_category(REGION.GANZE_SCHWEIZ)
# api.category_value = sys_config.product_categorizer.get_value_for_category(PRCAT.CHILD)
# api.sub_category_value = sys_config.product_categorizer.get_sub_category_value_for_sub_category(
#     PRCAT.CHILD, PRSUBCAT.CHILD_CLOTHES)

tutti = Tutti(sys_config)
# tutti.check_my_nth_sale_in_browser_against_similar_sales(1)
# tutti.check_my_nth_sale_in_browser_against_similar_sales(4)
# tutti.check_my_sales_against_similar_sales()
# tutti.check_my_nth_virtual_sale_against_similar_sales(1)
# tutti.check_my_virtual_sales_against_similar_sales()
sale_id = '27993639x'  # Pixie: 27943008 Schlafsack: 27959857 Schöffel: 27960542, Meda Stuhl: 27124330, Jakobsen: 28017241
# Kugelbahn: 27993639, Sunrise Tower: 28105850
# tutti.print_details_for_tutti_sale_id(sale_id)
# tutti.check_sale_on_platform_against_sale_in_db_by_sale_id(sale_id)
# tutti.check_sale_in_db_against_similar_sales_by_sale_id(sale_id)
# tutti.check_sale_on_platform_against_similar_sales_by_sale_id(sale_id)

# api.search_string = 'Leder Handtasche von Gucci und Mango und Even&Odd und H&M, Wenig gebraucht. Für 100.- statt 200.-'
# api.search_string = 'Fritz Hansen / Jacobsen - Serie 7 Stuhl / 6 Stk. / Original + neuwertig, Für 100.- statt 200.-'
# api.search_string = 'Dyson hot & cool AM09, Neuwertiger Dyson hot+cool , zum kühlen und heizen Mit Garantie'
# api.search_string = 'Schöffel Kinder Winterjacke, Grösse 152'
# api.search_string = 'Vitra Meda Bürostuhl, flexibler Rücken'
# api.search_string = 'tasche leder Louis Vuitton'
# api.search_string = 'Dyson hot+cool AM09'
api.search_string = "Hape, Kugelbahn 'The Roundabout' 91-teilig"
# api.search_string = "Damen Hut von Risa, Grösse 56, etwas Besonderes"
# api.search_string = 'Wilde+Spieth, Stuhl, SE 68 Multi Purpose Chair'

api.print_api_details()
results = tutti.check_search_by_api_against_similar_sales(api)

# print(results)
# tutti.printing.print_sales_head()
tutti.close_excel()

