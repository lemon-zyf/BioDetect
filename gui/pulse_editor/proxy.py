from PyQt5 import QtCore, QtWidgets
from logic.sequence import Pulse, ChannelData
from util.Mixin import BaseMixin


class QPulseProxy(QtCore.QObject, BaseMixin):
    sigChannelDurationChanged = QtCore.pyqtSignal(int, tuple)
    sigChannelIncreaseChanged = QtCore.pyqtSignal(int, tuple)
    sigNameChanged = QtCore.pyqtSignal(str)
    sigDurationChanged = QtCore.pyqtSignal(int)
    sigIncreaseChanged = QtCore.pyqtSignal(int)

    def __init__(self, pulse: Pulse):
        super().__init__()
        self._pulse = pulse
        self._channel_number = len(self.children)

    @property
    def name(self):
        return self._pulse.name

    @property
    def pulse(self):
        return self._pulse

    @property
    def duration(self):
        return self._pulse.duration

    @property
    def increase(self):
        return self._pulse.increase

    @property
    def children(self):
        return self._pulse.children

    def set_name(self, name: str):
        self._pulse.set_name(name)
        self.sigNameChanged.emit(self.name)

    def set_duration(self, duration):
        if duration < 0:
            duration = 0
        self._pulse.set_duration(duration)
        self.sigDurationChanged.emit(duration)
        for channel_index, child in enumerate(self.children):
            self.sigChannelDurationChanged.emit(channel_index, (child.high_time, child.low_time))

    def set_increase(self, increase):
        if increase < 0:
            increase = 0
        self._pulse.set_increase(increase)
        self.sigIncreaseChanged.emit(increase)
        for channel_index, child in enumerate(self.children):
            self.sigChannelIncreaseChanged.emit(channel_index, (child.high_increase, child.low_increase))

    def set_high_time(self, channel_index, high_time):
        if high_time < 0:
            high_time = 0
        self._pulse.set_high_time(channel_index, high_time)
        self.sigChannelDurationChanged.emit(channel_index, (
            self.children[channel_index].high_time, self.children[channel_index].low_time))

    def set_low_time(self, channel_index, low_time):
        if low_time < 0:
            low_time = 0
        self._pulse.set_low_time(channel_index, low_time)
        self.sigChannelDurationChanged.emit(channel_index, (
            self.children[channel_index].high_time, self.children[channel_index].low_time
        ))

    def set_high_increase(self, channel_index, high_increase):
        if high_increase < 0:
            high_increase = 0
        self._pulse.set_high_increase(channel_index, high_increase)
        self.sigChannelIncreaseChanged.emit(channel_index, (
            self.children[channel_index].high_increase, self.children[channel_index].low_increase
        ))

    def set_low_increase(self, channel_index, low_increase):
        if low_increase < 0:
            low_increase = 0
        self._pulse.set_low_increase(channel_index, low_increase)
        self.sigChannelIncreaseChanged.emit(channel_index, (
            self.children[channel_index].high_increase, self.children[channel_index].low_increase
        ))
