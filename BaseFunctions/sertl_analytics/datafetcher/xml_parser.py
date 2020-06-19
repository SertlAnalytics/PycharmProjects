"""
Description: This module contains the main function for parsing XML - with some applications
Author: Josef Sertl
Link to BeautifulSoup docu: https://wiki.python.org/moin/beautiful%20soup
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-05
"""
import bs4 as bs
import requests
from sertl_analytics.myexceptions import MyException
from sertl_analytics.my_text import MyText


class WebParser:
    def __init__(self, url: str):
        self._url = url
        self._result_list = []
        self.__fill_result_list__()

    def get_result_list(self):
        return self._result_list

    def get_result_dic(self):
        return {x[0]: x[1] for x in self._result_list}

    def __fill_result_list__(self):
        resp = requests.get(self._url)
        for ind, line in enumerate(resp.text.splitlines()):
            if ind > 0:
                element = MyText.split_at_first(line, ' ')
                self._result_list.append(element)

    def __remove_ending_line_break__(self, element_list: list):
        return_list = [element[:-1] if  element[-1] == '\n' else element for element in element_list]
        return return_list

    def __remove_prefix__(self, element_list: list):
        # Sometimes we get a prefix for the element like NYSE: MMM
        return_list = []
        for element in element_list:
            return_element = ' '.join(element.split())
            position = return_element.find(' ')
            if position > - 1:
                return_element = return_element[position+1:]
            return_list.append(return_element)
        return return_list

class WebParser4FSE(WebParser):
    def __init__(self):
        WebParser.__init__(self, 'https://stooq.com/db/l/?g=29')

    def __fill_result_list__(self):
        WebParser.__fill_result_list__(self)
        for element in self._result_list:
            element[0] = element[0][:len(element[0])-3]

class XMLParserApi:
    def __init__(self):
        self.url = ''
        self.parent_tag = ''
        self.parent_tag_attribute_dic = {}
        self.tag = ''
        self.tag_attribute_dic = {}
        self.sub_tag = ''
        self.sub_tag_dic = {}

class XMLParser(WebParser):
    def __init__(self, api: XMLParserApi):
        self._url = api.url
        self._parent_tag = api.parent_tag
        self._parent_tag_attribute_dic = api.parent_tag_attribute_dic
        self._tag = api.tag
        self._tag_attribute_dic = api.tag_attribute_dic
        self._sub_tag = api.sub_tag
        self._sub_tag_dic = api.sub_tag_dic
        self._result_list = []
        self.__fill_result_list__()

    def get_result_list(self):
        return self._result_list

    def get_result_dic(self):
        return {x[0]:x[1] for x in self._result_list}

    def __fill_result_list__(self):
        resp = requests.get(self._url)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        if self._parent_tag != '':
            parent_tag_object = soup.find(self._parent_tag, self._parent_tag_attribute_dic)
            tag_object = parent_tag_object.findNext(self._tag, self._tag_attribute_dic)
        else:
            tag_object = soup.find(self._tag, self._tag_attribute_dic)

        if self._tag in ['ol', 'ul']:
            for li in tag_object.findAll(self._sub_tag):
                anchor = li.find('a')
                ticker = li.text.replace('(', ' ').replace(')', '').split()[-1]
                self._result_list.append([ticker, anchor.text])
        elif self._tag == 'table':
            for sub_tag in tag_object.findAll(self._sub_tag)[1:]:
                td_list = sub_tag.findAll('td')
                element = [td_list[self._sub_tag_dic[column]].text for column in self._sub_tag_dic]
                element = self.__remove_ending_line_break__(element)
                element = self.__remove_prefix__(element)
                self._result_list.append(element)
        else:
            raise MyException('No XML parser defined for tag "{}"'.format(self._tag))

    def __remove_ending_line_break__(self, element_list: list):
        return_list = [element[:-1] if  element[-1] == '\n' else element for element in element_list]
        return return_list

    def __remove_prefix__(self, element_list: list):
        # Sometimes we get a prefix for the element like NYSE: MMM
        return_list = []
        for element in element_list:
            return_element = ' '.join(element.split())
            position = return_element.find(' ')
            if position > - 1:
                return_element = return_element[position+1:]
            return_list.append(return_element)
        return return_list


class XMLParser4SP500(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        api.tag = 'table'
        api.tag_attribute_dic = {'class': 'wikitable sortable'}
        api.sub_tag = 'tr'
        api.sub_tag_dic = {'ticker': 0, 'name': 1}
        XMLParser.__init__(self, api)


class XMLParser4DowJones(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'
        api.tag = 'table'
        api.tag_attribute_dic = {'class': 'wikitable sortable'}
        api.sub_tag = 'tr'
        api.sub_tag_dic = {'ticker': 2, 'name': 0}
        XMLParser.__init__(self, api)


class XMLParser4Nasdaq100(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
        api.tag = 'table'
        # api.tag_attribute_dic = {'class': 'wikitable sortable'}
        api.tag_attribute_dic = {'id': 'constituents'}  # changed on 2020-02-08
        api.sub_tag = 'tr'
        api.sub_tag_dic = {'ticker': 1, 'name': 0}
        XMLParser.__init__(self, api)


class XMLParser4Nasdaq100Old(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
        api.parent_tag = 'div'
        api.parent_tag_attribute_dic = {'class': 'div-col columns column-width'}
        api.tag = 'ul'
        api.tag_attribute_dic = {}
        api.sub_tag = 'li'
        api.sub_tag_dic = {'ticker': 2, 'name': 0}
        XMLParser.__init__(self, api)

class XMLParser4Dax(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'https://de.wikipedia.org/wiki/DAX'
        api.tag = 'table'
        api.tag_attribute_dic = {'class': 'wikitable sortable'}
        api.sub_tag = 'tr'
        api.sub_tag_dic = {'ticker': 1, 'name': 0}
        XMLParser.__init__(self, api)

class XMLParser4MDax(XMLParser):
    def __init__(self):
        api = XMLParserApi()
        api.url = 'https://de.wikipedia.org/wiki/MDAX'
        api.tag = 'table'
        api.tag_attribute_dic = {'class': 'wikitable sortable'}
        api.sub_tag = 'tr'
        api.sub_tag_dic = {'ticker': 1, 'name': 0}
        XMLParser.__init__(self, api)

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