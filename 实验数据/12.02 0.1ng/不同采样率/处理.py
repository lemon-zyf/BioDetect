from data_process.data_process import preprocess, lockIn
from math import pi
import matplotlib.pyplot as plt
import os
import numpy as np

"""
periodNumber=1
10ms: 55.411; 12.598
20ms: 110.255; 26.311
50ms: 220.340; 78.953
100ms: 326.569; 138.667
200ms: 1143.440; 257.516
"""

folder = "./10ms"
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
