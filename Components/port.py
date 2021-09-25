from collections import OrderedDict
from PyQt5 import QtGui, QtCore, QtWidgets
from Model import constants, serializable

__all__ = ["Port"]


class Port(QtWidgets.QGraphicsWidget, serializable.Serializable):

    width = 16.0
    color = QtGui.QColor(49, 115, 100, 255)
    border_color = QtGui.QColor(29, 202, 151, 255)
    hovered_color = QtGui.QColor(17, 43, 82, 255)
    hovered_border_color = QtGui.QColor(136, 255, 35, 255)
    activated_color = QtGui.QColor(14, 45, 59, 255)
    activated_border_color = QtGui.QColor(107, 166, 193, 255)

    def __init__(self, port_type, port_truth, parent):
        super(Port, self).__init__(parent)
        self.port_type = port_type
        self.port_truth = port_truth
        # BASIC SETTINGS
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemSendsScenePositionChanges | self.ItemIsSelectable)
        self.setZValue(constants.Z_VAL_PORT)
        self.setCacheMode(constants.ITEM_CACHE_MODE)

        # STORE PIPES
        self.pipes = list()

        # DRAW PARAMETERS
        self.border_size = 1
        self.hovered = False

        # Style init
        self.width_flag = False
        self.color_flag = False
        self.border_color_flag = False
        self.hovered_color_flag = False
        self.hovered_border_color_flag = False
        self.activated_color_flag = False
        self.activated_border_color_flag = False

    def get_node(self):
        return self.parentItem()

    def add_pipes(self, pipe_widget):
        self.pipes.append(pipe_widget)

    def remove_pipes(self, pipe_widget):
        if pipe_widget in self.pipes:
            self.pipes.remove(pipe_widget)

    def update_pipes_position(self):
        for pipe in self.pipes:
            pipe.update_position()

    def start_pipes_animation(self):
        for pipe in self.pipes:
            pipe.perform_evaluation_feedback()

    def end_pipes_animation(self):
        for pipe in self.pipes:
            pipe.end_evaluation_feedback()

    def boundingRect(self) -> QtCore.QRectF:
        # Width init
        if self.scene().port_style_width and not self.width_flag:
            self.width = self.scene().port_style_width
        return QtCore.QRectF(0.0, 0.0, self.width, self.width)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        # Color init
        if self.scene().port_style_color and not self.color_flag:
            self.color = self.scene().port_style_color
        if self.scene().port_style_border_color and not self.border_color_flag:
            self.border_color = self.scene().port_style_border_color
        if self.scene().port_style_hovered_color and not self.hovered_color_flag:
            self.hovered_color = self.scene().port_style_hovered_color
        if self.scene().port_style_hovered_border_color and not self.hovered_border_color_flag:
            self.hovered_border_color = self.scene().port_style_hovered_border_color
        if self.scene().port_style_activated_color and not self.activated_color_flag:
            self.activated_color = self.scene().port_style_activated_color
        if self.scene().port_style_activated_border_color and not self.activated_border_color_flag:
            self.activated_border_color = self.scene().port_style_activated_border_color
        # SIZE
        rect_width = self.width / 1.8
        rect_height = self.width / 1.8
        rect_x = self.boundingRect().center().x() - (rect_width / 2)
        rect_y = self.boundingRect().center().y() - (rect_height / 2)
        port_rect = QtCore.QRectF(rect_x, rect_y, rect_width, rect_height)

        # COLOR
        if self.hovered:
            color = self.hovered_color
            border_color = self.hovered_border_color
        elif self.pipes:
            color = self.activated_color
            border_color = self.activated_border_color
        else:
            color = self.color
            border_color = self.border_color

        # PAINTER
        pen = QtGui.QPen(border_color, 1.8)
        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawEllipse(port_rect)

        # OTHER OPTIONS
        if self.pipes and not self.hovered:
            painter.setBrush(border_color)
            w = port_rect.width() / 2.5
            h = port_rect.height() / 2.5
            rect = QtCore.QRectF(port_rect.center().x() - w / 2,
                                 port_rect.center().y() - h / 2,
                                 w, h)
            border_color = self.border_color
            pen = QtGui.QPen(border_color, 1.6)
            painter.setPen(pen)
            painter.setBrush(border_color)
            painter.drawEllipse(rect)
        elif self.hovered:
            if len(self.pipes) >= 2:
                pen = QtGui.QPen(border_color, 1.4)
                painter.setPen(pen)
                painter.setBrush(color)
                w = port_rect.width() / 1.8
                h = port_rect.height() / 1.8
            else:
                painter.setBrush(border_color)
                w = port_rect.width() / 3.5
                h = port_rect.height() / 3.5
            rect = QtCore.QRectF(port_rect.center().x() - w / 2,
                                 port_rect.center().y() - h / 2,
                                 w, h)
            painter.drawEllipse(rect)

    def hoverEnterEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        self.hovered = True
        super(Port, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QtWidgets.QGraphicsSceneHoverEvent) -> None:
        self.hovered = False
        super(Port, self).hoverLeaveEvent(event)

    def serialize(self):
        pipes = list()
        for pipe_widget in self.pipes:
            pipes.append(pipe_widget.id)

        return OrderedDict([
            ('id', self.id),
            ('port type', self.port_type),
            ('port truth', self.port_truth),
            ('pipes', pipes),
            # style
            ('width', self.width),
            ('color', self.color.rgba()),
            ('border color', self.border_color.rgba()),
            ('hovered color', self.hovered_color.rgba()),
            ('hovered border color', self.hovered_border_color.rgba()),
            ('activated color', self.activated_color.rgba()),
            ('activated border color', self.activated_border_color.rgba()),
            # flag
            ('width flag', self.width_flag),
            ('color flag', self.color_flag),
            ('border color flag', self.border_color_flag),
            ('hovered color flag', self.hovered_color_flag),
            ('hovered border color flag', self.hovered_border_color_flag),
            ('activated color flag', self.activated_color_flag),
            ('activated border color flag', self.activated_border_color_flag)
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        if flag:
            # id and hashmap
            self.id = data['id']
            hashmap[data['id']] = self

            # style
            self.width = data['width']

            self.color = QtGui.QColor()
            self.color.setRgba(data['color'])

            self.border_color = QtGui.QColor()
            self.border_color.setRgba(data['border color'])

            self.hovered_color = QtGui.QColor()
            self.hovered_color.setRgba(data['hovered color'])

            self.hovered_border_color = QtGui.QColor()
            self.hovered_border_color.setRgba(data['hovered border color'])

            self.activated_color = QtGui.QColor()
            self.activated_color.setRgba(data['activated color'])

            self.activated_border_color = QtGui.QColor()
            self.activated_border_color.setRgba(data['activated border color'])

            # flag
            self.width_flag = data['width flag']
            self.color_flag = data['color flag']
            self.border_color_flag = data['border color flag']
            self.hovered_color_flag = data['hovered color flag']
            self.hovered_border_color_flag = data['hovered border color flag']
            self.activated_color_flag = data['activated color flag']
            self.activated_border_color_flag = data['activated border color flag']

        else:
            # deserialize pipes
            pass
