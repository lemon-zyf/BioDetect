from data_process.data_process import preprocess, lockIn, movingAverageFilter
from math import pi
import matplotlib.pyplot as plt
import numpy as np
import os

Fm = 0.05
folders = ('0.1mg', '0.01mg', '1ug', '0mg')
files = ('10', '20', '50', '100', '200')
filter_window = 0.5 * 1 / (np.array([10, 20, 50, 100, 200]) / 1000)
fig, axes_array = plt.subplots(len(folders), len(files), sharey='none', sharex='all')
for row, folder in enumerate(folders):
    for col, file in enumerate(files):
        ax: plt.Axes = axes_array[row, col]
        filepath = os.path.join(folder, "".join([file, ".DAT"]))
        timelist, counts = preprocess(filepath)
        filter_timelist, filter_counts = movingAverageFilter(counts, timelist, round(filter_window[col]))
        ax.plot(filter_timelist, filter_counts, lw=0.5)
        ax.yaxis.set_ticklabels([])
        ax.yaxis.set_ticks([])

for i in range(len(folders)):
    axes_array[i, 0].set_ylabel(folders[i], rotation=0, labelpad=20)

for i in range(len(files)):
    axes_array[0, i].set_title("".join([files[i], "ms"]))
plt.xlim(left=0, right=5 / Fm)
fig.supxlabel("Time (s)")
# fig.supylabel("Counts")
plt.savefig("figure/with_filter.png", bbox_inches='tight', dpi=600)
# plt.show()
