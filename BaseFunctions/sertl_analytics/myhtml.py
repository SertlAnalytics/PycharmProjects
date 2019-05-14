"""
Description: This module contains the wrapper classed for html and HtmlElement
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
See: https://docs.python-guide.org/scenarios/scrape/
Date: 2019-04-08
"""

from lxml import html
from lxml.html import HtmlElement


class MyHtmlElement:
    def __init__(self, html_element: HtmlElement):
        self._html_element = html_element

    @property
    def body(self):
        return self._html_element.body

    @property
    def classes(self):
        return self._html_element.classes
    
    def text_content(self):
        return self._html_element.text_content()
        
    def get_html_element_for_sub_class(self, sub_class: str):
        html_elements_for_sub_class = self._html_element.find_class(sub_class)
        if len(html_elements_for_sub_class) > 0:
            return MyHtmlElement(html_elements_for_sub_class[0])

    def get_text_for_sub_class(self, sub_class):
        child_element = self.__find_child_element_for_sub_class__(sub_class)
        return '. '.join(child_element.itertext()).strip()

    def __find_child_element_for_sub_class__(self, class_name):
        # we have sometimes more classes: <div class="_3HMUQ Gk7KC _1KGC- _3Ejud"><h2 class="-zQvW"> 350.-</h2></div>
        class_list = [class_name] if type(class_name) is str else list(class_name)
        elements_with_class = self._html_element.find_class(class_list[0])
        for element_with_class in elements_with_class:
            if set(element_with_class.classes) == set(class_list):
                return element_with_class

    def get_attribute_for_sub_class(self, sub_class: str, att: str):
        child_element = self.__find_child_element_for_sub_class__(sub_class)
        return child_element.get(att)