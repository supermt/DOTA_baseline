from gflag_loading import *
from math import exp
from math import floor
from math import ceil
import numpy as np


class KeyrangeUnit():
    keyrange_start = 0
    keyrange_access = 0
    keyrange_keys = 0

    def __init__(self):
        pass


class GenerateTwoTermExpKeys():
    keyrange_rand_max_ = 0
    keyrange_size_ = 0
    keyrange_num_ = 0
    initiated_ = False
    keyrange_set_ = []  # keyrangeUnit vector
    FLAGS_ = None

    def __init__(self, FLAGS):
        self.keyrange_rand_max_ = FLAGS.num
        self.initiated_ = False
        self.FLAGS_ = FLAGS
        pass

    def InitiateExpDistribution(self, total_keys, prefix_a, prefix_b, prefix_c, prefix_d):
        amplify = 0
        keyrange_start = 0
        self.initiated_ = True
        if self.FLAGS_.keyrange_num <= 0:
            self.keyrange_num = 1
        else:
            self.keyrange_num_ = self.FLAGS_.keyrange_num

        self.keyrange_size_ = int(total_keys/self.keyrange_num_)

        # calculate the keyrange shares size based on the input
        for pfx in range(self.keyrange_num_, 0, -1):
            # step 1
            keyrange_p = float(prefix_a * exp(prefix_b * pfx) +
                               prefix_c * exp(prefix_d*pfx))
            if keyrange_p < pow(10.0, -16.0):
                keyrange_p = 0.0
            # step 2
            if amplify == 0 and keyrange_p > 0:
                amplify = int(floor(1/keyrange_p)) + 1
            # step 3
            p_unit = KeyrangeUnit()
            p_unit.keyrange_start = keyrange_start
            if 0.0 >= keyrange_p:
                p_unit.keyrange_access = 0
            else:
                p_unit.keyrange_access = int(floor(amplify*keyrange_p))

            p_unit.keyrange_keys = self.keyrange_size_
            self.keyrange_set_.append(p_unit)
            keyrange_start += p_unit.keyrange_access
        self.keyrange_rand_max_ = keyrange_start

        # step 4
        np.random.shuffle(self.keyrange_set_)

        # step 5
        offset = 0
        for p_unit in self.keyrange_set_:
            p_unit.keyrange_start = offset
            offset += p_unit.keyrange_access

    def DistGetKeyID(self, ini_rand, key_dist_a, key_dist_b):
        keyrange_rand = int(ini_rand % self.keyrange_rand_max_)

        start = 0
        end = int(len(self.keyrange_set_))

        while start + 1 < end:
            mid = start + int((end-start)/2)
            assert(mid >= 0 and mid < int(len(self.keyrange_set_)))
            if keyrange_rand < self.keyrange_set_[mid].keyrange_start:
                end = mid
            else:
                start = mid

        keyrange_id = start

        key_offset = 0
        key_seed = 0
        if key_dist_a == 0 or key_dist_b == 0:
            key_offset = int(ini_rand % self.keyrange_size_)
        else:
            u = float(ini_rand % self.keyrange_size_) / self.keyrange_size_
            key_seed = ceil(pow(u/key_dist_a), (1/key_dist_b))
            np.random.seed(key_seed)
            key_offset = np.random.rand()*self.keyrange_size_
        return self.keyrange_size_ * keyrange_id + key_offset
