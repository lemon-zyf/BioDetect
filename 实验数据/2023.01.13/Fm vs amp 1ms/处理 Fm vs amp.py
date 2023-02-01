import concurrent.futures
import os.path
import re
import threading
from dataclasses import dataclass
import subprocess
import multiprocessing
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
    print(file_path)
    global data_mutex
    data = np.loadtxt(file_path)
    file_name = os.path.basename(os.path.abspath(file_path)).split(".txt")[0]
    Fs, Fm = re.findall("\d+", file_name)
    Fs = int(Fs)
    Fm = int(Fm)

    filter_span = int(1.5 * Fs / Fm)
    xlim = [0, 10 / Fm]
    time_list = data[:, 0]
    counter_list = data[:, 1]
    draw_process1 = multiprocessing.Process(target=draw, args=(
        time_list, counter_list, xlim, os.path.join("./figure/origin data", file_name)))
    draw_process1.start()
    # draw(time_list, counter_list, xlim, os.path.join("./figure/origin data", file_name))
    filter_time_list, filter_counter_list = movingAverageFilter(counter_list, time_list, filter_span)
    draw_process2 = multiprocessing.Process(target=draw, args=(
        filter_time_list, filter_counter_list, xlim, os.path.join("./figure/after filter", file_name)))
    draw_process2.start()
    # draw(filter_time_list, filter_counter_list, xlim, os.path.join("./figure/after filter", file_name))
    amp = pi / 2 * lockIn(filter_counter_list, filter_time_list, Fm)
    mutex.acquire()
    if Fs not in Fm_vs_amp.keys():
        Fm_vs_amp[Fs] = CounterData()
    Fm_vs_amp[Fs].Fm.append(Fm)
    Fm_vs_amp[Fs].amp.append(amp)
    mutex.release()
    draw_process1.join()
    draw_process2.join()
    # print(len(Fm_vs_amp[Fs].Fm), len(Fm_vs_amp[Fs].amp), Fs, Fm)


if __name__ == '__main__':
    data_mutex = threading.Lock()
    Fm_vs_amp = dict()
    task_list = []
    thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=6)
    for files in os.listdir("./data"):
        task_list.append(thread_pool.submit(process_single_file, os.path.join("./data", files)))
    done, not_done = concurrent.futures.wait(task_list, return_when=concurrent.futures.ALL_COMPLETED)
    print("all done")
    fig = plt.figure()
    Fs_list = sorted(Fm_vs_amp.keys(), reverse=True)
    for Fs in Fs_list:
        counter_data = Fm_vs_amp[Fs]
        plt.plot(sorted(counter_data.Fm),
                 sorted(counter_data.amp, key=lambda val: counter_data.Fm[counter_data.amp.index(val)]), label=Fs,
                 marker='.')
    plt.legend(title="Fs")
    plt.xlabel("Fm (Hz)")
    plt.ylabel("Amp")
    plt.savefig("Fm vs Amp.png", dpi=600, bbox_inches='tight')
    plt.show()
