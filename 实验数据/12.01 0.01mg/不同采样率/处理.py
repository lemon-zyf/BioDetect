from data_process.data_process import preprocess, lockIn
import matplotlib.pyplot as plt
import os
from math import pi
import numpy as np

"""
periodNumber=1
10ms: 67.596;20.938
20ms: 190.670;42.604
50ms: 442.867;66.634
100ms: 844.383;204.593
200ms: 1855.881;438.398
"""


folder = "./200ms"
amp_list = []
Fm = 1
periodNumber = 1
for file in os.listdir(folder):
    filepath = os.path.join(folder, file)
    timelist, counts = preprocess(filepath)
    plt.figure()
    plt.plot(timelist, counts)
    amp_list.append(pi / 2 * lockIn(counts, timelist, Fm, periodNumber))

amp_list = np.array(amp_list)
print("amp mean: {:.3f}\namp std: {:.3f}".format(amp_list.mean(), amp_list.std()))
# plt.show()
