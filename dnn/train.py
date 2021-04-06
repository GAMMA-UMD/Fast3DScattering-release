from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import os
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
import sys
import argparse
import numpy as np
import tensorflow as tf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from module import Module
from moduleConfig import Config
from util import printout


def placeholder_inputs(batch_size, point_num, coef_num):
    obj_ph = tf.placeholder(tf.float32, shape = (batch_size, point_num, 3))
    coef_ph = tf.placeholder(tf.float32, shape = (batch_size, coef_num))
    return obj_ph, coef_ph


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
            formatter_class = argparse.RawTextHelpFormatter,
            description = "Spherical harmonics"
            )
    arg_parser.add_argument(
            "--file_pattern",
            dest = "file_pattern",
            required = True,
            help = "tfrecord file pattern"
            )
    arg_parser.add_argument(
            "--valid_file_pattern",
            dest = "valid_file_pattern",
            required = True,
            help = "tfrecord file pattern for validation"
            )
    arg_parser.add_argument(
            "--ckpt_dir",
            dest = "ckpt_dir",
            required = True,
            help = "checkpoint dir"
            )
    arg_parser.add_argument(
            "--point_num",
            dest = "point_num",
            default = 1024,
            help = "point number"
            )
    arg_parser.add_argument(
            "--coef_num",
            dest = "coef_num",
            default = 16,
            help = "number of spherical harmonics coefs"
            )
    arg_parser.add_argument(
            "--freq",
            dest = "freq",
            help = "coef freq",
            required = True
            )
    arg_parser.add_argument(
            "--batch_size",
            "-b",
            dest = "batch_size",
            default = 64,
            help = "batch size"
            )
    arg_parser.add_argument(
            "--epoch",
            "-e",
            dest = "epoch",
            default = 1000,
            help = "number of epochs"
            )
    arg_parser.add_argument(
            "--learning_rate",
            "-lr",
            dest = "learning_rate",
            default = 0.001,
            help = "base learning rate"
            )
    arg_parser.add_argument(
            "--optimizer",
            dest = "optimizer",
            default = "adam",
            help = "momemtum / adam"
            )

    args = arg_parser.parse_args()
    args.epoch = int(args.epoch)
    args.batch_size = int(args.batch_size)
    args.point_num = int(args.point_num)
    args.coef_num = int(args.coef_num)
    args.learning_rate = float(args.learning_rate)

    if not tf.test.is_gpu_available():
        print("gpu unavailable")
        exit(1)

    if not os.path.isdir(args.ckpt_dir):
        os.makedirs(args.ckpt_dir)
        print('\tmkdir {}\n'.format(args.ckpt_dir))
    
    os.system('cp train.py %s/' % os.path.abspath(args.ckpt_dir ))
    os.system('cp module.py %s/' % os.path.abspath(args.ckpt_dir))
    os.system('cp moduleConfig.py %s/' % os.path.abspath(args.ckpt_dir))

    flog = open(os.path.join(args.ckpt_dir, 'log.txt'), 'w')
  
    module_config = Config()
    module = Module(
            module_config,
            tf.estimator.ModeKeys.TRAIN)
    print(args.file_pattern)
    
    with tf.Graph().as_default():

        module.get_dataset(
                args.file_pattern,
                args.batch_size,
                args.epoch
                )
        module.get_valid_dataset(
                args.valid_file_pattern,
                args.batch_size,
                args.epoch
                )
        obj_ph, coef_ph = placeholder_inputs(
                args.batch_size, 
                args.point_num, 
                args.coef_num
                )
        is_training_ph = tf.placeholder(tf.bool, shape = ())
        batch = tf.Variable(0, trainable = False)
        get_learning_rate = lambda _batch : \
            tf.maximum(
                   tf.train.exponential_decay(
                       args.learning_rate,
                       _batch * args.batch_size,
                       module_config.decay_step,
                       module_config.decay_rate,
                       staircase = True),
                   module_config.learning_rate_clip
                   )

        learning_rate = get_learning_rate(batch)
        get_bn_decay = lambda _batch : \
            tf.minimum(
                    module_config.bn_decay_clip,
                    1 - tf.train.exponential_decay(
                        module_config.bn_init_decay,
                        _batch * args.batch_size,
                        module_config.bn_decay_step,
                        module_config.bn_decay_rate,
                        staircase = True
                        )
                    )
        bn_decay = get_bn_decay(batch)
        lr_op = tf.summary.scalar('learning_rate', learning_rate)
        batch_op = tf.summary.scalar('batch_number', batch)
        bn_decay_op = tf.summary.scalar('bn_decay', bn_decay)

        predict  = module.get_model(
                obj_ph,
                coef_ph,
                is_training_ph,
                args.batch_size,
                bn_decay = bn_decay,
                bn = True
                )
        loss, loss_cat = module.get_loss(predict, coef_ph)
        print(loss_cat.get_shape())
        
        tf.summary.scalar('loss', loss)
        tf.summary.scalar('log loss', tf.math.log(loss))
        for idx in range(args.coef_num):
            tf.summary.scalar('coef_%d' % idx, loss_cat[idx])

        if args.optimizer == "momemtum":
            optimizer = tf.train.MomemtumOptimizer(
                    learning_rate,
                    momemtum = MOMEMTUM
                    )
        elif args.optimizer == "adam":
            optimizer = tf.train.AdamOptimizer(learning_rate)

        train_op = optimizer.minimize(loss, global_step = batch)

        saver = tf.train.Saver(max_to_keep = module_config.max_to_keep)
        ## Session
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        config.allow_soft_placement = True

        ## Summary
        merged = tf.summary.merge_all()

        with tf.Session(config = config) as sess:
            train_writer = tf.summary.FileWriter(
                os.path.join(args.ckpt_dir, 'train'),
                sess.graph
                )
            valid_writer = tf.summary.FileWriter(
                    os.path.join(args.ckpt_dir, 'valid'),
                    sess.graph
                    )
            sess.run(tf.global_variables_initializer(), {is_training_ph : True})

            training_handle = sess.run(module.training_iter.string_handle())
            valid_handle = sess.run(module.valid_iter.string_handle())

            ops = {
                'obj_ph' : obj_ph,
                'coef_ph' : coef_ph,
                'predict' : predict,
                'loss' : loss,
                'is_training_ph' : is_training_ph,
                'train_op' : train_op,
                'merged' : merged,
                'step' : batch
                }


            best_val_error = 1e5
            for e in range(args.epoch):
                is_training = True
                sess.run(module.training_iter.initializer)
                sess.run(module.valid_iter.initializer)
                printout(flog, "\t-----EPOCH %d-----\n" % e)
                sys.stdout.flush()
                
                ### train one epoch
                loss_sum = 0
                sample_cnt = 0
               
                while True:
                    try:
                        obj, coef = sess.run(
                                module.next_element,
                                feed_dict = {
                                    module.handle : training_handle}
                                )
                        if obj.shape[0] !=  args.batch_size:
                            printout(flog, "skip this batch")
                            break
                        sample_cnt += obj.shape[0]
                        feed_dict = {
                            ops['obj_ph'] : obj,
                            ops['coef_ph'] : coef[args.freq],
                            ops['is_training_ph'] : is_training
                            }
                        summary, step, _, loss_val, predict_val = sess.run(
                            [
                                ops['merged'],
                                ops['step'],
                                ops['train_op'],
                                ops['loss'],
                                ops['predict']
                                ],
                            feed_dict = feed_dict)
                        train_writer.add_summary(summary, step)
                        loss_sum += loss_val
                        # if sample_cnt % 10 == 0:
                        #     printout(flog, 'Current batch : %d' % (sample_cnt ))
                        #     printout(flog, 'Current loss : %f' % (float(loss_sum) / sample_cnt))

                    except tf.errors.OutOfRangeError:
                        ### finish this epoch
                        pass

                epoch_loss = float(loss_sum) / sample_cnt
                summary = tf.Summary(value=[
                    tf.Summary.Value(tag="epoch_loss", simple_value=epoch_loss),
                ])
                train_writer.add_summary(summary, e)
                printout(flog, 'mean loss : %f' % epoch_loss)


                if e % 10  == 0:
                    save_path = saver.save(sess, os.path.join(args.ckpt_dir, 'model_%d.ckpt' % e))
                    printout(flog, 'Model saved in file : %s' % save_path)

                # validation
                is_training = False
                sess.run(module.valid_iter.initializer)
                valid_loss_sum = 0
                valid_sample_cnt = 0
                while True:
                    try:
                        obj, coef = sess.run(
                            module.valid_next_element,
                            feed_dict = {
                                module.valid_handle : valid_handle}
                            )
                        if obj.shape[0] !=  args.batch_size:
                            printout(flog, "skip this batch")
                            break
                        valid_sample_cnt += obj.shape[0]
                        feed_dict = {
                            ops['obj_ph'] : obj,
                            ops['coef_ph'] : coef[args.freq],
                            ops['is_training_ph'] : is_training
                            }
                        summary, step,  loss_val, predict_val = sess.run(
                            [
                                ops['merged'],
                                ops['step'],
                                ops['loss'],
                                ops['predict']
                                ],
                            feed_dict = feed_dict)
                        valid_writer.add_summary(summary, step)
                        valid_loss_sum += loss_val
                        # printout(flog, 'Valid/Current batch : %d' % (valid_sample_cnt))
                        # printout(flog, 'Valid/Current loss : %f' % (float(valid_loss_sum) / valid_sample_cnt))


                    except tf.errors.OutOfRangeError:
                        break

                epoch_loss = float(valid_loss_sum) / valid_sample_cnt
                if epoch_loss < best_val_error:
                    best_val_error = epoch_loss
                    save_path = saver.save(sess, os.path.join(args.ckpt_dir, 'model_best.ckpt'))
                    printout(flog, 'Found new best model on epoch {}'.format(e))

                summary = tf.Summary(value=[
                    tf.Summary.Value(tag="epoch_loss", simple_value=epoch_loss),
                ])
                valid_writer.add_summary(summary, e)
                printout(flog, '\tValid/mean loss %f\n' % (float(valid_loss_sum) / valid_sample_cnt))




    

