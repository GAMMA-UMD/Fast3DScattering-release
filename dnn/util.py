import os
import sys
import numpy as np
import tensorflow as tf

def readObj(fname):
    with open(fname, 'r') as f:
        parsed = [line.split('\n') for line in f.readlines()]
        # filter out empty string
        parsed = [list(filter(None, line)) for line in parsed]
        parsed = [line for line in parsed if line]
        parsed = [line[0] for line in parsed if 'v' in line[0] and '#' not in line[0]]
        parsed = [line.split(' ') for line in parsed]
        parsed = [line[1:] for line in parsed]
        parsed = [[float(ll) for ll in line] for line in parsed]
        return np.array(parsed)

def writeObj(fname, points):
    with open(fname, 'w') as out:
        for p in points:
            out.write('v {} {} {}\n'.format(
                p[0], p[1], p[2]))

   
def read_filelist(fname):
    with open(fname , 'r') as f:
        lines = [line.split('\n') for line in f.readlines()]
        lines = [list(filter(None, line)) for line in lines]
        lines = [line[0] for line in lines]
        return lines


def proto_example(serialized_example, obj_num = 1024, coef_num = 16):
    feature_description = {
            'obj' : tf.io.FixedLenFeature([obj_num * 3], tf.float32),
            'coef125' : tf.io.FixedLenFeature([coef_num], tf.float32),
            'coef250' : tf.io.FixedLenFeature([coef_num], tf.float32),
            'coef500' : tf.io.FixedLenFeature([coef_num], tf.float32),
            'coef1000' : tf.io.FixedLenFeature([coef_num], tf.float32)
            }
    proto_value = tf.io.parse_single_example(
            serialized_example,
            feature_description
            )
    obj = proto_value['obj']
   
    obj = tf.reshape(obj, (obj_num, 3))
    
    coef = {'coef125' : proto_value['coef125'],
            'coef250' : proto_value['coef250'],
            'coef500' : proto_value['coef500'],
            'coef1000' : proto_value['coef1000']
            }

    return obj, coef

def printout(flog, data):
    print(data)
    flog.write(data + '\n')
    flog.flush()

