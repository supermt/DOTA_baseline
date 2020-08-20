import re
import json
import os
import glob
import statistics


TRANS_MICRO_SEC = 1000000

def dev(input_list):
    return statistics.stdev(input_list)


def avg(input_list):
    return statistics.mean(input_list)


def column_values_time(compaction_sequence):
    return "%s,%.2f,%.2f,%s,%.2f,%s" % (len(compaction_sequence), sum([x / TRANS_MICRO_SEC for x in compaction_sequence]), max([x / TRANS_MICRO_SEC for x in compaction_sequence]), min(compaction_sequence), avg([x / TRANS_MICRO_SEC for x in compaction_sequence]), dev(compaction_sequence))


def column_values_record(compaction_sequence):
    return "%s,%s,%s,%s,%.2f" % (len(compaction_sequence), sum(compaction_sequence), max(compaction_sequence), min(compaction_sequence), avg(compaction_sequence))


def print_row(throughput, compaction_latencies, compaction_cpu_latencies, compaction_input, compaction_redundant):
    # Throughput,Compaction Frequency,Cumulative Compaction Cost, Cumulative CPU Time,Compaction Input Records,Compacted Redundant Records
    
    return "%s,%s,%.2f,%.2f,%s,%s" % (throughput,len(compaction_latencies), sum(compaction_latencies)/TRANS_MICRO_SEC,
                                  sum(compaction_cpu_latencies)/TRANS_MICRO_SEC, sum(
                                      compaction_input), sum(compaction_redundant)
                                  )



def handle_log_file(log_file):
    pass


def handle_stdout_file(stdout_file):
    try:
        speedline = open(stdout_file, "r").readlines()[-1]
        # print(speedline)
        throughput = speedline.split("op ")[1].split(" ops/sec")[0]
        return throughput
    except:
        stderr_file = stdout_file.replace("stdout","stderr")
        speedline = open(stderr_file,"r").readlines()
        # print(speedline)
        return 0

print("DISK TYPE,CPU,Memtable Size,Throughput,Compaction Frequency,Overall Compaction Cost,Cumulative CPU Time,Cumulative Compaction Input,Overall Redundant Records")
# print("DISK TYPE,CPU,Memtable Size,Number of Compactions,Overall Compaction Redundant Records,Max Compaction Redundant Records,Min Compaction Redundant Records,Avg of Compaction Redundant Records,Dev of Compaction Redundant Records")

materials = ["PM", "PM_NOVA", "NVMeSSD"]
# materials = ["SATASSD"]
CPUs = [2, 4, 8]
memtable_sizes = [16, 32, 64, 128]

for material in materials:
    for cpu_count in CPUs:
        for memtable_size in memtable_sizes:
            name = "%s/%s/%s" % ("StorageMaterial."+material,
                                 str(cpu_count)+"CPU", str(memtable_size)+"MB")
            log_file = [os.path.abspath(filename) for filename in glob.glob(
                name+"/**") if "LOG" in filename][0]

            log_lines = open(log_file, "r").readlines()

            compaction_latencies = []
            compaction_cpu_latencies = []
            compaction_input = []
            compaction_output = []
            compaction_redundant = []

            for log_line in log_lines:
                line_split = re.search('(\{.+\})', log_line)
                if line_split:
                    try:
                        log_dict = json.loads(line_split[0])
                        # print(log_dict['time_micros'])
                        if log_dict['event'] == "compaction_finished":
                            compaction_latencies.append(
                                log_dict['compaction_time_micros'])
                            compaction_cpu_latencies.append(
                                log_dict['compaction_time_cpu_micros'])
                            compaction_input.append(
                                log_dict['num_input_records'])
                            compaction_output.append(
                                log_dict['num_output_records'])
                            compaction_redundant.append(
                                log_dict['num_input_records']-log_dict['num_output_records'])
                    except json.decoder.JSONDecodeError:
                        pass

            stdout_file = [os.path.abspath(filename) for filename in glob.glob(
                name+"/**") if "stdout" in filename][0]
            throughput = handle_stdout_file(stdout_file)

            print("%s,%s,%s,%s" % (material, cpu_count, memtable_size,
                                   print_row(throughput, compaction_latencies,
                                             compaction_cpu_latencies,
                                             compaction_input, compaction_redundant)))

# DISK TYPE,CPU,Memtable Size,Throughput,Overall Compaction Input,Compaction Frequency,Overall Compaction Cost, Cumulative CPU Time, Overall Redundant Records
