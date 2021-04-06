class Config(object):
    def __init__(self):
        self.decay_rate = 0.9
        self.decay_step = 160000 * 10
        self.learning_rate_clip = 1e-5
        self.bn_init_decay = 0.5
        self.bn_decay_rate = 0.5
        self.bn_decay_step = float(self.decay_step * 2)
        self.bn_decay_clip = 0.99

        self.base_learning_rate = 0.001
        self.momemtum = 0.9

        self.max_to_keep = 200
        import numpy as np
        self.weight = np.ones((1,16)) / 16
        self.weight[0, 0] *= 10
        self.weight[0, 1:4] *= 5
