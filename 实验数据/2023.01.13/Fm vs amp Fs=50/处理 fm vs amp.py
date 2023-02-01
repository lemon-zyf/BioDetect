import os.path
import re
from matplotlib import pyplot as plt
import numpy as np
from math import pi
from algorithm import high_pass_filter

from data_process.data_process import movingAverageFilter, lockIn


def draw(x, y, save_path, xlim=None):
    fig = plt.figure()
    plt.plot(x, y)
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    if xlim:
        plt.xlim(xlim)
    plt.savefig(save_path, dpi=600, bbox_inches='tight')
    plt.close(fig)


def process_single_file(file):
    fs = 50
    data = np.loadtxt(file)
    file_name = os.path.basename(file).split('.txt')[0]
    time_list = data[:, 0]
    counter_list = data[:, 1]
    fm, et = re.findall("\d+", file_name)
    fm = int(fm)
    et = int(et)

    filter_time_list, filter_counter_list = movingAverageFilter(counter_list, time_list, int(1.5 * fs / fm))

    high_pass_time_counter_list = high_pass_filter.high_pass_filter(filter_counter_list, fm * 0.8, fs, 3)

    amp = pi / 2 * lockIn(filter_counter_list, high_pass_time_counter_list, fm)

    if et not in fm_vs_amp.keys():
        fm_vs_amp[et] = ([], [])
    fm_vs_amp[et][0].append(fm)
    fm_vs_amp[et][1].append(amp)

    xlim = [0, 10 / fm]
    draw(time_list, counter_list, xlim=xlim, save_path="./figure/origin data/{}.png".format(file_name))
    draw(filter_time_list, filter_counter_list, "./figure/after filter/{}.png".format(file_name), xlim)
    draw(filter_time_list, high_pass_time_counter_list, "./figure/after high pass/{}.png".format(file_name), xlim)


if __name__ == '__main__':
    fm_vs_amp = dict()

    for file in os.listdir("./data"):
        process_single_file(os.path.join("./data", file))
    fig = plt.figure()
    for et in sorted(fm_vs_amp.keys()):
        fm_list = fm_vs_amp[et][0]
        amp_list = fm_vs_amp[et][1]
        plt.plot(sorted(fm_list), sorted(amp_list, key=lambda val: fm_list[amp_list.index(val)]), marker='.')
    plt.show()
