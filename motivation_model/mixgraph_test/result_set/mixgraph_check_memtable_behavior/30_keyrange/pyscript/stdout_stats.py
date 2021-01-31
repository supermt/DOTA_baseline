from traversal import *
import sqlite3
import plotly.express as px
from functools import cmp_to_key
import string_utils
from shared_macro import *

perf_keys_ddl = ' '.join([x+" INT," for x in perf_keys])


perf_keys_ddl = perf_keys_ddl[:-1]
# [x+" INT," for x in perf_keys]
print(perf_keys_ddl)

def create_data_table(conn):
    c = conn.cursor()

    c.execute('''Drop Table if exists speed_results''')
    c.execute("CREATE TABLE %s (op_distribution TEXT,media TEXT, cpu TEXT, batch_size text," % SPEED_TABLE_NAME +
              "IOPS INT, average_latency_ms REAL," +
              perf_keys_ddl +
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split(os.sep)[-COLUMN_NUM:]
    data_row = string_utils.pk_list_to_columns(primary_key_list)
    iops, avg_latency = std_reader.get_iops_and_avg_latency(stdfile[0])

    data_row += str(iops) + "," + str(avg_latency) + ","


    perf_dict = std_reader.get_perf_string_result(stdfile[0])

    for perf_key in perf_keys:
        data_value = perf_dict.get(perf_key, 0)
        # print(perf_key, data_value)
        data_row += str(data_value)+","
    return data_row[:-1]


def legend_sorter(x, y):
    if len(x) > 2:
        return x[1:-2] < y[1:-2]

    if x.isnumeric():
        return float(x) - float(y)
    else:
        return x < y


def plot_single_graph(paint_df, IOPS_or_latency="IOPS"):
    fig = px.bar(paint_df, x="cpu", y=IOPS_or_latency, color="media", barmode="group",
                 facet_row="batch_size",
                 facet_col="op_distribution",
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
    for perf_key in perf_keys:
        plot_single_graph(paint_df, perf_key)


#     # plot_by_io_option("block_size")
