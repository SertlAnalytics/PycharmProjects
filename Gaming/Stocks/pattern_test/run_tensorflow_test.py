import tensorflow as tf

var = tf.Variable(10)
a = tf.constant(4)


i = tf.constant(4)
new_var = tf.add(var, i)
update = tf.assign(var, new_var)

init_var = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init_var)
    print("Initial var :\n",sess.run(var))
    print("Initial new_var :\n", sess.run(new_var))
    print("Printing after updating var in each iteration : ")
    for _ in range(5):
        sess.run(update)
        print(sess.run(var))