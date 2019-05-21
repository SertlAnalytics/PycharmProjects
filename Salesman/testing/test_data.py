"""
Description: This module contains test data for sale tests
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2019-05-21
"""


class TCKEY:  # Test cases keys
    MASTER = 'Master'
    CHILD_01 = 'Child_01'
    CHILD_02 = 'Child_02'


class SaleTestDataFactory:
    @staticmethod
    def get_test_data_dict_for_master_child_test():
        return {
            TCKEY.MASTER: {'Sale_ID': 'T_M_01', 'Version': 1, 'Is_my_sale': 1, 'Source': 'Tutti.ch', 'Region': 'Aargau',
                       'Product_Category': 'Spielzeuge & Basteln', 'Product_SubCategory': 'Spielzeuge',
                       'Sale_State': 'open', 'Link': 'https://www.tutti.ch/de/vi/aargau/spielzeuge-basteln/spielzeuge/hape-kugelbahn-the-roundabout-91-teilig/27993639',
                       'Start_Date': '2019-05-19', 'Location': 'Aargau, 5430', 'Object_State': 'like new',
                       'Title': "Hape, Kugelbahn 'The Roundabout' 91-teilig",
                       'Description': 'Nicht mehr ganz vollzählig (eines der 8 roten Teilchen und ein paar Kugeln fehlen). Sonst alles wie neu. Altersempfehlung: ab 4 Jahren',
                       'Material': '', 'Properties': '', 'Price': 30.0, 'Price_single': 30.0, 'Is_total_price': False,
                       'Price_orig': 0, 'Size': '', 'Number': 1, 'Visits': 25, 'Bookmarks': 2,
                       'Entity_labels': 'Hape, Kugelbahn, Roundabout',
                       'Entity_labels_dictionary': 'Hape (COMPANY), Kugelbahn (OBJECT), Roundabout (PRODUCT)',
                       'Found_by_labels': '', 'Last_Check_Date': '2019-05-19', 'Comment': 'Changes: Start_Date'},
            TCKEY.CHILD_01: {'Sale_ID': 'T_C_01', 'Version': 1, 'Is_my_sale': 0, 'Source': 'Tutti.ch', 'Region': 'Aargau',
                       'Product_Category': 'Spielzeuge & Basteln', 'Product_SubCategory': 'Spielzeuge',
                       'Sale_State': 'open',
                       'Link': 'https://www.tutti.ch/de/vi/aargau/spielzeuge-basteln/spielzeuge/hape-kugelbahn-the-roundabout-91-teilig/27993639',
                       'Start_Date': '2019-05-19', 'Location': 'Aargau, 5430', 'Object_State': 'like new',
                       'Title': "Hape, Kugelbahn 'The Roundabout' 91-teilig",
                       'Description': 'Nicht mehr ganz vollzählig (eines der 8 roten Teilchen und ein paar Kugeln fehlen). Sonst alles wie neu. Altersempfehlung: ab 4 Jahren',
                       'Material': '', 'Properties': '', 'Price': 30.0, 'Price_single': 30.0, 'Is_total_price': False,
                       'Price_orig': 0, 'Size': '', 'Number': 1, 'Visits': 25, 'Bookmarks': 2,
                       'Entity_labels': 'Hape, Kugelbahn, Roundabout',
                       'Entity_labels_dictionary': 'Hape (COMPANY), Kugelbahn (OBJECT), Roundabout (PRODUCT)',
                       'Found_by_labels': '', 'Last_Check_Date': '2019-05-19', 'Comment': 'Changes: Start_Date'},
            TCKEY.CHILD_02: {'Sale_ID': 'T_C_02', 'Version': 1, 'Is_my_sale': 0, 'Source': 'Tutti.ch', 'Region': 'Aargau',
                         'Product_Category': 'Spielzeuge & Basteln', 'Product_SubCategory': 'Spielzeuge',
                         'Sale_State': 'open',
                         'Link': 'https://www.tutti.ch/de/vi/aargau/spielzeuge-basteln/spielzeuge/hape-kugelbahn-the-roundabout-91-teilig/27993639',
                         'Start_Date': '2019-05-19', 'Location': 'Aargau, 5430', 'Object_State': 'like new',
                         'Title': "Hape, Kugelbahn 'The Roundabout' 91-teilig",
                         'Description': 'Nicht mehr ganz vollzählig (eines der 8 roten Teilchen und ein paar Kugeln fehlen). Sonst alles wie neu. Altersempfehlung: ab 4 Jahren',
                         'Material': '', 'Properties': '', 'Price': 30.0, 'Price_single': 30.0, 'Is_total_price': False,
                         'Price_orig': 0, 'Size': '', 'Number': 1, 'Visits': 25, 'Bookmarks': 2,
                         'Entity_labels': 'Hape, Kugelbahn, Roundabout',
                         'Entity_labels_dictionary': 'Hape (COMPANY), Kugelbahn (OBJECT), Roundabout (PRODUCT)',
                         'Found_by_labels': '', 'Last_Check_Date': '2019-05-19', 'Comment': 'Changes: Start_Date'}
        }