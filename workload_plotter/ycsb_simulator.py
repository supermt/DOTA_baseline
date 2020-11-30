import numpy as np
import sys
from gflag_loading import *
from mixgraph_simulator import *


class ZipfianGenerator():
    # well this implementation is much faster than YCSB generation,
    # but... the calculation process is different
    zipfian_constant = 0.99
    items = 0
    base = 0
    zipfian_alpha = 2

    def __init__(self, num, **kwargs):
        self.items = num
        self.base = kwargs.get("range_min", 0)
        self.zipfian_alpha = kwargs.get("zipfian_alpha", 3)

    @staticmethod
    def zetastatic(st, n, theta, initialsum):
        sum_ = initialsum
        for i in range(st, n):
            sum_ += 1.0 / (pow(i+1, theta))
        return sum_

    def FillKeyList(self):
        return np.random.zipf(self.zipfian_alpha, self.items)

    def __str__(self):
        return "Zipfian alpha = %.6f" % self.zipfian_alpha


class UniformLongGenerator():
    def __init__(self, num, **kwargs):
        self.interval_ = num
        self.lb_ = kwargs.get("lower_bound", 0)
        self.rb_ = kwargs.get("upper_bound", self.lb_+self.interval_)

    def FillKeyList(self):
        random_arr = np.random.rand(self.interval_)
        return ((random_arr*(self.rb_ - self.lb_)).astype("int64")) + self.lb_

    def __str__(self):
        return "Uniform lower_bound at %.2e, upper_bound at %.2e" % (self.lb_, self.rb_)


class SkewedLatestGenerator():
    # well, this is generated from the understanding of YCSB Skewed Latest workload,
    # but... I'm not sure
    def __init__(self, num, **kwargs):
        self.max_ = num
        self.zipfian_alpha = kwargs.get("zipfian_alpha", 1.001)
        # pass

    def FillKeyList(self):
        max_arr = np.full(self.max_, self.max_)
        zipfian_arr = np.random.zipf(self.zipfian_alpha, self.max_)
        return max_arr-zipfian_arr

    def __str__(self):
        return "SkewedLatest, generate by zipfian alpha %.4f" % self.zipfian_alpha


class HotspotIntegerGenerator():
    def __init__(self, num, **kwargs):
        self.lower_bound = kwargs.get("lower_bound", 0)
        self.upper_bound = kwargs.get(
            "upper_bound", self.lower_bound+num)

        hotsetFraction = kwargs.get("hotsetFraction", 0.0)
        hotOpnFraction = kwargs.get("hotOpnFraction", 0.0)
        if hotsetFraction < 0.0 or hotsetFraction > 1.0:
            hotsetFraction = 0.0
        if hotOpnFraction < 0.0 or hotOpnFraction > 1.0:
            hotOpnFraction = 0.0

        assert(self.lower_bound < self.upper_bound)
        self.hotsetFraction = hotsetFraction
        self.interval = self.upper_bound - self.lower_bound + 1
        self.num = num
        self.hotInterval = int(self.interval * hotsetFraction)
        self.coldInterval = self.interval - self.hotInterval
        self.hotOpnFraction = hotOpnFraction
        pass

    def nextValue(self):
        value = 0
        next_double = np.random.rand()
        if next_double < self.hotOpnFraction:
            value = self.lower_bound + abs(np.random.rand()) * self.hotInterval
        else:
            value = self.lower_bound + self.hotInterval + \
                abs(np.random.rand() * self.coldInterval)
        return int(value)

    def FillKeyList(self):
        result = np.zeros(self.num)
        for i in range(self.num):
            result[i] = self.nextValue()
        return result

    def __str__(self):
        return "HotspotInteger, with HotSet Fraction %.2f and bound pair (%d,%d)" % (self.hotsetFraction, self.lower_bound, self.upper_bound)


def fillrandom_YCSB(entry_count, distribution=ZipfianGenerator, **kwargs):
    # key_gen = Keygenerator(num=entry_count, mode=fillrandom_unique)
    np.random.seed(kwargs.get("seed", 0))
    key_gen = distribution(entry_count, **kwargs)
    key_list = key_gen.FillKeyList()
    return key_list, str(key_gen)
