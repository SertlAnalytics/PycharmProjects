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
from salesman_nlp.salesman_spacy import SalesmanSpacy
from spacy import displacy

my_spacy = SalesmanSpacy()
doc = my_spacy.nlp('Das ist ein Satz')
doc = my_spacy.nlp('Leder schwarz. Den Widerstand der Rückenlehne kann man noch einstellen. '
                   'Untergestell hat leichte Kratzspuren. Leder ist aber wie neu.')
displacy.serve(doc, style='dep')

"""
Using the 'dep' visualizer
Serving on http://0.0.0.0:5000 ...
NOW: open http://localhost:5000/
"""





