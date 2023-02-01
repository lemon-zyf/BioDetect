from matplotlib import pyplot as plt
import numpy as np
from data_process.data_process import movingAverageFilter

filepath = "0.1mg/50.txt"
data = np.loadtxt(filepath)

timelist = data[:, 0]
counter_data = data[:, 1]

new_tlist, new_counter_data = movingAverageFilter(counter_data, timelist, 75)

plt.plot(new_tlist, new_counter_data)
plt.show()
