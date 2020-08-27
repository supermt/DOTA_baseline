
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

handles = []
colors = ['blue', 'red','black','green']
markers = ['1','2','o','v']



MemSetNo = 5
MemSetBase = 8
MemSetGap = 2
Memory_budgets = np.logspace(MemSetBase, MemSetBase + MemSetNo - 1,MemSetNo, base=MemSetGap)

CPUSetNo = 3
CPUSetBase = 0
CPUSetGap = 2

CPU_cores = np.logspace(CPUSetBase, CPUSetBase + CPUSetNo - 1, CPUSetNo, base=CPUSetGap)


legend_list=['SATA HDD', 'SATA SSD','NVMe SSD', 'OptaneDC PM']
fig,axs = plt.subplots(len(CPU_cores),1,sharey=True)

stamps = [10,15,25,30]
for unit,CPU_Core,stamp in zip(axs,CPU_cores,stamps):
    unit.set_ylabel("Throughput")
    unit.set_title("CPU: " + str(int(CPU_Core)))

    for i in range(0,len(legend_list),1):
        ratio = randrange(len(Memory_budgets),0.8,1.5)
        ratio.sort()
        ratio = ratio * stamp
        unit.plot(Memory_budgets,ratio,label=legend_list[i])
        unit.legend()

plt.show()

