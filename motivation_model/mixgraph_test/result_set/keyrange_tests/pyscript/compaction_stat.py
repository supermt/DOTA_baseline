from traversal import *

import traversal as tv
import string_utils
import plotly.express as px
from log_file_handler import get_data_list, open_file

COLUMN_NUM = 4

TABLE_NAME_COMPACTION_ANALYSIS = "compaction_analysis"

def pk_list_to_columns(primary_key_list):
    data_row = ""
    print(primary_key_list[-4].split("_"))    
    data_row += '%s,' % primary_key_list[-4].split("_")[1]

    data_row += '"%s",' % primary_key_list[-3].replace("StorageMaterial.","")
    data_row += '"%s",' % primary_key_list[-2]
    data_row += '"%s",' % primary_key_list[-1]
    return data_row

def create_data_table(conn):
    c = conn.cursor()

    c.execute("Drop Table if exists "+TABLE_NAME_COMPACTION_ANALYSIS)
    c.execute("CREATE TABLE "+TABLE_NAME_COMPACTION_ANALYSIS+" (keyrange_count INT,media text, cpu text, batch_size text" +
              #   ",IOPS INT, average_latency_ms REAL" +
              ",compaction_frequency INT, overall_compaction_latency INT" +
              ",overall_compaction_cpu_latency INT" +
              ",overall_input_record INT" +
              ",overall_output_record INT" +
              ",overall_redundant_record INT" +
              ")")
    conn.commit()

    print("table created")
    
def get_row(dir_path):
    stdfile, logfile = tv.get_log_and_std_files(dir_path)
    primary_key_list = dir_path.split(os.sep)[-COLUMN_NUM:]
    data_row = pk_list_to_columns(primary_key_list)
    value_list = get_data_list(open_file(logfile))
    compaction_frequency = len(value_list[0])

    data_row += str(compaction_frequency)+","
    
    for value in value_list:
        data_row += str(sum(value))+","
    return data_row[0:-1]


dirs = get_log_dirs("../")
print(dirs)


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

import pandas as pd
df = pd.read_sql_query(
    "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

keyranges=[15,30,60,90]
paint_dfs = []
for keyrange in keyranges:
#     print("SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS +" WHERE keyrange_count = '%d'"%keyrange)
    paint_df = pd.read_sql_query("SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS +" WHERE keyrange_count = '%d'"%keyrange, db_conn)
    paint_dfs.append(paint_df)

df = pd.read_sql_query(
    "SELECT * FROM "+TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

column_list = list(df.columns.values)[-6:]

def paint_for_one_column(column_name,paint_df):

    df = pd.read_sql_query("SELECT * FROM %s" %
                           TABLE_NAME_COMPACTION_ANALYSIS, db_conn)

    column_label = column_name.replace("_", " ")
    column_label = column_label.replace("overall", "cumulative")
    column_label = column_label.replace("latency", "latency (ms)")

    fig = px.bar(df, x="cpu", y=column_name, color="keyrange_count", barmode="group",
                 facet_col="media",
#                  facet_row="batch_size",
                 category_orders={
                     "media": ["SATASSD", "SATAHDD", "NVMeSSD","PM"],
                     "cpu": [str(x)+"CPU" for x in [8,16,32]],
                     "batch_size":[str(x)+"MB" for x in range(64,128)]
                     #  "media": sorted_media,
                     #  "media1_size":["1GB","5GB","10GB"]
                 },
                 labels={"media": "Storage Media",
                         "workload_size": "Estimate Input Size",
                         "IOPS": "OPs/sec","cpu":"",
                         "batch_size":"Operation Batch Size"},
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
    fig.show()
#     fig_name = "../image/%s.pdf" % column_name
#     print("plotting fig %s finished" % fig_name)
#     fig.write_image(fig_name)
for paint_df in paint_dfs:
    for column in column_list:
        paint_for_one_column(column,paint_df)