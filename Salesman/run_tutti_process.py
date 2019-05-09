"""
Description: This module is the manually starting point our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from salesman_tutti.tutti import Tutti
from time import sleep
from salesman_system_configuration import SystemConfiguration

sys_config = SystemConfiguration()
sys_config.with_nlp = True
sys_config.write_to_excel = False
sys_config.load_sm = True
sys_config.write_to_database = False
sys_config.print_details = False

tutti = Tutti(sys_config)
# tutti.check_my_nth_sale_against_similar_sales(1)
# tutti.check_my_nth_sale_against_similar_sales(4)
# tutti.check_my_sales_against_similar_sales()
# tutti.check_my_nth_virtual_sale_against_similar_sales(1)
# tutti.check_my_virtual_sales_against_similar_sales()
sale_id = '27993639'  # Pixie: 27943008 Schlafsack: 27959857 Schöffel: 27960542, Meda Stuhl: 27124330, Jakobsen: 28017241
# Kugelbahn: 27993639, Sunrise Tower: 28105850
# tutti.print_details_for_tutti_sale_id(sale_id)
# tutti.check_sale_against_sale_in_db_by_sale_id(sale_id)
tutti.check_sale_in_db_against_similar_sales_by_sale_id(sale_id)
# tutti.check_sale_on_tutti_against_similar_sales_by_sale_id(sale_id)
# results = tutti.search_on_tutti(
    # 'Leder Handtasche von Gucci und Mango und Even&Odd und H&M', 'Wenig gebraucht. Für 100.- statt 200.-'
    # 'Fritz Hansen / Jacobsen - Serie 7 Stuhl / 6 Stk. / Original + neuwertig', 'Wenig gebraucht. Für 100.- statt 200.-'
    # 'Dyson hot & cool AM09', 'Neuwertiger Dyson hot+cool , zum kühlen und heizen Mit Garantie'
    # 'Schöffel Kinder Winterjacke, Grösse 152'
    # 'Vitra Meda Bürostuhl, flexibler Rücken', ''
    # 'tasche leder Louis Vuitton'
    # 'Dyson hot+cool AM09'
    # "Hape, Kugelbahn 'The Roundabout' 91-teilig", ''
    # "Damen Hut von Risa, Grösse 56, etwas Besonderes"
#     'Wilde+Spieth, Stuhl, SE 68 Multi Purpose Chair'
# )
# print(results)
# tutti.printing.print_sales_head()
tutti.close_excel()

