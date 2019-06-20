"""
Description: This module contains the important sale checker classes - which are fundamental for a good result
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-08
"""

from sertl_analytics.my_text import MyText
from sertl_analytics.constants.salesman_constants import SLDC
from sertl_analytics.constants.salesman_constants import EL
from salesman_sale import SalesmanSale
from entities.salesman_entity_handler import SalesmanEntityHandler


class SaleInformationScore:
    def __init__(self, sale_01: SalesmanSale, sale_02: SalesmanSale=None):
        self._sale_01 = sale_01
        self._sale_02 = sale_02
        self._intersection_labels = []
        self._information_score_01 = self.__get_information_score__(1)
        self._information_score_intersection = self.__get_information_score__(0)
        self._information_score_02_relative_to_01 = self.__get_information_score__(2)

    @property
    def information_score_intersection(self):
        return self._information_score_intersection

    @property
    def information_score_01(self):
        return self._information_score_01

    @property
    def information_score_02_relative_to_01(self):
        return self._information_score_02_relative_to_01

    @property
    def intersection_labels(self):
        return self._intersection_labels

    def __get_information_score__(self, target_flag: int) -> int:
        i_score = 0
        if target_flag == 1 and self._sale_01 is None:
            return 0
        if target_flag == 2 and self._sale_02 is None:
            return 0
        if target_flag == 0 and self._sale_01 is None or self._sale_02 is None:
            return 0
        for label, value_list in self.__get_label_value_list_dict__(target_flag).items():
            i_score += SalesmanEntityHandler.get_similarity_score_for_entity_label(label) * len(value_list)
        return i_score

    def __get_label_value_list_dict__(self, target_flag: int) -> dict:
        if target_flag == 1:
            return self._sale_01.entity_label_main_values_dict
        elif target_flag == 2:
            return_dict = {}
            for label in self._sale_01.entity_label_main_values_dict:
                if label in self._sale_02.entity_label_main_values_dict:
                    return_dict[label] = self._sale_02.entity_label_main_values_dict[label]
            return return_dict

        return_dict = {}
        entity_label_main_value_list_dict_01 = self._sale_01.entity_label_main_values_dict
        entity_label_main_value_list_dict_02 = self._sale_02.entity_label_main_values_dict
        for label_01, value_list_01 in entity_label_main_value_list_dict_01.items():
            if label_01 in entity_label_main_value_list_dict_02:
                self._intersection_labels.append(label_01)
                set_01 = set([value.lower() for value in value_list_01])
                set_02 = set([value.lower() for value in entity_label_main_value_list_dict_02[label_01]])
                return_dict[label_01] = list(set_01.intersection(set_02))
        return return_dict


class SaleSimilarityCheck4EntityLabel:
    def __init__(self, sale_source: SalesmanSale, sale_to_check: SalesmanSale, entity_label: str):
        self._sale_source = sale_source
        self._sale_to_check = sale_to_check
        self._entity_label = entity_label
        self._entity_list_source = self._sale_source.get_entity_list_by_entity_label(self._entity_label)
        self._entity_list_to_be_checked = self._sale_to_check.get_entity_list_by_entity_label(self._entity_label)
        self._is_sale_to_be_checked_similar_to_source = self.__is_sale_to_be_checked_similar_to_source__()
        self._is_sale_to_be_checked_identical_to_source = self.__is_sale_to_be_checked_identical_to_source__()

    @property
    def elements_sale_source(self) -> int:
        return len(self._entity_list_source)

    @property
    def elements_sale_to_be_checked(self) -> int:
        return len(self._entity_list_source)

    @property
    def is_sale_to_be_checked_similar_to_source(self) -> bool:
        return self._is_sale_to_be_checked_similar_to_source

    @property
    def is_sale_to_be_checked_identical_to_source(self) -> bool:
        return self._is_sale_to_be_checked_identical_to_source

    def __is_sale_to_be_checked_similar_to_source__(self) -> bool:
        if self.elements_sale_source == self.elements_sale_to_be_checked == 0:
            return False
        if self.elements_sale_to_be_checked == 0:
            return False
        # Now we have at least one entry in any of the lists...
        set_01 = set([entity_name.lower() for entity_name in self._entity_list_source])
        set_02 = set([entity_name.lower() for entity_name in self._entity_list_to_be_checked])
        set_intersection = set_01.intersection(set_02)
        if len(set_intersection) == 0:  # we don't have anything in common
            return False
        if self._entity_label == EL.OBJECT:
            return len(set_intersection) * 2 >= max(len(set_01), len(set_02))  # we have too many other entities per set
        else:
            return len(set_intersection) > 0

    def __is_sale_to_be_checked_identical_to_source__(self) -> bool:
        set_01 = set([entity_name.lower() for entity_name in self._entity_list_source])
        set_02 = set([entity_name.lower() for entity_name in self._entity_list_to_be_checked])
        set_intersection = set_01.intersection(set_02)
        return len(set_intersection) == len(set_01) == len(set_02)


