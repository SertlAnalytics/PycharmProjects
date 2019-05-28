import seaborn as sns
import time
import pandas as pd

data = sns.load_dataset('iris')


def compute_class(petal_length):
    if petal_length <= 2:
        return 1
    elif 2 < petal_length < 5:
        return 2
    else:
        return 3


start = time.monotonic()
class_list = list()
for index, data_row in data.iterrows():
    petal_length = data_row['petal_length']
    class_num = compute_class(petal_length)
    class_list.append(class_num)
end = time.monotonic()
print("Iterrows run time = {}".format(end - start))

start = time.monotonic()
class_list = data.apply(lambda row: compute_class(row['petal_length']), axis=1)
end = time.monotonic()
print(".apply() run time = {}".format(end - start))

start = time.monotonic()
data['petal_lenght_class'] = data['petal_length'].apply(compute_class)
class_list = list(data['petal_lenght_class'])
end = time.monotonic()
print(".apply() without lambda - run time = {}".format(end - start))

start = time.monotonic()
lass_list = pd.cut(x=data.petal_length, bins=[0, 2, 5, 100], include_lowest=True, labels=[1, 2, 3]).astype(int)
end = time.monotonic()
print(".cut() run time = {}".format(end - start))

# print('Class_list={}'.format(class_list))