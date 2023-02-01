import enum
import sys
from ctypes import *
from typing import Callable, Tuple, Dict, Union, Optional, List
from typing import Sequence as Seq
from collections import OrderedDict
from hardware.interface.ASG_Interface import ASG8x00Interface, ERROR_CALLBACKTYPE, COUNT_CALLBACKTYPE, ErrorCode
import os
from util.Mixin import BaseMixin
import copy as cp

COUNT_ROW_TYPE = Tuple[int, Tuple[bool, bool]]
COUNT_SEG_TYPE = Tuple[int, List[COUNT_ROW_TYPE]]
COUNT_DATA_TYPE = List[COUNT_SEG_TYPE]

ASG_ROW_TYPE = Tuple[int, Tuple[int, int, int, int, int, int, int, int]]
ASG_SEG_TYPE = Tuple[int, List[ASG_ROW_TYPE]]
ASG_DATA_TYPE = List[ASG_SEG_TYPE]


def get_error_message(code: int):
    if code not in ErrorCode:
        return None
    return ErrorCode[code]


class ASGStatus(enum.Enum):
    IS_RUNNING = "is_running"
    NOT_CONNECTED = "not_connected"
    IDLE = "idle"


class ASGCLockMode(enum.IntFlag):
    COUNT = 0x80
    DISABLE = 0x00
    EXT_CLOCK_10M = 0x41
    EXT_CLOCK_100M = 0x42


def _check_status(require_status):
    def check_status(func):
        def inner_check(*args, **kwargs):
            self = args[0]
            if self._status != require_status:
                self.logger.warning(
                    "function {} is called, ASG status is {}, require {}".format(func.__name__, self._status,
                                                                                 require_status))
                return False
            return func(*args, **kwargs)

        return inner_check

    return check_status


