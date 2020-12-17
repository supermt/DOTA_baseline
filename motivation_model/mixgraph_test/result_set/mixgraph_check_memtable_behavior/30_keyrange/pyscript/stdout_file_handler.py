def get_iops_and_avg_latency(file_name):
    iops = 0
    avg_latency = 0
    record_lines = open(file_name, "r").readlines()
    index = record_lines.index(" PERF_CONTEXT:\n")
    record = record_lines[index-1]
    data = record.split(" ")
    data = [x for x in data if x != ""]
    avg_latency = float(data[2])
    iops = int(data[4])
    return iops, avg_latency


def get_perf_string_result(file_name):
    perf_result = {}
    record_lines = open(file_name, "r").readlines()
    perf_line = record_lines[record_lines.index(
        " PERF_CONTEXT:\n") + 1].replace(" ", "")
    splits = perf_line.split("=")
    keys = [splits[0]]
    values = []
    last_key = ""
    for slices in splits:
        if "," in slices:
            slice_string = slices.split(",")
            if len(slice_string) == 2:
                # has only one value, next part is the key
                keys.append(slice_string[-1])
                last_key = slice_string[-1]
                values.append(slice_string[0])
            else:
                temp = slice_string[0:-1]
                keys.pop()
                for k_l_slice in temp:
                    keys.append(last_key + "@" + k_l_slice.split("@")[1])
                    values.append(k_l_slice.split("@")[0])
                # values.append(''.join([x+"," for x in temp])[:-1])
                keys.append(slice_string[-1])
                last_key = slice_string[-1]
        else:  # the only split without '=' is the first one
            # just skip, we will build two lists, and use zip to bulid up the dict
            pass
    perf_result = dict(zip(keys, values))
    return perf_result
