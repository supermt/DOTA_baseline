import sqlite3
import plotly.express as px
from functools import cmp_to_key
import pandas as pd
import glob

SPPED_LINE_INDEX = -5
DISK_LINE_INDEX = -2
SPEED_MBPS_INDEX = 4

DIR_PREFIX = "PersonalServer/"
TABLE_NAME = 'fio_result'


def get_speed_from_filelines(filelines):
    speed_line = filelines[SPPED_LINE_INDEX]
    # speed_line.split(" ")
    # print(speed_line.split(" ")[4])
    speed_in_MBPS = speed_line.split(" ")[4]
    return speed_in_MBPS.replace("MB/s),", "").replace("(", "")
    # return result


def get_disk_util_from_flielines(filelines):
    disk_line = filelines[DISK_LINE_INDEX]
    disk_util = disk_line.split(" ")[-1]
    # print(disk_util)
    disk_util = disk_util.replace("util=","").replace("%","")
    return disk_util


def extract_file(filename):
    filelines = open(filename).readlines()
    # print(len(filelines))
    speed_numeric_string = get_speed_from_filelines(filelines)
    disk_util = get_disk_util_from_flielines(filelines)

    # pharse the filename to a parameter list
    filename = filename.split("/")[-1]
    filename = filename.replace(".txt", "")
    para_list = filename.split("_")

    return para_list, speed_numeric_string, disk_util


def para_list_to_record_row(para_list, speed, disk_util):
    insert_sql = "INSERT INTO %s VALUES (" % TABLE_NAME

    int_values = [1, 2, 4]
    for i in range(len(para_list)):
        if i in int_values:
            insert_sql += "%s," % para_list[i].replace("k", "")
        else:
            insert_sql += "'%s'," % para_list[i]

    insert_sql += speed +","
    insert_sql += disk_util
    insert_sql += ")"
    print(insert_sql)
    return insert_sql


def create_data_table(conn):
    c = conn.cursor()

    # op,iodepth,numjobs,ioengine,bs,media
    c.execute("Drop Table if exists %s" % TABLE_NAME)
    c.execute("CREATE TABLE %s (workload text, iodepth int, numjobs int, ioengine text, bs int, media," % TABLE_NAME +
              "MBPS REAL," + "diskutil REAL"
              ")")
    conn.commit()

    print("table created")


def legend_sorter(x, y):
    if x.isnumeric():
        return float(x) - float(y)
    else:
        return x < y


if __name__ == "__main__":
    # extract_file("PersonalServer/10G_60_write_0_1_1_psync_4k_nvme.txt")
    file_list = glob.glob(DIR_PREFIX+"*.txt")
    db_conn = sqlite3.connect('fio_result.db')
    create_data_table(db_conn)
    for file in file_list:
        print("loading file %s" % file)
        para_list, speed, disk_util = extract_file(file)
        sql_query = para_list_to_record_row(para_list, speed, disk_util)
        db_conn.execute(sql_query)
    print("table loaded")

    df = pd.read_sql_query("SELECT * from %s" % TABLE_NAME, db_conn)

    print(df)
    media = ["hdd", "ssd", "nvme"]
    media_label_map = {
        "hdd": "SATA HDD",
        "ssd": "SATA SSD",
        "nvme": "NVMe SSD"
    }

    workloads = ['randwrite', 'write']
    workload_title = {"randwrite": "Random Write Performance",
                      "write": "Sequential Write Performance"}

    for workload in workloads:
        fig_name = workload
        df = pd.read_sql_query(
            "SELECT iodepth,ioengine,bs,media,MBPS FROM %s where workload = '%s'" % (TABLE_NAME, workload), db_conn)

        fig = px.bar(df.replace({'media': media_label_map}), x="iodepth", y="MBPS", barmode="group", facet_row="ioengine", facet_col="bs",
                     color="media",
                     category_orders={
                         "iodepth": [1, 16, 32, 64, 256],
                         "media": list(media_label_map.values()),
                         "bs": [4, 16, 64]
        },
            labels={
                         "bs": "block size (KB)", "MBPS": "Throughput (MB/s)", "media": "Storage Device", "iodepth": "iodepth"}
        )
        fontsize = 24
        fig.update_layout(
            autosize=False,
            width=900,
            height=700,
            font=dict(size=fontsize),
            plot_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.5
            ),
        )
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(showgrid=False, type='category')
        # fig.show()
        fig_name = "image/%s.pdf" % fig_name
        print("plotting fig %s finished" % fig_name)
        fig.write_image(fig_name)
        # fig.show()
