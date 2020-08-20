'''
==============
3D scatterplot
==============

Demonstration of a basic scatterplot in 3D.
'''

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import random

# Fixing random state for reproducibility
np.random.seed(19680801)


def randrange(n, vmin, vmax):
    '''
    Helper function to make an array of random numbers having shape (n, )
    with each number distributed Uniform(vmin, vmax).
    '''
    return (vmax - vmin)*np.random.rand(n) + vmin

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

handles = []
colors = ['blue', 'red','black','green']
markers = ['1','2','o','v']

MemSetNo = 5
MemSetBase = 8
MemSetGap = 2
Memory_budgets = np.logspace(MemSetBase, MemSetBase + MemSetNo - 1,MemSetNo, base=MemSetGap)

CPUSetNo = 6
CPUSetBase = 0
CPUSetGap = 2

CPU_cores = np.logspace(CPUSetBase, CPUSetBase + CPUSetNo - 1, CPUSetNo, base=CPUSetGap)


legend_list=['SATA HDD', 'SATA SSD','NVMe SSD', 'OptaneDC PM']
Sets=[]
scatter_proxys = []

# read/generate the data
for i in range(0,len(legend_list),1):
    X = []
    Y = []
    Z = []
    for CPU_core in CPU_cores:
        stamps = randrange(len(CPU_cores),10 + i * 20,18 + i * 20)
        stamps.sort()
        # stamps = [10.3, 13.4, 15.6, 17.8, 17.6]
        ratio = randrange(len(Memory_budgets),0.8,1.5)

        for Mem_size,rate,stamp in zip(Memory_budgets,ratio,stamps):
            X.append(CPU_core)
            Y.append(Mem_size)
            Z.append(stamp * rate)
    MaterialThroughput = [X,Y,Z]
    Sets.append(MaterialThroughput)


# plot the dots
for color,dot_marker,Set in zip(colors,markers,Sets):
    scatter = ax.scatter(Set[0], Set[1], Set[2], c = color, marker = dot_marker,s=100)
    scatter_proxy = matplotlib.lines.Line2D([0],[0],linestyle="none", c=color, marker = dot_marker)
    scatter_proxys.append(scatter_proxy)

# add legend
ax.legend(scatter_proxys,legend_list , numpoints = 1)


ax.set_xlabel('CPU cores')
ax.set_ylabel('Memory Budget (MB)')
ax.set_zlabel('Throughput (ops per sec)')

plt.show()
