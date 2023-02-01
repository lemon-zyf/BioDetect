from data_process.data_process import preprocess, lockIn
from math import pi
import matplotlib.pyplot as plt
import os
import numpy as np

"""
periodNumber=1
10ms: 51.333; 19.036
20ms: 101.490; 15.701
50ms: 208.012; 67.696
100ms: 514.467; 90.623
200ms: 980.806; 279.179
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
# plt.show()
