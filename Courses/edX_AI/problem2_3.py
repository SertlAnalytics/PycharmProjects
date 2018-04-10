# ColumbiaX: course-v1:ColumbiaX+CSMM.101x+1T2018 - Assigment week 7
# II. Linear Regression- 2018-04-05
# Each point is a comma-separated ordered triple, representing age, weight, and height.
# Copyright Josef Sertl (https://www.sertl-analytics.com)
# $ python3 problem2_3.py input2.csv output2.csv
# CAUTION: Please remove all plotting - will raise an error within the workbench on vocareum

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d import Axes3D


class LinearRegressionPlotter:
    def __init__(self, x, y, z, label_list):
        self.x = x
        self.y = y
        self.z = z
        self.x_mean = np.mean(self.x)
        self.x_std = np.std(self.x)
        self.y_mean = np.mean(self.y)
        self.y_std = np.std(self.y)
        # print('x_mean={}, x_std={}, y_mean={}, y_std={}'.format(self.x_mean, self.x_std, self.y_mean, self.y_std))
        self.label_list = label_list
        self.fig = None
        self.ax = None
        self.plot_values_as_scatter_3d()
        self.X = None
        self.Y = None
        self.init_basis_for_meshgrid()

    def show(self):
        plt.legend(loc=0)
        plt.show()

    def plot_values_as_scatter_3d(self):
        self.fig = plt.figure()
        self.ax = plt.axes(projection='3d')
        self.ax.scatter3D(self.x, self.y, self.z, c=self.z, cmap='Greens')
        self.ax.set_xlabel(self.label_list[0])
        self.ax.set_ylabel(self.label_list[1])
        self.ax.set_zlabel(self.label_list[2])

    def init_basis_for_meshgrid(self):
        x_r = np.arange(np.min(self.x), np.max(self.x), 0.1)
        y_r = np.arange(np.min(self.y), np.max(self.y), 0.25)
        self.X, self.Y = np.meshgrid(x_r, y_r)

    def plot_surface(self, alpha, lr_param, with_color_bar: bool):
        # print('plot_surface - lr_param = {}'.format(lr_param))
        zs = np.array([self.get_z_value(x, y, lr_param) for x, y in zip(np.ravel(self.X), np.ravel(self.Y))])
        Z = zs.reshape(self.X.shape)
        surf = self.ax.plot_surface(self.X, self.Y, Z, cmap=cm.coolwarm)
        # if with_color_bar:
        #     self.fig.colorbar(surf, shrink=0.5, aspect=5)

    def get_z_value(self, x, y, lr_param):
        return lr_param[0] + lr_param[1] * (x - self.x_mean)/self.x_std + lr_param[2] * (y - self.y_mean)/self.y_std


class LinearRegression:
    def __init__(self, input_file: str, output_file, to_be_plotted: bool, write_to_output: bool = False):
        self.input_file = input_file
        self.output_file = output_file
        self.to_be_plotted = to_be_plotted
        self.write_to_output = write_to_output
        self.df = self.get_data_frame_from_file()
        self.df.columns = ['age', 'weight', 'height']
        # self.print_df_details()
        self.np_input = np.array(self.df)
        self.np_values = self.np_input[:, :-1]
        self.number_test_cases = self.np_values.shape[0]
        self.np_labels = self.np_input[:, -1].reshape(self.np_values.shape[0], 1)
        self.np_mean = np.mean(self.np_values, axis=0)
        self.np_std = np.std(self.np_values, axis=0)
        self.scale_np_values()
        self.add_intercept_to_np_values()
        self.number_features = self.np_values.shape[1]
        self.beta_v = None
        self.init_beta()
        self.alpha_list = [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5, 10, 0.3]
        # self.alpha_list = [0.5, 1]
        self.output_list = []
        self.plotter = self.get_plotter()
        self.plot_start()

    def get_plotter(self):
        x = np.array(self.df['age'])
        y = np.array(self.df['weight'])
        z = np.array(self.df['height'])
        label_list = ['Age (in years)', 'Weight (in kg)', 'Height (in meters)']
        return LinearRegressionPlotter(x, y, z, label_list)

    def print_df_details(self):
        print(self.df)
        print(self.df.info())
        print(self.df.describe())

    def init_beta(self):
        self.beta_v = np.zeros((self.number_features, 1))

    def scale_np_values(self):
        self.np_values = (self.np_values - np.mean(self.np_values, axis=0)) / np.std(self.np_values, axis=0)

    def add_intercept_to_np_values(self):
        self.np_values = np.c_[np.ones(self.number_test_cases), self.np_values]

    def plot_start(self):
        if self.to_be_plotted:
            self.plotter.plot_values_as_scatter_3d()

    def get_loss(self):
        f = self.get_vector_product(self.np_values, self.beta_v)
        f_y = f - self.np_labels
        loss = 1/(2 * self.number_test_cases) * (self.get_vector_product(np.transpose(f_y), f_y))
        return loss[0][0]

    def calculate_new_beta(self, alpha: float):
        f = self.get_vector_product(self.np_values, self.beta_v)
        f_y = f - self.np_labels
        np_values_transpose = np.transpose(self.np_values)
        correction = (self.get_vector_product(np_values_transpose, f_y))
        self.beta_v = self.beta_v - (alpha/self.number_test_cases) * correction

    @staticmethod
    def get_vector_product(vector_1, vector_2):
        return vector_1.dot(vector_2)

    def get_data_frame_from_file(self):
        return pd.read_csv(self.input_file, header=None)

    def run_algorithm(self):
        run = 0
        for alpha in self.alpha_list:
            run += 1
            self.init_beta()
            loops = 1000 if alpha == 0.3 else 100
            for loop in range(0, loops):
                self.calculate_new_beta(alpha)
                loss = self.get_loss()
            self.output_list.append('{}, {}, {}, {}, {}, LOSS: {}'.
                                    format(alpha, loop + 1, self.beta(0), self.beta(1), self.beta(2), loss))
            self.add_plotting_data(alpha, run != -1)
        self.show_plotting()
        self.write_results()

    def print_data_details(self):
        print(self.df)
        print(self.np_input)

    def add_plotting_data(self, alpha, with_color_bar):
        if self.to_be_plotted:
            lr_param = [self.beta(0), self.beta(1), self.beta(2)]
            self.plotter.plot_surface(alpha, lr_param, with_color_bar)

    def y_vector(self, x_vector):
        if self.beta(2) == 0:
            return x_vector * 0
        else:
            return x_vector * (-self.beta(1) / self.beta(2)) - (self.beta(0) / self.beta(2))

    def beta(self, i):
        return round(self.beta_v[i][0], 4)

    def show_plotting(self):
        if self.to_be_plotted:
           self.plotter.show()

    def write_results(self):
        if self.write_to_output:
            with open(self.output_file, 'w') as file_obj:
                for entries in self.output_list:
                    file_obj.write(entries + '\n')
            print('Results written to {}'.format(file_obj.name))


test = True
if test:
    linReg = LinearRegression('input2.csv', 'output2.csv', True, True)
elif len(sys.argv)> 1:  # started from command prompt
    linReg = LinearRegression(sys.argv[1], sys.argv[2], False, True)
else:
    linReg = LinearRegression('input2.csv', 'output2.csv', True, False)

linReg.run_algorithm()