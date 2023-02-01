import time

from hardware.ASG.ASG8100 import ASG8100, ASGStatus, ASGCLockMode
from logic.sequence import Pulse, Sequence, Segment, Group
from ctypes import *
from datetime import datetime

save_file = "counter data {}.txt".format(datetime.today().strftime("%H-%M-%S"))


# with open(save_file, "w+") as f:
#     f.truncate()


@CFUNCTYPE(None, c_int, c_int, c_char_p)
def error_callback(type, length, data):
    print("type={}\tdata={}".format(type, data))
    if type == 2:
        print("type= {},length= {}, data= {}".format(type, length, data))
    if type == 3:
        if data[0] == 1:
            exit("采集速度太快")
        elif data[0] == 2:
            exit("接收段错乱")
    if type == 4:
        exit("设备断开连接")


@CFUNCTYPE(None, c_int, c_int, c_int, POINTER(c_uint32))
def count_callback(channel, seg, length, c_data):
    print("channel={}, seg={}, length={}".format(channel, seg, length))
    data1 = []
    data2 = []
    for i in range(length):
        if channel == 0:
            data1.append(c_data[i])
        else:
            data2.append(c_data[i])
    if channel == 0:
        print("data1", data1)
        with open(save_file, "a") as f:
            f.write("\t".join([str(d) for d in data1]))
            f.write('\n')
    else:
        with open(save_file, "a") as f:
            f.write("\t".join([str(d) for d in data2]))
            f.write("\n")
        print("data2", data2)


def draw():
    from matplotlib import pyplot as plt
    import numpy as np
    data = np.loadtxt("counter data 17-11-19.txt")
    plt.plot(data)
    plt.show()


draw()
exit()

# print(datetime.a)
if __name__ == '__main__':
    sequence = Sequence(name="test")
    counter_on = Pulse("counter", duration=int(1e9), increase=0)
    counter_on.set_low_time(8, 25)
    sequence.append_child(counter_on)
    data = sequence.to_hardware()
    asg_8100 = ASG8100()
    asg_8100.connect()
    asg_8100.set_loop(20)
    # asg_8100.set_high_level(0x0000)
    asg_8100.set_error_callback(error_callback)
    asg_8100.set_counter_callback(count_callback)
    asg_8100.set_asg_enable(False)
    asg_8100.set_input_mode(ASGCLockMode.COUNT, ASGCLockMode.DISABLE)
    asg_8100.download_asg_sequence(data['asg_pulses'], data['asg_length'], data['asg_loop'], 1)
    asg_8100.download_counter_sequence(data['counter_pulses'], data['counter_length'], data['counter_loop'], 1)
    # asg_8100.start()
    # time.sleep(25)
    draw()
