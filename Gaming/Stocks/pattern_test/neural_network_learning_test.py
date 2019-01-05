"""
Description: This module contains the test case for using neural networks from scikit-learn
Author: By Jose Portilla, Udemy Data Science Instructor.
https://www.kdnuggets.com/2016/10/beginners-guide-neural-networks-python-scikit-learn.html
Copyright: https://www.kdnuggets.com
Date: 2019-01-04
"""

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report,confusion_matrix


cancer = load_breast_cancer()
keys = cancer.keys()

X = cancer['data']
y = cancer['target']

X_train, X_test, y_train, y_test = train_test_split(X, y)

scaler = StandardScaler()
# Fit only to the training data
scaler.fit(X_train)

# Now apply the transformations to the data:
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

mlp = MLPClassifier(hidden_layer_sizes=(30,30,30))
mlp.fit(X_train,y_train)

predictions = mlp.predict(X_test)
print(confusion_matrix(y_test, predictions))
print(classification_report(y_test,predictions))
print('{}, {}, {}'.format(len(mlp.coefs_), len(mlp.coefs_[0]), len(mlp.intercepts_[0])))



