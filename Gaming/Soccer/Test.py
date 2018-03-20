import matplotlib.pyplot as plt
import seaborn as sns


class DataTypeTest:
    def __init__(self):
        self.t = (0, 1, 2, 3, 4, 5)
        self.x = [1, 2, "text"]
        self.y = [7, 3, 4, 5]
        self.dic = {1: 2, 2: 1, 3: 4, 4: 5, 5: 7}

    def plot(self):
        plt.plot(self.t, marker='x', label='tupel')
        plt.plot(self.y, marker='x', label='one list - horizontal = index')
        plt.plot(self.x, self.y, marker='x', label='lists x & y')

        # sns.barplot(self.dic)
        # plt.plot(self.dic, marker='x', label='dictionary')

        plt.legend(loc='lower right')
        plt.xticks(self.t)
        plt.yticks(self.t)

        plt.show()

    def show_is_in(self):
        print('tupel: a in t={}'.format(1 in self.t))
        print('list: 1 in y={}'.format(1 in self.y))
        print('dictionary: 7 in dic={}'.format(5 in self.dic))

    def show_sort(self):
        # print('tupel: t.sort()={}'.format(self.t.sort()))
        print('list: y.sort()={}'.format(self.y.sort()))
        # print('dictionary: dic.sort()={}'.format(self.dic.sort()))

    def get_count(self):
        print('tupel: t.count(1)={}'.format(self.t.count(1)))
        print('list: y.count(4)={}'.format(self.y.count("text")))
        # print('dictionary: dic.count(4)={}'.format(self.dic.count(4)))

    def get_index(self):
        print('tupel: t.index(1)={}'.format(self.t.index(1)))
        print('list: y.index(4)={}'.format(self.y.index("text")))
        # print('dictionary: dic.index(4)={}'.format(self.dic.index(4)))

    def show_len(self):
        print('tupel: len(t)={}'.format(len(self.t)))
        print('list: len(y)={}'.format(len(self.y)))
        print('dictionary: len(dic)={}'.format(len(self.dic)))

    def show_size(self):
        # print('tupel: t.size={}'.format(self.t.size))
        # print('list: y.size={}'.format(self.y.size))
        # print('dictionary: dic.size={}'.format(self.dic.size()))
        pass

    def show_shape(self):
        # print('tupel: t.shape={}'.format(self.t.shape))
        # print('list: y.shape={}'.format(self.y.shape))
        # print('dictionary: dic.shape={}'.format(self.dic.shape))
        pass

data_type_test = DataTypeTest()
data_type_test.show_is_in()
