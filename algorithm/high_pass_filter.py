from scipy import signal


def high_pass_filter(input_signal, cut_down_freq, fs, order):
    w0 = 2 * cut_down_freq / fs
    b, a = signal.butter(order, w0, 'highpass')
    out_put = signal.filtfilt(b, a, input_signal)
    return out_put
