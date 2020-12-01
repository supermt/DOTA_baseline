import json
import re
import gzip
import string_utils

import traversal as tv


def open_file(file_name):
    log_file = None
    if "gz" in file_name:
        log_file = gzip.open(file_name, "r")
    else:
        log_file = open(file_name, "r")

    return log_file


def handle_compaction_line(line):
    pass


def handle_flush_line(line):
    result = {}
    # print("flush_finished")
    return result


# compaction frequency, overall input, overall output, redundant records
def get_data_list(log_file):
    compaction_latencies = []
    compaction_cpu_latencies = []
    compaction_input = []
    compaction_output = []
    compaction_redundant = []
    l0_compaction = 0
    for line in log_file.readlines():
        line = str(line)
        line = re.search('(\{.+\})', line)
        if line:
            log_row = json.loads(line[0])
            # if "compaction_finished" in str(log_row):
            if log_row['event'] == 'compaction_started':
                if log_row['compaction_reason'] == "LevelL0FilesNum":
                    l0_compaction += 1
            if log_row['event'] == 'compaction_finished':
                compaction_latencies.append(
                    log_row['compaction_time_micros'])
                compaction_cpu_latencies.append(
                    log_row['compaction_time_cpu_micros'])
                compaction_input.append(
                    log_row['num_input_records'])
                compaction_output.append(
                    log_row['num_output_records'])
                compaction_redundant.append(
                    log_row['num_input_records']-log_row['num_output_records'])
            if log_row['event'] == 'flush_finished':
                handle_flush_line(log_row)
    return [compaction_latencies, compaction_cpu_latencies, compaction_input, compaction_output, compaction_redundant, l0_compaction]


def turn_list_to_sql_sentence(column_lists, sql_head="INSERT INTO speed_results VALUES"):

    sql_sentence = ""
    return sql_sentence
