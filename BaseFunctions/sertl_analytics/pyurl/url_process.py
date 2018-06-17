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
        # self.browser = Browser('chrome')
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
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
        self.driver.switch_to.frame('Fleft')
        # abmelden = self.driver.find_element_by_link_text('Abmelden')
        # if len(abmelden) > 0:
        #     abmelden[0].click()
        anmelden = self.driver.find_element_by_tag_name('link')

        if len(anmelden) == 0:
            anmelden = self.driver.find_element_by_link_text('Anmelden')
        if len(anmelden) > 0:
            print('anmelden...')
            anmelden[0].click()

    def send_email_to_sertl_analytics(self):
        self.driver.get(self.__get_url__())
        print(self.driver.title)
        # self.__print_all_elements__()

        dic = self.__get_field_value_dic__()
        for fields in dic:
            field_obj = self.driver.find_element_by_id(fields)
            field_obj.send_keys()
            field_obj.send_keys(dic[fields])

        self.__click_submit__()

    def loop_through_elements(self):
        self.driver.get(self.__get_url__())
        print(self.driver.title)
        # self.__print_all_elements__()

        dic = self.__get_field_value_dic__()
        for fields in dic:
            field_obj = self.driver.find_element_by_id(fields)
            field_obj.send_keys()
            field_obj.send_keys(dic[fields])

        self.__click_submit__()

        # title = self.driver.find_element_by_xpath('/html/head/title')
        # print('xpath.title={}'.format(title.text))
        # object = self.driver.find_element_by_name('Fmain')
        # elements = self.driver.find_elements_by_xpath('//frame')
        # self.driver.switch_to.frame('Fleft')
        # elements = self.driver.find_elements_by_xpath("//*[not(*)]")
        # for element in elements:
        #     print(element.tag_name)
        # print(self.driver.title)
        # title = self.driver.find_element_by_xpath('/html/head/title')
        # print('xpath.title={}'.format(title))
        # table = self.driver.find_element_by_xpath('//table')
        # print('xpath.table={}'.format(table))
        # links = self.driver.find_elements_by_xpath('//tr')
        # print('xpath.table.tr={}'.format(links))
        # links = self.driver.find_elements_by_xpath('//th')
        # print('xpath.table.th={}'.format(links))
        # tr = self.driver.find_elements_by_tag_name('tr')
        # print('find_elements_by_tag_name_tr={}'.format(tr))
        # th = self.driver.find_elements_by_tag_name('th')
        # print('find_elements_by_tag_name_th={}'.format(th))
        # links = self.driver.find_elements_by_xpath('/html/body/table/tr/th/a')
        # print('xpath/html/body/table/tr/th/a={}'.format(links))
        # home_link = self.driver.find_element_by_link_text('Home')
        # print('find_element_by_link_text_home'.format(home_link))
        # link_home = table.find_element_by_xpath('/html/body/table/tr/th/a[@href="welcome.asp"]').text
        # print(link_home)
        # # title = object.find_element_by_xpath('.//div[@class="title"]/a').text

    def __get_field_value_dic__(self):
        dic = {}
        dic['form_1509137867313_737065_value_firstname'] = 'Josef'
        dic['form_1509137867313_737065_value_lastname'] = 'Sertl'
        dic['form_1509137867313_737065_value_email'] = 'josef.sertl@web.de'
        dic['form_1509137867313_737065_value_telephone'] = '041 78 890 2261'
        dic['form_1509137867313_737065_value_message'] = 'My new message'
        return dic

    def __click_submit__(self):
        python_button = self.driver.find_elements_by_xpath("//input[@type='submit']")[0]
        python_button.click()

    def __print_all_elements__(self):
        elements = self.driver.find_elements_by_xpath("//*[not(*)]")
        for element in elements:
            print(element.tag_name)
        print(elements)

    def visit(self):
        with self.browser as browser:
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
# my_browser = MyUrlBrowser('https://wm2018.rs-home.com/', wm2018_user[0], wm2018_user[1])
# my_browser = MyUrlBrowser('https://wm2018.rs-home.com/')
my_browser = MyUrlBrowser('https://sertl-analytics.com/Contact/')
my_browser.send_email_to_sertl_analytics()
