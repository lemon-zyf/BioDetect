from data_process.data_process import preprocess, lockIn
from math import pi
import matplotlib.pyplot as plt
import os
import numpy as np

"""
periodNumber=1
10ms: 67.491; 15.170
20ms: 155.008; 14.935
50ms: 359.503; 104.300
100ms: 759.080; 229.479
200ms: 1219.067; 236.450
"""

folder = "./200ms"
Fm = 1
periodNumber = 1
amp_list = []
for file in os.listdir(folder):
    filepath = os.path.join(folder, file)
    timelist, counts = preprocess(filepath)
    plt.figure()
    plt.plot(timelist, counts)
    amp_list.append(pi / 2 * lockIn(counts, timelist, Fm, periodNumber))

amp_list = np.array(amp_list)
print("amp mean: {:.3f}\namp std: {:.3f}".format(amp_list.mean(), amp_list.std()))
plt.show()
