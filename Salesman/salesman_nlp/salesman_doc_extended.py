"""
Description: This module contains the npl doc with doc.extensions
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-03
"""
from sertl_analytics.constants.salesman_constants import OBJPROP, OBJST


class DocExtended:
    def __init__(self, doc):
        self._doc = doc
        self.price_original = self._doc._.price_original
        self.size = self._doc._.size
        self.age = self._doc._.age
        self.usage = self._doc._.usage
        self.warranty = self._doc._.warranty
        self.number = self._doc._.number
        self.is_for_renting = self._doc._.is_for_renting
        self.is_for_selling = self._doc._.is_for_selling
        self.is_new = self._doc._.is_new
        self.is_like_new = self._doc._.is_like_new
        self.is_cover_available = self._doc._.is_cover_available
        self.is_used = self._doc._.is_used
        self.price_single = self._doc._.price_single
        self.is_total_price = self._doc._.is_total_price
        self.is_single_price = self._doc._.is_single_price

    @property
    def doc(self):
        return self._doc

    @property
    def object_state(self):
        if self.is_like_new:
            return OBJST.LIKE_NEW
        elif self.is_used:
            return OBJST.USED
        else:
            return OBJST.NEW if self.is_new else OBJST.NOT_QUALIFIED

    def correct_single_price(self, price: float):
        if self.is_total_price and self.number != 0 and not self.is_single_price:
            self.price_single = int(price / self.number)
        if self.price_single == 0:
            self.price_single = price

    def get_property_dict(self):
        property_dict = {}
        if self.is_cover_available:
            property_dict[OBJPROP.ORIGINAL_COVER] = 'Yes'
        if self.size != '':
            property_dict[OBJPROP.SIZE] = self.size
        if self.age != '':
            property_dict[OBJPROP.AGE] = self.age
        if self.usage != '':
            property_dict[OBJPROP.USAGE] = self.usage
        if self.warranty != '':
            property_dict[OBJPROP.WARRANTY] = self.warranty
        return property_dict

    def get_property_dict_as_list(self):
        property_dict = self.get_property_dict()
        return ['{}: {}'.format(prop, property_dict[prop]) for prop in property_dict]

    def get_properties_for_data_dict(self):
        return ', '.join(self.get_property_dict_as_list())


