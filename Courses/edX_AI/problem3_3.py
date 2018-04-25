# ColumbiaX: course-v1:ColumbiaX+CSMM.101x+1T2018 - Assigment week 7
# III. Classification - 2018-04-06
# Each point is a comma-separated ordered triple, representing age, weight, and height.
# Copyright Josef Sertl (https://www.sertl-analytics.com)
# $ python3 problem2_3.py input2.csv output2.csv
# CAUTION: Please remove all plotting - will raise an error within the workbench on vocareum
# svm_linear,0.59,0.59
# svm_polynomial,0.7067,0.7
# svm_rbf,0.95,0.945
# logistic,0.55,0.525
# knn,0.9333,0.935
# decision_tree,0.9567,0.97
# random_forest,0.9667,0.945

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_validate
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


class ClassificationPlotter:
    def __init__(self, X, y, number_models: int):
        self.number_subplots = number_models + 1  # one extra for the original
        self.number_subplot_rows = int((self.number_subplots + 1)/2)
        self.fig = plt.figure(facecolor='w', edgecolor='r')
        self.ax = self.fig.add_subplot(111)
        self.ax.patch.set_facecolor('#ffb07c')  # https://xkcd.com/color/rgb/
        self.X = X
        self.y = y
        self.X1 = self.X[:, 0]
        self.X2 = self.X[:, 1]
        self.xx, self.yy = self.get_meshgrid()
        self.current_subplot = 0
        self.y_c = self.get_y_color()
        # print(self.y_c)

    def show(self):
        # plt.legend(loc=0)
        plt.tight_layout()
        plt.show()

    def get_y_color(self):
        color = ['blue', 'green', 'red']
        return [color[int(v)] for v in self.y]

    def activate_next_subplot_with_original_data(self, title: str):
        self.activate_next_subplot()
        plt.scatter(self.X1, self.X2, marker='o', edgecolors='w', c=self.y_c, s=20)
        plt.title(title)

    def mark_misclassified_test_data(self, X_test, y_test, y_pred):
        mask_ok = np.where((y_test == y_pred), True, False)

        X_test_ok = X_test[np.ix_(mask_ok)]
        plt.scatter(X_test_ok[:, 0], X_test_ok[:, 1], s=40, facecolors='none', edgecolors='g'
                    , label='correctly classified test data')

        mask_nok = np.logical_not(mask_ok)
        X_test_nok = X_test[mask_nok, :]
        plt.scatter(X_test_nok[:, 0], X_test_nok[:, 1], s=40, facecolors='none', edgecolors='y'
                    , label='misclassified test data')

        plt.legend(loc=0)

        # print(X_test)
        # print(mask_ok)
        # print(y_test)
        # print(y_pred)

    def plot_decision_function_for_model(self, model_name, model):
        self.activate_next_subplot_with_original_data(model_name)
        if model_name == 'xsvm_linear':
            Z = model.decision_function(np.c_[self.xx.ravel(), self.yy.ravel()])
            # Put the result into a color plot
            Z = Z.reshape(self.xx.shape)
            plt.pcolormesh(self.xx, self.yy, Z > 0, cmap=plt.cm.Paired)
            plt.contour(self.xx, self.yy, Z, colors=['k', 'k', 'k'],
                        linestyles=['--', '-', '--'], levels=[-.5, 0, .5])
        else:
            Z = model.predict(np.c_[self.xx.ravel(), self.yy.ravel()])
            Z = Z.reshape(self.xx.shape)
            plt.contourf(self.xx, self.yy, Z, cmap=plt.cm.coolwarm, alpha=0.8)

    def activate_next_subplot(self):
        self.current_subplot += 1
        plt.subplot(self.number_subplot_rows, 2, self.current_subplot)

    def get_meshgrid(self, h=0.02):
        x_min, x_max = self.X1.min() - 1, self.X1.max() + 1
        y_min, y_max = self.X2.min() - 1, self.X2.max() + 1
        print('x_min={}, x_max={}, y_min={}, y_max={}'.format(x_min, x_max, y_min, y_max))
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))
        return xx, yy


