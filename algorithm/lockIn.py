import numpy as np
from math import pi


def lockIn(inputSignal: np.ndarray, tlist: np.ndarray, Fm: float, periodNumber: int = None) -> float:
    sine = np.sin(2 * pi * Fm * tlist)
    cosine = np.cos(2 * pi * Fm * tlist)
    v_x = inputSignal * sine
    v_y = inputSignal * cosine
    if periodNumber is None:
        X = np.mean(v_x)
        Y = np.mean(v_y)
    else:
        X = np.mean(v_x[np.where((tlist >= 0) & (tlist <= periodNumber / Fm))])
        Y = np.mean(v_y[np.where((tlist >= 0) & (tlist <= periodNumber / Fm))])
    return np.sqrt(X ** 2 + Y ** 2)


def movingAverageFilter(inputSignal: np.ndarray, tlist: np.ndarray, windowWidth: int):
    if windowWidth <= 0:
        windowWidth = 1
    outputSignal = np.zeros(len(inputSignal) - windowWidth + 1)
    for i in range(len(outputSignal)):
        outputSignal[i] = np.mean(inputSignal[i:i + windowWidth])
    tlist = tlist[0:len(outputSignal)]
    return tlist, outputSignal
