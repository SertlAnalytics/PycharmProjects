"""
Description: This module contains the factory class for sales
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC
from salesman_tutti.tutti_constants import SCLS, SLSCLS, SLCLS
from salesman_nlp.salesman_spacy import SalesmanSpacy
from salesman_system_configuration import SystemConfiguration
from salesman_tutti.tutti_url_factory import TuttiUrlFactory, OnlineSearchApi
import requests
import math
from lxml import html
from lxml.html import HtmlElement
from sertl_analytics.myhtml import MyHtmlElement
from time import sleep


class SalesmanWebParser:
    def __init__(self, sys_config: SystemConfiguration, salesman_spacy: SalesmanSpacy):
        self.sys_config = sys_config
        self._salesman_spacy = salesman_spacy
        self._nlp_sale = self._salesman_spacy.nlp
        self._url_factory = TuttiUrlFactory(self.sys_config, self._salesman_spacy)
        self._online_search_api = None

    @property
    def url_base_for_request(self):
        return 'https://www.tutti.ch/de/vi/'

    def adjust_by_online_search_api(self, api: OnlineSearchApi):
        self._online_search_api = api
        self._url_factory.adjust_by_online_search_api(api)

    def get_search_string_found_number_dict(self, search_label_lists: list) -> dict:
        # gets the number and used search label list for a search_string - only positive searches are given back
        return_dict = {}
        for search_label_list in search_label_lists:
            search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
            url = self._url_factory.get_url_with_search_string(search_string)
            request = requests.get(url)
            tree = html.fromstring(request.content)
            xpath_numbers = tree.xpath('//div[@class="{}"]'.format(SCLS.FOUND_NUMBERS))
            number_found = self.__get_number_from_number_item__(xpath_numbers)
            if number_found > 0:
                return_dict[search_string] = [number_found, search_label_list]
                print('{} --> found {} by search_label_list "{}"'.format(url, number_found, search_label_list))
        return return_dict

    def get_online_search_api_index_number_dict(self, api_list: list, search_label_lists) -> dict:
        return_dict = {}
        for idx, api in enumerate(api_list):
            return_dict[idx] = 0
            self._url_factory.adjust_by_online_search_api(api)
            for search_label_list in search_label_lists:
                encoded_search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
                url = self._url_factory.get_url_with_search_string(encoded_search_string)
                return_dict[idx] += self.__get_found_number_for_product_category_url__(url)
        return return_dict

    def get_product_categories_value_list_for_search_labels(self, search_label_lists: list) -> list:
        category_number_dict = {}
        category_value_list = self.sys_config.product_categorizer.get_category_value_list(exceptions=['angebote'])
        for search_label_list in search_label_lists:
            encoded_search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
            self.__fill_category_value_found_number_dict__(
                category_value_list, category_number_dict, encoded_search_string)
        number_list = [number for category, number in category_number_dict.items()]
        max_number = max(number_list)
        return [[category, ''] for category in category_number_dict
                if math.sqrt(category_number_dict[category]) > math.sqrt(max_number)/3]

    def get_html_elements_for_sale_via_request_by_sale_id(self, sale_id: str) -> list:
        url = '{}{}'.format(self.url_base_for_request, sale_id)
        request = requests.get(url)
        sleep(1)
        tree = html.fromstring(request.content)
        product_categories = tree.xpath('//span[@class="{}"]'.format(SLSCLS.PRODUCT_CATEGORIES))
        sales = tree.xpath('//div[@class="{}"]'.format(SLSCLS.OFFERS))
        return [url, sales[0], product_categories]

    def get_sale_data_dict_for_sale_id(self, sale_id: str):
        url = '{}{}'.format(self.url_base_for_request, sale_id)
        request = requests.get(url)
        sleep(1)
        print('...get_sale_data_dict_for_sale_id.url: {}'.format(url))
        tree = html.fromstring(request.content)
        product_categories = tree.xpath('//span[@class="{}"]'.format(SLSCLS.PRODUCT_CATEGORIES))
        sales = tree.xpath('//div[@class="{}"]'.format(SLSCLS.OFFERS))
        sale_data_dict = self.__get_sale_data_dict_for_sale_id_by_html_element__(sales[0], product_categories)
        if len(sale_data_dict) == 0:
            return sale_data_dict
        sale_data_dict[SLDC.SALE_ID] = sale_id
        sale_data_dict[SLDC.HREF] = url
        return sale_data_dict

    def get_sales_data_dict_for_search_label_list(self, search_label_list: list) -> dict:
        return_sales_data_dict = {}
        encoded_search_string = MyText.get_url_encode_plus(' '.join(search_label_list))
        url_list = self._url_factory.get_url_list(encoded_search_string)
        navigation_pages = ''
        for idx, url in enumerate(url_list):
            if navigation_pages.find(str(idx)) < 0 < idx:  # we stop paging if there is no number found
                break
            print('checking url: {}'.format(url))
            request = requests.get(url)
            tree = html.fromstring(request.content)
            if idx == 0:
                navigation_elements = tree.xpath('//ul[@class="{}"]'.format(SCLS.NAVIGATION_MAIN))
                for navigation in navigation_elements:
                    navigation_pages = str(navigation.text_content())
            sales = tree.xpath('//div[@class="{}"]'.format(SCLS.OFFERS))
            for sale_element_in_list in sales:
                sale_data_dict = self.__get_sale_data_dict_for_sale_html_element_in_list__(sale_element_in_list)
                return_sales_data_dict[sale_data_dict[SLDC.SALE_ID]] = sale_data_dict
        return return_sales_data_dict

    def get_sale_data_dict_by_browser_sale_element(self, browser_html_element):
        offer_id_obj = browser_html_element.find_element_by_class_name(SLCLS.MAIN_ANKER)
        href = offer_id_obj.get_attribute('href')
        return_dict = self._url_factory.get_href_component_dict_for_url(href)
        return_dict[SLDC.HREF] = href
        return_dict[SLDC.LOCATION] = browser_html_element.find_element_by_class_name(SLCLS.LOCATION).text
        return_dict[SLDC.START_DATE] = browser_html_element.find_element_by_class_name(SLCLS.DATE).text
        return_dict[SLDC.TITLE] = browser_html_element.find_element_by_class_name(SLCLS.LINK).text
        return_dict[SLDC.DESCRIPTION] = browser_html_element.find_element_by_class_name(SLCLS.DESCRIPTION).text
        return_dict[SLDC.PRICE] = browser_html_element.find_element_by_class_name(SLCLS.PRICE).text
        numbers = browser_html_element.find_elements_by_class_name(SLCLS.NUMBERS)
        return_dict[SLDC.VISITS] = numbers[0].text
        return_dict[SLDC.BOOK_MARKS] = numbers[1].text
        return return_dict

    def __get_sale_data_dict_for_sale_html_element_in_list__(self, html_element_in_list: HtmlElement):
        my_html_element = MyHtmlElement(html_element_in_list)
        href = my_html_element.get_attribute_for_sub_class(SLCLS.MAIN_ANKER, 'href')
        href = '{}{}'.format(self._url_factory.domain, href)
        return_dict = self._url_factory.get_href_component_dict_for_url(href)
        return_dict[SLDC.HREF] = href
        return_dict[SLDC.LOCATION] = my_html_element.get_text_for_sub_class(SLCLS.LOCATION)
        return_dict[SLDC.START_DATE] = my_html_element.get_text_for_sub_class(SLCLS.DATE)
        return_dict[SLDC.TITLE] = my_html_element.get_text_for_sub_class(SLCLS.TITLE)
        return_dict[SLDC.DESCRIPTION] = my_html_element.get_text_for_sub_class(SLCLS.DESCRIPTION)
        return_dict[SLDC.PRICE] = my_html_element.get_text_for_sub_class(SLCLS.PRICE)
        return return_dict

    @staticmethod
    def __get_sale_data_dict_for_sale_id_by_html_element__(html_element: HtmlElement, product_categories: list):
        my_html_element = MyHtmlElement(html_element)
        description = my_html_element.get_text_for_sub_class(SLSCLS.DESCRIPTION)
        print('description={}, type={}'.format(description, type(description)))
        location_html_element = my_html_element.get_html_element_for_sub_class(SLSCLS.LOCATION_CLASS)
        if location_html_element is None:
            return {}
        date_html_element = my_html_element.get_html_element_for_sub_class(SLSCLS.DATE_CLASS)
        category_off_set = 1 if len(product_categories) <= 3 else 2
        product_sub_category = '' if len(product_categories) <= category_off_set+1 else \
            product_categories[category_off_set+1].text_content()
        return {
            SLDC.LOCATION: location_html_element.get_text_for_sub_class(SLSCLS.LOCATION_SUB_CLASS),
            SLDC.REGION: product_categories[category_off_set-1].text_content(),
            SLDC.PRODUCT_CATEGORY: product_categories[category_off_set].text_content(),
            SLDC.PRODUCT_SUB_CATEGORY: product_sub_category,
            SLDC.START_DATE: date_html_element.get_text_for_sub_class(SLSCLS.DATE_SUB_CLASS),
            SLDC.TITLE: my_html_element.get_text_for_sub_class(SLSCLS.TITLE),
            SLDC.DESCRIPTION: my_html_element.get_text_for_sub_class(SLSCLS.DESCRIPTION),
            SLDC.PRICE: my_html_element.get_text_for_sub_class(SLSCLS.PRICE),
        }

    def __fill_category_value_found_number_dict__(
            self, category_value_list: list, category_number_dict: dict, search_string: str):
        # fills the found number for each product category_value
        category_value_remove_list = []
        for category_value in category_value_list:
            if self._online_search_api.category_value == '' or category_value == self._online_search_api.category_value:
                if category_value == self._online_search_api.category_value:
                    self._url_factory.adjust_by_online_search_api(self._online_search_api)
                else:
                    self._online_search_api.category_value = category_value
                    self._online_search_api.sub_category_value = ''
                    self._url_factory.adjust_by_online_search_api(self._online_search_api)
                url = self._url_factory.get_url_with_search_string(search_string)
                number_found = self.__get_found_number_for_product_category_url__(url)
                if number_found == 0:
                    if category_value not in category_number_dict:
                        category_value_remove_list.append(category_value)  # we don't want to have this in the next loop
                else:
                    if category_value in category_number_dict:
                        category_number_dict[category_value] += number_found
                    else:
                        category_number_dict[category_value] = number_found
                print('url={}: found: {}'.format(url, number_found))
        for category_value in category_value_remove_list:
            category_value_list.remove(category_value)

    def __get_found_number_for_product_category_url__(self, url: str):
        request = requests.get(url)
        tree = html.fromstring(request.content)
        xpath_numbers = tree.xpath('//div[@class="{}"]'.format(SCLS.FOUND_NUMBERS))
        return self.__get_number_from_number_item__(xpath_numbers)

    def __get_number_from_number_item__(self, xpath_numbers):
        if xpath_numbers is None or len(xpath_numbers) == 0:
            return 0
        number_item = xpath_numbers[0] if type(xpath_numbers) is list else xpath_numbers
        doc_number = self._nlp_sale(str(number_item.text_content()).replace("'", ""))
        # self._salesman_spacy.print_tokens_for_doc(doc_number)
        number_results = doc_number._.first_pos_number
        return 0 if number_results is None else number_results