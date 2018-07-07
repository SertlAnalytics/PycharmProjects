"""
Description: This module contains the main function for parsing XML - with some applications
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-05
"""
import bs4 as bs
import requests
from sertl_analytics.pybase.exceptions import MyException


class XMLParser:
    def __init__(self, url: str, tag: str, tag_attribute_dic: dict, sub_tag: str, sub_tag_dic: dict):
        self.__url = url
        self.__tag = tag
        self.__tag_attribute_dic = tag_attribute_dic
        self.__sub_tag = sub_tag
        self.__sub_tag_dic = sub_tag_dic
        self.__result_list = []
        self.__fill_result_list__()

    def get_result_list(self):
        return self.__result_list

    def get_result_dic(self):
        return {x[0]:x[1] for x in self.__result_list}

    def __fill_result_list__(self):
        resp = requests.get(self.__url)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        tag_object = soup.find(self.__tag, self.__tag_attribute_dic)
        if self.__tag == 'ol':
            for li in tag_object.findAll(self.__sub_tag):
                anchor = li.find('a')
                ticker = li.text.replace('(', ' ').replace(')', '').split()[-1]
                self.__result_list.append([ticker, anchor.text])
        elif self.__tag == 'table':
            for sub_tag in tag_object.findAll(self.__sub_tag)[1:]:
                td_list = sub_tag.findAll('td')
                element = [td_list[self.__sub_tag_dic[column]].text for column in self.__sub_tag_dic]
                element = self.__remove_ending_line_break__(element)
                self.__result_list.append(element)
        else:
            raise MyException('No XML parser defined for tag "{}"'.format(self.__tag))

    def __remove_ending_line_break__(self, element_list: list):
        return_list = [element[:-1] if  element[-1] == '\n' else element for element in element_list]
        return return_list


class XMLParser4SP500(XMLParser):
    def __init__(self):
        self.url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        self.tag = 'table'
        self.tag_attribute_dic = {'class': 'wikitable sortable'}
        self.sub_tag = 'tr'
        self.sub_tag_dic = {'ticker': 0, 'name': 1}
        XMLParser.__init__(self, self.url, self.tag, self.tag_attribute_dic, self.sub_tag, self.sub_tag_dic)


class XMLParser4DowJones(XMLParser):
    def __init__(self):
        self.url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
        self.tag = 'table'
        self.tag_attribute_dic = {'class': 'wikitable sortable'}
        self.sub_tag = 'tr'
        self.sub_tag_dic = {'ticker': 2, 'name': 0}
        XMLParser.__init__(self, self.url, self.tag, self.tag_attribute_dic, self.sub_tag, self.sub_tag_dic)


class XMLParser4Nasdaq100(XMLParser):
    def __init__(self):
        self.url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
        self.tag = 'ol'
        self.tag_attribute_dic = {}
        self.sub_tag = 'li'
        self.sub_tag_dic = {'ticker': 2, 'name': 0}
        XMLParser.__init__(self, self.url, self.tag, self.tag_attribute_dic, self.sub_tag, self.sub_tag_dic)


def save_sp500_tickers():
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        name = row.findAll('td')[1].text
        tickers.append([ticker, name])
    return tickers


# print(save_sp500_tickers())
# parser = XMLParser4Nasdaq100()
# print(parser.get_result_list())