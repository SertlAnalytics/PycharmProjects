"""
Description: This module contains the handler calls for all named entities for Salesman
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-06-04
"""


from sertl_analytics.constants.salesman_constants import EL
from entities.named_entity import NamedEntity
from entities.salesman_named_entity import ActivityEntity, AnimalEntity, BlackListEntity
from entities.salesman_named_entity import CompanyEntity, ClothesEntity, ColorEntity
from entities.salesman_named_entity import JobEntity, EducationEntity, EnvironmentEntity
from entities.salesman_named_entity import ProductEntity, PropertyEntity, PropertyPartEntity
from entities.salesman_named_entity import ObjectEntity, TargetGroupEntity
from entities.salesman_named_entity import MaterialEntity, PaymentEntity, ShopEntity
from entities.salesman_named_entity import TechnologyEntity, TransportEntity, VehicleEntity


class SalesmanEntityHandler:
    def __init__(self):
        self._label_list = EL.get_all()
        self._label_entity_dict = {label: self.__get_entity_for_entity_label__(label) for label in self._label_list}
        self._label_values_dict = {label: entity.entity_names
                                   for label, entity in self._label_entity_dict.items() if entity is not None}
        self._label_phrase_values_dict = {label: entity.get_entity_names_for_phrase_matcher()
                                          for label, entity in self._label_entity_dict.items() if entity is not None}
        self._entity_names = self.__get_entity_names__()
        self._entity_names_lower = [name.lower() for name in self._entity_names]
        self._entity_phrase_names = self.__get_entity_phrase_names__()

    @property
    def entity_names(self) -> list:
        return self._entity_names

    @property
    def entity_names_lower(self) -> list:
        return self._entity_names_lower

    @property
    def entity_phrase_names(self) -> list:
        return self._entity_phrase_names

    def get_entity_for_entity_label(self, entity_label: str) -> NamedEntity:
        return self._label_entity_dict.get(entity_label, None)

    def __get_entity_names__(self):
        return_list = []
        for label, names in self._label_values_dict.items():
            for name in names:
                if name in return_list:
                    raise Exception(label, 'Already as entity name available: {}'.format(name))
                else:
                    return_list.append(name)
        return return_list

    def __get_entity_phrase_names__(self):
        return_list = []
        for label, phrase_names in self._label_phrase_values_dict.items():
            for name in phrase_names:
                if name not in return_list:
                    return_list.append(name)
        return return_list

    def get_entity_names_for_all_entity_labels_without_loc(self, with_lower=False):
        return_list = []
        for entity_label in EL.get_all_without_loc():
            return_list = return_list + self._label_values_dict.get(entity_label, [])
        return [entry.lower() for entry in return_list] if with_lower else return_list

    def get_entity_phrase_names_for_entity_label(self, entity_label):
        return self._label_phrase_values_dict.get(entity_label, [])

    def get_synonyms_for_entity_name(self, entity_label: str, entity_name: str) -> list:
        # print('get_synonyms_for_entity_name: entity_label={}, entity_name={}'.format(entity_label, entity_name))
        entity_object = self._label_entity_dict[entity_label]
        if entity_object is None:
            return []
        synonym_dict = entity_object.entity_synonym_dict
        for key, synonym_list in synonym_dict.items():
            synonym_list_lower = [synonym.lower() for synonym in synonym_list]
            if key.lower() == entity_name.lower():
                return list(synonym_list)
            elif entity_name.lower() in synonym_list_lower:
                result_list = list(synonym_list)
                result_list.append(key)
                if entity_name in result_list:
                    result_list.remove(entity_name)
                return result_list
        return []

    def get_main_entity_name_for_entity_name(self, entity_label: str, entity_name: str) -> str:
        # print('get_main_entity_name_for_entity_name: entity_label={}, entity_name={}'.format(entity_label, entity_name))
        entity_obj = self._label_entity_dict[entity_label]
        if entity_obj is None:
            return entity_name
        for key, synonym_list in entity_obj.entity_synonym_dict.items():
            if entity_name == key:  # entity_name is already main entity_name
                return entity_name
            if entity_name in synonym_list:
                return key
        return entity_name

    def get_main_entity_value_label_dict(self, entity_value_label_dict: dict) -> dict:
        return {
            label_value: entity_label for label_value, entity_label in entity_value_label_dict.items()
            if self.get_main_entity_name_for_entity_name(entity_label, label_value) == label_value
        }

    @staticmethod
    def get_similarity_score_for_entity_label(entity_label: str) -> int:
        if entity_label in [EL.ANIMAL, EL.COMPANY, EL.PRODUCT]:
            return 10
        elif entity_label in [EL.EDUCATION, EL.TARGET_GROUP]:
            return 5
        elif entity_label in [EL.VEHICLE]:
            return 3
        else:
            return 1

    @staticmethod
    def __get_entity_for_entity_label__(entity_label: str) -> NamedEntity:
        return {
            EL.ACTIVITY: ActivityEntity(),
            EL.ANIMAL: AnimalEntity(),
            EL.BLACK_LIST: BlackListEntity(),
            EL.COMPANY: CompanyEntity(),
            EL.CLOTHES: ClothesEntity(),
            EL.COLOR: ColorEntity(),
            EL.JOB: JobEntity(),
            EL.EDUCATION: EducationEntity(),
            EL.ENVIRONMENT: EnvironmentEntity(),
            EL.PRODUCT: ProductEntity(),
            EL.PROPERTY: PropertyEntity(),
            EL.PROPERTY_PART: PropertyPartEntity(),
            EL.OBJECT: ObjectEntity(),
            EL.TARGET_GROUP: TargetGroupEntity(),
            EL.MATERIAL: MaterialEntity(),
            EL.PAYMENT: PaymentEntity(),
            EL.SHOP: ShopEntity(),
            EL.TECHNOLOGY: TechnologyEntity(),
            EL.TRANSPORT: TransportEntity(),
            EL.VEHICLE: VehicleEntity(),
        }.get(entity_label, None)