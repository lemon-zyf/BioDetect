import concurrent.futures
import copy
import multiprocessing
import os.path
import queue
import re
import sys
import logging
import threading
import time
from math import pi
import typing
import matplotlib.pyplot as plt
import numpy as np
from data_process.data_process import lockIn, movingAverageFilter
from util.Mixin import set_logger

DATA_PATH = "./data"
SPAN_WIDTH_FACTOR = 0.5
INTEGRAL_PERIOD = None
DRAW_FLAG = False
SAVE_PATH = "./figure/after filter/{}/".format(SPAN_WIDTH_FACTOR)
XLIM_FACTOR = 10
logger = set_logger()


def load_file(file_queue, data_queue):
    while True:
        if file_queue.empty():
            break
        file_name = file_queue.get()
        data = np.loadtxt(file_name)
        fs, fm = re.findall("\d+", file_name)
        data_queue.put({
            "name": os.path.basename(file_name).split(".txt")[0],
            "fs": int(fs),
            "fm": int(fm),
            "time list": data[:, 0],
            "counter data": data[:, 1]
        })


def moving_average_filter(data: typing.Dict, span_width_factor: float):
    fs = data['fs']
    fm = data['fm']
    time_list = data['time list']
    counter_list = data['counter data']
    span_width = int(span_width_factor * fs / fm)
    out_time_list, out_counter_list = movingAverageFilter(counter_list, time_list, span_width)
    data['time list'] = out_time_list
    data['counter data'] = out_counter_list


def get_lock_in_amp(data, result_queue, integral_period: typing.Optional[int] = None):
    logger.info(data['name'])
    fm = data['fm']
    time_list = data['time list']
    counter_list = data['counter data']
    amp = pi / 2 * lockIn(counter_list, time_list, fm, integral_period)
    # logger.info("name: {}, amp: {:.3f}".format(data['name'], amp))
    result_queue.put({
        "name": data['name'],
        "fs": data['fs'],
        "fm": data['fm'],
        "time list": data['time list'],
        "counter data": data['counter data'],
        "amp": amp,
        "measure time": integral_period / fm if integral_period is not None else None
    })


def _draw(data, x_lim_factor, save_path):
    x = data['time list']
    y = data['counter data']
    fs = data['fs']
    fm = data['fm']
    fig = plt.figure()
    plt.plot(x, y)
    plt.xlabel("Time (s)")
    plt.ylabel("Counts")
    plt.title("Fm={},Fs={}".format(fm, fs))
    logging.debug(x_lim_factor)
    if x_lim_factor:
        x_lim = [0, x_lim_factor / data['fm']]
        plt.xlim(x_lim)
    if save_path:
        if not os.path.exists(save_path):
            os.mkdir(save_path)
        plt.savefig(os.path.join(save_path, data['name'] + ".png"), bbox_inches='tight', dpi=600)
    plt.close(fig)


def draw(q, x_lim_factor: typing.Optional[int] = None, save_path: typing.Optional[str] = None):
    while True:
        if q.empty():
            break
        data = q.get()
        sub_process = multiprocessing.Process(target=_draw, args=(data, x_lim_factor, save_path))
        sub_process.start()
        sub_process.join()


def fm_vs_amp():
    global file_queue

    def _process(data_queue, result_queue):
        while True:
            if data_queue.empty():
                break
            data = data_queue.get()
            moving_average_filter(data, SPAN_WIDTH_FACTOR)
            get_lock_in_amp(data, result_queue, INTEGRAL_PERIOD)

    def _get_fm_vs_amp(q):
        data = {}
        while True:
            if q.empty():
                return data
            t = q.get()
            if t['fs'] not in data.keys():
                data[t['fs']] = {
                    "fm": [],
                    "amp": []
                }
            else:
                data[t['fs']]['fm'].append(t['fm'])
                data[t['fs']]['amp'].append(t['amp'])

    data_queue = queue.Queue()
    result_queue = queue.Queue()
    pool = concurrent.futures.ThreadPoolExecutor()
    threads = []

    for i in range(6):
        threads.append(pool.submit(load_file, file_queue, data_queue))

    for i in range(4):
        threads.append(pool.submit(_process, data_queue, result_queue))

    if DRAW_FLAG:
        for i in range(os.cpu_count()):
            threads.append(pool.submit(draw, result_queue, XLIM_FACTOR, SAVE_PATH))
    pool.shutdown()
    if not DRAW_FLAG:
        data = _get_fm_vs_amp(result_queue)
        fig = plt.figure()
        for fs in sorted(data.keys(), reverse=True):
            plt.plot(sorted(data[fs]['fm']),
                     sorted(data[fs]['amp'], key=lambda x: data[fs]['fm'][data[fs]['amp'].index(x)]), marker='.',
                     label="fs={}".format(fs))
        plt.xlabel("Fm (Hz)")
        plt.ylabel("Amp")
        plt.legend()
        plt.savefig("./figure/fm vs amp/{}.png".format(SPAN_WIDTH_FACTOR), bbox_inches='tight', dpi=600)
        # plt.show()


def measure_time_vs_amp():
    global file_queue

    def _process(data_queue, result_queue):
        while True:
            if data_queue.empty():
                break
            data = data_queue.get()
            moving_average_filter(data, SPAN_WIDTH_FACTOR)
            max_period = data['time list'][-1] * data['fm']
            max_period = int(max_period)
            for i in range(max_period):
                get_lock_in_amp(data, result_queue, i)

    data_queue = queue.Queue()
    result_queue = queue.Queue()
    pool = concurrent.futures.ThreadPoolExecutor()
    threads = []

    for i in range(6):
        threads.append(pool.submit(load_file, file_queue, data_queue))

    for i in range(12):
        threads.append(pool.submit(_process, data_queue, result_queue))

    pool.shutdown()
    result_list = []
    while not result_queue.empty():
        result_list.append(result_queue.get())
    fm = 10
    measure_time_vs_amp_dif_fs = {}
    for data in result_list:
        if data['fm'] == fm:
            if data['fs'] not in measure_time_vs_amp_dif_fs.keys():
                measure_time_vs_amp_dif_fs[data['fs']] = {
                    "measure time": [],
                    "amp": []
                }
            else:
                measure_time_vs_amp_dif_fs[data['fs']]['measure time'].append(data['measure time'])
                measure_time_vs_amp_dif_fs[data['fs']]['amp'].append(data['amp'])
    fig = plt.figure()
    for fs in sorted(measure_time_vs_amp_dif_fs.keys(), reverse=True):
        plt.plot(
            sorted(measure_time_vs_amp_dif_fs[fs]['measure time']),
            sorted(measure_time_vs_amp_dif_fs[fs]['amp'],
                   key=lambda val: measure_time_vs_amp_dif_fs[fs]['measure time'][
                       measure_time_vs_amp_dif_fs[fs]['amp'].index(val)]),
            label=fs,
            marker='.'
        )
    plt.xlabel("Measure Time (s)")
    plt.ylabel("Amp")
    plt.legend(title="Fs")
    plt.title("Fm={} Hz".format(fm))
    save_path = "./figure/measure time vs amp/span width={}".format(SPAN_WIDTH_FACTOR)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    plt.savefig(os.path.join(save_path, "Fm={}.png".format(fm)), dpi=600, bbox_inches='tight')
    # plt.show()


if __name__ == '__main__':
    file_queue = queue.Queue()
    for files in os.listdir(DATA_PATH):
        file_queue.put(os.path.join(DATA_PATH, files))
    measure_time_vs_amp()
