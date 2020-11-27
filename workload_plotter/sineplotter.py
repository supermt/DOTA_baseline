import numpy as np

import matplotlib.pyplot as plot
import random
import sys
from gflag_loading import compile_the_argv

random.seed(0)


def AddNoise(origin, noise_ratio, sine_a):
    if noise_ratio < 0.0 or noise_ratio > 1.0:
        return origin
    band_int = int(sine_a)
    delta = (random.random() % band_int - band_int / 2) * noise_ratio
    if origin + delta < 0:
        return origin
    else:
        return origin + delta


def SineRate(x, sine_a, sine_b, sine_c, sine_d):
    return sine_a*np.sin((sine_b*x) + sine_c) + sine_d


def sine_plot(FLAGS):
    sine_a = FLAGS.sine_a
    sine_b = FLAGS.sine_b
    sine_c = FLAGS.sine_c
    sine_d = FLAGS.sine_d

    time = np.arange(0, 14 * 24 * 3600, 1)

    read_rate_curve = []
    write_rate_curve = []

    for second in time:
        mix_rate_with_noise = AddNoise(SineRate(
            second, sine_a, sine_b, sine_c, sine_d), FLAGS.sine_mix_rate_noise, sine_a)
        read_rate = mix_rate_with_noise * (query.ratio_[0] + query.ratio_[2])
        write_rate = mix_rate_with_noise * \
            query.ratio_[1]
        # * FLAGS.mix_ave_kv_size
        read_rate_curve.append(read_rate)
        write_rate_curve.append(write_rate)
    # print(read_rate_curve)
    # print(write_rate_curve)
    fig, ax = plot.subplots(figsize=(16, 9))
    ax.plot(time,read_rate_curve, 'C1', label="Read rate (Query per seconds)")
    ax.plot(time,write_rate_curve, 'C2', label="Write rate (Query per seconds)")
    
    sine_para_str = "\n Sine parameters %.2e %.2e %.2e %.2e" % (
        sine_a, sine_b, sine_c, sine_d)
    ax.set_title('Simulated QPS according to %s' % (sine_para_str))

    # Give x axis label for the sine wave plot

    ax.set_xlabel('Time')

    # Give y axis label for the sine wave plot

    ax.set_ylabel('Incoming QPS = %.2e sin(%.2ex + %.2e) + %.2e' %
                (sine_a, sine_b, sine_c, sine_d))
    
    ax.legend()
    # ax.grid(True, which='both')

    fig.savefig("sine_plot_%.2e_%.2e_%.2e_%.2e.png" %
                 (sine_a, sine_b, sine_c, sine_d))

if __name__ == "__main__":
    FLAGS = compile_the_argv(sys.argv)
    
    ratio = [FLAGS.mix_get_ratio, FLAGS.mix_put_ratio, FLAGS.mix_seek_ratio]

    from QueryDecider import query_dispatcher
    query = query_dispatcher(ratio)
    sine_plot(FLAGS)
