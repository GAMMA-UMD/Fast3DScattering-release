from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os
import sys
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

### user defined functions
from util import proto_example
import tf_util

class Module(object):
    def __init__(self, config, mode):
        assert mode in {tf.estimator.ModeKeys.TRAIN, 
                tf.estimator.ModeKeys.EVAL,
                tf.estimator.ModeKeys.PREDICT}
        self.mode = mode
        self.config = config
        self.config.weight = config.weight.reshape((1,16))
       
    def get_dataset(self, file_pattern, batch_size, epoch):
        files = tf.matching_files(file_pattern)
        print('Loading files {}\n'.format(files))
        dataset = tf.data.Dataset.from_tensor_slices(files)
        dataset = dataset.shuffle(tf.cast(tf.shape(files)[0], tf.int64))
        #dataset = dataset.repeat(epoch)
        dataset = dataset.interleave(
                tf.data.TFRecordDataset, 
                cycle_length = 8,
                block_length = 16)
        dataset = dataset.shuffle(buffer_size = 16 * 10000)
        parsed = dataset.map(proto_example)
        parsed = parsed.batch(batch_size)
        self.dataset = parsed
        self.handle = tf.placeholder(tf.string, shape = [])
        iterator = tf.data.Iterator.from_string_handle(
                self.handle,
                self.dataset.output_types,
                self.dataset.output_shapes
                )
        self.next_element = iterator.get_next()
        self.training_iter = self.dataset.make_initializable_iterator()

    def get_valid_dataset(self, file_pattern, batch_size, epoch):
        files = tf.matching_files(file_pattern)
        print("Loading Validation files : {}\n".format(files))
        dataset = tf.data.Dataset.from_tensor_slices(files)
        dataset = dataset.shuffle(tf.cast(tf.shape(files)[0], tf.int64))
        dataset = dataset.interleave(
                tf.data.TFRecordDataset,
                cycle_length = 1,
                block_length = 1
                )
        dataset = dataset.shuffle(buffer_size = 64 * 1000)
        parsed = dataset.map(proto_example)
        parsed = parsed.batch(batch_size)
        self.valid_dataset = parsed
        self.valid_handle = tf.placeholder(tf.string, shape = [])
        valid_iterator = tf.data.Iterator.from_string_handle(
                self.valid_handle,
                self.valid_dataset.output_types,
                self.valid_dataset.output_shapes
                )
        self.valid_next_element = valid_iterator.get_next()
        self.valid_iter = self.valid_dataset.make_initializable_iterator()


    def get_model(self, point_cloud, coef, is_training,  batch_size, bn_decay = None, num_point = 1024, k = 5, bn = False):
        assert point_cloud.get_shape()[0].value == batch_size
        assert coef.get_shape()[0].value == batch_size
        batch_size = point_cloud.get_shape()[0].value
        num_point = point_cloud.get_shape()[1].value
        self.config.weight = tf.convert_to_tensor(self.config.weight, dtype = tf.float32)

        input_image = tf.expand_dims(point_cloud, -1)
        # CONV
        net = tf_util.conv2d(input_image, 64, [1,3], padding='VALID', stride=[1,1],
                             bn=True, is_training=is_training, scope='conv1', bn_decay=bn_decay)
        net = tf_util.conv2d(net, 64, [1,1], padding='VALID', stride=[1,1],
                             bn=True, is_training=is_training, scope='conv2', bn_decay=bn_decay)
        net = tf_util.conv2d(net, 64, [1,1], padding='VALID', stride=[1,1],
                             bn=True, is_training=is_training, scope='conv3', bn_decay=bn_decay)
        net = tf_util.conv2d(net, 128, [1,1], padding='VALID', stride=[1,1],
                             bn=True, is_training=is_training, scope='conv4', bn_decay=bn_decay)
        points_feat1 = tf_util.conv2d(net, 1024, [1,1], padding='VALID', stride=[1,1],
                             bn=True, is_training=is_training, scope='conv5', bn_decay=bn_decay)
        # MAX
        pc_feat1 = tf_util.max_pool2d(points_feat1, [num_point,1], padding='VALID', scope='maxpool1')
        # FC
        pc_feat1 = tf.reshape(pc_feat1, [batch_size, -1])
        pc_feat1,_ = tf_util.fully_connected(pc_feat1, 256, bn=bn, is_training=is_training, scope='fc1', bn_decay=bn_decay)
        pc_feat1,_ = tf_util.fully_connected(pc_feat1, 128, bn=bn, is_training=is_training, scope='fc2', bn_decay=bn_decay, activation_fn = tf.math.tanh)
        pc_feat1,self.l2_weights = tf_util.fully_connected(pc_feat1, 16, bn = bn, is_training = is_training, scope = 'fc3', bn_decay = bn_decay, activation_fn = tf.math.tanh)
        print(pc_feat1.get_shape())
       
        return pc_feat1


    def get_loss(self, predict, target):
        #loss = tf.math.abs(predict - target)
        loss = tf.multiply(predict - target, predict - target)
        #print(loss.get_shape())
        loss_sum = tf.reduce_sum(loss, axis = 1)
        loss_cat = tf.reduce_sum(loss, axis = 0)
        print(loss_cat.get_shape())
        loss_total = tf.reduce_mean(loss_sum) + tf.reduce_sum(self.l2_weights * self.l2_weights)*0.1 
        
        return loss_total, loss_cat
        


    
