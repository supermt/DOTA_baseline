from ycsb_simulator import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from db_bench_simulator import *
# import seaborn as sns
# sns.set()

NUM = 500*1000
load_percentage = 0.1  # how many data loaded before we run the queries
random_seed = 0

CURVE_LIST = [0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.9999]


def workload_generator(workload_name, entry_count, FLAGS=None, ycsb_distribution=ZipfianGenerator, **kwargs):
    if workload_name == mixgraph:
        keys, prefix_name = workload_name(entry_count, FLAGS)
    elif workload_name == fillrandom_YCSB:
        keys, prefix_name = workload_name(
            entry_count, ycsb_distribution, **kwargs)
    else:
        keys, prefix_name = workload_name(entry_count)
    unique_keys, key_counts = np.unique(keys, return_counts=True)
    heatmap_df = pd.DataFrame({'keys': unique_keys, 'count': key_counts})

    return heatmap_df, prefix_name


def paint_the_curve(dataset, ax, label_name, curve_point=CURVE_LIST, linestyle='-'):
    length = dataset.shape[0]
    ax.plot(dataset['count'].values, label=label_name, linestyle=linestyle)


if __name__ == "__main__":
    # YCSB part only
    workloads = [fillrandom_YCSB]
    linestyles = ['-', '--', '-.', ':']
    distribution_map = {
        ZipfianGenerator: [{"zipfian_alpha": 1.001}, {
            "zipfian_alpha": 1.005}, {"zipfian_alpha": 1.009}],
        UniformLongGenerator: [{"lower_bound": 10, "upper_bound": 10000}, {}, {
            "lower_bound": 100, "upper_bound": 1000}],
        SkewedLatestGenerator: [{"zipfian_alpha": 1.001}, {
            "zipfian_alpha": 1.005}, {"zipfian_alpha": 1.009}],
        HotspotIntegerGenerator: [{"lower_bound": 0, "upper_bound": 1000, "hotsetFraction": 0.3},
                                  {"lower_bound": 0, "upper_bound": 10000,
                                      "hotsetFraction": 0.3},
                                  {"lower_bound": 0, "upper_bound": 1000, "hotsetFraction": 0.7}]
    }

    sort_by = 'count'
    figure = plt.figure(figsize=(16, 9))
    plt.title("Access Frequency in 5M put() Operations")
    plt.xlabel("Number of Unique Keys")
    plt.ylabel("Access Frequency (times)")
    ax = plt.gca()
    line_style_index = 0
    FLAGS = compile_the_argv(sys.argv)
    for workload in workloads:
        for distribution in distribution_map:
            for argument_set in distribution_map[distribution]:
                inserted_keys, workload_name_str = workload_generator(
                    workload, NUM, FLAGS, distribution, **argument_set)
                heatsorted_keys = inserted_keys.sort_values(by=sort_by)
                paint_the_curve(heatsorted_keys, ax,
                                label_name="workload: %s" % workload_name_str, linestyle=linestyles[line_style_index])
            line_style_index += 1

    plt.legend()
    # plt.savefig("wokrload_hotness.pdf")
    plt.show()
