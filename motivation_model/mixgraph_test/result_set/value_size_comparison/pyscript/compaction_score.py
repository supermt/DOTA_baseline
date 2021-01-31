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

line_modes = ["lines", "lines", "lines"]

line_modes = dict(zip(mix_range_nums, line_modes))

medias = ["SATAHDD", "SATASSD", "NVMeSSD", "PM"]
medias = ["StorageMaterial."+x for x in medias]
colors = [
    "rgb(66,106,199)",
    "rgb(254,117,0)",
    "rgb(165,165,165)",
    "rgb(255,194,0)"
]
fontsize = 20
media_color_map = dict(zip(medias, colors))
prefix = "../"

layout = go.Layout(yaxis=dict(range=[0, 16]))
for mix_range in line_modes:
    # differnt figures
    subplot_titles = []
    for row in row_labels:
        for column in column_labels:
            subplot_titles.append(row + " " + column)

    fig = make_subplots(rows=len(row_labels), cols=len(
        column_labels), shared_xaxes=True, shared_yaxes=True, subplot_titles=subplot_titles)

    for column_id in range(len(column_labels)):
        for row_id in range(len(row_labels)):
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
                values = list(compaction_dict.values())
                values.sort()
                fig.add_trace(
                    go.Scatter(
                        x=list(range(len(values))),
                        y=values,
                        mode=line_modes[mix_range],
                        line=dict(color=media_color_map[media]),
                        name=media,
                        showlegend=(row_id == 0 and column_id == 0)),
                    row=row_id+1,
                    col=column_id+1
                )
                fig.update_yaxes(title_text="compaction score", range=[
                                 0, 18], row=row_id+1, col=column_id+1)

    fig.update_layout(
        title={
            'text': "compaction scores in range num %s cases" % mix_range.split("_")[2],
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'}
    )
    fig.update_layout(
        autosize=False,
        width=1600,
        height=900,
        font=dict(size=fontsize),
        # plot_bgcolor='white',
    )
    # fig.update_layout(legend=dict(
    #     orientation="h",
    #     yanchor="bottom",
    #     y=0,
    #     xanchor="left",
    #     x=0.25,
    #     font=dict(size=fontsize+4)
    # ))

    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(automargin=True)
    fig.update_xaxes(showgrid=False)
    # fig.show()
    fig_name = "./image/compaction_score%s.pdf" % mix_range
    png_fig_name = "./image/compaction_score%s.png" % mix_range
    print("plotting fig %s finished" % fig_name)
    fig.write_image(fig_name)
    fig.write_image(png_fig_name)

# for dir in dirs:
#     stdfile, logfile = tv.get_log_and_std_files(dir)
#     compaction_list, l0_compaction_ids = get_compaction_score(
#         open_file(logfile))
#     iops, avg_latency = get_iops_and_avg_latency(stdfile[0])
