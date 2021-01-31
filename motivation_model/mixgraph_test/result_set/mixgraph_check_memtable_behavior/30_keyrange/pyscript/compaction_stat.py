import pandas as pd
from traversal import *

import traversal as tv
import string_utils
import plotly.express as px
from log_file_handler import get_data_list, open_file

COLUMN_NUM = 4

TABLE_NAME_COMPACTION_ANALYSIS = "compaction_analysis"

def create_data_table(conn):
    c = conn.cursor()

    c.execute("Drop Table if exists "+TABLE_NAME_COMPACTION_ANALYSIS)
    c.execute("CREATE TABLE "+TABLE_NAME_COMPACTION_ANALYSIS+" (op_distribution text,media text, cpu text, batch_size text" +
              #   ",IOPS INT, average_latency_ms REAL" +
              ",compaction_frequency INT, overall_compaction_latency INT" +
              ",overall_compaction_cpu_latency INT" +
              ",overall_input_record INT" +
              ",overall_output_record INT" +
              ",overall_redundant_record INT" +
              ",l0_compaction_ratio REAL"
              ")")
    conn.commit()

    print("table created")


def get_row(dir_path):
    stdfile, logfile = tv.get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split(os.sep)[-COLUMN_NUM:]
    data_row = string_utils.pk_list_to_columns(primary_key_list)
    value_list = get_data_list(open_file(logfile))
    compaction_frequency = len(value_list[0])

    data_row += str(compaction_frequency)+","

    # the last element is the l0 compaction count, no need for adding up
    for value in value_list[0:-3]:
        data_row += str(sum(value))+","
    data_row += str(round(float(value_list[-3])/compaction_frequency , 2))

    print(dir_path)
    zipped_list = zip(value_list[-2],value_list[-1])
    repeat_ratio = [round(x[1]/x[0] ,2) for x in zipped_list]
    print("repeat_ratio_list",repeat_ratio)
    return data_row


dirs = get_log_dirs("../85g14p01s")


db_conn = sqlite3.connect('speed_info.db')

create_data_table(db_conn)

insert_sql_head = "INSERT INTO "+TABLE_NAME_COMPACTION_ANALYSIS+" VALUES"

for dir in dirs:
    sql_data_row = get_row(dir)
    sql_sentence = insert_sql_head + "(" + sql_data_row + ")"
#     print(sql_sentence)
    db_conn.execute(sql_sentence)

print("DB Loaded")
# df = pd.read_sql_query(
#     "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

# column_list = list(df.columns.values)[-6:]

paint_df = pd.read_sql_query(
    "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

# keyranges=[15,30,60,90]
# paint_dfs = []
# for keyrange in keyranges:
# #     print("SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS +" WHERE keyrange_count = '%d'"%keyrange)
#     paint_df = pd.read_sql_query("SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS +" WHERE keyrange_count = '%d'"%keyrange, db_conn)
#     paint_dfs.append(paint_df)

df = pd.read_sql_query(
    "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

column_list = list(df.columns.values)[-7:]


def paint_for_one_column(column_name, paint_df):

    column_label = column_name.replace("_", " ")
    column_label = column_label.replace("overall", "cumulative")
    column_label = column_label.replace("latency", "latency (ms)")

    fig = px.bar(paint_df, x="op_distribution", y=column_name, color="media", barmode="group",
                 facet_col="cpu",
                 facet_row="batch_size",
                 category_orders={
                     "media": ["SATASSD", "SATAHDD", "NVMeSSD", "PM"],
                     "cpu": [str(x)+"CPU" for x in [8, 16, 32]],
                     "batch_size": [str(x)+"MB" for x in range(64, 128)],
                     #  "media": sorted_media,
                     #  "media1_size":["1GB","5GB","10GB"]
                     "value_size": ["mixed_size_"+str(x) + "_keyrange" for x in [15, 30, 60]]
                 },
                 labels={"media": "Storage Media",
                         "workload_size": "Estimate Input Size",
                         "IOPS": "OPs/sec", "cpu": "CPU count",
                         "batch_size": "Operation Batch Size",
                         "value_size": "Mode of value size"},
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
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    # fig.show()
    fig_name = "./image/%s.pdf" % column_name
    png_fig_name = "./image/%s.png" % column_name
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)
    fig.write_image(png_fig_name)


for column in column_list:
    paint_for_one_column(column, paint_df)
