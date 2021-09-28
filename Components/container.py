import math

from collections import OrderedDict
from PyQt5 import QtWidgets, QtGui, QtCore
from Model import constants, serializable


class Container(QtWidgets.QGraphicsPathItem, serializable.Serializable):
    width = 1
    color = QtGui.QColor(0, 51, 102, 255)
    selected_color = QtGui.QColor(128, 0, 0, 128)

    def __init__(self, last_point, parent=None):
        super(Container, self).__init__(parent)
        self.last_point = last_point
        self.current_point = {}
        self.draw_line = QtGui.QPainterPath(self.last_point['pos'])

        self._brush = QtGui.QBrush(self.color)
        self._pen = QtGui.QPen(self._brush, self.width, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)
        self._selected_pen = QtGui.QPen(self.selected_color, self.width)

        self.update_flag = False

        self.setZValue(constants.Z_VAL_CONTAINERS)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)

        self.deserialize_flag = False

    def boundingRect(self) -> QtCore.QRectF:
        return self.draw_line.boundingRect()

    def update_brush(self, *args):
        self.current_point['pos'] = args[0]
        self.current_point['pressure'] = args[1]
        self.current_point['rotation'] = args[2]

        hue, saturation, value, alpha = self.color.getHsv()

        self.color.setAlphaF(self.current_point['pressure'])
        self.color.setHsv(hue, int(self.current_point['pressure'] * 255.0), value, alpha)

        self._pen.setWidthF(self.width * self.current_point['pressure'])
        self._pen.setColor(self.color)

        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(self.color)

        self.draw_line.lineTo(self.current_point['pos'])
        self.draw_line.moveTo(self.current_point['pos'])

        self.update()

    def paint(self, painter, option, widget=None) -> None:
        painter.save()

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self._pen)
        painter.setBrush(self._brush)

        self.setPath(self.draw_line)
        painter.drawPath(self.path())

        painter.restore()

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('width', self.width),
            ('color', self.color.rgba()),
            ('selected color', self.selected_color.rgba()),
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # added into scene and view
        view.current_scene.addItem(self)
        view.containers.append(self)
        # id
        self.id = data['id']
        # draw point
        self.points = data['points']
        self.deserialize_flag = True
        # style
        self.width = data['width']

        self.color = QtGui.QColor()
        self.color.setRgba(data['color'])

        self.selected_color = QtGui.QColor()
        self.selected_color.setRgba(data['selected color'])

        # flag
        self.width_flag = data['width flag']
        self.color_flag = data['color flag']
        self.selected_color_flag = data['selected color flag']

        return True


#         half_width = self.last_point['pressure']
#         brush_adjust = QtCore.QPointF(math.sin(math.radians(-self.last_point['rotation'])) * half_width,
#                                       math.cos(math.radians(-self.last_point['rotation'])) * half_width)
#         self.poly.append(self.last_point['pos'] + brush_adjust)
#         self.poly.append(self.last_point['pos'] - brush_adjust)
#
#         half_width = self._pen.widthF()
#         brush_adjust = QtCore.QPointF(math.sin(math.radians(-self.current_point['rotation'])) * half_width,
#                                       math.cos(math.radians(-self.current_point['rotation'])) * half_width)
#         self.poly.append(self.current_point['pos'] - brush_adjust)
#         self.poly.append(self.current_point['pos'] + brush_adjust)