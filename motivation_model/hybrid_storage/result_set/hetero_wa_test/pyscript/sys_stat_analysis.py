from traversal import *

from log_file_handler import *
import string_utils
import pandas as pd
import plotly.express as px
import traversal as tv
import re

TABLE_NAME_SYSSTAT_ANALYSIS = "compaction_analysis"
TABLE_NAMES = ["nvme_only", "nvme_ssd", "nvme_hdd"]
COLUMN_NUM = 6

def create_data_table(conn):
    c = conn.cursor()
    c.execute("Drop Table if exists "+TABLE_NAME_SYSSTAT_ANALYSIS)
    c.execute("CREATE TABLE "+TABLE_NAME_SYSSTAT_ANALYSIS+
    " (compaction_style TEXT, workload_size REAL, media text, media1_size TEXT, cpu text, batch_size text"
    + ", total_write REAL"
              ")")
    conn.commit()

    for table_name in TABLE_NAMES:
        c.execute("Drop Table if exists "+table_name)
        c.execute("CREATE TABLE "+table_name
                  + " (timestamp TEXT, cpu_util REAL, hdd_read REAL, hdd_write REAL, ssd_read REAL, ssd_write REAL, nvme_read REAL, nvme_write REAL" +
                  #   ",IOPS INT, average_latency_ms REAL" +
                  ")")
        conn.commit()


def paint_for_one_column(column_name, db_conn):

    df = pd.read_sql_query("SELECT * FROM %s" %
                           TABLE_NAME_SYSSTAT_ANALYSIS, db_conn)

    column_label = column_name.replace("_", " ")
    column_label = column_label.replace("overall", "cumulative")
    column_label = column_label.replace("latency", "latency (ms)")

    fig = px.bar(df, x="media1_size", y=column_name, color="media", barmode="group",
                 facet_col="compaction_style",
                 facet_row="workload_size",
                 category_orders={
                     "media1_size": ['1GB', '5GB', '10GB'],
                     "media": ["SATASSD+NVMeSSD", "SATASSD+SATAHDD",
                               "SATAHDD+NVMeSSD", "SATAHDD+SATASSD",
                               "NVMeSSD+SATASSD", "NVMeSSD+SATAHDD",
                               ]
                     #  "media": sorted_media,
                     #  "media1_size":["1GB","5GB","10GB"]
                 },
                 labels={"media1_size": "Capacity of First Medium",
                         "workload_size": "Estimate Input Size", "IOPS": "Throughput (OPs/sec)"},
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
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    # fig.show()
    fig_name = "../image/%s.pdf" % column_name
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)


def get_writed_bytes(df):
    row_num = df.shape[0]
    column_num = df.shape[1]
    nvme_write_index = -1 + column_num
    ssd_write_index = -4 + column_num
    hdd_write_index = -7 + column_num
    nvme_write_bytes = df.iloc[-1][nvme_write_index] - \
        df.iloc[0][nvme_write_index]
    ssd_write_bytes = df.iloc[-1][ssd_write_index] - \
        df.iloc[0][ssd_write_index]
    hdd_write_bytes = df.iloc[-1][hdd_write_index] - \
        df.iloc[0][hdd_write_index]

    # print(nvme_write_bytes, ssd_write_bytes, hdd_write_bytes)
    return nvme_write_bytes + ssd_write_bytes + hdd_write_bytes
    pass

def get_row(dir_path):
    filename = tv.get_stat_files(dir_path)
    total_writes = get_writed_bytes(pd.read_csv(dir_path + "/" + filename, header=None))
    primary_key_list = dir_path.split("/")[-COLUMN_NUM:]
    print(primary_key_list)
    data_row = string_utils.pk_list_to_columns(primary_key_list)
    data_row += "%d" % total_writes
    return data_row

if __name__ == '__main__':
    dirs = get_log_dirs("../")
    print("Directory Scanned")


    
    db_conn = sqlite3.connect('speed_info.db')
    create_data_table(db_conn)
    # create_data_table(db_conn)
    insert_sql_head = "INSERT INTO "+TABLE_NAME_SYSSTAT_ANALYSIS+" VALUES"

    for dir in dirs:
        print(dir)
        sql_data_row = get_row(dir)
        sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
        db_conn.execute(sql_sentence)
    
    paint_for_one_column('total_write',db_conn)