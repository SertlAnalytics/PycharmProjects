# ColumbiaX: course-v1:ColumbiaX+CSMM.101x+1T2018 - Assigment week 7
# I. Perceptron Learning Algorithm - 2018-04-04
# Copyright Josef Sertl (https://www.sertl-analytics.com)
# $ python3 problem1_3.py input1.csv output1.csv

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Perceptron:
    def __init__(self, input_file: str, output_file, to_be_plotted: bool, write_to_output: bool = False):
        self.input_file = input_file
        self.output_file = output_file
        self.to_be_plotted = to_be_plotted
        self.write_to_output = write_to_output
        self.df = self.get_data_frame_from_file()
        self.df.columns = ['x1', 'x2', 'y']
        self.df_a = self.df[self.df.y == 1]
        self.df_b = self.df[self.df.y != 1]
        self.np_input = np.array(self.df)
        self.np_values = self.np_input[:, :-1]
        self.np_values_a = np.array(self.df_a)[:, :-1]
        self.np_values_b = np.array(self.df_b)[:, :-1]
        self.np_labels = self.np_input[:, -1].reshape(self.np_values.shape[0],1)
        self.w_0 = 0
        self.weight = np.array([0,0])
        self.output_list = []
        self.plot_start()

    def plot_start(self):
        if self.to_be_plotted:
            plt.plot(self.np_values_a[:, 0], self.np_values_a[:, 1], 'g+')
            plt.plot(self.np_values_b[:, 0], self.np_values_b[:, 1], 'ro')
            plt.xticks(np.arange(0, 5, 0.25), rotation=40)

    def get_value_with_last_weight(self, w_0, value_vector, weight_vector) -> int:
        return w_0 + self.get_vector_product(value_vector, weight_vector)

    @staticmethod
    def get_vector_product(vector_1, vector_2) -> int:
        return vector_1.dot(vector_2)

    def get_offset(self, value_vector, weight_vector):
        return -self.get_vector_product(value_vector, weight_vector)

    @staticmethod
    def get_perceptron_value(val) -> int:
        return 1 if val > 0 else -1

    def get_data_frame_from_file(self):
        return pd.read_csv(self.input_file, header=None)

    def run_perceptron_algorithm(self):
        end_loop = False
        counter = 0
        while not end_loop:
            counter += 1
            # print('counter = {}'.format(counter))
            index = 0
            w_0 = self.w_0
            weight_v = np.array(self.weight)
            for value_v in self.np_values:
                y = self.np_labels[index][0]
                last_value = self.get_value_with_last_weight(w_0, value_v, weight_v)
                value_to_check = y * self.get_perceptron_value(last_value)
                if value_to_check <= 0:
                    weight_v = weight_v + y * value_v
                    w_0 = w_0 + y
                    print('error with {}, y = {} : new weight = {}, new b = {}'.format(value_v, y, weight_v, w_0))
                index += 1
            if np.array_equal(self.weight, weight_v) or counter > 200:
                self.add_plotting_data()
                end_loop = True
            self.w_0 = w_0
            self.weight = np.array(weight_v)
            self.output_list.append('{},{},{}'.format(self.weight[0], self.weight[1], self.w_0))
            if counter % 4 == 0:
                self.add_plotting_data()
        self.show_plotting()
        self.write_results()

    def print_data_details(self):
        print(self.df)
        print(self.df_a)
        print(self.df_b)
        print(self.np_values)
        print(self.np_values.shape)
        print(self.np_labels)
        print(self.np_labels.shape)
        print(self.weight)

    def add_plotting_data(self):
        if self.to_be_plotted:
            label = str(self.weight) + ' / b=' + str(self.w_0)
            plt.plot(self.np_values[:, 0], self.decision_boundary(self.np_values[:, 0]), label=label)

    def show_plotting(self):
        if self.to_be_plotted:
            plt.legend(loc=0)
            plt.show()

    def decision_boundary(self, x_vector):
        if self.weight[1] == 0:
            return x_vector * 0
        else:
            return x_vector * (-self.weight[0]/self.weight[1]) - (self.w_0/self.weight[1])

    def write_results(self):
        if self.write_to_output:
            with open(self.output_file, 'w') as file_obj:
                for entries in self.output_list:
                    file_obj.write(entries + '\n')
            print('Results written to {}'.format(file_obj.name))


test = False
if test:
    ptron = Perceptron('input1.csv', 'output1.csv', True, False)
elif len(sys.argv)> 1:  # started from command prompt
    ptron = Perceptron(sys.argv[1], sys.argv[2], False, True)
else:
    ptron = Perceptron('input1.csv', 'output1.csv', True, False)

ptron.run_perceptron_algorithm()