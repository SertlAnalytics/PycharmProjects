"""
Description: This module starts the pattern detection application. It is NOT stored on git hub.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-10
"""

from sertl_analytics.myprofiler import MyProfiler
from salesman_dash.my_dash_for_salesman import MyDash4Salesman
from salesman_system_configuration import SystemConfiguration

sys_config = SystemConfiguration()
sys_config.plot_results = False
sys_config.write_to_database = True

my_profiler = MyProfiler()
my_dash = MyDash4Salesman(sys_config)
my_dash.get_salesman()
my_dash.run_on_server()
my_profiler.disable(False)

# Head Shoulder: GE Date BETWEEN '2016-01-25' AND '2019-10-30'
# Triangle: Processing KO (Coca Cola)...Date BETWEEN '2017-10-25' AND '2019-10-30'
# NEO_USD, EOS_USD, IOTA_USD, BCH_USD, BTC_USD, ETH_USD, LTC_USD
