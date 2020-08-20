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

# data = table[table["CPU numbers"] == 8]
data = table

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
    for i in CPU_options:
        data = project_material[project_material["CPU numbers"] == i]    
        Y = data["Operation Unit Size"]
        X = data["Material"]
        Z = data["Throughput (kOps/sec)"]

        dash_or_not = "solid"
        if material == 1:
            dash_or_not = "dot"
        elif material == 3:
            dash_or_not = "dash"
        elif material == 5:
            dash_or_not = "solid"
        

        fig.add_trace(go.Scatter3d(
            #data
            x=X,y = Y,z = Z,mode="lines+markers", text=Z,textposition="top center",
            # line
            line = dict(width=1),
            marker=dict(symbol=material_symbols[material], size=5),
            legendgroup=str(material_symbols[material]),
            name = material_dict[material] + "/" + str(i) + "CPUs",
            
            )
        )


# fig.update_layout(showlegend=False)
dict(
showarrow=True,
x="5",
y="6",
z=200,
text="Performance of PM hardly changed",
)
fig.update_layout(scene = dict(
                    xaxis = dict(title='',ticktext= ['SATASSD','NVMeSSD','PM'],tickvals= [1,3,5],backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    yaxis = dict(title='Operation Unit Size (MB)',backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    zaxis = dict(title='Throughput (kOps/sec)',backgroundcolor="white",gridcolor='rgb(209,209,209)'),
                    camera = dict(
                        eye = dict(x=1.7,y=1.9,z=0.5)
                    ),
                    annotations= [
                      ]
                    
                  ),
                  autosize=False,
                  width=750,
                  height=650
                )

fig.update_xaxes(automargin=True)
fig.update_yaxes(automargin=True)
# fig.update_zaxes(automargin=True)

fig.show()
fig.write_image("fixed_cpu.pdf")