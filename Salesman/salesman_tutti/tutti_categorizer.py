"""
Description: This module contains the category_value tree for product selection.
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-04-02
"""

from sertl_analytics.constants.salesman_constants import REGION
from salesman_tutti.tutti_constants import PRCAT, PRSUBCAT
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
            PRCAT.ALL: PRCAT.ALL,
        }
        for category in PRCAT.get_all():
            if category not in return_dict:
                category_changed = MyText.get_with_replaced_umlaute(category.lower())
                return_dict[category] = category_changed.replace(' & ', '-')
        return return_dict

    def get_sub_category_lists_for_category(self, category: str):
        return [[PRSUBCAT.ALL, PRSUBCAT.ALL]] + self.__get_sub_category_lists_for_category__(category)

    @staticmethod
    def get_alternative_search_category_sub_categories(category: str, sub_category: str) -> list:
        if category == PRCAT.CHILD and sub_category == PRSUBCAT.CHILD_CLOTHES:
            return [PRCAT.CLOTHES_OTHERS, '']
        elif category == PRCAT.COMPUTER and sub_category == PRSUBCAT.COMPUTER_COMPONENTS:
            return [PRCAT.PHONE_NAVI, PRSUBCAT.PHONE_COMPONENTS]

    @staticmethod
    def __get_sub_category_list_for_category__(category: str):
        sub_category_dict = {
            PRCAT.BOOKS: [PRSUBCAT.BOOK_NOVELS, PRSUBCAT.BOOK_ADVISORS],
            PRCAT.CHILD: [PRSUBCAT.CHILD_STROLLER, PRSUBCAT.CHILD_ROOM, PRSUBCAT.CHILD_CLOTHES],
            PRCAT.CLOTHES_OTHERS: [PRSUBCAT.CLOTHES_FEMALE, PRSUBCAT.CLOTHES_MALE, PRSUBCAT.SHOES_FEMALE,
                                   PRSUBCAT.SHOES_MALE,
                                   PRSUBCAT.OTHERS_BAGS, PRSUBCAT.OTHERS_WATCHES],
            PRCAT.COMPUTER: [PRSUBCAT.COMPUTER, PRSUBCAT.COMPUTER_COMPONENTS, PRSUBCAT.SOFTWARE, PRSUBCAT.TABLETS],
            PRCAT.SERVICE: [PRSUBCAT.SERVICE_OFFICE, PRSUBCAT.SERVICE_COMPUTER, PRSUBCAT.SERVICE_FINANCE,
                            PRSUBCAT.SERVICE_CRAFT, PRSUBCAT.SERVICE_TRANSPORT],
            PRCAT.BUSINESS: [PRSUBCAT.BUSINESS_MATERIAL, PRSUBCAT.BUSINESS_EQUIPMENT],
            PRCAT.SPORT_OUTDOOR: [PRSUBCAT.SPORT_CAMPING, PRSUBCAT.SPORT_FITNESS, PRSUBCAT.SPORT_BIKE,
                                  PRSUBCAT.SPORT_WINTER, PRSUBCAT.SPORT_OTHERS],
            PRCAT.PHONE_NAVI: [PRSUBCAT.PHONE_FIX, PRSUBCAT.PHONE_MOBILE,
                               PRSUBCAT.PHONE_NAVI, PRSUBCAT.PHOTO_COMPONENTS],
            PRCAT.VEHICELS: [PRSUBCAT.VEHICELS_CARS, PRSUBCAT.VEHICELS_COMPONENTS, PRSUBCAT.VEHICELS_BOATS,
                             PRSUBCAT.VEHICELS_BIKE_COMPONENTS,
                             PRSUBCAT.VEHICELS_BIKE, PRSUBCAT.VEHICELS_UTILITIES, PRSUBCAT.VEHICELS_CAMPERS],
            PRCAT.REAL_ESTATE: [PRSUBCAT.REAL_ESTATE_HOLIDAY, PRSUBCAT.REAL_ESTATE_BUSINESS,
                                PRSUBCAT.REAL_ESTATE_PROPERTY, PRSUBCAT.REAL_ESTATE_HOUSES,
                                PRSUBCAT.REAL_ESTATE_PARKING, PRSUBCAT.REAL_ESTATE_COMMUNITY,
                                PRSUBCAT.REAL_ESTATE_FLATS],
            PRCAT.PHOTO_VIDEO: [PRSUBCAT.PHOTO_CAMERA, PRSUBCAT.VIDEO_CAMERA, PRSUBCAT.PHOTO_COMPONENTS],
            PRCAT.GARDEN_CRAFT: [PRSUBCAT.GARDEN_MATERIAL, PRSUBCAT.GARDEN_EQUIPMENT, PRSUBCAT.GARDEN_TOOLS],
            PRCAT.HOUSEHOLD: [PRSUBCAT.HOUSEHOLD_LIGHT, PRSUBCAT.HOUSEHOLD_TOOLS,
                              PRSUBCAT.HOUSEHOLD_FOOD, PRSUBCAT.HOUSEHOLD_FURNITURE],
            PRCAT.JOBS: [PRSUBCAT.JOBS_HEALTH, PRSUBCAT.JOBS_OTHERS],
        }
        return sub_category_dict.get(category, [])



