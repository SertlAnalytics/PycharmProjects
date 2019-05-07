"""
Description: This module contains the url helper class for handling tutti urls
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-07
"""
from sertl_analytics.constants.salesman_constants import SLDC, PRCAT, REGION
from salesman_tutti.tutti_categorizer import ProductCategorizer, RegionCategorizer


class TuttiUrlHelper:
    def __init__(self, search_string: str, region='ganze-schweiz', category='angebote', sub_category='',
                 region_categorizer=None, product_categorizer=None):
        # 'https://www.tutti.ch/de/li/ganze-schweiz/angebote?'
        # https://www.tutti.ch/de/li/aargau?o=6&q=weste
        self._url_base = 'https://www.tutti.ch/de/li'
        self._region = region
        self._category = category
        self._sub_category = sub_category
        self._order = 0
        self._search_string = search_string  # could be an href string as well
        self._url_extended_base = self.__get_url_extended_base__()
        self._region_categorizer = region_categorizer
        self._product_categorizer = product_categorizer

    @property
    def domain(self):
        return 'https://www.tutti.ch'

    @property
    def search_string(self):
        return self._search_string

    @property
    def url(self):
        p_dict = {
            'o': '' if self._order == 0 else '{}'.format(self._order),
            'q': '{}'.format(self._search_string)
        }
        p_list = ['{}={}'.format(key, value) for key, value in p_dict.items() if value != '']
        url = '{}?{}'.format(self._url_extended_base, '&'.join(p_list))
        return url

    def get_href(self):
        href = self._search_string
        return '{}{}'.format(self.domain, href) if href.find('https') < 0 else href

    def get_href_component_dict(self) -> dict:
        #  For examples see: testing/test_tutti_url_helper.py
        href_parts = self._search_string.split('/')
        field_list = [SLDC.REGION, SLDC.PRODUCT_CATEGORY, SLDC.PRODUCT_SUB_CATEGORY, SLDC.TITLE, SLDC.SALE_ID]
        return_dict = {field: '' for field in field_list}
        if len(href_parts) > 6:
            for i in range(1, 6):
                region = self._region_categorizer.get_category_for_value(href_parts[i])
                if region in REGION.get_regions_for_tutti_search():
                    return_dict[SLDC.REGION] = region
                    break
            product_category = self._product_categorizer.get_category_for_value(href_parts[-3])
            if product_category in PRCAT.get_all():
                return_dict[SLDC.PRODUCT_CATEGORY] = product_category
                return_dict[SLDC.PRODUCT_SUB_CATEGORY] = ''
            else:
                product_category = self._product_categorizer.get_category_for_value(href_parts[-4])
                return_dict[SLDC.PRODUCT_CATEGORY] = product_category
                return_dict[SLDC.PRODUCT_SUB_CATEGORY] = self._product_categorizer.get_sub_category_for_value(
                    product_category, href_parts[-3])
            return_dict[SLDC.TITLE] = href_parts[-2]
            return_dict[SLDC.SALE_ID] = href_parts[-1]
        return return_dict

    def get_url_with_search_string(self, search_string: str):
        self._search_string = search_string
        return self.url

    def get_url_list(self, search_string: str):
        self._search_string = search_string
        url_list = []
        for i in range(0, 11):
            self._order = i
            url_list.append(self.url)
        self._order = 0  # reset it....
        return url_list

    def adjust_category_sub_category(self, category: str, sub_category: str):
        self._category = category
        self._sub_category = sub_category
        self._url_extended_base = self.__get_url_extended_base__()

    def __get_url_extended_base__(self):
        region = '' if self._region == '' else '/{}'.format(self._region)
        category = '' if self._category == '' else '/{}'.format(self._category)
        sub_category = '' if self._sub_category in ['', 'GANZE_SCHWEIZ'] else '/{}'.format(self._sub_category)
        return '{}{}{}{}'.format(self._url_base, region, category, sub_category)