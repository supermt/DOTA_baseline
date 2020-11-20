import gflags


def compile_the_argv(argv):
    FLAGS = gflags.FLAGS

    gflags.DEFINE_float('sine_a', 1,
                        "A in f(x) = A sin(bx + c) + d")

    gflags.DEFINE_float('sine_b', 1,
                        "B in f(x) = A sin(bx + c) + d")

    gflags.DEFINE_float('sine_c', 0,
                        "C in f(x) = A sin(bx + c) + d")

    gflags.DEFINE_float('sine_d', 1,
                        "D in f(x) = A sin(bx + c) + d")
    gflags.DEFINE_float('mix_get_ratio', 1.0,
                        "The ratio of Get queries of mix_graph workload")
    gflags.DEFINE_float('mix_put_ratio', 0.0,
                        "The ratio of Put queries of mix_graph workload")
    gflags.DEFINE_float('mix_seek_ratio', 0.0,
                        "The ratio of Seek queries of mix_graph workload")
    gflags.DEFINE_float('sine_mix_rate_noise', 0.0,
                        "Add the noise ratio to the sine rate, it is between 0.0 and 1.0")
    gflags.DEFINE_integer('mix_ave_kv_size', 512,
                      "The average key-value size of this workload")
    
    gflags.FLAGS(argv)

    return FLAGS
