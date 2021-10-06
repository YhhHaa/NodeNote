import time
from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore, QtGui
from Components.attribute import AttributeWidget
from Model import serializable, constants, stylesheet


class Todo(QtWidgets.QGraphicsWidget, serializable.Serializable):
    def __init__(self, parent=None):
        super(Todo, self).__init__(parent)

        self.parent_item = parent

        # common setting
        self.setZValue(constants.Z_VAL_NODE)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # widget
        self.central_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.control_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)

        self.edit = QtWidgets.QLineEdit("task")
        self.edit.setStyleSheet(stylesheet.STYLE_QLINEEDIT)

        self.time_show = QtWidgets.QLabel("0:0:0 + 0:0:0")
        self.time_show.setStyleSheet(stylesheet.STYLE_QLABEL)
        self.time_show.setMinimumWidth(135)

        self.start_png = QtGui.QIcon(QtGui.QPixmap('Resources/TodoList/start.png'))
        self.pause_png = QtGui.QIcon(QtGui.QPixmap('Resources/TodoList/pause.png'))
        self.time_button = QtWidgets.QToolButton()
        self.time_button.setIcon(self.start_png)
        self.time_button.setStyleSheet(stylesheet.STYLE_QTOOLBUTTON)

        self.graphics_edit = QtWidgets.QGraphicsProxyWidget()
        self.graphics_edit.setWidget(self.edit)

        self.graphics_show = QtWidgets.QGraphicsProxyWidget()
        self.graphics_show.setWidget(self.time_show)

        self.graphics_button = QtWidgets.QGraphicsProxyWidget()
        self.graphics_button.setWidget(self.time_button)

        self.central_layout.addItem(self.graphics_edit)
        self.central_layout.addItem(self.control_layout)
        self.control_layout.addItem(self.graphics_show)
        self.control_layout.addItem(self.graphics_button)
        self.setLayout(self.central_layout)

        # control
        self.start = True
        self.total_time = 0
        self.start_time = 0
        self.use_time = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.time_update)
        self.time_button.pressed.connect(self.turn_start if self.start else self.turn_pause)

        # layout
        self.item_row = 0
        self.item_column = 0

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        painter.save()

        pen = QtGui.QPen(AttributeWidget.border_color, 0.5)
        selected_pen = QtGui.QPen(AttributeWidget.selected_border_color, 0.5)
        painter.setPen(pen if not self.isSelected() else selected_pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRoundedRect(0, 0, self.size().width(), self.size().height(), 5, 5)

        painter.restore()

    def turn_start(self):
        self.time_button.setIcon(self.pause_png)
        self.timer.start(1000)
        self.start_time = time.time()
        self.time_button.pressed.connect(self.turn_pause)

    def turn_pause(self):
        self.time_button.setIcon(self.start_png)
        self.timer.stop()
        self.time_button.pressed.connect(self.turn_start)
        self.total_time += self.use_time
        self.start_time = time.time()
        self.time_update()

    def time_update(self):
        total_time_hour = int(self.total_time // 60 // 60)
        total_time_min = int((self.total_time // 60) - 60 * total_time_hour)
        total_time_sec = int(self.total_time - 60 * 60 * total_time_hour - 60 * total_time_min)

        self.use_time = time.time() - self.start_time
        use_time_hour = int(self.use_time // 60 // 60)
        use_time_min = int((self.use_time // 60) - 60 * use_time_hour)
        use_time_sec = int(self.use_time - 60 * 60 * use_time_hour - 60 * use_time_min)

        self.time_show.setText('%s:%s:%s' % (total_time_hour, total_time_min, total_time_sec) +
                               ' + %s:%s:%s' % (use_time_hour, use_time_min, use_time_sec))

    def serialize(self, todo_serialization=None):
        todo_serialization.todo_id = self.id
        todo_serialization.task = self.edit.text()
        todo_serialization.time = self.total_time
        todo_serialization.todo_location.append(self.item_row)
        todo_serialization.todo_location.append(self.item_column)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        self.id = data.todo_id
        self.edit.setText(data.task)
        self.total_time = data.time
        self.item_row = data.todo_location[0]
        self.item_column = data.todo_location[1]

        self.start_time = time.time()
        self.time_update()
