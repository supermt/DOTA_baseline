from traversal import *

from log_file_handler import *

import plotly.express as px

TABLE_NAME_COMPACTION_ANALYSIS = "compaction_analysis"


def create_data_table(conn):
    c = conn.cursor()

    c.execute("Drop Table if exists "+TABLE_NAME_COMPACTION_ANALYSIS)
    c.execute("CREATE TABLE "+TABLE_NAME_COMPACTION_ANALYSIS+" (compaction_style TEXT, workload_size REAL, media text, media1_size TEXT, cpu text, batch_size text" +
              #   ",IOPS INT, average_latency_ms REAL" +
              ",compaction_frequency INT, overall_compaction_latency INT" +
              ",overall_compaction_cpu_latency INT" +
              ",overall_input_record INT" +
              ",overall_output_record INT" +
              ",overall_redundant_record INT" +
              ")")
    conn.commit()

    print("table created")


def paint_for_one_column(column_name, db_conn):

    df = pd.read_sql_query("SELECT * FROM %s" %
                           TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

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


if __name__ == '__main__':
    dirs = get_log_dirs("../")
    print("Directory Scanned")

    db_conn = sqlite3.connect('speed_info.db')

    create_data_table(db_conn)

    insert_sql_head = "INSERT INTO "+TABLE_NAME_COMPACTION_ANALYSIS+" VALUES"

    for dir in dirs:
        print(dir)
        sql_data_row = get_row(dir)
        sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
        db_conn.execute(sql_sentence)

    print("DB Loaded")
    df = pd.read_sql_query(
        "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

    print(df)
    column_list = list(df.columns.values)[-6:]
    print(column_list)
    for column in column_list:
        paint_for_one_column(column, db_conn)
#     cpu_group = [1, 4, 8, 12]
#     cpu_group = [str(x) + "CPU" for x in cpu_group]
#     bandwidth_group = ['400', '800', '1200', '1600', '2000']
#     bandwidth_group = [x + "mb" for x in bandwidth_group]
# #   size_color = {16: "rgb(66,106,199)", 32: "rgb(254,117,0)",
# #              64: "rgb(165,165,165)", 128: "rgb(255,194,0)"}
#     batch_size_to_color_map = {
#         "16MB": "rgb(66,106,199)",
#         "32MB": "rgb(254,117,0)",
#         "64MB": "rgb(165,165,165)",
#         "128MB": "rgb(255,194,0)"
#     }
#     media = "NVMeSSD"
#     batch_size_group = ["16MB", "32MB", "64MB", "128MB"]

#     df = pd.read_sql_query(
#         "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

#     column_list = list(df.columns.values)[4:]
