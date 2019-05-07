"""
Description: This module contains the category tree for product selection.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import PRCAT, REGION
from sertl_analytics.pybase.value_categorizer import ValueCategorizer
from sertl_analytics.my_text import MyText


class RegionCategorizer(ValueCategorizer):
    @staticmethod
    def __get_category_list__():
        return REGION.get_regions_for_tutti_search()

    @staticmethod
    def __get_default_value_for_category__():
        return 'ganze-schweiz'

    @staticmethod
    def __get_category_value_dict__() -> dict:
        return_dict = {
            REGION.NID_OBWALDEN: 'nid-obwalden',
            REGION.ST_GALLEN: 'st-gallen',
        }
        for region in REGION.get_regions_for_tutti_search():
            if region not in return_dict:
                region_changed = MyText.get_with_replaced_umlaute(region.lower())
                return_dict[region] = region_changed.replace(' ', '-')
        return return_dict


class ProductCategorizer(ValueCategorizer):  # Product Category, german: Rubrik
    @staticmethod
    def __get_category_list__():
        return PRCAT.get_all()

    @staticmethod
    def __get_default_value_for_category__():
        return 'angebote'

    @staticmethod
    def __get_category_value_dict__() -> dict:
        return_dict = {
            PRCAT.ALL: 'angebote',
        }
        for category in PRCAT.get_all():
            if category not in return_dict:
                category_changed = MyText.get_with_replaced_umlaute(category.lower())
                return_dict[category] = category_changed.replace(' & ', '-')
        return return_dict

    def get_sub_category_lists_for_category(self, category: str):
        return [['Alle', 'ALL']] + self.__get_sub_category_lists_for_category__(category)

    @staticmethod
    def get_search_category_sub_categories(category: str, sub_category: str) -> list:
        return_list = [[category, sub_category]]
        if category == PRCAT.CHILD and sub_category == 'Kleider & Schuhe':
            return_list.append([PRCAT.CLOTHES_OTHERS, PRCAT.ALL])
        elif category == PRCAT.COMPUTER and sub_category == 'Komponenten & Zubehör':
            return_list.append([PRCAT.PHONE_NAVI, 'Zubehör'])
        return return_list

    @staticmethod
    def __get_sub_category_list_for_category__(category: str):
        sub_category_dict = {
            PRCAT.BOOKS: ['Romane', 'Sachbücher & Ratgeber'],
            PRCAT.CHILD: ['Kinderwagen & Sitze', 'Kinderzimmer', 'Kleider & Schuhe'],
            PRCAT.CLOTHES_OTHERS: ['Kleidung für Damen', 'Kleidung für Herren', 'Schuhe für Damen', 'Schuhe für Herren',
                                   'Taschen und & Portmonnaies', 'Uhren & Schmuck'],
            PRCAT.COMPUTER: ['Computer', 'Komponenten & Zubehör', 'Software', 'Tablets'],
            PRCAT.SERVICE: ['Büroservice', 'Computer & Handys', 'Finanzen & Recht', 'Handwerk', 'Umzug & Transport'],
            PRCAT.BUSINESS: ['Büromaterial & Büromöbel', 'Geschäftseinrichtungen'],
            PRCAT.SPORT_OUTDOOR: ['Camping', 'Fitness', 'Velos', 'Wintersport', 'Sonstige Sportarten'],
            PRCAT.PHONE_NAVI: ['Festnetztelefone', 'Handys', 'Navigationssysteme', 'Zubehör'],
            PRCAT.VEHICELS: ['Autos', 'Autozubehör', 'Boote & Zubehör', 'Motorradzubehör',
                             'Motorräder', 'Nutzfahrzeuge', 'Wohnmobile'],
            PRCAT.REAL_ESTATE: ['Ferienobjekte', 'Gewerbeobjekte', 'Grundstücke', 'Häuser',
                                'Parkplätze', 'WG-Zimmer', 'Wohnungen'],
            PRCAT.FOTO_VIDEO: ['Fotokameras', 'Videokameras', 'Zubehör'],
            PRCAT.GARDEN_CRAFT: ['Baumaterial', 'Gartenausstattung', 'Werkzeuge & Maschinen'],
            PRCAT.HOUSEHOLD: ['Beleuchtung', 'Geräte & Utensilien', 'Lebensmittel', 'Möbel'],
            PRCAT.JOBS: ['Gesundheitswesen', 'Sonstige Stellen'],
        }
        return sub_category_dict.get(category, [])



