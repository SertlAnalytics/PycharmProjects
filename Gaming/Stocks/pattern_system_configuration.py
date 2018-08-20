"""
Description: This module contains the global system configuration classes for stock pattern detection
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

from sertl_analytics.constants.pattern_constants import Indices
from sertl_analytics.datafetcher.web_data_fetcher import IndicesComponentList
from pattern_data_container import PatternDataHandler
from pattern_configuration import PatternConfiguration, RuntimeConfiguration, PatternDebugger


class SystemConfiguration:
    def __init__(self):
        self.config = PatternConfiguration()
        self.runtime = RuntimeConfiguration()
        self.crypto_ccy_dic = IndicesComponentList.get_ticker_name_dic(Indices.CRYPTO_CCY)
        self.pdh = PatternDataHandler(self.config)


debugger = PatternDebugger()

# Todo Signals and expected win & connection to Bifinex
"""
ToDo list:
a) Signals - later: With support from KI
- Breakout (differ between false breakout and real breakout
- pullback: within a range (opposite from "expected" breakout) and Fibonacci compliant, i.e. 5th wave completed
b) Expected win for all these case
c) Channel Pattern: sometimes (???) there are only 2 hits on the entrance side and 3 or more on the opposite (breakout)
side - so I think we have to go back with the f_params to the left side as well...
d) Connection to Bitfinex (from 01.09.2018): https://www.bitfinex.com/posts/267
e) Correlation: Please check BCH_USD and EOS - both had TKEs together....
"""