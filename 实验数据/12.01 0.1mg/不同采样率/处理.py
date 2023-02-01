import os
from math import pi
from data_process.data_process import preprocess, lockIn
from matplotlib import pyplot as plt
import numpy as np

"""
periodNumber=1
10ms: 385.744; 13.741
20ms: 870.509; 41.300
50ms: 2101.091; 48.204
100ms: 4208.858; 246.690
200ms: 8321.757; 252.071
"""

"""
periodNumber=10
10ms: 29.898; 8.013
20ms: 842.717; 16.156
50ms: 1994.026; 58.335
100ms: 4005.919; 102.408
200ms: 7663.656; 227.467
"""

"""
periodNumber=20
10ms: 26.122; 5.054
20ms: 784.561; 24.228
50ms: 1514.241; 110.869
100ms: 3327.377; 277.185
200ms: 5984.854; 560.934
"""

"""
periodNumber=1
counts/sec
"""

folder = "./50ms"
amp_list = []
Fm = 1
periodNumber = 1
for file in os.listdir(folder):
    filepath = os.path.join(folder, file)
    timelist, counts = preprocess(filepath)
    # counts = counts / 0.01
    amp_list.append(pi / 2 * lockIn(counts, timelist, Fm, periodNumber))
    plt.figure()
    plt.plot(timelist, counts)

amp_list = np.array(amp_list)
print("amp mean: {:.3f}\namp std: {:.3f}".format(amp_list.mean(), amp_list.std()))
plt.show()