class SaleSimilarityCheck:
    def __init__(self, sale_source: SalesmanSale, sale_to_check: SalesmanSale):
        self._sale_source = sale_source
        self._sale_to_be_checked = sale_to_check
        self._are_sales_similar = False
        self._similar_label = ''
        self._similar_score = 0
        self._source_length_dict = {}
        self._to_check_length_dict = {}
        self._is_similar_dict = {}
        self._is_identical_dict = {}
        self._is_identical_or_similar_dict = {}
        self.__check_sales_for_similarity__()

    @property
    def are_sales_similar(self) -> bool:
        return self._are_sales_similar

    @property
    def similar_label(self) -> str:
        return self._similar_label

    @property
    def similar_score(self) -> int:
        return self._similar_score

    def __check_sales_for_similarity__(self):
        intersection_score_obj = SaleInformationScore(self._sale_source, self._sale_to_be_checked)
        i_s_source = intersection_score_obj.information_score_01
        i_s_intersection = intersection_score_obj.information_score_intersection
        i_s_check_relative_to_source = intersection_score_obj.information_score_02_relative_to_01
        self._are_sales_similar = 0.5 * i_s_source <= i_s_intersection <= i_s_check_relative_to_source < 2 * i_s_source
        self._similar_label = ', '.join(intersection_score_obj.intersection_labels)
        self._similar_score = i_s_intersection


class SaleIdenticalCheck:
    def __init__(self, sale_01: SalesmanSale, sale_02: SalesmanSale, number_from_db=0):
        self._sale_01 = sale_01
        self._sale_02 = sale_02
        self._number_from_db = number_from_db
        self._prefixes = self.__get_print_prefixes__()
        self._different_columns = []
        self._are_identical = self.__are_sales_identical__()

    @property
    def are_identical(self):
        return self._are_identical

    @property
    def different_columns(self):
        return ', '.join(self._different_columns)

    def __get_print_prefixes__(self):
        return {0: ['a', 'b'], 1: ['DB', 'Online'], 2: ['Online', 'DB']}.get(self._number_from_db, ['a', 'b'])

    def __are_sales_identical__(self) -> bool:
        are_all_values_identical = True
        for col in self.__get_columns_to_be_compared__():
            value_01, value_02 = self._sale_01.get_value(col), self._sale_02.get_value(col)
            are_single_values_identical = value_01 == value_02
            if not are_single_values_identical:
                if col == SLDC.BOOK_MARKS:  # we want to have the higher number in the database
                    if self._number_from_db == 2:
                        are_single_values_identical = value_02 >= value_01
                    else:
                        are_single_values_identical = value_01 >= value_02
                else:
                    if type(value_01) is str and type(value_02) is str:
                        are_single_values_identical = MyText.are_values_identical(value_01, value_02)
            if not are_single_values_identical:
                self._different_columns.append(col)
                print('\nNot identical "{}": \n{}) {} \n{}) {}'.format(
                    col, self._prefixes[0], value_01, self._prefixes[1], value_02))
                are_all_values_identical = False
        return are_all_values_identical

    def __get_columns_to_be_compared__(self):
        base_list = [SLDC.START_DATE, SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE_SINGLE, SLDC.PRICE, SLDC.NUMBER]
        if self._number_from_db > 0:
            base_list.append(SLDC.BOOK_MARKS)
        return base_list

