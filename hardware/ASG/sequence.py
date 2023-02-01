from typing import List, Tuple, Dict, Optional, Union
from typing import Sequence as Seq
import copy as cp
from collections import OrderedDict
import numpy as np
import json
from util.Mixin import BaseMixin


class SequenceMixin(BaseMixin):
    def __init__(self, name: str):
        super().__init__()
        if name.strip() == "":
            raise ValueError("invalid sequence name")
        self._name = name.rstrip().lstrip()
        self._children = []

    @property
    def children(self):
        return cp.deepcopy(self._children)

    def get_child(self, index: int):
        return self._children[index]

    def clear_children(self):
        self._children.clear()

    def remove_child(self, index):
        self._children.pop(index)

    def append_child(self, child):
        self._children.append(child)

    def insert_child(self, index: int, child):
        self._children.insert(index, child)

    @property
    def name(self):
        return self._name

    def set_name(self, name: str):
        if name.strip() == "":
            self.logger.error("set name failed, invalid name")
            return
        self._name = name.rstrip().lstrip()

    def to_dict(self):
        raise NotImplemented

    @classmethod
    def from_dict(cls, settings: Dict):
        raise NotImplemented


class ChannelData(BaseMixin):
    def __init__(self, high_time: int = 0, low_time: int = 0, high_increase: int = 0, low_increase: int = 0):
        super().__init__()
        self._high_time = high_time
        self._low_time = low_time
        self._high_increase = high_increase
        self._low_increase = low_increase

    @property
    def duration(self):
        return self._high_time + self._low_time

    @property
    def high_time(self):
        return self._high_time

    @property
    def low_time(self):
        return self._low_time

    @property
    def increase(self):
        return self._high_increase + self._low_increase

    @property
    def high_increase(self):
        return self._high_increase

    @property
    def low_increase(self):
        return self._low_increase

    def set_duration(self, duration: int):
        if duration <= self.duration:
            if self.high_time >= duration:
                self._high_time = duration
                self._low_time = 0
            else:
                self._low_time = duration - self._high_time

        else:
            self._low_time = duration - self._high_time

    def set_increase(self, increase: int):
        if increase <= self.increase:
            if self._high_increase >= increase:
                self._high_increase = increase
                self._low_increase = 0
            else:
                self._low_increase = increase - self._high_increase
        else:
            self._low_increase = increase - self._high_increase

    def set_high_increase(self, increase):
        if increase >= self.increase:
            self._high_increase = self.increase
            self._low_increase = 0
        else:
            self._low_increase = self.increase - increase
            self._high_increase = increase

    def set_low_increase(self, increase):
        if increase >= self.increase:
            self._low_increase = self.increase
            self._high_increase = 0
        else:
            self._high_increase = self.increase - increase
            self._low_increase = increase

    def set_high_time(self, high_time):
        if high_time >= self.duration:
            self._high_time = self.duration
            self._low_time = 0
        else:
            self._low_time = self.duration - high_time
            self._high_time = high_time

    def set_low_time(self, low_time):
        if low_time >= self.duration:
            self._low_time = self.duration
            self._high_time = 0
        else:
            self._high_time = self.duration - low_time
            self._low_time = low_time

    def to_dict(self):
        return {
            "type": "channel data",
            "high_time": self._high_time,
            "low_time": self._low_time,
            "high_increase": self._high_increase,
            "low_increase": self._low_increase
        }

    @classmethod
    def from_dict(cls, settings: Dict):
        high_time = settings['high_time']
        low_time = settings['low_time']
        high_increase = settings['high_increase']
        low_increase = settings['low_increase']
        return ChannelData(high_time, low_time, high_increase, low_increase)


class Pulse(SequenceMixin):
    def __init__(self, name: str, duration: int = 0, increase: int = 0, channel_number=10):
        super().__init__(name=name)
        self._channel_number = channel_number
        self._duration = duration
        self._increase = increase
        for i in range(self._channel_number):
            self._children.append(ChannelData(low_time=duration, low_increase=increase))

    def _check_index_in_range(self, index):
        if index < 0 or index >= self._channel_number:
            raise IndexError("index out of range")

    @property
    def duration(self):
        return self._duration

    @property
    def increase(self):
        return self._increase

    def set_duration(self, duration):
        self._duration = duration
        [ch.set_duration(duration) for ch in self._children]

    def set_increase(self, increase):
        self._increase = increase
        [ch.set_increase(increase) for ch in self._children]

    def set_high_time(self, channel_index: int, time: int):
        self._check_index_in_range(channel_index)
        self._children[channel_index].set_high_time(time)

    def set_low_time(self, channel_index: int, time: int):
        self._check_index_in_range(channel_index)
        self._children[channel_index].set_low_time(time)

    def set_high_increase(self, channel_index: int, increase: int):
        self._check_index_in_range(channel_index)
        self._children[channel_index].set_high_increase(increase)

    def set_low_increase(self, channel_index: int, increase: int):
        self._check_index_in_range(channel_index)
        self._children[channel_index].set_low_increase(increase)

    def to_dict(self):
        return {
            "type": "pulse",
            "name": self._name,
            "duration": self._duration,
            "increase": self._increase,
            "children": [ch.to_dict() for ch in self._children]
        }

    @classmethod
    def from_dict(cls, settings: Dict):
        if settings['type'] != "pulse":
            raise ValueError("instantiate pulse failed. expect type: pulse, get {}".format(settings['type']))
        name = settings['name']
        duration = settings['duration']
        increase = settings['increase']
        instance = Pulse(name, duration, increase)
        instance.clear_children()
        for child in settings['children']:
            instance.append_child(ChannelData.from_dict(child))
        return instance


