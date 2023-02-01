from matplotlib import pyplot as plt
import numpy as np
from data_process.data_process import movingAverageFilter

filepath = "Fm=0.1,50ms.txt"
file2 = "Fm=0.1,50ms,mw=1.txt"
data = np.loadtxt(filepath)
data2 = np.loadtxt(file2)

timelist = data[:, 0]
counter_data = data[:, 1]

timelist2 = data2[:, 0]
counter_data2 = data2[:, 1]

new_tlist, new_counter_data = movingAverageFilter(counter_data, timelist, 25)
new_tlist2, new_counter_data2 = movingAverageFilter(counter_data2, timelist2, 25)
plt.subplot(2, 1, 1)
plt.plot(new_tlist, new_counter_data)
plt.subplot(2, 1, 2)
plt.plot(new_tlist2, new_counter_data2)
plt.show()
