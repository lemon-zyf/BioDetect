import copy
import enum
from abc import abstractmethod
from typing import List, Tuple, Dict, Union, Optional, Callable
from ctypes import *
from util.Mixin import BaseMixin

ERROR_CALLBACKTYPE = CFUNCTYPE(None, c_int, c_int, c_char_p)
COUNT_CALLBACKTYPE = CFUNCTYPE(None, c_int, c_int, c_int, POINTER(c_uint32))

ErrorCode = {
    0: "成功",
    1: "设备未连接",
    2: "设备断开连接",
    3: "握手超时",
    4: "握手数据错误",
    5: "关闭等待超时",
    6: "",
    7: "无设备",

    65537: "错误信息回调函数为空",
    65538: "count数据回调函数为空",
    65539: "ASG通道设置参数错误",
    65540: "COUNT使能参数错误",
    65541: "工作模式参数错误",
    65542: "工作模式参数错误",
    65543: "asg和count段信息不相同",

    131073: "ASG脉宽必须是1ns的正整数倍",
    131074: "ASG脉宽必须是2ns的正整数倍",
    131076: "ASG脉宽必须是4ns的正整数倍",
    131077: "ASG段数错误",
    131078: "最大脉宽1.6s",
    131079: "最大总时长8260s",
    131080: "ASG循环必须大于0",

    196609: "COUNT脉宽是5的整数倍",
    196610: "COUNT高电平最小10ns",
    196611: "COUNT低电平最小20ns",
    196612: "COUNT最小以25ns低电平结束",
    196613: "COUNT读取线程已存在",
    196614: "COUNT最大脉宽5497558138880",
    196615: "COUNT循环必须大于0",
    196616: "COUNT采集停止超时",
}


class ASG8x00Interface(BaseMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect the asg device
        :return: True if success
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        disconnect with asg
        :return: True if success
        """
        pass

    @abstractmethod
    def monitor_status(self) -> int:
        """
        Get the device status
        :return: status code, 0 is ok, other is error
        """
        pass

    @abstractmethod
    def set_error_callback(self, func: Callable) -> bool:
        """
        set error callback function
        :param func: ERROR_CALLBACKTYPE type
        :return: True is set callback success. False if failed
        """
        pass

    @abstractmethod
    def set_counter_callback(self, func: Callable) -> bool:
        """
        set count callback function
        :param func: COUNT_CALLBACK type
        :return: True if set callback success. False if failed
        """
        pass

    @abstractmethod
    def set_asg_enable(self, enable: bool) -> bool:
        """
        set asg function enable or disable
        :param enable:
        :return:
        """
        pass

    @abstractmethod
    def set_loop(self, loop: int):
        """
        set the loop number of asg sequence. If loop==0, the sequence will continuously play
        :param loop:
        :return:
        """
        pass

    @abstractmethod
    def get_loop(self) -> int:
        """
        get loop number of asg sequence
        :return:
        """

    @abstractmethod
    def config_settings(self, settings: dict):
        """
        a dictionary is passed to set the asg, including loop number,
        channel enabled, counter enabled
        :param settings:
        :return:
        """

    @abstractmethod
    def get_setting(self) -> dict:
        """
        return current settings of the asg
        :return:
        """

    @abstractmethod
    def reset_device(self):
        """
        reset the ASG to default settings
        :return:
        """
        pass

    @abstractmethod
    def start(self):
        """
        start play asg sequence
        :return:
        """
        pass

    @abstractmethod
    def stop(self):
        """
        stop play
        :return:
        """
        pass
