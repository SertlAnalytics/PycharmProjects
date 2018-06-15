"""
Description: This module contains different url tools - lile reading or submitting
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-06-15
"""
from splinter import Browser
from sertl_analytics.pyurl.url_username_passwords import WebPasswords
from selenium import webdriver


class MyUrlBrowser:
    def __init__(self, url: str, user_name = '', password = ''):
        self.brower = Browser('chrome')
        self.driver = webdriver.Chrome()
        self.__url = url
        self.__user_name = user_name
        self.__password = password

    def __get_url__(self):
        if self.__user_name == '':
            return self.__url
        else:
            return 'https://' + self.__user_name + ':' + self.__password + '@wm2018.rs-home.com/'

    def get_by_selenium(self):
        self.driver.get(self.__get_url__())
        self.driver.switch_to_frame('Fleft')
        # abmelden = self.driver.find_element_by_link_text('Abmelden')
        # if len(abmelden) > 0:
        #     abmelden[0].click()
        anmelden = self.driver.find_element_by_link_text('Anmelden')
        if len(anmelden) == 0:
            anmelden = self.driver.find_link_by_href('login.asp?info=logon')
        if len(anmelden) > 0:
            print('anmelden...')
            anmelden[0].click()



    def visit(self):
        with self.brower as browser:
            browser.visit(self.__get_url__())
            object = browser.get_iframe('Fleft')
            browser.switch_to_frame(0)
            tag_list = browser.find_by_tag('frame')
            for tags in tag_list:
                print(tags.tag_name)
            abmelden = browser.find_link_by_text('Abmelden')
            if len(abmelden) > 0:
                abmelden[0].click()
            anmelden = browser.find_link_by_text('Anmelden')
            if len(anmelden) == 0:
                anmelden = browser.find_link_by_href('login.asp?info=logon')
            if len(anmelden) > 0:
                print('anmelden...')
                anmelden[0].click()

    def visit_old(self, url: str):
        with self.brower as browser:
            # Visit URL
            url = "http://www.google.com"
            browser.visit(url)
            browser.fill('q', 'splinter - python acceptance testing for web applications')
            # Find and click the 'search' button
            button = browser.find_by_name('btnG')
            # Interact with elements
            button.click()
            if browser.is_text_present('splinter.readthedocs.io'):
                print("Yes, the official website was found!")
            else:
                print("No, it wasn't found... We need to improve our SEO techniques")


wm2018_user = WebPasswords.WM2018_WATSON
my_browser = MyUrlBrowser('https://wm2018.rs-home.com/', wm2018_user[0], wm2018_user[1])
my_browser.get_by_selenium()
