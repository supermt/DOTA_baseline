COLUMN_NUM = 4
SPEED_TABLE_NAME = "speed_results"

perf_keys_single = [
    "get_from_memtable_count",
    "block_cache_hit_count",
    "block_cache_miss_count",
    "seek_on_memtable_count",
]
perf_keys_leveling = [
    "block_cache_hit_count",
    "block_cache_miss_count",
]

max_level = 3
prefix="level"

perf_keys = perf_keys_single

for multi_val_perf_key in perf_keys_leveling:
    for i in range(max_level):
        # perf_keys_ddl += multi_val_perf_key+"_"+prefix+str(i) +","
        perf_keys.append(multi_val_perf_key+"_"+prefix+str(i))
