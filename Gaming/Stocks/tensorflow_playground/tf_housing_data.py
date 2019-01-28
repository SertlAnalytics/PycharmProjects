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
from sertl_analytics.constants.pattern_constants import TFOP
from datetime import datetime


class TensorFlowHousingGraph:
    def __init__(self):
        self.X = None
        self.XT = None
        self.y = None
        self.theta = None
        self.theta_ne = None  # node for normal equation solution
        self.prediction = None
        self.error = None
        self.loss = None
        self.loss_theta = None  # node for loss function to compare the thetas
        self.training_optimizer = None
        self.loss_summary = None
        self.file_writer = None


class TensorFlowHousingData:
    def __init__(self, batch_size=None):
        self._batch_size = batch_size
        self._x_data = None
        self._y_data = None
        self._x_records = 0
        self._x_features = 0
        self._batch_number = 0
        self._graph = TensorFlowHousingGraph()
        self.__get_scaled_source_data__()
        self.__construct_graph__()

    @property
    def save_path(self):
        return '../tmp/my_model_final.ckpt'

    def run_graph(self, epochs=1000, learning_rate: float=0.01, optimizer=TFOP.MOMENTUM_OPTIMIZER,
                  save=False, restore=False):
        self.__construct_optimizer_nodes__(learning_rate, optimizer)  # we need the learning rate, and the optimizer
        init = tf.global_variables_initializer()
        saver = tf.train.Saver()
        with tf.Session() as sess:
            if restore:
                saver.restore(sess=sess, save_path=self.save_path)
                print('Restored model from {}..'.format(self.save_path))
            else:
                sess.run(init)
            print('theta_start={}'.format(self._graph.theta.eval()))
            if self._batch_size is None:
                self.__run_whole_data_set__(sess, epochs)
            else:
                self.__run_batches__(sess, epochs)
            best_theta = self._graph.theta.eval()
            print('best_theta={}'.format(best_theta))
            if save:
                saver.save(sess=sess, save_path=self.save_path)

    def __run_batches__(self, sess: tf.Session, epochs: int):
        batch_number = int(np.ceil(self._x_records / self._batch_size))
        for epoch in range(epochs):
            if epoch % 100 == 0:
                print('Epoch {:4d}/{:4d}: theta={}'.format(epoch, epochs, self._graph.theta.eval()))
            for batch_index in range(batch_number):
                X_batch, y_batch = self.__get_batch__(epoch, batch_index)
                self._x_records = X_batch.shape[0]
                sess.run(self._graph.training_optimizer, feed_dict={self._graph.X: X_batch, self._graph.y: y_batch})

    def __run_whole_data_set__(self, sess: tf.Session, epochs: int):
        # print('y={}'.format(self._graph.y.eval()))
        for epoch in range(epochs):
            if epoch % 100 == 0:
                print('Epoch {:4d}/{:4d}: loss={}'.format(epoch, epochs, self._graph.loss.eval()))
                summary_str = self._graph.loss_summary.eval(
                    feed_dict={self._graph.X: self._x_data, self._graph.y: self._y_data})
                step = epoch
                self._graph.file_writer.add_summary(summary_str, step)
            sess.run(self._graph.training_optimizer)
        print('theta_ne={}'.format(self._graph.theta_ne.eval()))
        print('loss_best_theta_vs_theta_ne={:.12f}'.format(self._graph.loss_theta.eval()))
        self._graph.file_writer.close()

    def __get_scaled_source_data__(self):
        scaler = StandardScaler()
        housing = fetch_california_housing()
        scaler.fit(housing.data)
        housing_data = scaler.transform(housing.data)
        self._x_records, self._x_features = housing_data.shape
        self._x_data = np.c_[np.ones((self._x_records, 1)), housing_data]
        self._y_data = housing.target.reshape(-1, 1)

    def __get_batch__(self, epoch: int, batch_index: int):
        start = batch_index * self._batch_size
        end = min(start + self._batch_size - 1, self._x_data.shape[0])
        return self._x_data[start:end], self._y_data[start:end]

    def __construct_data_nodes__(self):
        if self._batch_size is None:
            self._graph.X = tf.constant(self._x_data, dtype=tf.float32, name='X')
            self._graph.y = tf.constant(self._y_data, dtype=tf.float32, name='y')
        else:
            self._graph.X = tf.placeholder(dtype=tf.float32, shape=(None, self._x_features + 1), name='X')
            self._graph.y = tf.placeholder(dtype=tf.float32, shape=(None, 1), name='y')
        self._graph.XT = tf.transpose(self._graph.X)

    def __construct_theta_nodes__(self):
        self._graph.theta_ne = \
            tf.matmul(tf.matmul(tf.matrix_inverse(tf.matmul(self._graph.XT, self._graph.X)),
                                self._graph.XT), self._graph.y)
        self._graph.theta = tf.Variable(tf.random_uniform([self._x_features + 1, 1], -1.0, 1.0), name='theta')

    def __construct_prediction_node__(self):
        self._graph.prediction = tf.matmul(self._graph.X, self._graph.theta, name='prediction')

    def __construct_error_node__(self):
        self._graph.error = self._graph.prediction - self._graph.y

    def __construct_loss_function_nodes__(self):
        self._graph.loss = tf.reduce_mean(tf.square(self._graph.error), name='mse')
        self._graph.loss_theta = tf.reduce_mean(tf.square(self._graph.theta_ne - self._graph.theta), name='mse_theta')

    def __construct_optimizer_nodes__(self, learning_rate: float, optimizer: str):
        if optimizer == TFOP.GRADIENT_DESCENT_MANUAL:
            gradients = 2/self._x_records * tf.matmul(tf.transpose(self._graph.X), self._graph.error)
            self._graph.training_optimizer = tf.assign(self._graph.theta, self._graph.theta - learning_rate * gradients)
        elif optimizer == TFOP.GRADIENT_DESCENT:
            gradients = tf.gradients(self._graph.loss, [self._graph.theta])[0]
            self._graph.training_optimizer = tf.assign(self._graph.theta, self._graph.theta - learning_rate * gradients)
        elif optimizer == TFOP.GRADIENT_DESCENT_OPTIMIZER:
            optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
            self._graph.training_optimizer = optimizer.minimize(self._graph.loss)
        elif optimizer == TFOP.MOMENTUM_OPTIMIZER:
            optimizer = tf.train.MomentumOptimizer(learning_rate=learning_rate, momentum=0.9)  # BEST !!!!
            self._graph.training_optimizer = optimizer.minimize(self._graph.loss)

    def __construct_file_writer__(self):
        now = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        root_log_dir = 'tf_logs'
        log_dir = '{}/run-{}/'.format(root_log_dir, now)
        self._graph.loss_summary = tf.summary.scalar('Loss', self._graph.loss)
        self._graph.file_writer = tf.summary.FileWriter(log_dir, tf.get_default_graph())

    def __construct_graph__(self):
        self.__construct_data_nodes__()
        self.__construct_theta_nodes__()
        self.__construct_prediction_node__()
        self.__construct_error_node__()
        self.__construct_loss_function_nodes__()
        self.__construct_file_writer__()


housing_graph = TensorFlowHousingData(batch_size=None)
housing_graph.run_graph(epochs=1000, optimizer=TFOP.MOMENTUM_OPTIMIZER, restore=False)









