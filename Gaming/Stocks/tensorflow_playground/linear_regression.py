"""
Description: This module contains linear regression with TensorFlow
Author: Josef Sertl
Copyright: SERTL Analytics, https://sertl-analytics.com
Date: 2018-05-14
"""

import numpy as np
from sklearn.datasets import fetch_california_housing
import tensorflow as tf
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
housing = fetch_california_housing()
scaler.fit(housing.data)
housing_data = scaler.transform(housing.data)
m, n = housing_data.shape
housing_data_plus_bias = np.c_[np.ones((m, 1)), housing_data]

X = tf.constant(housing_data_plus_bias, dtype=tf.float32, name='X')
y = tf.constant(housing.target.reshape(-1, 1), dtype=tf.float32, name='y')

XT = tf.transpose(X)
theta_ne = tf.matmul(tf.matmul(tf.matrix_inverse(tf.matmul(XT, X)), XT), y)

n_epochs = 10000
learning_rate = tf.constant(0.01)

theta = tf.Variable(tf.random_uniform([n + 1, 1], -1.0, 1.0), name='theta')
y_pred = tf.matmul(X, theta, name='prediction')
error = y_pred - y
mse = tf.reduce_mean(tf.square(error), name='mse')
mse_theta = tf.reduce_mean(tf.square(theta_ne-theta), name='mse_theta')
# gradients = 2/m * tf.matmul(tf.transpose(X), error)
with_optimizer = True
if with_optimizer:
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
    # optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.9)  # BEST !!!!
    training_op = optimizer.minimize(mse)
else:
    gradients = tf.gradients(mse, [theta])[0]
    training_op = tf.assign(theta, theta - learning_rate * gradients)

init = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)
    print('theta={}'.format(theta.eval()))
    print('y={}'.format(y.eval()))
    for epoch in range(n_epochs):
        if epoch % 100 == 0:
            print('Epoch {:4d}: MSE={}'.format(epoch, mse.eval()))
        sess.run(training_op)
    best_theta = theta.eval()
    print('best_theta={}'.format(best_theta))
    print('theta_ne={}'.format(theta_ne.eval()))
    print('mse_thetas={:.12f}'.format(mse_theta.eval()))


