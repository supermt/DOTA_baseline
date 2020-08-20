from collections import defaultdict
import csv
import matplotlib.pyplot as plt
import numpy as np

# Some example data to display
x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)


def plot_another_subfig(ax, data_seg, memtable_size_para, cpu_para, unit="Throughput ops/sec"):
    x = np.arange(3)
    groups = [str(label) + "CPUs" for label in cpu_para]

    data_period_sets = []
    group_size = len(cpu_para)

    cluster_width = len(memtable_size_para)

    width = int(10/(1+cluster_width))/10

    labels = [str(size) + "MB" for size in memtable_size_para]

    align = (cluster_width * width)/2

    for i in range(len(labels)):
        #data_seg[i*group_size: ((i+1)*group_size)]
        data_period = [data_seg[index+i]
                       for index in np.arange(0, len(data_seg), cluster_width)]
        data_period_sets.append(data_period)

    for i, data_period, label in zip(range(len(labels)), data_period_sets, labels):
        ax.bar(x + width * i - align, data_period, width,
               label=label, zorder=3, align='edge')

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel(unit)
    ax.grid(axis='y', linestyle='-', zorder=0)


def plot_one_subfig(ax, data_seg, memtable_size_para, cpu_para, unit="Throughput ops/sec"):
    ax.set_zorder(10)
    x = np.arange(len(memtable_sizes))

    labels = [str(label) + "CPUs" for label in cpu_para]

    data_period_sets = []
    group_size = len(memtable_size_para)
    # group size is how many data in the same color

    width = int(10/len(cpu_para))/10
    groups = [str(size) + "MB" for size in memtable_size_para]

    align = (len(cpu_para) * width)/2

    for i in range(len(labels)):
        data_period_sets.append(data_seg[i*group_size: ((i+1)*group_size)])

    for i, data_period, label in zip(range(len(labels)), data_period_sets, labels):
        ax.bar(x + width*i - align, data_period, width,
               label=label, zorder=3, align='edge')

    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    ax.set_ylabel(unit)
    ax.grid(axis='y', linestyle='-', zorder=0)



column_unit_dict = {
    "Throughput":"ops/sec",
    "Cumulative Compaction Input":"records",
    "Compaction Frequency":"times in one workload",
    "Overall Compaction Cost":"sec",
    "Cumulative CPU Time":"sec",
    "Overall Redundant Records":"records"
}



def plot_one_file(data,column_name):
    materials = ["PM", "PM_NOVA", "NVMeSSD"]
    memtable_sizes = ['16', '32', '64', '128']
    cpu_cores = [2, 4, 8]

    subfig_counts = len(materials)

    segment_length = len(cpu_cores) * len(memtable_sizes)


    fig, axs = plt.subplots(1, subfig_counts, sharex='col', sharey='row',
                            gridspec_kw={'hspace': 0, 'wspace': 0})
    fig.suptitle(column_name, fontsize=16)

    for i in range(subfig_counts):
        data_segment = data[i*segment_length: ((i+1) * segment_length)]
        axs[i].set_title(materials[i], fontsize=10)
        axs[i].spines['top'].set_visible(False)

        if i != 0:
            axs[i].spines['left'].set_color(None)
            # axs[i].set_yticks([])

        plot_another_subfig(axs[i], data_segment, memtable_sizes, cpu_cores,column_name+" ("+column_unit_dict[column_name]+")")

    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels)
    for ax in axs.flat:
        ax.label_outer()
    fig.set_size_inches(23, 5)
    plt.savefig(column_name+".png")


statistics = defaultdict(list)  # each value in each column is appended to a list

with open('result.csv') as f:
    reader = csv.DictReader(f)  # read rows into a dictionary format
    for row in reader:  # read a row as {column1: value1, column2: value2,...}
        for (k, v) in row.items():  # go over each column name and value
            statistics[k].append(v)  # append the value into the appropriate list
            # based on column name k

for column_name in column_unit_dict:
    if column_unit_dict[column_name] == 'sec':
        print(column_name)
        input_data = [float(x) for x in statistics[column_name]]
        plot_one_file(input_data,column_name)
    else:
        print(column_name)
        input_data = [int(x) for x in statistics[column_name]]
        plot_one_file(input_data,column_name)

