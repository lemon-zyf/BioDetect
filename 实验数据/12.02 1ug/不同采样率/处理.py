from data_process.data_process import preprocess, lockIn
from math import pi
import matplotlib.pyplot as plt
import os
import numpy as np

"""
periodNumber=1
10ms: 27.518; 9.261
20ms: 79.242; 13.687
50ms: 192.243; 73.566
100ms: 441.313; 82.363
200ms: 632.227; 223.095
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
