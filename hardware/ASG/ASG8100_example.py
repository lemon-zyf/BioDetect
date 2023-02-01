import sys
from ASG8100PySDK import *
from ctypes import *
import ctypes
import threading
import time


# 本示例asg和count同时使用


# 提示信息回调函数，打印提示信息
@CFUNCTYPE(None, c_int, c_int, c_char_p)
def error_callback(type, length, data):
    print("type= {}\tdata={}".format(type, data))
    if type == 2:
        print("type = ", type, "length = ", length, "data = ", data)
    if type == 3:
        if data[0] == 1:
            exit("采集速度太快")
        elif data[0] == 2:
            exit("接收段错乱")
    if type == 4:
        exit("设备断开连接")


# count数据回调函数，这里接收到数据直接打印，不保存
@CFUNCTYPE(None, c_int, c_int, c_int, POINTER(c_uint32))
def count_callback(channel, seg, length, c_data):
    print("channel = ", channel, "seg = ", seg, "length = ", length)
    data1 = []
    data2 = []
    for i in range(length):
        if channel == 0:
            data1.append(c_data[i])

        else:
            data2.append(c_data[i])
    if channel == 0:
        print("data1", data1)

    else:
        print("data2", data2)


# asg序列
#   asg_data = [(segment1),(segment2),...,(segmentn)]     asg_Data由segment列表组成
#   segment = (loop,[(row1),(row2),...,(rown)])           segment由循环和行列表组成
#   row = (time,[ch1,c h2,ch3,ch4,ch5,ch6，ch7，ch8])       row由电平持续时间和各通道在这一行的电平组成
asg_data = [
    (1, [
        (25, [0, 1, 1, 1, 1, 1, 1, 1]),
        (25, [1, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (1000, [0, 0, 0, 0, 0, 0, 0, 0])
    ]),
    (1, [
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 1]),
        (25, [0, 0, 0, 0, 0, 0, 0, 0]),
        (25, [1, 1, 1, 1, 1, 1, 1, 0]),
        (1000, [0, 0, 0, 0, 0, 0, 0, 0])
    ])
]

# count序列
#   count_data = [(segment1),(segment2),...,(segmentn)]   count_data由segment列表组成
#   segment = (loop,[(row1),(row2),...,(rown)])           segment由循环和行列表组成
#   row = (time,[ch1,ch2])                                row由电平持续时间和各通道在这一行的电平组成
count_data = [
    (1, [(50, [1, 1]),
         (25, [0, 0]),
         (80, [1, 1]),
         (25, [0, 0]),
         (500, [1, 1]),
         (900, [0, 0])
         ]),
    (1, [(50, [1, 1]),
         (25, [0, 0]),
         (80, [1, 1]),
         (25, [0, 0]),
         (100, [1, 1]),
         (1000000000, [0, 0])
         ])
]

# 实例化对象
asg8100 = ASG8x00()
asg8100.AsgDownload(asg_data)
# 配置提示信息回调函数
ret = asg8100.error_callback(error_callback)
if ret != 0: exit(ErrorCode[ret])

# 配置count数据回调函数
ret = asg8100.count_callback(count_callback)
if ret != 0: exit(ErrorCode[ret])

# 连接设备
ret = asg8100.connect()
if ret != 0: exit(ErrorCode[ret])

# 配置asg和count使能
'''
高8bit表示ASG输出常高电平控制:   每一bit对应一个通道，为1时，高电平输出，0时，低电平输出。
低8bit表示ASG通道开关:   Bit[0] 表示counter计数功能开关
'''
iLevel = 0
ret = asg8100.AsgSetHightLevel(iLevel)
if ret != 0: exit(ErrorCode[ret])

iEnable = 0x1ff
ret = asg8100.ASG8x00_AsgSetChannelEnable(iEnable)
if ret != 0: exit(ErrorCode[ret])

# 配置IN1、IN2功能
'''
高8bit表示IN1的模式
7	    0：时钟模式     1: Counter模式，bit[6:0]无效
6	    0: 内部时钟，bit[5:0]无效   1： 外部时钟
5-0     1：外部时钟10M  02为外部时钟100M

低8bit表示IN2的模式
7	    0：触发模式   1:  Counter模式，bit[6:0]无效
6-0     00: 正常工作模式，输出只受播放停止命令控制   01：trigger模式，播放后收到trigger信号才输出
'''
IN1 = 0x80
IN2 = 0x80
ret = asg8100.SetClockAndWorkMode(IN1, IN2)
if ret != 0: exit(ErrorCode[ret])

# 下载asg数据
ret = asg8100.AsgDownload(asg_data)
if ret != 0: exit(ErrorCode[ret])

# 下载count数据
ret = asg8100.CounterDownload(count_data)
if ret != 0: exit(ErrorCode[ret])

input("enter to start：")  # 回车开始播放
# 计算segment是否合法
Loop = 10
seg_num_count = len(count_data)
seg_num_asg = len(asg_data)

# 开始播放(播放次数)
rep = seg_num_asg * Loop
ret = asg8100.start()
if ret != 0: exit(ErrorCode[ret])

input("enter to stop：")  # 回车停止播放
# 停止播放
ret = asg8100.stop()
if ret != 0: exit(ErrorCode[ret])
