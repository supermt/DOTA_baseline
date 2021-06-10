import pandas as pd
cpu_num_list = [1, 4, 8]
STDOUT_DIR = "db_bench_results"
material_list = ["pm", "nvme", "ssd", "hdd"]


def thread_idle_gap_dict_to_statistics(idle_gap_dict):
    result = {}
    for idle_gap in idle_gap_dict:
        result[idle_gap] = sum(idle_gap_dict[idle_gap])
    return result


def idle_time_to_row(thread_num, material_name, compction_idle, flush_idle):
    result_head = "%s,%s," % (thread_num, material_name)
    result = []
    for compaction_thread_id in compction_idle:
        result.append(result_head + "compaction_"+str(compaction_thread_id) +
                      ","+str(compction_idle[compaction_thread_id])+"\n")
    for flush_thread_id in flush_idle:
        result.append(result_head + "flush_"+str(flush_thread_id) +
                      ","+str(flush_idle[flush_thread_id])+"\n")
    temp = ""
    for line in result:
        temp+=line
    return temp


for cpu_num in cpu_num_list:
    for material in material_list:
        filename = "%d/%s/%s.stdout" % (cpu_num, STDOUT_DIR, material)
        lines = open(filename, "r").readlines()
        compaction_start_line_num = lines.index(
            "micro seconds waiting for next mission\n")+1
        flush_start_line_num = lines[compaction_start_line_num +
                                     1:].index("micro seconds waiting for next mission\n") + compaction_start_line_num + 2
        compaction_thread_lines = lines[compaction_start_line_num +
                                        1:flush_start_line_num-4]
        flush_thread_lines = lines[flush_start_line_num:]
        temp_dict = {x: [] for x in range(cpu_num)}
        for compaction_line in compaction_thread_lines:
            temp = compaction_line.split(":")
            temp_dict[int(temp[0])].append(int(temp[1]))

        compaction_thread_pool_idling_map = thread_idle_gap_dict_to_statistics(
            temp_dict)
        temp_dict = {x: [] for x in range(1)}
        for flush_line in flush_thread_lines:
            temp = flush_line.split(":")
            temp_dict[int(temp[0])].append(int(temp[1]))
        flush_thread_pool_idling_map = thread_idle_gap_dict_to_statistics(
            temp_dict)
        print(idle_time_to_row(cpu_num, material,
                               compaction_thread_pool_idling_map, flush_thread_pool_idling_map)[:-1])
