import sys

from PyQt5 import QtGui, QtCore, QtWidgets
from typing import Dict, List, Sequence, Iterable, Tuple, Union, Optional
from logic.sequence import ChannelData, Pulse, Group, Segment
from gui.pulse_editor.proxy import QPulseProxy


class _PulseEditDialog(QtWidgets.QDialog):
    def __init__(self, channel_name_dict: Dict[int, str], pulse: Pulse,
                 parent=None):
        super().__init__(parent)
        self._pulse = QPulseProxy(pulse)
        self._name = self._pulse.name
        self._channel_name_dict = channel_name_dict

        font = QtGui.QFont("微软雅黑")
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFont(font)
        name_editor = QtWidgets.QLineEdit(self._name)
        name_editor.setMaximumWidth(250)
        name_editor.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Maximum)
        duration_label = QtWidgets.QLabel("Duration:")
        duration_label.setFont(font)
        duration_editor = QtWidgets.QLineEdit(str(self._pulse.duration))
        increase_label = QtWidgets.QLabel("Increase:")
        increase_label.setFont(font)
        increase_editor = QtWidgets.QLineEdit(str(self._pulse.increase))

        self._time_editors = dict()

        tab_widget = QtWidgets.QTabWidget()
        for channel_index, channel_name in channel_n ame_dict.items():
            widget = QtWidgets.QWidget()
            high_time_label = QtWidgets.QLabel("High time:")
            high_time_label.setFont(font)
            high_time_editor = QtWidgets.QLineEdit(str(self._pulse.children[channel_index].high_time))
            low_time_label = QtWidgets.QLabel("Low time:")
            low_time_label.setFont(font)
            low_time_editor = QtWidgets.QLineEdit(str(self._pulse.children[channel_index].low_time))
            high_increase_label = QtWidgets.QLabel("High increase:")
            high_increase_label.setFont(font)
            high_increase_editor = QtWidgets.QLineEdit(str(self._pulse.children[channel_index].high_increase))
            low_increase_label = QtWidgets.QLabel("Low increase:")
            low_increase_label.setFont(font)
            low_increase_editor = QtWidgets.QLineEdit(str(self._pulse.children[channel_index].low_increase))

            self._time_editors[channel_index] = dict()
            self._time_editors[channel_index]['high_time'] = high_time_editor
            self._time_editors[channel_index]['low_time'] = low_time_editor
            self._time_editors[channel_index]['high_increase'] = high_increase_editor
            self._time_editors[channel_index]['low_increase'] = low_increase_editor

            high_time_editor.editingFinished.connect(self._get_slot(channel_index, "high_time"))
            high_increase_editor.editingFinished.connect(self._get_slot(channel_index, "high_increase"))
            low_time_editor.editingFinished.connect(self._get_slot(channel_index, "low_time"))
            low_increase_editor.editingFinished.connect(self._get_slot(channel_index, "low_increase"))

            layout = QtWidgets.QGridLayout()
            layout.addWidget(high_time_label, 0, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(high_time_editor, 0, 1, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(low_time_label, 0, 2, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(low_time_editor, 0, 3, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(high_increase_label, 1, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(high_increase_editor, 1, 1, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(low_increase_label, 1, 2, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(low_increase_editor, 1, 3, QtCore.Qt.AlignmentFlag.AlignLeft)
            layout.setColumnStretch(0, 1)
            layout.setColumnStretch(1, 3)
            layout.setColumnStretch(2, 1)
            layout.setColumnStretch(3, 3)
            widget.setLayout(layout)
            tab_widget.addTab(widget, channel_name)

        name_editor.editingFinished.connect(lambda: self._pulse.set_name(name_editor.text()))
        duration_editor.editingFinished.connect(lambda: self._pulse.set_duration(int(duration_editor.text())))
        increase_editor.editingFinished.connect(lambda: self._pulse.set_increase(int(increase_editor.text())))
        self._pulse.sigChannelDurationChanged.connect(self._update_duration)
        self._pulse.sigChannelIncreaseChanged.connect(self._update_increase)

        self._duration_editor = duration_editor
        self._name_editor = name_editor
        self._increase_editor = increase_editor

        layout = QtWidgets.QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_editor, 0, 1)
        layout.addWidget(duration_label, 1, 0)
        layout.addWidget(duration_editor, 1, 1)
        layout.addWidget(increase_label, 2, 0)
        layout.addWidget(increase_editor, 2, 1)
        layout.addWidget(tab_widget, 3, 0, 1, 4)
        self.setLayout(layout)

    def _pop_msg(self, msg):
        reply = QtWidgets.QMessageBox.critical(self, "error", msg)

    def _get_slot(self, channel_index, _type):
        widget = self._time_editors[channel_index][_type]
        if _type == "high_time":
            f = self._pulse.set_high_time
        elif _type == "high_increase":
            f = self._pulse.set_high_increase
        elif _type == "low_time":
            f = self._pulse.set_low_time
        else:
            f = self._pulse.set_low_increase

        def func():
            try:
                value = int(widget.text())
                f(channel_index, value)
            except:
                self._pop_msg("time must be an integer")

        return func

    def _update_duration(self, channel_index, duration: Tuple[int, int]):
        high_time_editor = self._time_editors[channel_index]['high_time']
        low_time_editor = self._time_editors[channel_index]['low_time']
        high_time_editor.setText(str(duration[0]))
        low_time_editor.setText(str(duration[1]))

    def _update_increase(self, channel_index, increase: Tuple[int, int]):
        high_increase_editor = self._time_editors[channel_index]['high_increase']
        low_increase_editor = self._time_editors[channel_index]['low_increase']
        high_increase_editor.setText(str(increase[0]))
        low_increase_editor.setText(str(increase[1]))


class PulseEditDialog(QtWidgets.QDialog):
    def __init__(self, channel_map: Dict[int, str], pulse: Pulse, parent=None):
        super().__init__(parent)
        self._channel_map = channel_map
        self._pulse = QPulseProxy(pulse)

        font = QtGui.QFont("微软雅黑")
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFont(font)
        name_editor = QtWidgets.QLineEdit(self._pulse.name)
        duration_label = QtWidgets.QLabel("Duration:")
        duration_label.setFont(font)
        duration_spinbox = QtWidgets.QSpinBox()
        duration_spinbox.setSuffix("ns")
        duration_spinbox.setRange(0, int(2.6e9))
        increase_label = QtWidgets.QLabel("Increase:")
        increase_label.setFont(font)
        increase_spinbox = QtWidgets.QSpinBox()
        increase_spinbox.setSuffix("ns")
        increase_spinbox.setRange(0, int(2.6e9))

        self._time_spinbox = dict()

        tab_widget = QtWidgets.QTabWidget()
        for channel_index, channel_name in self._channel_map.items():
            widget = QtWidgets.QWidget()
            high_time_label = QtWidgets.QLabel("High time:")
            high_time_label.setFont(font)
            high_time_spinbox = QtWidgets.QSpinBox()
            high_time_spinbox.setSuffix("ns")
            high_time_spinbox.setRange(duration_spinbox.minimum(), duration_spinbox.value())
            low_time_label = QtWidgets.QLabel("Low time:")
            low_time_label.setFont(font)
            low_time_spinbox = QtWidgets.QSpinBox()
            low_time_spinbox.setSuffix("ns")
            low_time_spinbox.setRange(duration_spinbox.minimum(), duration_spinbox.value())

            high_increase_label = QtWidgets.QLabel("High increase:")
            high_increase_label.setFont(font)
            high_increase_spinbox = QtWidgets.QSpinBox()
            high_increase_spinbox.setSuffix("ns")
            high_increase_spinbox.setRange(increase_spinbox.minimum(), increase_spinbox.value())

            low_increase_label = QtWidgets.QLabel("Low increase:")
            low_increase_label.setFont(font)
            low_increase_spinbox = QtWidgets.QSpinBox()
            low_increase_spinbox.setSuffix("ns")
            low_increase_spinbox.setRange(increase_spinbox.minimum(), increase_spinbox.value())

            high_time_spinbox.valueChanged.connect()

            self._time_spinbox[channel_index]['high_time'] = high_time_spinbox
            self._time_spinbox[channel_index]['low_time'] = low_time_spinbox
            self._time_spinbox[channel_index]['high_increase'] = high_increase_spinbox
            self._time_spinbox[channel_index]['low_increase'] = low_increase_spinbox


class PulseAddDialog(QtWidgets.QDialog):
    sigCreateChild = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        font = QtGui.QFont("微软雅黑")
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFont(font)
        name_editor = QtWidgets.QLineEdit("new child")
        child_select_label = QtWidgets.QLabel("Type:")
        child_select_label.setFont(font)
        child_select_combo_box = QtWidgets.QComboBox()
        child_select_combo_box.addItems(["pulse", "group"])
        loop_label = QtWidgets.QLabel("Loop:")
        loop_label.setFont(font)
        loop_editor = QtWidgets.QLineEdit("1")
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_editor, 0, 1)
        layout.addWidget(child_select_label, 1, 0)
        layout.addWidget(child_select_combo_box, 1, 1)
        layout.addWidget(loop_label, 2, 0)
        layout.addWidget(loop_editor, 2, 1)
        layout.addWidget(button_box, 3, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 3)

        self.setLayout(layout)
        self._name_editor = name_editor
        self._child_select_combo_box = child_select_combo_box
        self._loop_editor = loop_editor
        self._loop_label = loop_label
        self._button_box = button_box

        self._child_select_combo_box.currentIndexChanged.connect(self._on_child_type_changed)
        self._child_select_combo_box.setCurrentIndex(0)
        self._loop_label.setEnabled(False)
        self._loop_editor.setEnabled(False)
        self._button_box.accepted.connect(self._on_accept)
        self._button_box.rejected.connect(self._on_rejected)

    def _on_child_type_changed(self, index):
        if index == 0:
            self._loop_label.setEnabled(False)
            self._loop_editor.setEnabled(False)
        else:
            self._loop_editor.setEnabled(True)
            self._loop_label.setEnabled(True)

    def _on_accept(self):
        can_close = True
        if self._check_name_valid(self._name_editor.text()):
            self._name_editor.setText(self._name_editor.text().rstrip().lstrip())
        else:
            can_close = False

        if not self._check_loop(self._loop_editor.text()):
            can_close = False

        if can_close:
            if self._child_select_combo_box.currentIndex() == 0:
                self.sigCreateChild.emit(Pulse(name=self._name_editor.text()))
            else:
                self.sigCreateChild.emit(
                    Group(name=self._name_editor.text(), repeat_number=int(self._loop_editor.text())))
            self.close()
        else:
            pass

    def _on_rejected(self):
        self.close()

    def _check_loop(self, loop: str):
        try:
            loop = int(loop)
            if loop <= 0:
                self._pop_msg("loop number should be positive")
                return False
            else:
                return True
        except:
            self._pop_msg("loop should be an integer")
            return False

    def _check_name_valid(self, name: str):
        if name.strip() == "":
            self._pop_msg("name can not be empty")
            return False
        else:
            return True

    def _pop_msg(self, msg):
        reply = QtWidgets.QMessageBox.critical(self, "error", msg, QtWidgets.QMessageBox.StandardButton.Ok)


class GroupEditDialog(QtWidgets.QDialog):
    def __init__(self, group: Group, parent=None):
        super().__init__(parent)
        self._group = group

        font = QtGui.QFont("微软雅黑")
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFont(font)
        name_editor = QtWidgets.QLineEdit(group.name)
        loop_label = QtWidgets.QLabel("Loop:")
        loop_label.setFont(font)
        loop_editor = QtWidgets.QLineEdit(str(group.repeat_number))
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_editor, 0, 1)
        layout.addWidget(loop_label, 1, 0)
        layout.addWidget(loop_editor, 1, 1)
        layout.addWidget(button_box, 2, 1)

        self.setLayout(layout)
        self._name_editor = name_editor
        self._loop_editor = loop_editor
        self._button_box = button_box

        self._button_box.accepted.connect(self._on_accepted)
        self._button_box.rejected.connect(self._on_rejected)

    def _on_accepted(self):
        can_close = True

        if self._check_name_valid(self._name_editor.text()):
            self._name_editor.setText(self._name_editor.text().rstrip().lstrip())
        else:
            can_close = False

        if not self._check_loop_valid(self._loop_editor.text()):
            can_close = False

        if can_close:
            self._group.set_name(self._name_editor.text())
            self._group.set_repeat_number(int(self._loop_editor.text()))
            self.close()

    def _on_rejected(self):
        self._name_editor.setText(self._group.name)
        self._loop_editor.setText(str(self._group.repeat_number))
        self.close()

    def _check_name_valid(self, name: str):
        if name.strip() == "":
            self._pop_msg("name can not be empty")
            return False
        return True

    def _check_loop_valid(self, loop: str):
        try:
            loop = int(loop)
            if loop <= 0:
                self._pop_msg("loop must be positive")
                return False
            return True
        except:
            self._pop_msg("loop must be an integer")
            return False

    def _pop_msg(self, msg):
        reply = QtWidgets.QMessageBox.critical(self, "error", msg, QtWidgets.QMessageBox.StandardButton.Ok)


class GroupAddDialog(PulseAddDialog):
    pass


class SegmentEditDialog(QtWidgets.QDialog):
    def __init__(self, segment: Segment, parent=None):
        super().__init__(parent)
        self._segment = segment

        font = QtGui.QFont("微软雅黑")
        name_label = QtWidgets.QLabel("Name:")
        name_label.setFont(font)
        name_editor = QtWidgets.QLineEdit(self._segment.name)
        loop_label = QtWidgets.QLabel("Loop:")
        loop_label.setFont(font)
        loop_editor = QtWidgets.QLineEdit(str(self._segment.loop))
        validator = QtGui.QIntValidator(1, 999, self)
        loop_editor.setValidator(validator)
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)

        layout = QtWidgets.QGridLayout()
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_editor, 0, 1)
        layout.addWidget(loop_label, 1, 0)
        layout.addWidget(loop_editor, 1, 1)
        layout.addWidget(button_box, 2, 1)

        self._name_editor = name_editor
        self._loop_editor = loop_editor
        self._button_box = button_box

        self.setLayout(layout)


if __name__ == '__main__':
    print(id(PulseAddDialog.sigCreateChild), id(GroupAddDialog.sigCreateChild))
    channel_dict = {
        0: "laser",
        1: "mw",
        2: "CH3",
        3: "CH4",
        4: "trigger",
        5: "CH6",
        6: "CH7",
        7: "CH8",
        8: "counter",
        9: "IN2"
    }
    pulse = Pulse(name="start", duration=20, increase=0)
    seg = Segment("step", loop=20)
    app = QtWidgets.QApplication(sys.argv)
    dialog = SegmentEditDialog(seg)
    dialog.show()
    sys.exit(app.exec())
