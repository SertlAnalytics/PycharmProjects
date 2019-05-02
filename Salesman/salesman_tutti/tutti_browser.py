"""
Description: This module is the base class for our Tutti Salesman application.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.pyurl.url_process import MyUrlBrowser
from sertl_analytics.pyurl.url_username_passwords import WebPasswords
from salesman_system_configuration import SystemConfiguration
from sertl_analytics.constants.salesman_constants import SLSRC
from salesman_tutti.tutti_sale import TuttiSale
from salesman_tutti.tutti_constants import SLCLS
from salesman_nlp.salesman_spacy import SalesmanSpacy


class MyUrlBrowser4Tutti(MyUrlBrowser):
    def __init__(self, sys_config: SystemConfiguration, spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._url_login = 'https://www.tutti.ch/de/start/login'
        self._url_search = 'https://www.tutti.ch/de/li'
        self._spacy = spacy
        self._nlp = self._spacy.nlp
        MyUrlBrowser.__init__(self,  self._url_login, WebPasswords.TUTTI[0],  WebPasswords.TUTTI[1])

    def enter_and_submit_credentials(self):
        self.__enter_and_submit_credentials__()

    def __get_credential_values__(self) -> dict:
        return {'email': self._user_name, 'password': self._password}

    @staticmethod
    def get_url_for_sale_editing(sale_id: int):
        return 'https://www.tutti.ch/de/ai/start?load={}'.format(sale_id)

    def get_my_sales_from_tutti(self):
        return self.__get_sales_from_tutti__(SLCLS.OFFERS)

    def get_my_nth_sale_from_tutti(self, number: int) -> TuttiSale:
        return self.__get_nth_sale_from_tutti__(SLCLS.OFFERS, number)

    def __click_submit__(self):
        xpath = '//*[@id="pageContainer"]/div[2]/div/div/div/div[3]/div/div/form/div[3]/button'
        link_einloggen = self.driver.find_element_by_xpath(xpath=xpath)
        link_einloggen.click()

    def __change_price_for_my_sales__(self, my_sales: list):
        for sale in my_sales:
            self.__change_price_for_sale__(sale)

    def __change_price_for_sale__(self, sale: TuttiSale):
        if not sale.is_price_ready_for_update_in_tutti():
            return
        self.__open_site_for_editing__(sale.sale_id)
        self.__click_next_page__()      # click "Nächste Seite"
        self.__enter_price_new__(sale.price_new)
        self.__click_next_page__()      # click "Nächste Seite"
        self.__click_next_page__()      # click "Vorschau"
        self.__click_next_page__()      # click "Nächste Seite"
        self.__publish_without_conditions__()  # click "Ohne Hervorhebung veröffentlichen"

    def __open_site_for_editing__(self, sale_id: int):
        self.driver.get(self.get_url_for_sale_editing(sale_id))

    def __enter_price_new__(self, price_new: float):
        price_field = self.driver.find_element_by_name('price')
        price_field.clear()
        price_field.send_keys(str(price_new))

    def __click_search__(self):
        xpath = '//*[@id="pageContainer"]/div[1]/div/div/header/div/div/div/div/div[2]/div/form/div/button'
        self.__find_button_by_xpath_and_press_click__(xpath)

    def __click_next_page__(self):
        xpath = '//*[@id="pageContainer"]/div[2]/div/div/div/div/form/div/div/button'
        self.__find_button_by_xpath_and_press_click__(xpath)

    def __publish_without_conditions__(self):
        xpath = '//*[@id="aiSubmitFree"]'
        self.__find_button_by_xpath_and_press_click__(xpath)

    def __get_sales_from_tutti__(self, class_name: str, search_labels=None) -> list:
        tutti_sales = []
        sale_elements = self.__get_sales_elements_by_class_name__(class_name)
        for sale_element in sale_elements:
            tutti_sale = self.__get_tutti_sale_from_sale_element__(sale_element, search_labels)
            tutti_sale.set_source(SLSRC.TUTTI_CH)
            tutti_sales.append(tutti_sale)
        return tutti_sales

    def __get_nth_sale_from_tutti__(self, class_name: str, number: int) -> TuttiSale:
        sales_elements = self.__get_sales_elements_by_class_name__(class_name)
        if number - 1 < len(sales_elements):
            return self.__get_tutti_sale_from_sale_element__(sales_elements[number - 1], None)

    def __get_tutti_sale_from_sale_element__(self, sale_element, search_labels):
        sale = TuttiSale(self._spacy, self.sys_config, search_labels)
        sale.init_by_sale_element(sale_element)
        return sale

    def __get_sales_elements_by_class_name__(self, class_name: str):
        return self.driver.find_elements_by_class_name(class_name)

    def __get_current_sale_elements_by_x_path__(self):
        xpath = '//*[@id="pageContainer"]/div[2]/div/div/div/div[2]/div/div[2]'
        return self.driver.find_element_by_xpath(xpath=xpath)

    def __open_search_site__(self):
        self.driver.get(self._url_search)