class ASG8100(ASG8x00Interface):
    __channel_to_hex = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80)
    _initial_flag = False
    __asg_channel_number = 8

    def __init__(self):
        if not self._initial_flag:
            super().__init__()
            self._error_callback = None
            self._counter_callback = None
            self._asg_sequence = False
            self._counter_sequence = False
            self._loop = 0
            self._counter_loop = 0
            self._asg_loop = 0
            self._high_level = 0x0000
            self._asg_enable = True
            self._in1 = ASGCLockMode.DISABLE,
            self._in2 = ASGCLockMode.DISABLE
            self._status = ASGStatus.NOT_CONNECTED
            self._initial_flag = True

            dll_path = os.path.join(os.path.dirname(__file__), "ASG8100_x64.dll")
            if os.path.isfile(dll_path):
                self.__dll = CDLL(dll_path)
                self.logger.debug("using dll: {}".format(dll_path))
            else:
                self.logger.error("dll file not found")
                sys.exit()

            self.__dll.ASG8x00_Connect.restype = c_int
            self.__dll.ASG8x00_Disconnect.restype = c_int
            self.__dll.ASG8x00_DeviceMonitor.restype = c_int
            self.__dll.ASG8x00_StartPlay.argtypes = [c_int]
            self.__dll.ASG8x00_StartPlay.restype = c_int
            self.__dll.ASG8x00_StopPlay.restype = c_int
            self.__dll.ASG8x00_SetErrorCallback.restype = c_int
            self.__dll.ASG8x00_SetCountCallback.restype = c_int
            self.__dll.ASG8x00_AsgSetHightLevel.argtypes = [c_int]
            self.__dll.ASG8x00_AsgSetHightLevel.restype = c_int
            self.__dll.ASG8x00_AsgSetChannelEnable.argtypes = [c_int]
            self.__dll.ASG8x00_AsgSetChannelEnable.restype = c_int
            self.__dll.ASG8x00_AsgDownload.restype = c_int
            self.__dll.ASG8x00_CounterDownload.restype = c_int
            self.__dll.ASG8x00_SetClockAndWorkMode.argtypes = [c_int, c_int]
            self.__dll.ASG8x00_SetClockAndWorkMode.restype = c_int

    @property
    def error_callback(self):
        return self._error_callback

    @property
    def counter_callback(self):
        return self._counter_callback

    @property
    def has_asg_sequence(self):
        return self._asg_sequence

    @property
    def has_counter_sequence(self):
        return self._counter_sequence

    @property
    def loop(self):
        return self._loop

    @property
    def input_mode(self):
        return {
            "in1": self._in1,
            "in2": self._in2
        }

    @property
    def asg_enabled(self):
        return self._asg_enable

    @property
    def counter_enabled(self):
        return self._in1 == ASGCLockMode.COUNT or self._in2 == ASGCLockMode.COUNT

    @property
    def high_level(self):
        return self._high_level

    def set_loop(self, loop: int):
        if loop < 0:
            self.logger.error("loop number must be non-negative")
            return
        self._loop = loop

    @_check_status(ASGStatus.NOT_CONNECTED)
    def connect(self) -> bool:
        error_code = self.__dll.ASG8x00_Connect()
        if error_code:
            self.logger.error("connect ASG failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
        else:
            self.logger.debug("connect to ASG success")
            self._status = ASGStatus.IDLE
        return error_code == 0

    @_check_status(ASGStatus.IDLE)
    def disconnect(self) -> bool:
        error_code = self.__dll.ASG8x00_Disconnect()
        if error_code:
            self.logger.error(
                "disconnect ASG failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
        else:
            self.logger.debug("disconnect ASG success.")
            self._status = ASGStatus.NOT_CONNECTED
        return error_code == 0

    @_check_status(ASGStatus.IDLE)
    def monitor_status(self):
        return self.__dll.ASG8x00_DeviceMonitor()

    def set_error_callback(self, func: Callable):
        success = True
        if type(func) == ERROR_CALLBACKTYPE:
            error_code = self.__dll.ASG8x00_SetErrorCallback(func)
            if error_code:
                success = False
                self.logger.error(
                    "set error callback failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
            else:
                self._error_callback = func
                self.logger.debug("set error callback success")
        else:
            success = False
            self.logger.error("invalid function type")
        return success

    def set_counter_callback(self, func: Callable):
        success = True
        if type(func) == COUNT_CALLBACKTYPE:
            error_code = self.__dll.ASG8x00_SetCountCallback(func)
            if error_code:
                success = False
                self.logger.error(
                    "set counter callback failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
            else:
                self.logger.debug("set counter callback success.")
                self._counter_callback = func
        else:
            success = False
            self.logger.error("invalid function type")
        return success

    def set_high_level(self, level: int) -> bool:
        """
        set ASG channel to always high level
        :param level: 2 byte int. bit[8:16] corresponding to channels 1-8. set bit to 1 to enable high level, set bit to
        0 to set channel to normal
        :return:
        """
        success = True
        level &= 0xff00
        error_code = self.__dll.ASG8x00_AsgSetHightLevel(c_int(level))
        if error_code:
            self.logger.error("set high level failed, code: {}, msg: {}, level: {:#06x}".format(error_code,
                                                                                                get_error_message(
                                                                                                    error_code), level))
            success = False
        else:
            self._high_level = level
            self.logger.debug("set high level success, level: {:#06x}".format(level))
        return success

    def set_high_level_by_index(self, channel: int, level: int):
        """
        set single channel to high or low level
        :param channel: channel index
        :param level: 1 or 0
        :return:
        """
        success = True
        if self._check_index_in_range(channel):
            level = int(bool(level))
            if level == 1:
                high_level = (self.__channel_to_hex[channel] << 8) | self._high_level
            else:
                high_level = (~(self.__channel_to_hex[channel] << 8)) & self._high_level
            success = self.set_high_level(high_level)
            if success:
                self.logger.debug("set channel {} to {} success".format(channel, level))
            else:
                self.logger.error("set channel {} to {} failed".format(channel, level))

        else:
            success = False
        return success

    def _check_index_in_range(self, channel: int):
        if channel < 0 or channel >= self.__asg_channel_number:
            self.logger.error("channel index out of range")
            return False
        return True

    def set_asg_enable(self, enable: bool):
        """
        enable or disable ASG function
        :param enable:
        :return:
        """
        success = True
        if enable:
            code = 0x1ff
        else:
            code = 0x0ff
        error_code = self.__dll.ASG8x00_AsgSetChannelEnable(c_int(code))
        if error_code:
            success = False
            self.logger.error(
                "set asg to {} failed, code: {}, msg: {}".format(enable, error_code, get_error_message(error_code)))
        else:
            self._asg_enable = enable
            self.logger.debug("set asg to {} success".format(enable))
        return success

    def set_input_mode(self, in1: ASGCLockMode, in2: ASGCLockMode) -> bool:
        """
        set modes of the two input port
        :param in1:
        :param in2:
        :return:
        """
        success = True
        error_code = self.__dll.ASG8x00_SetClockAndWorkMode(c_int(in1), c_int(in2))
        if error_code:
            self.logger.error(
                "set in1 to {}, in2 to {} failed, code: {}, msg: {}".format(in1.name, in2.name, error_code,
                                                                            get_error_message(error_code)))
        else:
            self.logger.debug("set in1 to {}, in2 to {} success".format(in1.name, in2.name))
            self._in1 = in1
            self._in2 = in2
        return success

    def download_asg_sequence(self, pulses, length, loop, seg_num: int):
        """
        download asg sequence to hardware
        :param pulses: int[8][], 每行表示一个channel，第奇数个元素代表高电平持续时间，偶数元素代表低电平持续时间
        :param length: int[seg_num][8]，length[i,j]表示第j个channel在第i个segment中，高低电平的个数
        :param loop: int[seg_num]，每个segment循环的次数
        :param seg_num: segment的个数
        :return:
        """
        lp = cp.deepcopy(loop)
        success = True
        if len(pulses) != self.__asg_channel_number:
            self.logger.error("length of pulses must be {}".format(self.__asg_channel_number))
            success = False
        if len(length) != seg_num or any(len(e) != self.__asg_channel_number for e in length):
            self.logger.error("arg 'length' error")
            success = False
        if len(loop) != seg_num:
            self.logger.error("length of loop must equal to seg number")
            success = False

        if success:
            c_pulses = []
            for i in range(self.__asg_channel_number):
                c_pulses.append((c_longlong * len(pulses[i]))(*pulses[i]))
            c_pulses = (POINTER(c_longlong) * len(c_pulses))(*c_pulses)
            ttype = c_longlong * 8
            length = (ttype * seg_num)(*(tuple(i) for i in length))
            loop = (c_ushort * len(loop))(*loop)
            seg_num = c_ushort(seg_num)
            error_code = self.__dll.ASG8x00_AsgDownload(c_pulses, length, loop, seg_num)
            if error_code:
                self.logger.error(
                    "download asg sequence failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
                success = False
            else:
                self._asg_loop = sum(lp)
                self._asg_sequence = True
                self.logger.debug("download asg sequence success")
        else:
            pass
        return success

    def download_counter_sequence(self, pulses, length, loop, seg_num: int):
        """
        download counter sequence to hardware
        :param pulses:
        :param length:
        :param loop:
        :param seg_num:
        :return:
        """
        lp = cp.deepcopy(loop)
        success = True
        if len(pulses) != 2:
            self.logger.error("length of pulses must be 2")
            success = False
        if len(length) != seg_num or any(len(e) != 2 for e in length):
            self.logger.error("len(length) must be equal to seg_num, and each element should be List[int,int]")
            success = False
        if len(loop) != seg_num:
            self.logger.error("length of loop must be equal to seg_num")
            success = False
        if success:
            t_length = [[], []]
            for i in range(len(length)):
                t_length[0].append(length[i][0])
                t_length[1].append(length[i][1])
            c_pulses = []
            c_length = []
            for i in range(2):
                c_pulses.append((c_longlong * len(pulses[i]))(*pulses[i]))
                c_length.append((c_longlong * len(t_length[i]))(*t_length[i]))

            c_pulses = (POINTER(c_longlong) * len(c_pulses))(*c_pulses)
            c_length = (POINTER(c_longlong) * len(c_length))(*c_length)
            loop = (c_ushort * len(loop))(*loop)
            seg_num = c_ushort(seg_num)
            error_code = self.__dll.ASG8x00_CounterDownload(c_pulses, c_length, loop, seg_num)
            if error_code:
                self.logger.error(
                    "set counter sequence failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
                success = False
            else:
                self._counter_sequence = True
                self._counter_loop = sum(lp)
                self.logger.debug("set counter sequence success")
        else:
            pass
        return success

    @_check_status(ASGStatus.IDLE)
    def reset_device(self):
        self.set_loop(0)
        self.set_asg_enable(True)
        self.set_high_level(0x0000)
        self.set_input_mode(in1=ASGCLockMode.DISABLE, in2=ASGCLockMode.DISABLE)

    @_check_status(ASGStatus.IDLE)
    def start(self):
        def start_play(loop):
            if loop > 0xfffffffe:
                self.logger.error("too much loop")
                return False
            error_code = self.__dll.ASG8x00_StartPlay(c_int(loop))
            if error_code:
                self.logger.error(
                    "start play failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
            else:
                self._status = ASGStatus.IS_RUNNING
                self.logger.debug("start play success")
            return error_code == 0

        success = True
        if not self.asg_enabled:
            self.logger.debug("asg disabled")
            if not self.counter_enabled:
                self.logger.error(
                    "both asg function and counter function are disabled, please enable at least one of them")
                success = False
            else:
                self.logger.debug("counter enabled")
                if not self.has_counter_sequence:
                    self.logger.error("counter enabled, but no counter sequence has been loaded to hardware")
                    success = False
                else:
                    self.logger.debug("counter sequence has been loaded")
                    loop = self._loop * self._counter_loop
                    success = start_play(loop)
        else:
            self.logger.debug("asg enabled")
            if not self.has_asg_sequence:
                self.logger.error("asg enabled, but no asg sequence loaded")
                success = False
            else:
                self.logger.debug("asg sequence has been loaded")
                if self.counter_enabled:
                    self.logger.debug("counter enabled")
                    if not self.has_counter_sequence:
                        self.logger.error("counter enabled, but not counter sequence loaded")
                        success = False
                    else:
                        self.logger.debug("counter sequence has been loaded")
                        if self._asg_loop != self._counter_loop:
                            self.logger.error("the total loop number of asg and counter must be equal, but get {} for "
                                              "asg, and {} for counter".format(self._asg_loop, self._counter_loop))
                            success = False
                        else:
                            loop = self._loop * self._asg_loop
                            success = start_play(loop)
                else:
                    self.logger.debug("counter disabled")
                    loop = self._loop * self._asg_loop
                    success = start_play(loop)
        return success

    @_check_status(ASGStatus.IS_RUNNING)
    def stop(self):
        error_code = self.__dll.ASG8x00_StopPlay()
        if error_code:
            self.logger.error("stop play failed, code: {}, msg: {}".format(error_code, get_error_message(error_code)))
        else:
            self.logger.debug("stop play success")
            self._status = ASGStatus.IDLE

    