import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from traversal import *

import traversal as tv
import string_utils
import plotly.express as px
from log_file_handler import get_data_list, open_file, get_compaction_score
from stdout_file_handler import get_iops_and_avg_latency

COLUMN_NUM = 4

dirs = []  # get_log_dirs("../")

column_labels = [8, 16, 32]
column_labels = [str(x)+"CPU" for x in column_labels]

row_labels = [64, 128]
row_labels = [str(x) + "MB" for x in row_labels]

mix_range_nums = [15, 30, 60]
mix_range_nums = ["mixed_size_"+str(x)+"_keyrange" for x in mix_range_nums]

line_modes = ["lines", "lines+markers", "markers"]

line_modes = dict(zip(mix_range_nums, line_modes))

medias = ["SATAHDD", "SATASSD", "NVMeSSD", "PM"]
medias = ["StorageMaterial."+x for x in medias]
colors = [
    "rgb(66,106,199)",
    "rgb(254,117,0)",
    "rgb(165,165,165)",
    "rgb(255,194,0)"
]

media_color_map = dict(zip(medias, colors))
prefix = "../"


fig = make_subplots(rows=len(row_labels), cols=len(column_labels))

for column_id in range(len(column_labels)):
    for row_id in range(len(row_labels)):
        for mix_range in line_modes:
            for media in media_color_map:
                dir_path = prefix + \
                    "%s/%s/%s/%s" % (mix_range, media, column_labels[column_id],
                                     row_labels[row_id])
                print(dir_path)
                stdfile, logfile = tv.get_log_and_std_files(dir_path)
                compaction_dict, l0_compaction_ids = get_compaction_score(
                    open_file(logfile))
                iops, avg_latency = get_iops_and_avg_latency(stdfile[0
                                                                     ])
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(compaction_dict.values()))),
                        y=list(compaction_dict.values()),
                        mode=line_modes[mix_range],
                        line=dict(color=media_color_map[media]),
                        name=media+mix_range
                    ),
                    row=row_id+1,
                    col=column_id+1
                )


fig.show()

# for dir in dirs:
#     stdfile, logfile = tv.get_log_and_std_files(dir)
#     compaction_list, l0_compaction_ids = get_compaction_score(
#         open_file(logfile))
#     iops, avg_latency = get_iops_and_avg_latency(stdfile[0])