class Group(SequenceMixin):
    def __init__(self, name: str, repeat_number: int):
        super().__init__(name)
        if repeat_number <= 0:
            raise ValueError("repeat number must be positive")
        self._repeat_number = repeat_number

    @property
    def repeat_number(self):
        return self._repeat_number

    def set_repeat_number(self, number):
        if number <= 0:
            raise ValueError("invalid repeat number")
        self._repeat_number = number

    def to_dict(self):
        return {
            "type": "group",
            "name": self.name,
            "repeat_number": self.repeat_number,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, settings: Dict):
        if settings['type'] != "group":
            raise ValueError("instantiate Group failed. except group, got {}".format(settings['type']))
        name = settings['name']
        repeat_number = settings['repeat_number']
        children = settings['children']
        instance = Group(name, repeat_number)
        for child in children:
            if child['type'] == "group":
                instance.append_child(Group.from_dict(child))
            elif child['type'] == "pulse":
                instance.append_child(Pulse.from_dict(child))
            else:
                raise ValueError("invalid child type: {}".format(child['type']))
        return instance


class Segment(SequenceMixin):
    def __init__(self, name: str, loop: int):
        super().__init__(name)
        if loop <= 0:
            raise ValueError("loop must be positive")
        self._loop = loop

    @property
    def loop(self):
        return self._loop

    def set_loop(self, loop_number: int):
        if loop_number <= 0:
            raise ValueError("invalid loop number: {}".format(loop_number))
        self._loop = loop_number

    def to_dict(self):
        return {
            "type": "segment",
            "name": self.name,
            "loop": self.loop,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, settings: Dict):
        if settings['type'] != "segment":
            raise ValueError("instantiate Segment failed. type: {}".format(settings['type']))
        name = settings['name']
        loop = settings['loop']
        instance = Segment(name, loop)
        for child in settings['children']:
            if child['type'] == "group":
                instance.append_child(Group.from_dict(child))
            elif child['type'] == "pulse":
                instance.append_child(Pulse.from_dict(child))
            else:
                raise ValueError("invalid child type: {}".format(child['type']))
        return instance


class Sequence(SequenceMixin):
    def __init__(self, name: str):
        super().__init__(name)

    def to_dict(self):
        return {
            "type": "sequence",
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, settings: Dict):
        if settings['type'] != 'sequence':
            raise ValueError("instantiate Sequence failed, get type: {}".format(settings['type']))
        name = settings['name']
        instance = Sequence(name)
        for child in settings['children']:
            if child['type'] == "group":
                instance.append_child(Group.from_dict(child))

    def to_hardware(self):
        def process_pulse(pulse: Pulse, loop_index: int):
            for channel_index, channel_data in enumerate(pulse.children):
                _pulses[channel_index].append(channel_data.high_time + loop_index * channel_data.high_increase)
                _pulses[channel_index].append(channel_data.low_time + loop_index * channel_data.low_increase)

        def process_group(group: Group, loop_index: int):
            for repeat_number in range(group.repeat_number):
                for child in group.children:
                    if isinstance(child, Pulse):
                        process_pulse(child, loop_index)
                    else:
                        process_group(child, loop_index)

        def process_segment(segment: Segment):
            for loop_index in range(segment.loop):
                for child in segment.children:
                    if isinstance(child, Pulse):
                        process_pulse(child, loop_index)
                    else:
                        process_group(child, loop_index)

        _pulses = []
        pulses = []
        loop = [1]
        for i in range(10):
            _pulses.append([])
            pulses.append([0])
        pulses = [[0]] * 10
        length = [[0] * 10]
        segment = 1

        for child in self.children:
            if isinstance(child, Pulse):
                process_pulse(child, 0)
            elif isinstance(child, Group):
                process_group(child, 0)
            elif isinstance(child, Segment):
                process_segment(child)

        for ch in range(10):
            for i in range(0, len(_pulses[ch]), 2):
                high_time = _pulses[ch][i]
                low_time = _pulses[ch][i + 1]
                if len(pulses[ch]) % 2 == 0:  # 低电平结尾
                    if high_time == 0:
                        pulses[ch][-1] += low_time
                    else:
                        pulses[ch].append(high_time)
                        if low_time == 0:
                            continue
                        else:
                            pulses[ch].append(low_time)
                else:  # 高电平结尾
                    if high_time != 0:
                        pulses[ch][-1] += high_time
                        if low_time != 0:
                            pulses[ch].append(low_time)
                        else:
                            continue
                    else:
                        pulses[ch].append(low_time)
            if len(pulses[ch]) % 2 != 0:
                pulses[ch].append(0)
            length[0][ch] = len(pulses[ch])

        asg_pulses = pulses[0:8]
        counter_pulses = pulses[8:10]
        asg_length = [length[0][0:8]]
        counter_length = [length[0][8:10]]
        counter_length_t = [[], []]
        for i in range(len(counter_length)):
            counter_length_t[0].append(counter_length[i][0])
            counter_length_t[1].append(counter_length[i][0])
        return {
            "asg_pulses": asg_pulses,
            "asg_length": asg_length,
            "asg_loop": loop,
            "segment": segment,
            "counter_pulses": counter_pulses,
            "counter_length_t": counter_length_t,
            "counter_loop": cp.deepcopy(loop),

        }


if __name__ == '__main__':
    pass
