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
        self._information_score = self.__get_information_score__()

    @property
    def information_score(self):
        return self._information_score

    @property
    def intersection_labels(self):
        return self._intersection_labels

    def __get_information_score__(self) -> int:
        i_score = 0
        for label, value_list in self.__get_label_value_list_dict__().items():
            i_score += SalesmanEntityHandler.get_similarity_score_for_entity_label(label) * len(value_list)
        return i_score

    def __get_label_value_list_dict__(self) -> dict:
        if self._sale_02 is None:
            return self._sale_01.get_entity_label_main_value_list_dict()

        return_dict = {}
        entity_label_main_value_list_dict_01 = self._sale_01.get_entity_label_main_value_list_dict()
        entity_label_main_value_list_dict_02 = self._sale_02.get_entity_label_main_value_list_dict()
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
        i_s_source = SaleInformationScore(self._sale_source).information_score
        i_s_check = SaleInformationScore(self._sale_to_be_checked).information_score
        intersection_score_obj = SaleInformationScore(self._sale_source, self._sale_to_be_checked)
        i_s_intersection = intersection_score_obj.information_score
        self._are_sales_similar = 0.5 * i_s_source <= i_s_intersection <= i_s_check <= 2 * i_s_source
        self._similar_label = ' ,'.join(intersection_score_obj.intersection_labels)
        self._similar_score = i_s_intersection

    def __check_sales_for_similarity_old__(self) -> tuple:
        check_list = EL.get_all_for_similarity_check()
        checker_dict = {label: SaleSimilarityCheck4EntityLabel(self._sale_source, self._sale_to_be_checked, label)
                        for label in check_list}

        self._source_length_dict = {label: checker.elements_sale_source for label, checker in checker_dict.items()}
        self._to_check_length_dict = {label: checker.elements_sale_to_be_checked for label, checker in checker_dict.items()}

        self._is_similar_dict = {
            label: checker.is_sale_to_be_checked_similar_to_source for label, checker in checker_dict.items()}
        self._is_identical_dict = {
            label: checker.is_sale_to_be_checked_identical_to_source for label, checker in checker_dict.items()}
        self._is_identical_or_similar_dict = {
            label: self._is_similar_dict[label] or self._is_identical_dict[label] for label in checker_dict}

        similar_label_list = [label for label in check_list if self._is_similar_dict[label]]

        # if not self._is_identical_or_similar_dict[EL.PROPERTY]:
        #     return False, EL.PROPERTY

        if self._source_length_dict[EL.TARGET_GROUP] > 0 and not self._is_identical_or_similar_dict[EL.TARGET_GROUP]:
            return False, EL.TARGET_GROUP

        for label in similar_label_list:
            if label == EL.ANIMAL:
                return self._is_identical_or_similar_dict[EL.PROPERTY] \
                       and self.__are_two_label_conditions_fulfilled__(EL.JOB, EL.OBJECT), label
            elif label == EL.JOB:
                return self.__are_two_label_conditions_fulfilled__(EL.ANIMAL, EL.COMPANY), label
            elif label == EL.COMPANY:
                if EL.PRODUCT in similar_label_list:
                    return self.__are_two_label_conditions_fulfilled__(EL.PRODUCT, EL.OBJECT), label
                else:
                    return self._is_identical_or_similar_dict[EL.OBJECT], label
            elif label == EL.PRODUCT:
                return (self.__are_two_label_conditions_fulfilled__(EL.MATERIAL, EL.TARGET_GROUP)) or \
                       (self.__are_two_label_conditions_fulfilled__(EL.PROPERTY, EL.OBJECT)), label
            elif label in [EL.TARGET_GROUP, EL.COLOR]:
                return self.__are_two_label_conditions_fulfilled__(EL.PROPERTY, EL.OBJECT), label
        return False, ''

    def __are_two_label_conditions_fulfilled__(self, label_01: str, label_02: str):
        if self._is_identical_or_similar_dict[label_01] and self._is_identical_or_similar_dict[label_02]:
            return max(self._source_length_dict[label_01], self._to_check_length_dict[label_01],
                       self._source_length_dict[label_02], self._to_check_length_dict[label_02]) > 0
        return False


class SaleIdenticalCheck:
    def __init__(self, sale_01: SalesmanSale, sale_02: SalesmanSale, number_from_db=0):
        self._sale_01 = sale_01
        self._sale_02 = sale_02
        self._number_from_db = number_from_db
        self._different_columns = []
        self._are_identical = self.__are_sales_identical__()

    @property
    def are_identical(self):
        return self._are_identical

    @property
    def different_columns(self):
        return ', '.join(self._different_columns)

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
                print('\nNot identical "{}": \na) {} \nb) {}'.format(col, value_01, value_02))
                are_all_values_identical = False
        return are_all_values_identical

    def __get_columns_to_be_compared__(self):
        base_list = [SLDC.START_DATE, SLDC.TITLE, SLDC.DESCRIPTION, SLDC.PRICE_SINGLE, SLDC.PRICE, SLDC.NUMBER]
        if self._number_from_db > 0:
            base_list.append(SLDC.BOOK_MARKS)
        return base_list