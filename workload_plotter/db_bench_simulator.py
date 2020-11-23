import numpy as np
import sys
from gflag_loading import *
from mixgraph_simulator import *


def normal_distributed():
    pass


def fillrandom(entry_count, distribution=normal_distributed):
    key_gen = Keygenerator(num=entry_count)
    key_list = key_gen.FillKeyList()
    return key_list, "fillrandom"


def fillrandom_unique(entry_count, distribution=None):
    key_gen = Keygenerator(num=entry_count, mode=fillrandom_unique)
    key_list = key_gen.FillKeyList()
    return key_list, "fillrandom_unique"


class Keygenerator():
    values_ = np.zeros(100)
    num_ = 500*1000
    random_seed = 0

    def __init__(self, rand_gen=None, mode=fillrandom, num=500*1000, next=0):
        self.rand = rand_gen
        self.num_ = num
        np.random.seed(self.random_seed)
        if self.rand == None:
            # use default random.random() to generate the next value
            self.rand = np.random
        self.mode_ = mode
        if self.mode_ == fillrandom_unique:
            self.values_ = np.arange(self.num_)
            np.random.shuffle(self.values_)
        self.next_ = next

    def Next(self):
        if self.mode_ == fillrandom:
            return int(self.rand.rand() * self.num_)
        if self.mode_ == fillrandom_unique:
            assert(self.next_ < self.num_)
            self.next_ += 1
            return self.values_[self.next_-1]

    def FillKeyList(self):
        if self.mode_ == fillrandom_unique:
            # if the model is fillrandom_unique, the keys has already been generated
            return self.values_
        else:
            return self.rand.randint(self.num_, size=self.num_)


def generateKeyFromInt(key_size_, v, num_keys, FLAGS=None):
    pos = bytearray()
    temp = bytearray()
    keys_per_prefix = FLAGS.keys_per_prefix
    prefix_size_ = FLAGS.prefix_size
    # python's int.to_bytes() function will transform a integer into big endian, so don't need to check the endian
    if keys_per_prefix > 0:
        #   ----------------------------
        #   | prefix 00000 | key 00000 |
        #   ----------------------------
        num_prefix = num_keys / keys_per_prefix
        prefix = int(v % num_prefix)
        print(prefix)
        bytes_to_fill = min(prefix_size_, 8)
        pos.extend(prefix.to_bytes(bytes_to_fill, "big"))
        if prefix_size_ > 8:
            pos.extend(temp.center(prefix_size_ - 8, b'0'))
        #   ----------------------------
        #   |        key 00000         |
        #   ----------------------------
    bytes_to_fill = min(key_size_ - len(pos), 8)
    # don't know why, but it works fine... in some cases, even I can't transform it in hex calculator
    # target_array = v.to_bytes(bytes_to_fill,"big")
    # print("integer value %d"%v,target_array)
    # print("change back from it ", int.from_bytes(target_array,"big"))

    pos.extend(v.to_bytes(bytes_to_fill, "big"))
    if key_size_ > len(pos):
        pos.extend(temp.center(key_size_-len(pos), b'0'))

    hex_str = ''.join('{:02x}'.format(x) for x in pos)

    # return pos  # Should we decode or not?
    return hex_str

# this will be very very long


def GetRandomKey(rand_generator):
    return rand_generator.Next()


def mixgraph(entry_count, FLAGS, integer_value_only=True):
    key_list = []
    gen_exp = GenerateTwoTermExpKeys(FLAGS)
    rand_generator = Keygenerator(num=entry_count)
    FLAGS.num = entry_count
    # use_random_modeling = False
    # use_prefix_modeling = False

    if (FLAGS.keyrange_dist_a != 0.0 or FLAGS.keyrange_dist_b != 0.0 or
            FLAGS.keyrange_dist_c != 0.0 or FLAGS.keyrange_dist_d != 0.0):
        use_prefix_modeling = True
        gen_exp.InitiateExpDistribution(FLAGS.num, FLAGS.keyrange_dist_a, FLAGS.keyrange_dist_b,
                                        FLAGS.keyrange_dist_c, FLAGS.keyrange_dist_d)
    if FLAGS.key_dist_a == 0 or FLAGS.key_dist_b == 0:
        use_random_modeling = True

    # according to the paper in FAST 2020, it uses the prefix_modeling model
    # to simplify the problem, we use it too

    for i in range(entry_count):
        ini_rand = GetRandomKey(rand_generator)
        key_int = gen_exp.DistGetKeyID(
            ini_rand, FLAGS.key_dist_a, FLAGS.key_dist_b)

        if integer_value_only:
            key = key_int
        else:
            key = generateKeyFromInt(FLAGS.key_size, key_int, FLAGS.num, FLAGS)

        key_list.append(key)

    # return key_list, "mixgraph%d" % FLAGS.keyrange_num
    return key_list, "mixgraph"

