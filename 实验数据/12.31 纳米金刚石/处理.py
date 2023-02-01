import matplotlib.pyplot as plt
import numpy as np
from data_process.data_process import movingAverageFilter, lockIn
import os
from math import pi


def process_single_file(file, Fm, period_number):
    data = np.loadtxt(file)
    time_list = data[:, 0]
    counter_data = data[:, 1]
    amp = pi / 2 * lockIn(counter_data, time_list, Fm, period_number)
    print("file:{}\t\tFm:{}\t amp: {:.3f}".format(file, Fm, amp))
    fig = plt.figure()
    plt.plot(time_list, counter_data)
    plt.title("{},amp={:.3f}".format(os.path.basename(file).split('.')[0], amp))
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    plt.savefig("figure/{}.png".format(os.path.basename(file).split(".")[0]), bbox_inches='tight', dpi=600)
    plt.close(fig)
    # del fig


folder = "./0.1mg"
period_number = 20
for file in os.listdir(folder):
    Fm = int(file.split(".txt")[0].split("Fm=")[1])
    process_single_file(os.path.join(folder, file), Fm, period_number)
