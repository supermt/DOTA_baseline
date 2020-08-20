import re

def filelines_to_speed_list(filelines):
    result = []
    for line in filelines:
        m = re.search(r'[0-9]*(\.[0-9]*)*[K-M]iB/s',line)
        # print(m[0])
        speed = m[0]
        m = re.search(r'[0-9]*(\.[0-9]*)*',speed)
        unit = speed[len(m[0])]
        speed_num = float(m[0])
        if unit == 'K':
            speed_num /= 1000
        # result.append(m[0].replace("MiB/s",""))
        result.append(speed_num)
    return result

start_index=5
ssd_real_time_list = filelines_to_speed_list(open("ssd.txt").readlines())
hdd_real_time_list = filelines_to_speed_list(open("hdd.txt").readlines())
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(len(ssd_real_time_list))), y=ssd_real_time_list,line=dict(dash="dash"),name="Real time speed of SSD"))
fig.add_trace(go.Scatter(x=list(range(len(hdd_real_time_list))), y=hdd_real_time_list,name="Real time speed of HDD"))

fontsize = 16
fig.update_layout(
    autosize=False,
    width=600,
    height=300,
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
fig.update_yaxes(automargin=True,title="Throughput (MiB/s)")
fig.update_xaxes(showgrid=False,title="Elapsed time")
# fig.show()
fig_name = "image/realspeed.pdf" 
fig.write_image(fig_name)
# fig.show()

