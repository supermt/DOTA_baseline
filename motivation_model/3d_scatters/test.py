from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt



fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

material =[1,2,3]
material_label = ['SATA','NVMe','PMM']

CPU_numbers = [2,4,8]
table_sizes = [16,32,64,128]
throughput = []

ax.set_xticks(material)
ax.set_xticklabels(material_label)

ax.set_yticks(CPU_numbers)

data_points = [
(1,2,16,112766),(1,2,32,160806),(1,2,64,195766),(1,2,128,267181),(1,4,16,90149),(1,4,32,134096),(1,4,64,145165),(1,4,128,203186),(1,8,16,66760),(1,8,32,93234),(1,8,64,109228),(1,8,128,148402),
(2,2,16,335898),(2,2,32,331184),(2,2,64,312457),(2,2,128,308432),(2,4,16,403296),(2,4,32,389617),(2,4,64,371045),(2,4,128,344215),(2,8,16,413797),(2,8,32,393490),(2,8,64,378156),(2,8,128,342011),
(3,2,16,191920),(3,2,32,195239),(3,2,64,194287),(3,2,128,188181),(3,4,16,204116),(3,4,32,199442),(3,4,64,196285),(3,4,128,192417),(3,8,16,200460),(3,8,32,203867),(3,8,64,195460),(3,8,128,191389),
]


shape_material = ['o','*','v']
color_size = ['r','g','b','y']

for color in range(4):
    table_size = table_sizes[color]

    X = {1:[],2:[],3:[]}
    Y = {2:[],4:[],8:[]}
    Z = {1:[],2:[],3:[]}

    for point in data_points:
        # 16 MB only
        if point[2] == table_size:
            print(point)
            X[point[0]].append(point[0]) 
            Y[point[1]].append(point[1])
            Z[point[0]].append(point[3]/1000)

    for i in range(1,4):
        ax.plot(X[i],[2,4,8],Z[i],c=color_size[color],marker=shape_material[i-1],label=str(table_sizes[color])+"MB / " + str(material_label[i-1]))

PM_tuned=[
    (3,2,16,324180),(3,2,32,326639),(3,2,64,321286),(3,2,128,314376),(3,4,16,399785),(3,4,32,381924),(3,4,64,367792),(3,4,128,337491),(3,8,16,406333),(3,8,32,387040),(3,8,64,372657),(3,8,128,352611),
]
NVMe_tuned = [
    (2,2,16,361160),(2,2,32,354021),(2,2,64,343760),(2,2,128,331772),(2,4,16,415079),(2,4,32,390275),(2,4,64,378710),(2,4,128,347905),(2,8,16,412403),(2,8,32,402515),(2,8,64,376904),(2,8,128,350244),
]

for color in range(4):
    table_size = table_sizes[color]

    X = {1:[],2:[],3:[]}
    Y = {2:[],4:[],8:[]}
    Z = {1:[],2:[],3:[]}

    for point in PM_tuned:
        # 16 MB only
        if point[2] == table_size:
            print(point)
            X[point[0]].append(point[0]) 
            Y[point[1]].append(point[1])
            Z[point[0]].append(point[3]/1000)

    for i in [3]:
        ax.plot(X[i],[2,4,8],Z[i],c=color_size[color],marker=shape_material[i-1],label=str(table_sizes[color])+"MB / " + "PMM_tuned")


ax.set_xlabel('Media Type')
ax.set_ylabel('CPU numbers')
ax.set_zlabel('Throughput (kOps/sec)')

plt.legend(title='Memtable & SSTable Size / Storage Media',loc='upper center',ncol=4)

plt.show()

# fig.savefig("result.pdf",bbox='tight')