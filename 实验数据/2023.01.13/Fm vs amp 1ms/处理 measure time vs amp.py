import re
from math import pi
from matplotlib import pyplot as plt
import numpy as np
from data_process.data_process import movingAverageFilter, lockIn
from scipy import signal

if __name__ == '__main__':
    file = "./data/Fs=1000,Fm=1.txt"
    Fs, Fm = re.findall("\d+", file)
    Fs = int(Fs)
    Fm = int(Fm)
    span_width = int(1.5 * Fs / Fm)
    data = np.loadtxt(file)
    time_list = data[:, 0]
    counter_list = data[:, 1]

    filter_time_list, filter_counter_list = movingAverageFilter(counter_list, time_list, span_width)

    wn = 2 * Fm * 0.8 / Fs
    b, a = signal.butter(3, wn, "highpass")
    filted_data = signal.filtfilt(b, a, filter_counter_list)
    amp = lockIn(filted_data, filter_time_list, Fm)
    print(amp)
