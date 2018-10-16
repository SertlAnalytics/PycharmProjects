import pandas as pd
from sertl_analytics.mymath import EntropyHandler


class EntropyHandlerTest:
    def __init__(self):
        self._test_data = self.__get_test_data_list__()
        self._features = ['Name', 'Sex', 'Hair_color', 'School_level', 'Age']
        self._labels = ['Schopping_Queen', 'University']
        self._df = pd.DataFrame(self._test_data, columns=self._features + self._labels)

    @property
    def df(self):
        return self._df

    @property
    def features(self):
        return self._features

    @property
    def labels(self):
        return self._labels

    def __get_test_data_list__(self):
        return [
            # ['Name', 'Sex', 'Hair_color', 'School_level', 'Age', 'Schopping_Queen', 'University'],
            ['Müller', 'M', 'Blond', 'High', '34', 'No', 'Yes'],
            ['Meier', 'M', 'Brown', 'College', '35', 'No', 'No'],
            ['Huber', 'M', 'Dark', 'High', '36', 'No', 'No'],
            ['Franz', 'M', 'Blond', 'College', '37', 'No', 'Yes'],
            ['Sertl', 'F', 'Brown', 'High', '20', 'Yes', 'No'],
            ['Göhl', 'F', 'Dark', 'College', '21', 'Yes', 'No'],
            ['Name', 'F', 'Blond', 'College', '22', 'Yes', 'Yes'],
            ['Müller', 'F', 'Brown', 'College', '23', 'Yes', 'No'],
        ]


test = EntropyHandlerTest()
entropy_handler = EntropyHandler(test.df, test.labels, test.features)
for label in test.labels:
    for feature in test.features:
        information_gain = entropy_handler.calculate_information_gain_for_label_and_feature(label, feature)
        print('label={}, feature={}: information_gain={}'.format(label, feature, information_gain))

