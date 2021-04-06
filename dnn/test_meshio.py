import tensorflow as tf
from util import proto_example

dataset = tf.data.TFRecordDataset('/home/zhy/Codes/Fast3DScattering/data/test/0')
dataset = dataset.map(proto_example)
print(dataset)

