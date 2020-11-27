import gflags


def compile_the_argv(argv):
    FLAGS = gflags.FLAGS

    gflags.DEFINE_float("keyrange_dist_a", 0.0,
                        "The parameter 'a' of prefix average access distribution "
                        "f(x)=a*exp(b*x)+c*exp(d*x)")
    gflags.DEFINE_float("keyrange_dist_b", 0.0,
                        "The parameter 'b' of prefix average access distribution "
                        "f(x)=a*exp(b*x)+c*exp(d*x)")
    gflags.DEFINE_float("keyrange_dist_c", 0.0,
                        "The parameter 'c' of prefix average access distribution"
                        "f(x)=a*exp(b*x)+c*exp(d*x)")
    gflags.DEFINE_float("keyrange_dist_d", 0.0,
                        "The parameter 'd' of prefix average access distribution"
                        "f(x)=a*exp(b*x)+c*exp(d*x)")
    gflags.DEFINE_integer("keyrange_num", 1,
                          "The number of key ranges that are in the same prefix "
                          "group, each prefix range will have its key access "
                          "distribution")
    gflags.DEFINE_float("key_dist_a", 0.0,
                        "The parameter 'a' of key access distribution model "
                        "f(x)=a*x^b")
    gflags.DEFINE_float("key_dist_b", 0.0,
                        "The parameter 'b' of key access distribution model "
                        "f(x)=a*x^b")
    gflags.DEFINE_float("value_theta", 0.0,
                        "The parameter 'theta' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("value_k", 0.0,
                        "The parameter 'k' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("value_sigma", 0.0,
                        "The parameter 'theta' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("iter_theta", 0.0,
                        "The parameter 'theta' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("iter_k", 0.0,
                        "The parameter 'k' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("iter_sigma", 0.0,
                        "The parameter 'sigma' of Generized Pareto Distribution "
                        "f(x)=(1/sigma)*(1+k*(x-theta)/sigma)^-(1/k+1)")
    gflags.DEFINE_float("mix_get_ratio", 1.0,
                        "The ratio of Get queries of mix_graph workload")
    gflags.DEFINE_float("mix_put_ratio", 0.0,
                        "The ratio of Put queries of mix_graph workload")
    gflags.DEFINE_float("mix_seek_ratio", 0.0,
                        "The ratio of Seek queries of mix_graph workload")
    gflags.DEFINE_integer("mix_max_scan_len", 10000,
                          "The max scan length of Iterator")
    gflags.DEFINE_integer("mix_ave_kv_size", 512,
                          "The average key-value size of this workload")
    gflags.DEFINE_integer("mix_max_value_size", 1024,
                          "The max value size of this workload")
    gflags.DEFINE_float("sine_mix_rate_noise", 0.0,
                        "Add the noise ratio to the sine rate, it is between 0.0 and 1.0")
    gflags.DEFINE_bool("sine_mix_rate", False,
                       "Enable the sine QPS control on the mix workload")
    gflags.DEFINE_integer("sine_mix_rate_interval_milliseconds", 10000,
                          "Interval of which the sine wave read_rate_limit is recalculated")
    gflags.DEFINE_integer("mix_accesses", -1,
                          "The total query accesses of mix_graph workload")

    gflags.DEFINE_integer(
        "num", 1000000, "Number of key/values to place in database")
    gflags.DEFINE_integer("key_size",16,"size of each key")
    gflags.DEFINE_integer("keys_per_prefix",0,"")
    gflags.DEFINE_integer("prefix_size", 0, "control the prefix size for HashSkipList and "
             "plain table");

    # gflags.DEFINE_float('sine_a', 1,
    #                     "A in f(x) = A sin(bx + c) + d")

    # gflags.DEFINE_float('sine_b', 1,
    #                     "B in f(x) = A sin(bx + c) + d")

    # gflags.DEFINE_float('sine_c', 0,
    #                     "C in f(x) = A sin(bx + c) + d")

    # gflags.DEFINE_float('sine_d', 1,
    #                     "D in f(x) = A sin(bx + c) + d")
    # gflags.DEFINE_float('mix_get_ratio', 1.0,
    #                     "The ratio of Get queries of mix_graph workload")
    # gflags.DEFINE_float('mix_put_ratio'", 0.0,
    #                     "The ratio of Put queries of mix_graph workload")
    # gflags.DEFINE_float('mix_seek_ratio'", 0.0,
    #                     "The ratio of Seek queries of mix_graph workload")
    # gflags.DEFINE_float('sine_mix_rate_noise'", 0.0,
    #                     "Add the noise ratio to the sine rate, it is between 0.0 and 1.0")
    # gflags.DEFINE_integer('mix_ave_kv_size', 512,
    #                   "The average key-value size of this workload")

    gflags.FLAGS(argv)

    return FLAGS
