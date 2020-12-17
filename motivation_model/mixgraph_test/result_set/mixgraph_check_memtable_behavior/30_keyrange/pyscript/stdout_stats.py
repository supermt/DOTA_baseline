from traversal import *
import sqlite3
import plotly.express as px
from functools import cmp_to_key
import string_utils

COLUMN_NUM = 3
SPEED_TABLE_NAME = "speed_results"

perf_keys_single = [
    "get_from_memtable_count",
    "block_cache_hit_count",
    "block_cache_miss_count",
    "seek_on_memtable_count",
]
perf_keys_leveling = [
    "bloom_sst_hit_count",
    "bloom_sst_miss_count",
]

perf_keys_ddl = ' '.join([x+" INT," for x in perf_keys_single])[:-1]
max_level = 3
prefix="level"

# [x+" INT," for x in perf_keys]


def create_data_table(conn):
    c = conn.cursor()

    c.execute('''Drop Table if exists speed_results''')
    c.execute("CREATE TABLE %s (media TEXT, cpu TEXT, batch_size text," % SPEED_TABLE_NAME +
              "IOPS INT, average_latency_ms REAL," +
              perf_keys_ddl +
              #   "get_from_memtable_count INT," +
              #   "block_cache_hit_count INT," +
              #   "block_cache_miss_count INT," +
              #   "seek_on_memtable_count INT," +
              #   "bloom_sst_hit_count INT," +
              #   "bloom_sst_miss_count INT," +
              #   "block_cache_hit_count INT," +
              #   "block_cache_miss_count INT" +
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split(os.sep)[-COLUMN_NUM:]
    data_row = string_utils.pk_list_to_columns(primary_key_list)

    iops, avg_latency = std_reader.get_iops_and_avg_latency(stdfile[0])

    data_row += str(iops) + "," + str(avg_latency)
    perf_dict = std_reader.get_perf_string_result(stdfile[0])
    print(perf_dict)
    data_row_dml = ''.join([perf_dict[perf_key]+"," for perf_key in perf_keys])

    print(data_row_dml)

    return data_row


def legend_sorter(x, y):
    if len(x) > 2:
        return x[1:-2] < y[1:-2]

    if x.isnumeric():
        return float(x) - float(y)
    else:
        return x < y


def plot_single_graph(paint_df, IOPS_or_latency="IOPS"):

    # legends = df['media1_size'].unique()
    # legends = sorted(legends,key=cmp_to_key(legend_sorter))

    fig = px.bar(paint_df, x="cpu", y=IOPS_or_latency, color="media", barmode="group",
                 facet_row="batch_size",
                 category_orders={
                     "media": ["SATASSD", "SATAHDD", "NVMeSSD", "PM"],
                     "cpu": [str(x)+"CPU" for x in [8, 16, 32]],
                     "batch_size": [str(x)+"MB" for x in range(64, 128)],
                     "value_size": ["mixed_size_"+str(x) + "_keyrange" for x in [15, 30, 60]]
                     #  "media": sorted_media,
                     #  "media1_size":["1GB","5GB","10GB"]
                 },
                 labels={"media": "Storage Media",
                         "workload_size": "Estimate Input Size",
                         "IOPS": "OPs/sec", "cpu": "CPU count",
                         "batch_size": "Operation Batch Size",
                         "value_size": "Mode of Value Size"},
                 #  color_discrete_map=batch_size_to_color_map
                 )
    fontsize = 20

    fig.update_layout(
        autosize=False,
        width=1600,
        height=900,
        font=dict(size=fontsize),
        # plot_bgcolor='white',
    )
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.1,
        xanchor="left",
        x=0.25,
        font=dict(size=fontsize+4)
    ))
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    # fig.show()
    fig_name = "./image/%s.pdf" % IOPS_or_latency
    png_fig_name = "./image/%s.png" % IOPS_or_latency
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)
    fig.write_image(png_fig_name)
    pass


