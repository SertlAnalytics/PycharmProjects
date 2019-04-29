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
sys_config.print_details = False

tutti = Tutti(sys_config)
# tutti.check_my_nth_sale_against_similar_sales(4)
# tutti.check_my_sales_against_similar_sales('')
# tutti.check_my_virtual_sales_against_similar_sales()
my_sale_id = '28017241'  # 27912013 Schlafsack: 27959857 Zimtstern: 24840384, Meda Stuhl: 27124330, Jakobsen: 28017241
# tutti.check_my_sale_on_tutti_by_sale_id_against_sale_in_db(my_sale_id)
# tutti.check_my_sale_on_tutti_by_sale_id_against_similar_sales(my_sale_id)

# tutti.check_my_nth_sale_against_similar_sales(1)
# tutti.check_my_nth_virtual_sale_against_similar_sales(1)
results = tutti.search_on_tutti(
    # 'Leder Handtasche von Gucci und Mango und Even&Odd und H&M', 'Wenig gebraucht. Für 100.- statt 200.-'
    # 'Fritz Hansen / Jacobsen - Serie 7 Stuhl / 6 Stk. / Original + neuwertig', 'Wenig gebraucht. Für 100.- statt 200.-'
    # 'Dyson hot & cool AM09', 'Neuwertiger Dyson hot+cool , zum kühlen und heizen Mit Garantie'
    # 'Schöffel Kinder Winterjacke, Grösse 152'
    # 'Vitra Meda Bürostuhl, flexibler Rücken'
    'tasche leder Louis Vuitton'
)
# print(results)
# tutti.printing.print_sales_head()
tutti.printing.print_box_plots()
sleep(2)
