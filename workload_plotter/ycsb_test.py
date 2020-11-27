from ycsb_simulator import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sns
# sns.set()

NUM = 500*1000
load_percentage = 0.1  # how many data loaded before we run the queries
random_seed = 0

CURVE_LIST = [0.05, 0.1, 0.15, 0.2, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99, 0.9999]


def workload_generator(workload_name, entry_count, FLAGS=None, ycsb_distribution=UniformLongGenerator):
    if workload_name == mixgraph:
        keys, prefix_name = workload_name(entry_count, FLAGS)
    elif workload_name == fillrandom_YCSB:
        keys, prefix_name = workload_name(entry_count, ycsb_distribution)
    else:
        keys, prefix_name = workload_name(entry_count)
    unique_keys, key_counts = np.unique(keys, return_counts=True)
    heatmap_df = pd.DataFrame({'keys': unique_keys, 'count': key_counts})

    return heatmap_df, prefix_name


def paint_the_curve(dataset, ax, label_name, curve_point=CURVE_LIST):
    length = dataset.shape[0]
    ax.plot(dataset['count'].values, label=label_name)


if __name__ == "__main__":
    workloads = [fillrandom_YCSB]
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

    plt.legend()
    # plt.savefig("wokrload_hotness.pdf")
    plt.show()
