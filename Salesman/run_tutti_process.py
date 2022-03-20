"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_tutti.tutti import Tutti
from time import sleep
from salesman_system_configuration import SystemConfiguration
from salesman_search import SalesmanSearchApi
from sertl_analytics.constants.salesman_constants import REGION
from salesman_tutti.tutti_constants import PRSUBCAT, PRCAT

sys_config = SystemConfiguration()
sys_config.with_nlp = True
sys_config.write_to_excel = False
sys_config.load_sm = True
sys_config.write_to_database = False
sys_config.print_details = False
sys_config.plot_results = True

api = SalesmanSearchApi('')
# api.region_value = sys_config.region_categorizer.get_value_for_category(REGION.AARGAU)
# api.category_value = sys_config.product_categorizer.get_value_for_category(PRCAT.REAL_ESTATE)
# api.sub_category_value = sys_config.product_categorizer.get_sub_category_value_for_sub_category(
#     PRCAT.REAL_ESTATE, PRSUBCAT.REAL_ESTATE_HOUSES)
# api.sub_category_value = sys_config.product_categorizer.get_sub_category_value_for_sub_category(
#     PRCAT.CHILD, PRSUBCAT.CHILD_CLOTHES)

tutti = Tutti(sys_config)
# tutti.check_my_nth_sale_in_browser_against_similar_sales(1)
# tutti.check_my_nth_sale_in_browser_against_similar_sales(4)
# tutti.check_my_sales_in_browser_against_similar_sales()
# tutti.check_my_nth_virtual_sale_against_similar_sales(1)
# tutti.check_my_virtual_sales_against_similar_sales()
sale_id = '18246884'  # Pixie: 27943008 Schlafsack: 27959857 Schöffel: 27960542, Meda Stuhl: 27124330, Jakobsen: 28017241
# Kugelbahn: 27993639, Sunrise Tower: 28105850
# tutti.print_details_for_sale_on_platform_by_sale_id(sale_id, with_data_dict=True)
# tutti.check_sale_on_platform_against_sale_in_db_by_sale_id(sale_id, write_to_db=False)
# sale = tutti.get_sale_from_db_by_sale_id(sale_id)
# tutti.check_sale_in_db_against_similar_sales_on_platform_by_sale_id(sale_id)
# master_sale_id = '24325487'
# tutti.check_similar_sales_in_db_against_master_sale_in_db()
# tutti.check_sale_on_platform_against_similar_sales_by_sale_id(sale_id)
# tutti.inspect_sales_on_platform_for_api(api)

# tutti.check_sales_for_similarity_by_sale_id('27124330', '22735190')

# api.search_string = 'Leder Handtasche von Gucci und Mango und Even&Odd und H&M, Wenig gebraucht. Für 100.- statt 200.-'
# api.search_string = 'Fritz Hansen / Jacobsen - Serie 7 Stuhl / 6 Stk. / Original + neuwertig, Für 100.- statt 200.-'
# api.search_string = 'Dyson hot & cool AM09, Neuwertiger Dyson hot+cool , zum kühlen und heizen Mit Garantie'
# api.search_string = 'Schöffel Kinder Winterjacke, Grösse 152'
# api.search_string = 'Vitra Meda Bürostuhl, flexibler Rücken'
# api.search_string = 'tasche leder Louis Vuitton'
# api.search_string = 'Dyson hot+cool AM09'
# api.search_string = "Hape, Kugelbahn 'The Roundabout' 91-teilig"
# api.search_string = "Gesucht 4.5 Zimmer Wohnung in Wettingen oder Baden"
# api.search_string = "Nespresso Pixie Kaffeemaschine von DeLonghi"
api.search_string = 'haus zur miete'
# api.search_string = 'Wir suchen Tiersitting für Hamster'
# api.search_string = "Damen Hut von Risa, Grösse 56, etwas Besonderes"
# api.search_string = 'Wilde+Spieth, Stuhl, SE 68 Multi Purpose Chair'
api.search_string = 'Winterschuhe gore-tex LOWA GTX'
api.search_string = 'Hochwertige Stehleuchte mit Bewegungsmelder (Waldmann)'
api.search_string = 'Wilde+Spieth, Stuhl, Sie haben ein ähnliches Design wie die Serie 7 von Jacobsen und Hansen'
api.search_string = 'Rettungsweste für Kinder (20-30kg)'
api.search_string = 'Jeans - Shorts von Terranova - Grösse 34'
api.search_string = 'Hamsterkäfig'

# api.print_api_details()
# results = tutti.check_search_by_api_against_other_sale(api, '9285456')
results = tutti.check_search_by_api_against_similar_sales(api)

# print(results)
# tutti.printing.print_sales_head()
tutti.close_excel()

