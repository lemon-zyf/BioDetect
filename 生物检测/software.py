import time

from hardware.microwave.SynthNV import SynthNV
from hardware.ASG.ASG8100 import ASGCLockMode, ASG8100
from logic.sequence import Sequence, Group, Pulse
from matplotlib import pyplot as plt
import numpy as np
from ctypes import *
import datetime

save_file = "./counter data/counter data-{}.txt".format(datetime.datetime.today().strftime("%H-%M-%S"))
print(save_file)

count = 0


@CFUNCTYPE(None, c_int, c_int, c_char_p)
def error_callback(c_type, length, data):
    print("type={}\tdata={}".format(c_type, data))
    if c_type == 2:
        print("type={},length={},data={}".format(c_type, length, data))
    elif c_type == 3:
        if data[0] == 1:
            exit("采集速度太快")
        elif data[0] == 2:
            exit("接受段错乱")
    elif c_type == 4:
        exit("设备断开连接")


@CFUNCTYPE(None, c_int, c_int, c_int, POINTER(c_uint32))
def counter_callback(channel, seg, length, c_data):
    global count
    data = []
    for i in range(length):
        data.append(c_data[i])
    print(data)
    with open(save_file, "a") as f:
        f.write("{:.4f}".format(count * 1 / Fs))
        f.write("\t\t")
        f.write("\t".join([str(d) for d in data]))
        f.write('\n')
    count += 1


Fm = 0.1
Fs = 1 / 0.05
loop = 0
exp_time = 15 / Fm

sequence = Sequence("bio detect")
pulse = Pulse("counter", duration=int(1 / Fs * 1e9), increase=0)
pulse.set_low_time(8, 25)
sequence.append_child(pulse)
data = sequence.to_hardware()

mw = SynthNV("ASRL3::INSTR")
mw.am = Fm

asg = ASG8100()
asg.connect()
asg.set_counter_callback(counter_callback)
asg.set_error_callback(error_callback)
asg.set_asg_enable(False)
asg.set_loop(loop)
asg.download_counter_sequence(data['counter_pulses'], data['counter_length'], data['counter_loop'], 1)
asg.set_input_mode(ASGCLockMode.COUNT, ASGCLockMode.DISABLE)

# mw.start_thread()
# time.sleep(1 / Fm)
asg.start()
input()
# time.sleep(exp_time)
asg.stop()
# mw.stop_thread()
