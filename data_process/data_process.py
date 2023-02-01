import fnmatch
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import savemat
from algorithm.lockIn import lockIn, movingAverageFilter
from matplotlib import pyplot as plt


def preprocess(file: str):
    """
    Return time array and counts array
    :param file:
    :return:
    """
    counts = []
    sample_time = 0
    if os.path.exists(file):
        with open(file, "r") as fp:
            data = fp.readlines()
        first_element = data.pop(0)
        sample_time = int(first_element.split("/")[1].split("ms")[0]) / 1000
        counts.append(int(first_element.split("/")[0]))
        for c in data:
            counts.append(int(c.split("/")[0]))
        counts=np.array(counts)
    else:
        print("can not find file")
    tlist = np.arange(0, sample_time * (len(counts)), sample_time)
    if len(tlist) - len(counts) == 1:
        print(len(tlist), len(counts))
        tlist = tlist[:-1]
    return tlist, np.array(counts)


def process(tlist: np.ndarray, inputSignal: np.ndarray, windowWidth: int, periodNumber: int):
    """
    process input signal with moving average filter, return fig and amp
    :param tlist:
    :param inputSignal:
    :param windowWidth:
    :param periodNumber:
    :return: float and plt.Figure
    """
    filtered_tlist, filtered_counts = movingAverageFilter(inputSignal, tlist, windowWidth)
    amp = lockIn(filtered_counts, filtered_tlist, Fm=1, periodNumber=periodNumber)
    fig, axeses = plt.subplots(2, 1, sharex='all', sharey='all')
    axeses[0].plot(tlist, inputSignal, lw=1, marker='.', label='Original Data')
    axeses[0].legend()
    axeses[1].plot(filtered_tlist, filtered_counts, lw=1, marker='.', label="Filtered Data")
    axeses[1].legend()
    plt.xlim(0, filtered_tlist[filtered_tlist < 10 / 1][-1])
    plt.xlabel("Time (s)")
    fig.supylabel("Counts")
    # plt.show()
    return amp, fig


def process_without_filter(tlist: np.ndarray, inputSignal: np.ndarray, periodNumber):
    """
    process data without moving average filter, return amp and figure
    :param tlist:
    :param inputSignal:
    :param periodNumber:
    :return: float and plt.Figure
    """
    fig = plt.figure()
    amp = lockIn(inputSignal, tlist, Fm=1, periodNumber=periodNumber)
    plt.plot(tlist, inputSignal, label="amp={:.3f}".format(amp), lw=1, marker='.')
    plt.legend()
    plt.xlim(0, tlist[tlist < 10 / 1][-1])
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    return amp, fig
