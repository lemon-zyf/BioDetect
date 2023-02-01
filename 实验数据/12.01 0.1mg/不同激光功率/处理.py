from data_process.data_process import preprocess, lockIn
from matplotlib import pyplot as plt
from math import pi
import os
import numpy as np

"""
0.95: 2042.174; 84.666; 120mW
0.9: 2040.412; 92.837; 110mW
0.85: 1949.001; 125.648; 92mW
0.8: 1630.493; 94.146; 71mW
0.75: 1305.116; 68.416; 47mW
"""

folder = "./0.85"
amp_list = []
Fm = 1
periodNumber = 1
for files in os.listdir(folder):
    filepath = os.path.join(folder, files)
    timelist, counts = preprocess(filepath)
    amp_list.append(pi / 2 * lockIn(counts, timelist, Fm, periodNumber))

amp_list = np.array(amp_list)
print("amp mean: {:.3f}\namp std: {:.3f}".format(amp_list.mean(), amp_list.std()))
