import numpy as np
import sys
from gflag_loading import *
from mixgraph_simulator import *


class ZipfianGenerator():
    zipfian_constant = 0.99
    items = 0
    base = 0
    zipfian_alpha = 2

    def __init__(self, num, zipfian_alpha=2, base=0):
        self.items = num
        self.base = base
        self.zipfian_alpha = zipfian_alpha

    def FillKeyList(self):
        return np.random.zipf(self.zipfian_alpha,self.items)

    def __str__(self):
        return "Zipfian alpha = %.4f" % self.zipfian_alpha


class UniformLongGenerator():
    def __init__(self):
        pass

    def __str__(self):
        return "Uniform"


class SkewedLatestGenerator():
    def __init__(self):
        pass


class HistogramGenerator():
    def __init__(self):
        pass


class HotspotIntegerGenerator():
    def __init__(self):
        pass


class ScrambledZipfianGenerator():
    def __init__(self):
        pass


class ExponentialGenerator():
    def __init__(self):
        pass

    def __str__(self):
        return "Exponential"


def fillrandom_YCSB(entry_count, distribution=UniformLongGenerator):
    # key_gen = Keygenerator(num=entry_count, mode=fillrandom_unique)
    key_gen = distribution(num=entry_count)
    key_list = key_gen.FillKeyList()
    return key_list, distribution
