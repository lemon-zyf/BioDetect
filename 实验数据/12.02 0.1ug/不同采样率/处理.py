from data_process.data_process import preprocess, lockIn
from math import pi
import matplotlib.pyplot as plt
import os
import numpy as np

"""
periodNumber=1
10ms: 46.616; 11.595
20ms: 103.603; 20.583
50ms: 228.042; 48.752
100ms: 507.345; 172.483
200ms: 1031.286; 405.351
"""

folder = "./50ms"
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