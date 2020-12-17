import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import string_utils
import traversal as tv
from log_file_handler import get_compaction_score, get_data_list, open_file
from stdout_file_handler import get_iops_and_avg_latency
from traversal import *

COLUMN_NUM=3

dirs=[]

column_labels = [8, 16, 32]
column_labels = [str(x)+"CPU" for x in column_labels]

row_labels = [64, 128]
row_labels = [str(x) + "MB" for x in row_labels]