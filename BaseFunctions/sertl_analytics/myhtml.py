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

    def get_text_for_sub_class(self, sub_class: str):
        sub_element = self._html_element.find_class(sub_class)[0]
        return sub_element.text_content()

    def get_attribute_for_sub_class(self, sub_class: str, att: str):
        sub_element = self._html_element.find_class(sub_class)[0]
        return sub_element.get(att)