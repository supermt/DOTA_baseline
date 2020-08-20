import plotly.graph_objects as go

import pandas as pd

table = pd.read_csv("data.csv")

# data = all_data[all_data.Material == "SATA SSD"]
size_options = list(set(table["Operation Unit Size"]))
CPU_options = list(set(table["CPU numbers"]))
Material_options = list(set(table["Material"]))

material_symbols = ['empty','square','square-open','circle','circle-open','diamond','diamond-open']
material_dict = ['empty','SATA SSD','SATA SSD tuned','NVMe SSD', 'NVMe SSD tuned','PMM','PMM tuned']

size_color = {16:"rgb(66,106,199)",32:"rgb(254,117,0)",64:"rgb(165,165,165)",128:"rgb(255,194,0)"}

data = table[table["Operation Unit Size"] == 64]

data = data[data.Material.isin([1,3,5])]

table = data

CPU_options.sort()
size_options.sort()

fig = go.Figure()

# for cpu_number in CPU_options:
#     line = data[data["CPU numbers"] == cpu_number]
#     X = line["Material"]
#     Y = line["CPU numbers"]
#     Z = line["Throughput (kOps/sec)"]
#     fig.add_trace(go.Scatter3d(
#         x=X,y = Y,z = Z,mode="lines+markers"
#         )
#     )

for material in Material_options:
    project_material = table[table.Material == material]
    for i in range(len(size_options)):
        data = project_material[project_material["Operation Unit Size"] == size_options[i]]    
        Y = data["CPU numbers"]
        X = data["Material"]
        Z = data["Throughput (kOps/sec)"]

        dash_or_not = "solid"
        if material % 2 == 0:
            dash_or_not = "dot"

        fig.add_trace(go.Scatter3d(
            #data
            x=X,y = Y,z = Z,mode="lines+markers", text=Z,textposition="top center",
            # line
            line = dict( width=6),
            legendgroup=str(material_symbols[material]),
            name = "Unit Size:"+str(size_options[i]) +"MB"
            )
        )
fig.update_layout(showlegend=False)


annotation_array = [dict(
    showarrow=False,
    x="PM",
    y="6",
    z=200,
    text="Performance of PM hardly changed",
    xanchor="left"
    )
]

fig.update_layout(scene = dict(
                    xaxis = dict(title='Material',ticktext= ['SATASSD','NVMeSSD','PM'],tickvals= [1,3,5],backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    yaxis = dict(title='CPU numbers',backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    zaxis = dict(title='Throughput (kOps/sec)',backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    camera = dict(
                        eye = dict(x=2.1,y=1.9,z=0.7)
                    ),
                    annotations= [
                        dict(
                            showarrow=True,
                            x="5",
                            y="6",
                            z=200,
                            text="Performance of PM hardly changed",
                            ),
                        dict(
                            showarrow=True,
                            x="3",
                            y="3",
                            z=340,
                            text="Rapid Performance Growth",
                        ),
                        dict(
                            showarrow=True,
                            x="3",
                            y="6",
                            z=375,
                            text="Slowly Performance Growth",
                        ),
                        dict(
                            showarrow=True,
                            x="1",
                            y="5",
                            z=140,
                            text="Performance of SATA SSD keeps dropping",
                        )
                      ]
                    
                  ),
                  autosize=False,
                  width=600,
                  height=600,
                  margin=dict(l=0,
                                r=0,
                                b=0,
                                t=0,
                                pad=0)
                )



fig.show()
fig.write_image("hardware_concern.pdf")