from traversal import *
import sqlite3
import plotly.express as px
from functools import cmp_to_key
import string_utils

COLUMN_NUM = 6


def create_data_table(conn):
    c = conn.cursor()

    c.execute('''Drop Table if exists speed_results''')
    c.execute("CREATE TABLE speed_results ( compaction_style TEXT, workload_size REAL, media text, media1_size TEXT, cpu text, batch_size text," +
              "IOPS INT, average_latency_ms REAL" +
              # ",compaction_frequency INT, overall_compaction_latency INT" +
              # ",overall_compaction_cpu_latency INT"+
              # ",overall_input_record INT"+
              # ",overall_output_record INT"+
              # ",overall_redundant_record INT"+
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split("/")[-COLUMN_NUM:]
    data_row = string_utils.pk_list_to_columns(primary_key_list)

    iops, avg_latency = std_reader.get_iops_and_avg_latency(stdfile[0])

    data_row += str(iops) + "," + str(avg_latency)

    return data_row


def legend_sorter(x, y):
    if len(x) > 2:
        return x[1:-2] < y[1:-2]

    if x.isnumeric():
        return float(x) - float(y)
    else:
        return x < y


def plot_single_graph(db_conn):
    df = pd.read_sql_query(
        "SELECT * FROM speed_results", db_conn)

    print(df)
    # legends = df['media1_size'].unique()
    # legends = sorted(legends,key=cmp_to_key(legend_sorter))

    fig = px.bar(df, x="media1_size", y="IOPS", color="media", barmode="group",
                 facet_col="compaction_style",
                 facet_row="workload_size",
                 category_orders={
                     "media1_size": ['1GB', '5GB', '10GB'],
                     "media":["SATASSD+NVMeSSD","SATASSD+SATAHDD", 
                            "SATAHDD+NVMeSSD","SATAHDD+SATASSD",
                            "NVMeSSD+SATASSD","NVMeSSD+SATAHDD",
                            "NVMeSSD Only"
                     ]
                     #  "media": sorted_media,
                     #  "media1_size":["1GB","5GB","10GB"]
                 },
                 labels={"media1_size": "Capacity of First Medium", "workload_size":"Estimate Input Size" , "IOPS": "Throughput (OPs/sec)"},
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
    fig_name = "../image/%s.pdf" % "IOPS"
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)
    pass


if __name__ == "__main__":
    dirs = get_log_dirs("../")
    print("Directory Scanned")

    db_conn = sqlite3.connect('speed_info.db')

    create_data_table(db_conn)

    insert_sql_head = "INSERT INTO speed_results VALUES"

    for dir in dirs:
        sql_data_row = get_row(dir)
        sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
        db_conn.execute(sql_sentence)

    print("DB Loaded")

    cursor = db_conn.cursor()

    plot_single_graph(db_conn)
#     # plot_by_io_option("block_size")
