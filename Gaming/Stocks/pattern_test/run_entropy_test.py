import pandas as pd
from sertl_analytics.mymath import EntropyHandler


class EntropyHandlerTest:
    def __init__(self):
        self._test_data = self.__get_test_data_list__()
        self._features = ['Name', 'Sex', 'Hair_color', 'School_level']
        self._labels = ['Schopping_Queen', 'University', 'Status']
        self._df = pd.DataFrame(self._test_data, columns=self._features + self._labels)
        # self._features = ['Hair_color']
        # self._labels = ['Schopping_Queen']
        # self._df = self._df[self._features + self._labels]

    @property
    def df(self):
        return self._df

    @property
    def features(self):
        return self._features

    @property
    def labels(self):
        return self._labels

    @staticmethod
    def __get_test_data_list__():
        return [
            # ['Name', 'Sex', 'Hair_color', 'School_level', 'Schopping_Queen', 'University'],
            ['Albert', 'M', 'Blond', 'High', 'No', 'Yes', 'Single'],
            ['Meier', 'M', 'Brown', 'College', 'No', 'No', 'Single'],
            ['Huber', 'M', 'Dark', 'High', 'No', 'Yes', 'Single'],
            ['Franz', 'M', 'Red', 'College', 'No', 'No', 'Single'],
            ['Miller', 'F', 'Blond', 'High', 'Yes', 'No', 'Maried'],
            ['Göhl', 'F', 'Brown', 'College', 'Yes', 'No', 'Maried'],
            ['Mirka', 'F', 'Dark', 'High', 'Yes', 'No', 'Partner'],
            ['Müller', 'F', 'Red', 'College', 'Yes', 'No', 'Partner'],
        ]

    @staticmethod
    def get_expected_result(label: str, feature: str):
        result_dict = {
            'Schopping_Queen_Name': [1.0, 0.0, 1.0, '100.0%'],
            'Schopping_Queen_Sex': [1.0, 0.0, 1.0, '100.0%'],
            'Schopping_Queen_Hair_color': [1.0, 1.0, 0.0, '0.0%'],
            'Schopping_Queen_School_level': [1.0, 1.0, 0.0, '0.0%'],
            'University_Name': [0.811, 0.0, 0.811, '100.0%'],
            'University_Sex': [0.811, 0.5, 0.311, '38.3%'],
            'University_Hair_color': [0.811, 0.5, 0.311, '38.3%'],
            'University_School_level': [0.811, 0.5, 0.311, '38.3%'],
            'Status_Name': [0.9055, 0.0, 0.9055, '100.0%'],
            'Status_Sex': [0.9055, 0.25, 0.6555, '72.4%'],
            'Status_Hair_color': [0.9055, 0.75, 0.1555, '17.2%'],
            'Status_School_level': [0.9055, 0.9055, 0.0, '0.0%']
        }
        return result_dict.get('{}_{}'.format(label, feature), [0, 0, 0, '0.0%'])

test = EntropyHandlerTest()
entropy_handler = EntropyHandler(test.df, test.labels, test.features)
for label in test.labels:
    for feature in test.features:
        information_gain = entropy_handler.calculate_information_gain_for_label_and_feature(label, feature)
        expected_gain = test.get_expected_result(label, feature)
        print('label={}, feature={}: information_gain={}'.format(label, feature, information_gain))
        if information_gain != expected_gain:
            print('...not equal - expected={}'.format(expected_gain))

"""
Comments to these results:
a) Name: The names are all different => if we know the name we get an instant correct result. Huge gain.
b) ???
label=Schopping_Queen, feature=Name: information_gain=[1.0, 0.0, 1.0, '100.0%']
label=Schopping_Queen, feature=Sex: information_gain=[1.0, 0.0, 1.0, '100.0%']
label=Schopping_Queen, feature=Hair_color: information_gain=[1.0, 1.0, 0.0, '0.0%']
label=Schopping_Queen, feature=School_level: information_gain=[1.0, 1.0, 0.0, '0.0%']
label=University, feature=Name: information_gain=[0.811, 0.0, 0.811, '100.0%']
label=University, feature=Sex: information_gain=[0.811, 0.5, 0.311, '38.3%']
label=University, feature=Hair_color: information_gain=[0.811, 0.5, 0.311, '38.3%']
label=University, feature=School_level: information_gain=[0.811, 0.5, 0.311, '38.3%']
"""

