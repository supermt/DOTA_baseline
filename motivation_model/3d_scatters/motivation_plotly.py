import plotly.graph_objects as go

import pandas as pd

table = pd.read_csv("data.csv")

# data = all_data[all_data.Material == "SATA SSD"]
size_options = list(set(table["Operation Unit Size"]))
CPU_options = list(set(table["CPU numbers"]))
Material_options = list(set(table["Material"]))

material_symbols = ['empty', 'square', 'square-open',
                    'circle', 'circle-open', 'diamond', 'diamond-open']
material_dict = ['empty', 'SATA SSD', 'SATA SSD tuned',
                 'NVMe SSD', 'NVMe SSD tuned', 'PMM', 'PMM tuned']

size_color = {16: "rgb(66,106,199)", 32: "rgb(254,117,0)",
              64: "rgb(165,165,165)", 128: "rgb(255,194,0)"}


CPU_options.sort()
size_options.sort()

# print(size_options,CPU_options,Material_options)
fig = go.Figure()

table = table[table["Material"].isin([3,4,5,6])]

for material in Material_options:
    project_material = table[table.Material == material]
    for i in range(len(size_options)):
        data = project_material[project_material["Operation Unit Size"]
                                == size_options[i]]
        Y = data["CPU numbers"]
        X = data["Material"]
        Z = data["Throughput (kOps/sec)"]

        dash_or_not = "solid"
        if material % 2 == 0:
            dash_or_not = "dot"

        fig.add_trace(go.Scatter3d(
            # data
            x=X, y=Y, z=Z, mode="lines+markers",
            # line
            line=dict(color=size_color[size_options[i]],
                      dash=dash_or_not, width=4),
            marker=dict(symbol=material_symbols[material], size=5),
            legendgroup=str(material_symbols[material]),
            name=material_dict[material]+"/"+str(size_options[i]) + "MB"
        )
        )

fig.update_layout(scene=dict(
    xaxis=dict(title='Material', ticktext=['SATASSD', 'NVMeSSD', 'PM'], tickvals=[
               1.5, 3.5, 5.5], backgroundcolor="white", gridcolor='rgb(209,209,209)'),
    yaxis=dict(title='CPU numbers', backgroundcolor="white",
               gridcolor='rgb(209,209,209)'),
    zaxis=dict(title='Throughput (kOps/sec)',
               backgroundcolor="white", gridcolor='rgb(209,209,209)'),
    camera=dict(
        eye=dict(x=1.75, y=1.25, z=0.8)
    ),
),
    autosize=False,
    width=900,
    height=600,
    font_size=16
)

fig.update_xaxes(automargin=True)
fig.update_yaxes(automargin=True)
# fig.update_zaxes(automargin=True)
fig.show()
fig.write_image("allset.pdf")