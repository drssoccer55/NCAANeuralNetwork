import tensorflow as tf

IN_SHAPE = 78
OUT_SHAPE = 1
LAYER_SIZE = 52

def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

x = tf.placeholder(tf.float32, shape=[None, IN_SHAPE])
y_ = tf.placeholder(tf.float32, shape=[None, OUT_SHAPE])

x_input = x

#FCL 1
W_fc1 = weight_variable([IN_SHAPE, LAYER_SIZE])
b_fc1 = bias_variable([LAYER_SIZE])

h_fc1 = tf.nn.relu(tf.matmul(x_input, W_fc1) + b_fc1)

keep_prob = tf.placeholder(tf.float32)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

#FCL 2
W_fc2 = weight_variable([LAYER_SIZE, OUT_SHAPE])
b_fc2 = bias_variable([OUT_SHAPE])

y = tf.matmul(h_fc1_drop, W_fc2) + b_fc2