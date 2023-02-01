import os.path
import re
from dataclasses import dataclass
from matplotlib import pyplot as plt
import numpy as np
from data_process.data_process import movingAverageFilter, lockIn
from math import pi

"""
金刚石浓度：1mg/ml
exposure time: 1ms
Fs: 1k,
Fm: 500
"""


class CounterData:
    def __init__(self):
        self.Fm = []
        self.amp = []


def draw(x, y, xlim, save_file=""):
    fig = plt.figure()
    plt.plot(x, y)
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    plt.xlim(xlim)
    if save_file:
        plt.savefig(save_file, dpi=600, bbox_inches='tight')
    plt.close(fig)


def process_single_file(file_path: str):
    data = np.loadtxt(file_path)
    file_name = os.path.basename(os.path.abspath(file_path)).split(".txt")[0]
    Fs, Fm = re.findall("\d+", file_name)
    Fs = int(Fs)
    Fm = int(Fm)

    filter_span = int(1.5 * Fs / Fm)
    xlim = [0, 10 / Fm]
    time_list = data[:, 0]
    counter_list = data[:, 1]
    draw(time_list, counter_list, xlim, os.path.join("./figure/origin data", file_name))
    filter_time_list, filter_counter_list = movingAverageFilter(counter_list, time_list, filter_span)
    draw(filter_time_list, filter_counter_list, xlim, os.path.join("./figure/after filter", file_name))
    amp = pi / 2 * lockIn(filter_counter_list, filter_time_list, Fm)
    if Fs not in Fm_vs_amp.keys():
        Fm_vs_amp[Fs] = CounterData()
    Fm_vs_amp[Fs].Fm.append(Fm)
    Fm_vs_amp[Fs].amp.append(amp)
    # print(len(Fm_vs_amp[Fs].Fm), len(Fm_vs_amp[Fs].amp), Fs, Fm)


if __name__ == '__main__':
    Fm_vs_amp = dict()
    for files in os.listdir("./data"):
        process_single_file(os.path.join("./data", files))

    fig = plt.figure()
    for Fs, counter_data in Fm_vs_amp.items():
        plt.plot(sorted(counter_data.Fm),
                 sorted(counter_data.amp, key=lambda val: counter_data.Fm[counter_data.amp.index(val)]), label=Fs,
                 marker='.')
    plt.legend(title="Fs")
    plt.xlabel("Fm (Hz)")
    plt.ylabel("Amp")
    plt.show()
