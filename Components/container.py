from collections import OrderedDict
from PyQt5 import QtWidgets, QtGui, QtCore
from Model import constants, serializable


class Container(QtWidgets.QGraphicsPathItem, serializable.Serializable):
    width = 10
    color = QtGui.QColor(255, 255, 255, 255)
    selected_color = QtGui.QColor(128, 0, 0, 128)

    def __init__(self, pos, parent=None):
        super(Container, self).__init__(parent)
        self.start_point = pos
        self.next_point = QtCore.QPointF()
        self.nex_pressure = 0
        self.points = list()
        self.points.append((pos.x(), pos.y()))
        self.pressures = list()
        self.pressures.append(self.nex_pressure)

        self.draw_path = QtGui.QPainterPath(self.start_point)

        self.pen = QtGui.QPen(self.color, self.width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self.selected_pen = QtGui.QPen(self.selected_color, self.width)

        self.setZValue(constants.Z_VAL_CONTAINERS)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)

        self.deserialize_flag = False

        # Style
        self.width_flag = False
        self.color_flag = False
        self.selected_color_flag = False

    def boundingRect(self) -> QtCore.QRectF:
        left_x = float("+inf")
        up_y = float("+inf")
        right_x = float("-inf")
        down_y = float("-inf")

        for point in self.points:
            if point[0] <= left_x:
                left_x = point[0]
            if point[1] <= up_y:
                up_y = point[1]
            if point[0] >= right_x:
                right_x = point[0]
            if point[1] >= down_y:
                down_y = point[1]

        return QtCore.QRectF(QtCore.QPointF(left_x, up_y), QtCore.QPointF(right_x, down_y))

    def update_brush(self, point: tuple, pressure):
        self.next_point = point
        self.nex_pressure = pressure

        #   Width and color init
        if self.scene().container_style_width and not self.width_flag:
            self.width = self.scene().container_style_width
        if self.scene().container_style_color and not self.color_flag:
            self.color = self.scene().container_style_selected_color
        if self.scene().container_style_selected_color and not self.selected_color_flag:
            self.selected_color = self.scene().container_style_selected_color

        self.selected_pen = QtGui.QPen(self.selected_color, self.width)

        hue, saturation, value, alpha = self.color.getHsv()

        self.color.setAlphaF(self.nex_pressure)
        self.color.setHsv(hue, int(self.nex_pressure * 255.0), value, alpha)
        self.pen.setWidthF(self.nex_pressure * self.width)
        self.pen.setColor(self.color)

        self.update()

    def paint(self, painter, option, widget=None) -> None:
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self.pen if not self.isSelected() else self.selected_pen)

        if not self.deserialize_flag:
            if self.next_point and self.nex_pressure:
                self.points.append((self.next_point[0], self.next_point[1]))
                self.pressures.append(self.nex_pressure)
                self.draw_path.lineTo(QtCore.QPointF(self.next_point[0], self.next_point[1]))
                self.draw_path.moveTo(QtCore.QPointF(self.next_point[0], self.next_point[1]))
            self.setPath(self.draw_path)
            painter.drawPath(self.path())
        else:
            for index in range(len(self.points)):
                self.update_brush(self.points[index], self.pressures[index])
                self.draw_path.lineTo(QtCore.QPointF(self.next_point[0], self.next_point[1]))
                self.draw_path.moveTo(QtCore.QPointF(self.next_point[0], self.next_point[1]))
            self.setPath(self.draw_path)
            painter.drawPath(self.path())
            self.deserialize_flag = False

        painter.restore()

    def serialize(self, container_serialization=None):
        container_serialization.container_id = self.id
        for point in self.points:
            point_data = container_serialization.points.add()
            point_data.x = point[0]
            point_data.y = point[1]
        for pressure in self.pressures:
            container_serialization.pressures.append(pressure)

        # ui
        container_serialization.self_container_width = self.width
        container_serialization.self_container_color.append(self.color.rgba())
        container_serialization.self_container_color.append(self.selected_color.rgba())

        # flag
        container_serialization.self_container_flag.append(self.width_flag)
        container_serialization.self_container_flag.append(self.color_flag)
        container_serialization.self_container_flag.append(self.selected_color_flag)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # added into scene and view
        view.current_scene.addItem(self)
        view.containers.append(self)
        # id
        self.id = data.container_id
        # draw point
        self.points = []
        for point in data.points:
            self.points.append((point.x, point.y))
        for pressure in data.pressures:
            self.pressures.append(pressure)
        self.deserialize_flag = True
        # style
        self.width = data.self_container_width

        self.color = QtGui.QColor()
        self.color.setRgba(data.self_container_color[0])

        self.selected_color = QtGui.QColor()
        self.selected_color.setRgba(data.self_container_color[1])

        # flag
        self.width_flag = data.self_container_flag[0]
        self.color_flag = data.self_container_flag[1]
        self.selected_color_flag = data.self_container_flag[2]

        return True
