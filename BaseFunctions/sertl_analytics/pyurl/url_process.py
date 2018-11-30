"""
Description: This module contains different _url tools - lile reading or submitting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""
from splinter import Browser
from sertl_analytics.pyurl.url_username_passwords import WebPasswords
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from time import sleep


class MyUrlBrowser:
    def __init__(self, url: str, user_name='', password='', enforce_password_in_url = False):
        # self.browser = Browser('chrome')
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        self._url = url
        self._user_name = user_name
        self._password = password
        self._enforce_password_in_url = enforce_password_in_url
        self.driver.get(self.__get_url__())

    def __get_url__(self):
        if self._enforce_password_in_url:
            return 'https://' + self._user_name + ':' + self._password + '@wm2018.rs-home.com/'
        else:
            return self._url

    def __enter_and_submit_credentials__(self):
        dic = self.__get_credential_values__()
        for fields in dic:
            field_obj = self.driver.find_element_by_name(fields)
            field_obj.send_keys(dic[fields])
        self.__click_submit__()

    def __get_credential_values__(self) -> dict:
        pass

    def __print_cookies__(self):
        cookies_list = self.driver.get_cookies()
        print(cookies_list)

    def __wm2018_click_submit__(self):
        python_button = self.driver.find_elements_by_xpath("//input[@type='submit']")[0]
        python_button.click()

    def __print_all_elements__(self):
        elements = self.driver.find_elements_by_xpath("//*[not(*)]")
        for element in elements:
            print(element.tag_name)
            if element.tag_name == 'a':
                print(element.text)

    def __click_submit__(self):
        python_button = self.driver.find_elements_by_xpath("//input[@type='submit']")[0]
        python_button.click()


class MyUrlBrowser4SertlAnalytics(MyUrlBrowser):
    def __init__(self):
        MyUrlBrowser.__init__(self, 'https://sertl-analytics.com')

    def send_email_message(self, message: str):
        link_contact = self.__get_link_for_contact__()
        link_contact.click()
        self.__add_message__(message)
        self.__click_submit__()

    def __get_link_for_contact__(self):
        link_list = self.driver.find_elements_by_tag_name('a')
        for link in link_list:
            if link.text == 'Contact':
                return link
        return None

    def __add_message__(self, message):
        dic = self.__get_field_value_dic__(message)
        for fields in dic:
            field_obj = self.driver.find_element_by_id(fields)
            field_obj.send_keys(dic[fields])

    def __get_field_value_dic__(self, message: str):
        dic = {}
        dic['form_1509137867313_737065_value_firstname'] = 'Josef'
        dic['form_1509137867313_737065_value_lastname'] = 'Sertl'
        dic['form_1509137867313_737065_value_email'] = 'josef.sertl@web.de'
        dic['form_1509137867313_737065_value_telephone'] = '041 78 890 2261'
        dic['form_1509137867313_737065_value_message'] = message
        return dic


class MyUrlBrowser4WM2018(MyUrlBrowser):
    def __init__(self, user_name: str, password: str):
        MyUrlBrowser.__init__(self, 'https://wm2018.rs-home.com', user_name, password, False)

    def add_results(self, result_list: list):
        self.__switch_to_sub_frame__('Fnavigate')
        self.__click_anmelden__()
        self.__switch_to_sub_frame__('Fcontent')
        self.__enter_and_submit_credentials__()
        self.__switch_to_sub_frame__('Fnavigate')
        self.__click_tippen__()
        self.__switch_to_sub_frame__('Fcontent')
        self.__add_and_submit_results__(result_list)

    def __add_and_submit_results__(self, result_list):
        for results in result_list:
            self.__add_match_result__(results[0], results[1], results[2])
        self.__click_submit__()

    def __add_match_result__(self, match_id: int, goal_1: int, goal_2: int):
        dic = {'USERA' + str(match_id): goal_1, 'USERB' + str(match_id): goal_2}
        for fields in dic:
            field_obj = self.driver.find_element_by_name(fields)
            field_obj.clear()
            field_obj.send_keys(dic[fields])

    def __click_tippen__(self):
        link_tippen = self.driver.find_element_by_xpath('//a[@href="results.asp"]')
        link_tippen.click()

    def __click_anmelden__(self):
        link_anmelden = self.driver.find_element_by_xpath('//a[@href="login.asp?info=logon"]')
        link_anmelden.click()

    def __switch_to_sub_frame__(self, sub_frame_name: str):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('Fmain')
        self.driver.switch_to.frame(sub_frame_name)

    def __get_credential_values__(self) -> dict:
        return {'EBUserName': self._user_name, 'EBPassword': self._password}


class MyUrlBrowser4WM2018Watson(MyUrlBrowser4WM2018):
    def __init__(self):
        MyUrlBrowser4WM2018.__init__(self,  WebPasswords.WM2018_WATSON[0],  WebPasswords.WM2018_WATSON[1])


class MyUrlBrowser4WM2018Wladimir(MyUrlBrowser4WM2018):
    def __init__(self):
        MyUrlBrowser4WM2018.__init__(self, WebPasswords.WM2018_WLADIMIR[0], WebPasswords.WM2018_WLADIMIR[1])


class MyUrlBrowser4CB(MyUrlBrowser):
    def __init__(self):
        _url = 'https://www.consorsbank.de/home'
        MyUrlBrowser.__init__(self, _url, WebPasswords.CB_JS[0], WebPasswords.CB_JS[1])

    def order_item(self, ticker: str, number: int):
        self.__click_anmelden__()
        self.__find_credential_fields__()
        # self.__enter_and_submit_credentials__()

    def __find_credential_fields__(self):
        self.driver.implicitly_wait(10)
        tags = self.driver.find_elements_by_tag_name('input')
        for tag in tags:
            print(tag.tag_name)

    def __click_anmelden__(self):
        link_anmelden = self.driver.find_element_by_xpath('//a[@class="button primary mini login ev-link-modal "]')
        link_anmelden.click()

    def __get_credential_values__(self) -> dict:
        return {'EBUserName': self._user_name, 'EBPassword': self._password}

# browser = MyUrlBrowser4WM2018Watson()
# browser.add_results([[15, 6, 2], [16, 7, 3], [18, 7, 4]])

# browser = MyUrlBrowser4SertlAnalytics()
# browser.send_email_message('Hallo world - 2018-06-18')
# result_list = [[15, 1, 2], [16, 2, 3], [17, 3, 4]]
# my_browser = MyUrlBrowser('https://wm2018.rs-home.com')  # https://Wladimir:E1wPlefv8V45N@wm2018.rs-home.com/results.asp
# my_browser.add_results(result_list)

