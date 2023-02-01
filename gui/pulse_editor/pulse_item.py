import sys

from PyQt5.QtWidgets import QTreeWidgetItem, QWidget, QPushButton, QHBoxLayout, QSizePolicy, QTreeWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from util.Mixin import BaseMixin
from logic.sequence import Pulse, Group, Sequence, Segment
import os


class QButtons(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        art_work_path = os.path.join(os.path.dirname(__file__), "../artwork")
        add_button = QPushButton()
        add_button.setIcon(QIcon(os.path.join(art_work_path, "add_icon.svg")))
        delete_button = QPushButton()
        delete_button.setIcon(QIcon(os.path.join(art_work_path, "delete_icon.svg")))
        edit_button = QPushButton()
        edit_button.setIcon(QIcon(os.path.join(art_work_path, "edit_icon.svg")))
        layout = QHBoxLayout()
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        layout.addWidget(add_button)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class PulseWidgetItem(QTreeWidgetItem, BaseMixin):
    def __init__(self, root: QTreeWidget, parent=None):
        super().__init__(parent)
        self._data = Pulse("new pulse", 10)
        self._buttons = QButtons()
        self._root = root
        self._sequence = self._root.children()[0]



if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QTreeWidget, QTreeWidgetItem

    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.resize(640, 480)
    buttons = QButtons()
    grid_layout = QGridLayout()
    tree_widget = QTreeWidget()
    tree_widget.setColumnCount(5)
    item1 = QTreeWidgetItem(tree_widget)
    item2 = QTreeWidgetItem()
    item2.setText(0, "item2")
    item2.setText(4, "test")
    item1.setText(0, "item1")
    tree_widget.setItemWidget(item1, 1, buttons)
    grid_layout.addWidget(tree_widget)
    main_window.setLayout(grid_layout)
    item1.addChild(item2)
    # main_window.show()

    tree_widget.show()
    sys.exit(app.exec())
