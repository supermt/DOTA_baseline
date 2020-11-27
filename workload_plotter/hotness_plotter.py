# What's this for?
# Plot out possible hotness distribution in
# 1. fillrandom workload in db_bench
# 2. mixgraph workload in Rocksdb/db_bench
# 3. zipfian distributed workloada in YCSB
# 4. normal distributed workloada in YCSB

from db_bench_simulator import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sns
# sns.set()

NUM = 500*10000
load_percentage = 0.1  # how many data loaded before we run the queries
random_seed = 0

CURVE_LIST = [0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.9999]


def workload_generator(workload_name, entry_count, FLAGS=None):
    if workload_name == mixgraph:
        keys, prefix_name = workload_name(entry_count, FLAGS)
    else:
        keys, prefix_name = workload_name(entry_count)
    unique_keys, key_counts = np.unique(keys, return_counts=True)
    heatmap_df = pd.DataFrame({'keys': unique_keys, 'count': key_counts})

    return heatmap_df, prefix_name


def paint_the_curve(dataset, ax, label_name, curve_point=CURVE_LIST):
    # print(dataset.shape[0]*curve_point)
    length = dataset.shape[0]
    # x = [ x /  for curve in curve_point]
    # x_percentage = [curve * 1 for curve in curve_point]
    # ax.plot(x_percentage, dataset['count'].values[x], label=label_name)
    ax.plot(dataset['count'].values, label=label_name)


if __name__ == "__main__":
    workloads = [fillrandom, fillrandom_unique]
    sort_by = 'count'
    figure = plt.figure(figsize=(16, 9))
    plt.title("Access Frequency in 5M put() Operations")
    plt.xlabel("Number of Unique Keys")
    plt.ylabel("Access Frequency (times)")
    ax = plt.gca()

    for workload in workloads:
        inserted_keys, workload_name_str = workload_generator(workload, NUM)
        heatsorted_keys = inserted_keys.sort_values(by=sort_by)
        paint_the_curve(heatsorted_keys, ax,
                        label_name="workload: %s" % workload_name_str)

        # plt.scatter(heatsorted_keys['keys'],heatsorted_keys['count'])
        # plt.plot(heatsorted_keys[sort_by].values[CURVE_LIST],
        #          label="workload: %s" % workload_name_str)
    keyrange_num_set = [1, 5, 15, 30, 60]

    # mixgraph workload, with different numbers of the keyrange
    FLAGS = compile_the_argv(sys.argv)
    FLAGS.num = NUM
    # sns.heatmap(keys)
    for keyrange_num in keyrange_num_set:
        FLAGS.keyrange_num = keyrange_num
        inserted_keys, workload_name_str = workload_generator(
            mixgraph, NUM, FLAGS)
        workload_name_str = "%s with %d keyrange unit" % (
            workload_name_str, keyrange_num)
        heatsorted_keys = inserted_keys.sort_values(by=sort_by)
        paint_the_curve(heatsorted_keys, ax,
                        label_name="workload: %s" % workload_name_str)
        # plt.plot(heatsorted_keys[sort_by].values,
        #          label="workload: %s" % workload_name_str)
    plt.legend()
    plt.savefig("wokrload_hotness.pdf")