if __name__ == "__main__":
    dirs = get_log_dirs("../")
    print("Directory Scanned")

    # perf_level = 2
    # with following entries
    # user_key_comparison_count = 24879682640, block_cache_hit_count = 1892474, block_read_count = 33443137, block_read_byte = 2189278935874, block_read_time = 0, block_cache_index_hit_count = 0, index_block_read_count = 0, block_cache_filter_hit_count = 0, filter_block_read_count = 0, compression_dict_block_read_count = 0, block_checksum_time = 0, block_decompress_time = 0, get_read_bytes = 0, multiget_read_bytes = 0, iter_read_bytes = 414378238, internal_key_skipped_count = 2994987237, internal_delete_skipped_count = 0, internal_recent_skipped_count = 0, internal_merge_count = 0, write_wal_time = 0, get_snapshot_time = 0, get_from_memtable_time = 0, get_from_memtable_count = 431979942, get_post_process_time = 0, get_from_output_files_time = 0, seek_on_memtable_time = 0, seek_on_memtable_count = 5083003, next_on_memtable_count = 157789183, prev_on_memtable_count = 0, seek_child_seek_time = 0, seek_child_seek_count = 21511348, seek_min_heap_time = 0, seek_internal_seek_time = 0, find_next_user_entry_time = 0, write_pre_and_post_process_time = 0, write_memtable_time = 0, write_thread_wait_nanos = 0, write_scheduling_flushes_compactions_time = 0, db_mutex_lock_nanos = 0, db_condition_wait_nanos = 0, merge_operator_time_nanos = 0, write_delay_time = 0, read_index_block_nanos = 0, read_filter_block_nanos = 0, new_table_block_iter_nanos = 0, new_table_iterator_nanos = 0, block_seek_nanos = 0, find_table_nanos = 0, bloom_memtable_hit_count = 0, bloom_memtable_miss_count = 0, bloom_sst_hit_count = 12430497, bloom_sst_miss_count = 1061023847, key_lock_wait_time = 0, key_lock_wait_count = 0, env_new_sequential_file_nanos = 0, env_new_random_access_file_nanos = 0, env_new_writable_file_nanos = 0, env_reuse_writable_file_nanos = 0, env_new_random_rw_file_nanos = 0, env_new_directory_nanos = 0, env_file_exists_nanos = 0, env_get_children_nanos = 0, env_get_children_file_attributes_nanos = 0, env_delete_file_nanos = 0, env_create_dir_nanos = 0, env_create_dir_if_missing_nanos = 0, env_delete_dir_nanos = 0, env_get_file_size_nanos = 0, env_get_file_modification_time_nanos = 0, env_rename_file_nanos = 0, env_link_file_nanos = 0, env_lock_file_nanos = 0, env_unlock_file_nanos = 0, env_new_logger_nanos = 0, get_cpu_nanos = 0, iter_next_cpu_nanos = 0, iter_prev_cpu_nanos = 0, iter_seek_cpu_nanos = 0, bloom_filter_useful = 446483293@level0, 233331388@level1, 381209166@level2, bloom_filter_full_positive = 5227145@level0, 2736235@level1, 4467117@level2, bloom_filter_full_true_positive = 0@level0, 0@level1, 0@level2, block_cache_hit_count = 147719@level0, 928965@level1, 815790@level2, block_cache_miss_count = 11065155@level0, 6460981@level1, 15917001@level2

    db_conn = sqlite3.connect('speed_info.db')

    create_data_table(db_conn)

    insert_sql_head = "INSERT INTO speed_results VALUES"

    for dir in dirs:
        sql_data_row = get_row(dir)
        sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
        db_conn.execute(sql_sentence)

    print("DB Loaded")

    cursor = db_conn.cursor()

    paint_df = pd.read_sql_query(
        "SELECT * FROM speed_results", db_conn)
    plot_single_graph(paint_df)
    plot_single_graph(paint_df, "average_latency_ms")
#     # plot_by_io_option("block_size")
