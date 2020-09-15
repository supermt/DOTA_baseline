import matplotlib.pyplot as plt
import datetime
import time
import csv
import pandas as pd
import json
import re
from traversal import get_log_dirs
from traversal import get_log_and_std_files

percentage_list = [0, 0.05, 0.1, 0.15, 0.25, 0.5, 0.75, 0.95, 0.99, 0.9999]


COMPACTION_LOG_HEAD = "/compaction/compaction_job.cc:755"
FLUSH_LOG_BEGIN = "flush_started"
FLUSH_LOG_END = "flush_finished"
FLUSH_FILE_CREATEION = "table_file_creation"


def readlines_from_log_file(log_file_name):
    # log_file_name = "../StorageMaterial.NVMeSSD/12CPU/64MB/LOG_1180"
    log_lines = open(log_file_name, "r").readlines()
    return log_lines


def get_flush_tuplers(log_lines):
    flush_start_lines = [x for x in log_lines if FLUSH_LOG_BEGIN in x]
    flush_end_lines = [x for x in log_lines if FLUSH_LOG_END in x]

    flush_start_row_list = []
    flush_end_row_list = []
    flush_job_id_list = []

    for line in flush_start_lines:
        line = re.search('(\{.+\})', line)
        if line:
            log_row = json.loads(line[0])
            flush_start_row_list.append(log_row)
            flush_job_id_list.append(log_row["job"])

    for line in flush_end_lines:
        line = re.search('(\{.+\})', line)
        if line:
            log_row = json.loads(line[0])
            flush_end_row_list.append(log_row)

    df1 = pd.DataFrame(flush_start_row_list)
    df2 = pd.DataFrame(flush_end_row_list)
    df1 = df1.sort_values('job')
    df2 = df2.sort_values('job')

    flush_speed = pd.DataFrame(columns=["job_id", "flush_size", "flush_speed"])
    for index, row in df1.iterrows():
        flush_speed.loc[index] = [row['job'], row["total_data_size"],
                                  row["total_data_size"] /
                                  (df2['time_micros']
                                   [index] - row['time_micros'])]

    flush_size_list = list(flush_speed["flush_size"])
    flush_speed_list = list(flush_speed["flush_speed"])

    flush_size_list.sort()
    flush_speed_list.sort()

    index_list = [int(x*len(flush_size_list)) for x in percentage_list]

    return index_list, [flush_size_list[i] for i in index_list], [flush_speed_list[i] for i in index_list]


def sql_row(dir, flush_size, flush_speed):
    pk_list = dir.split("/")[-3:]
    print(pk_list)


def get_line_from_dir(log_dir):
    log_lines = readlines_from_log_file(get_log_and_std_files(log_dir)[1])
    index_list, flush_size_list, flush_speed_list = get_flush_tuplers(
        log_lines)
    return percentage_list, list(flush_speed_list)


if __name__ == "__main__":
    log_dirs = get_log_dirs("../")

    color_map = {"64MB": "red", "128MB": "green", "32MB": "blue"}

    materials = ["StorageMaterial.SATAHDD",
                 "StorageMaterial.SATASSD", "StorageMaterial.NVMeSSD"]

    CPU_counts = ["1CPU", "2CPU", "4CPU", "8CPU", "12CPU"]

    prefix = "../"
    import matplotlib.pyplot as plt

    labels = []
    lines = []

    fig, ax_grid = plt.subplots(len(materials), len(
        CPU_counts), sharex=True, sharey=True, figsize=(16, 9))
    fig.text(0.05, 0.5, 'CDF of flush size', va='center', rotation='vertical')
    for i in range(len(materials)):
        fig.text(0.93, round(float(i)/len(materials), 2)*0.75 + 0.25, materials[i].replace("StorageMaterial.", ""),
                 va='center', rotation='-90')
    row = 0
    for material in materials:
        col = 0
        for cpu_count in CPU_counts:
            j = 1
            for batch_size in color_map:
                log_dir = prefix + \
                    "%s/%s/%s/" % (material, cpu_count, batch_size)
                x, y = get_line_from_dir(log_dir)
                print(log_dir, x, y)
                line = ax_grid[row][col].plot(
                    x, y, label=batch_size, color=color_map[batch_size])
                if row == len(materials) - 1:
                    ax_grid[row][col].set_xlabel(cpu_count)
                j += 1
            col += 1
        row += 1

    handles, labels = ax_grid[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=len(labels))

    plt.savefig("../image/flush_speed_cdf.pdf")

    # for log_dir in log_dirs:
    #     log_lines = readlines_from_log_file(get_log_and_std_files(log_dir)[1])
    #     flush_size_list,flush_speed_list = get_flush_tuplers(log_lines)
    #     sql_row(log_dir,flush_size_list,flush_speed_list)
