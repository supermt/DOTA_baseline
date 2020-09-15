import datetime
import time
import csv
import pandas as pd
import json
import re


COMPACTION_LOG_HEAD = "/compaction/compaction_job.cc:755"
FLUSH_LOG_BEGIN = "flush_started"
FLUSH_LOG_END = "flush_end"
FLUSH_FILE_CREATEION = "table_file_creation"

if __name__ == "__main__":
    log_file_name = "../StorageMaterial.NVMeSSD/12CPU/64MB/LOG_1180"
    log_lines = open(log_file_name, "r").readlines()
    flush_lines = [x for x in log_lines if FLUSH_LOG_BEGIN in x]
    event_log_list = []
    compaction_stat_list = []
    job_ids = []
    for line in log_lines:
        if COMPACTION_LOG_HEAD in line:
            compaction_stat_list.append(line)
        line = re.search('(\{.+\})', line)
        if line:
            log_row = json.loads(line[0])
            event_log_list.append(log_row)
    job_ids = set([event['job'] for event in event_log_list])

    job_events = {}
    job_event_map = {}
    for event in event_log_list:
        event_list = job_events.get(event["job"], [])
        event_list.append(event["event"])
        log_list = job_event_map.get(event["job"], [])
        log_list.append(event)
        job_events[event["job"]] = event_list
        job_event_map[event["job"]] = log_list

    flush_jobs = []
    compaction_jobs = []
    other_jobs = []
    for job in job_ids:
        if job_events[job][0] == "compaction_started":
            compaction_jobs.append(job)
        elif job_events[job][0] == "flush_started":
            flush_jobs.append(job)
        else:
            # most of these works are trivial_move and delete files
            other_jobs.append(job)

    machine_start_time = "2020/09/08-20:26:26.582175"
    start_time = datetime.datetime.strptime(
        machine_start_time, "%Y/%m/%d-%H:%M:%S.%f")
    # print("machine start time ", start_time.microsecond)
    start_time_micros = int(time.mktime(
        start_time.timetuple())) * 1000000 + start_time.microsecond
    # print(start_time_micros)

    compaction_stat_details_csv_file = open(
        'tables/compaction_time_line.csv', 'w', newline='')
    csv_writer = csv.writer(compaction_stat_details_csv_file, dialect='excel')
    csv_writer.writerow(["microseconds_start", "duration", "job_id", "RdMBPS",
                         "WtMBPS", "Input File Size (Input Level)", "Input File Size (Output Level)", "Output File Size (MB)", "output_level"])

    i = 0
    for stat_line in compaction_stat_list:
        speed_input = re.search('\d+.\d rd', stat_line)[0]
        speed_output = re.search('\d+.\d wr', stat_line)[0]
        filesize_input = re.search('in\(\d+.\d\, \d+.\d\)', stat_line)[0]
        filesize_output = re.search('out\(\d+.\d\)', stat_line)[0]
        # csv_writer.writerow([stat_line])
        job_id = compaction_jobs[i]
        end_id = job_events[job_id].index("compaction_finished")
        event_time_micros = job_event_map[job_id][end_id]["time_micros"]
        duration = job_event_map[job_id][end_id]["compaction_time_micros"]
        output_level = job_event_map[job_id][end_id]["output_level"]
        elasped_time_micros = event_time_micros - start_time_micros
        i = i + 1
        csv_writer.writerow(
            [elasped_time_micros, duration, job_id,
             speed_input[:-3], speed_output[:-3],
             filesize_input.split(",")[0][3:],
             filesize_input.split(",")[1][1:-1],
             filesize_output[4:-1],
             output_level])
    compaction_stat_details_csv_file.flush()
    compaction_stat_details_csv_file.close()

    df = pd.read_csv("tables/compaction_time_line.csv")

    # gap = df["duration"].min()
    gap = 1000000

    xx = list(range(0,
                    df["microseconds_start"].max()+df["duration"].max(), gap))
    # print(xx)
    concurrent_compactions = [0 for x in xx]

    for index, row in df.iterrows():
        start_index = int((row["microseconds_start"] - xx[0]) / gap)
        end_index = int((row["microseconds_start"] +
                         row["duration"] - xx[0]) / gap)
        # print(int(start_index),int(end_index))
        try:
            for i in range(start_index, end_index):
                concurrent_compactions[i] += 1
        except IndexError:
            print(start_index, end_index)
            break
        # concurrent_compactions[start_index:end_index]
        #     concurrent_compactions[i] = concurrent_compactions[i] + 1

    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(20, 9))
    ax = plt.subplot(111)
    # print(concurrent_compactions)
    ax.plot([x/1000000 for x in xx], concurrent_compactions,label="Concurrent Compactions",color="red")
    ax1 = ax.twinx()
    # ax.set_ylim(0,max(concurrent_compactions)+2)

    report_csv = "../StorageMaterial.NVMeSSD/12CPU/64MB/report.csv_1180"

    real_time_speed = pd.read_csv(report_csv)

    ax1.plot(real_time_speed['interval_qps'],label="Real Time Throughput (IOPS)")

    # plt.show()
    fig.savefig("temp.pdf")
