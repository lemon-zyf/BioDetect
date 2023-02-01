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
    print(datetime.datetime.now())
    with open(save_file, "a") as f:
        for i in range(length):
            # print(c_data[i])
            f.write("{:.4f}\t{}\n".format(count * 1 / Fs, c_data[i]))
            count += 1


Fs = 1 / 0.02
exposure_time = 0.0001
factor = 50
Fm = 1 / (factor * 1 / Fs)
print("Fs={}, Fm={}".format(Fs, Fm))
measure_time = 20
loop = int(measure_time * Fm)

sequence = Sequence(name="bio detect")
group = Group(name="high time", repeat_number=factor // 2)
pulse = Pulse(name="high time", duration=int(1 / Fs * 1e9), increase=0)
pulse.set_high_time(0, time=pulse.duration)
pulse.set_high_time(8, int(exposure_time * 1e9))
if pulse.get_child(8).high_time == pulse.duration:
    pulse.set_low_time(8, 25)
group.append_child(pulse)
sequence.append_child(group)

if factor % 2 != 0:
    pulse = Pulse(name="tunning_point", duration=int(1 / Fs * 1e9), increase=0)
    pulse.set_high_time(0, time=int(pulse.duration / 2))
    pulse.set_high_time(8, int(exposure_time * 1e9))
    if pulse.get_child(8).high_time == pulse.duration:
        pulse.set_low_time(8, 25)
    sequence.append_child(pulse)

group2 = Group(name="low time", repeat_number=factor // 2)
pulse = Pulse(name="low time", duration=int(1 / Fs * 1e9), increase=0)
pulse.set_high_time(8, int(exposure_time * 1e9))
if pulse.get_child(8).high_time == pulse.duration:
    pulse.set_low_time(8, 25)
group2.append_child(pulse)
sequence.append_child(group2)

data = sequence.to_hardware()

asg = ASG8100()
asg.connect()
asg.set_high_level(0x0000)
asg.set_counter_callback(counter_callback)
asg.set_error_callback(error_callback)
asg.set_asg_enable(True)
asg.set_loop(loop)
asg.download_asg_sequence(data['asg_pulses'], length=data['asg_length'], loop=data['asg_loop'], seg_num=1)
asg.download_counter_sequence(data['counter_pulses'], length=data['counter_length'], loop=data['counter_loop'],
                              seg_num=1)
asg.set_input_mode(ASGCLockMode.COUNT, ASGCLockMode.DISABLE)
success = asg.start()
if success:
    time.sleep((loop) * 1 / Fm + 2)
    # input()
    asg.stop()
