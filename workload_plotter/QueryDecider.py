import math


class query_dispatcher():
    def __init__(self, ratio_input):
        ratio_sum = 0.0
        range_max = 1000
        for ratio in ratio_input:
            ratio_sum += ratio

        self.range_ = 0
        self.type_ = []
        self.ratio_ = []

        # ratio_input = [get_ratio, put_ratio, seek_ratio]

        for ratio in ratio_input:
            self.range_ += int(math.ceil(range_max * (ratio/ratio_sum)))
            self.type_.append(self.range_)
            self.ratio_.append(ratio/ratio_sum)
        pass

    def getType(self, random_num):
        if (random_num < 0):
            random_num = random_num * (-1)
        assert(self.range_ != 0)
        pos = int(random_num % self.range_)
        for i in range(len(self.type_)):
            if pos < self.type_[i]:
                return i
        return 0