class Classification:
    def __init__(self, input_file: str, output_file, to_be_plotted: bool, write_to_output: bool = False):
        self.model_names = self.get_model_names()
        self.input_file = input_file
        self.output_file = output_file
        self.to_be_plotted = to_be_plotted
        self.write_to_output = write_to_output
        self.df = self.get_data_frame_from_file()
        # self.linearise_df()
        self.print_df_details()
        self.np_input = np.array(self.df)
        self.np_values = self.np_input[:, :-1]
        self.np_labels = self.np_input[:, -1]  #.reshape(self.np_values.shape[0],1)
        # self.overwrite_with_iris_data()
        self.number_test_cases = self.np_values.shape[0]
        self.np_mean = np.mean(self.np_values, axis=0)
        self.np_std = np.std(self.np_values, axis=0)
        self.output_list = []
        self.plotter = self.get_plotter()
        self.plot_start()

    def linearise_df(self):
        self.df.loc[self.df.A + self.df.B < 4, 'label'] = 1
        self.df.loc[self.df.A + self.df.B > 4, 'label'] = 0

    def overwrite_with_iris_data(self):
        iris = datasets.load_iris()
        # Take the first two features. We could avoid this by using a two-dim dataset
        self.np_values = iris.data[:, :2]
        self.np_labels = iris.target

    def get_model_names(self):
        return ['svm_linear', 'svm_polynomial', 'svm_rbf', 'logistic', 'knn', 'decision_tree', 'random_forest']
        return ['svm_linear']

    def get_plotter(self):
        return ClassificationPlotter(self.np_values, self.np_labels, len(self.model_names))

    def print_df_details(self):
        print(self.df)
        print(self.df.info())
        print(self.df.describe())

    def scale_np_values(self):
        self.np_values = (self.np_values - np.mean(self.np_values, axis=0)) / np.std(self.np_values, axis=0)

    def add_intercept_to_np_values(self):
        self.np_values = np.c_[np.ones(self.number_test_cases), self.np_values]

    def plot_start(self):
        if self.to_be_plotted:
            self.plotter.activate_next_subplot_with_original_data('original')

    @staticmethod
    def get_vector_product(vector_1, vector_2):
        return vector_1.dot(vector_2)

    def get_data_frame_from_file(self):
        return pd.read_csv(self.input_file, header=0)

    def run_algorithm(self):
        # fit the model
        X = self.np_values
        y = self.np_labels

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.40, stratify=y)
        print('X.shape={}, y.shape={}, X_train.shape={}, X_test.shape={}, y_train.shape={}, y_test.shape={}'
              .format(X.shape, y.shape, X_train.shape, X_test.shape, y_train.shape, y_test.shape))

        for index, model_name in enumerate(self.model_names):
            param_grid = self.get_param_grid(model_name)
            print('{}: parameters: {}'.format(model_name, param_grid))
            self.run_model(index + 1, model_name, param_grid, X, y, X_train, y_train, X_test, y_test)
        self.show_plotting()
        self.write_results()

    def run_model(self, run_number, model_name, param_grid, X, y, X_train, y_train, X_test, y_test):
        base_model = self.get_base_model(model_name)
        gs_cv = GridSearchCV(base_model, param_grid, cv=5)
        gs_cv.fit(X_train, y_train)
        # get real model with best parameters
        model = self.get_model_for_best_parameters(model_name, gs_cv)
        model.fit(X_train, y_train)
        # Predict the labels of the test set: y_pred
        y_pred = model.predict(X_test)
        # Compute and print metrics
        print("Best accuracy for training data: {}".format(gs_cv.best_score_))
        print("Accuracy for test data: {}".format(model.score(X_test, y_test)))
        # print(classification_report(y_test, y_pred))
        if self.to_be_plotted:
            self.plotter.plot_decision_function_for_model(model_name, model)
            self.plotter.mark_misclassified_test_data(X_test, y_test, y_pred)
        self.output_list.append('{},{},{}'.format(model_name, round(gs_cv.best_score_, 4),
                                                  round(model.score(X_test, y_test), 4)))

    def create_figure(self, run_number: int, model_name: str, model, X, X_test):
        plt.figure(run_number)
        plt.clf()
        plt.scatter(X[:, 0], X[:, 1], c='r', zorder=10, cmap=plt.cm.Paired,
                    edgecolor='k', s=20)

        # Circle out the test data
        plt.scatter(X_test[:, 0], X_test[:, 1], s=80, facecolors='none',
                    zorder=10, edgecolor='k')

        plt.axis('tight')
        x_min = X[:, 0].min()
        x_max = X[:, 0].max()
        y_min = X[:, 1].min()
        y_max = X[:, 1].max()

        XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
        Z = model.decision_function(np.c_[XX.ravel(), YY.ravel()])

        # Put the result into a color plot
        Z = Z.reshape(XX.shape)
        plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
        plt.contour(XX, YY, Z, colors=['k', 'k', 'k'],
                    linestyles=['--', '-', '--'], levels=[-.5, 0, .5])

        plt.title(model_name)

    def get_base_model(self, model_name: str):
        if model_name == 'svm_linear':
            return svm.SVC()
        elif model_name == 'svm_polynomial':
            return svm.SVC()
        elif model_name == 'svm_rbf':
            return svm.SVC()
        elif model_name == 'logistic':
            return LogisticRegression()
        elif model_name == 'knn':
            return KNeighborsClassifier()
        elif model_name == 'decision_tree':
            return DecisionTreeClassifier()
        elif model_name == 'random_forest':
            return RandomForestClassifier()

    def get_model_for_best_parameters(self, model_name: str, gs_cv: GridSearchCV):
        p_dic = gs_cv.best_params_
        print('{}: using best parameter: {}'.format(model_name, p_dic))
        if model_name == 'svm_linear':
            return svm.SVC(kernel='linear', C= p_dic['C'])
        elif model_name == 'svm_polynomial':
            return svm.SVC(kernel='poly', C=p_dic['C'], degree=p_dic['degree'], gamma=p_dic['gamma'])
        elif model_name == 'svm_rbf':
            return svm.SVC(kernel='rbf', C=p_dic['C'], gamma=p_dic['gamma'])
        elif model_name == 'logistic':
            return LogisticRegression(C=p_dic['C'])
        elif model_name == 'knn':
            return KNeighborsClassifier(n_neighbors=p_dic['n_neighbors'], leaf_size=p_dic['leaf_size'])
        elif model_name == 'decision_tree':
            return DecisionTreeClassifier(min_samples_split=p_dic['min_samples_split'])
        elif model_name == 'random_forest':
            return RandomForestClassifier(max_depth=p_dic['max_depth'], min_samples_split=p_dic['min_samples_split'])

    def get_param_grid(self, model_name: str):
        if model_name == 'svm_linear':
            return {'kernel': ['linear'], 'C': [0.1, 0.5, 1, 5, 10, 50, 100]}
        elif model_name == 'svm_polynomial':
            return {'kernel': ['poly'], 'C': [0.1, 1, 3], 'degree': [3, 4, 5, 6], 'gamma': [0.1, 0.5]}
        elif model_name == 'svm_rbf':
            return {'kernel': ['rbf'], 'C': [0.1, 0.5, 1, 5, 10, 50, 100], 'gamma': [0.1, 0.5, 1, 3, 6, 10]}
        elif model_name == 'logistic':
            return {'C': [0.1, 0.5, 1, 5, 10, 50, 100]}
        elif model_name == 'knn':
            return {'n_neighbors': [i for i in range(1, 51)], 'leaf_size': [i for i in range(5, 61, 5)]}
        elif model_name == 'decision_tree':
            return {'max_depth': [i for i in range(1, 51)], 'min_samples_split': [i for i in range(2, 11, 2)]}
        elif model_name == 'random_forest':
            return {'max_depth': [i for i in range(1, 51)], 'min_samples_split': [i for i in range(2, 11, 2)]}

    def print_data_details(self):
        print(self.df)
        print(self.np_input)

    def test(self):
        X = self.np_values
        y = self.np_labels

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.40, stratify=y)
        kernel_list = ['linear', 'rbf', 'poly']
        kernel_list = ['linear']
        for fig_num, kernel in enumerate(kernel_list):
            clf = svm.SVC(kernel=kernel, gamma=10)
            clf.fit(X_train, y_train)

            plt.figure(fig_num)
            plt.clf()
            plt.scatter(X[:, 0], X[:, 1], c='r', zorder=10, cmap=plt.cm.Paired,
                        edgecolor='k', s=20)

            # Circle out the test data
            plt.scatter(X_test[:, 0], X_test[:, 1], s=80, facecolors='none',
                        zorder=10, edgecolor='k')

            plt.axis('tight')
            x_min = X[:, 0].min()
            x_max = X[:, 0].max()
            y_min = X[:, 1].min()
            y_max = X[:, 1].max()

            XX, YY = np.mgrid[x_min:x_max:200j, y_min:y_max:200j]
            Z = clf.decision_function(np.c_[XX.ravel(), YY.ravel()])

            # Put the result into a color plot
            Z = Z.reshape(XX.shape)
            plt.pcolormesh(XX, YY, Z > 0, cmap=plt.cm.Paired)
            plt.contour(XX, YY, Z, colors=['k', 'k', 'k'],
                        linestyles=['--', '-', '--'], levels=[-.5, 0, .5])

            plt.title(kernel)
        plt.show()

    def add_plotting_data(self, alpha, with_color_bar):
        if self.to_be_plotted:
           pass

    def show_plotting(self):
        if self.to_be_plotted:
            self.plotter.show()

    def write_results(self):
        if self.write_to_output:
            with open(self.output_file, 'w') as file_obj:
                for entries in self.output_list:
                    file_obj.write(entries + '\n')
            print('Results written to {}'.format(file_obj.name))
        else:
            print('Writting not activated')

#
classification = Classification('input3.csv', 'output3.csv', True, False)
classification.run_algorithm()

# import some data to play with


def print_iris():
    # http://ogrisel.github.io/scikit-learn.org/sklearn-tutorial/auto_examples/tutorial/plot_knn_iris.html
    iris = datasets.load_iris()
    X = iris.data[:, :2] # we only take the first two features.
    Y = iris.target


    h = .02 # step size in the mesh

    knn=KNeighborsClassifier()

    # we create an instance of Neighbours Classifier and fit the data.
    knn.fit(X, Y)

    # Plot the decision boundary. For that, we will asign a color to each
    # point in the mesh [x_min, m_max]x[y_min, y_max].
    x_min, x_max = X[:,0].min() - .5, X[:,0].max() + .5
    y_min, y_max = X[:,1].min() - .5, X[:,1].max() + .5
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = knn.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure(1, figsize=(4, 3))
    plt.set_cmap(plt.cm.Paired)
    plt.pcolormesh(xx, yy, Z)

    # Plot also the training points
    plt.scatter(X[:,0], X[:,1],c=Y, marker='o' )
    plt.xlabel('Sepal length')
    plt.ylabel('Sepal width')

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.xticks(())
    plt.yticks(())

    plt.show()