from PyQt5 import QtGui, QtCore, QtWidgets
from ..Model import constants, serializable

__all__ = ["Port"]


class Port(QtWidgets.QGraphicsWidget, serializable.Serializable):
    """
    The port contains pipes.

    """

    width = 10.0
    color = QtGui.QColor(245, 237, 171, 255)
    border_color = QtGui.QColor(118, 184, 182, 255)
    hovered_color = QtGui.QColor(118, 184, 182, 255)
    hovered_border_color = QtGui.QColor(99, 180, 255, 255)
    activated_color = QtGui.QColor(14, 45, 59, 255)
    activated_border_color = QtGui.QColor(107, 166, 193, 255)

    def __init__(self, port_type, port_truth, parent):
        """
        Create pipes.

        Args:
            port_type: Input 0 or output type 1.
            port_truth: TRUE 1 or FALSE 0.
            parent: Parent item.
        """

        super(Port, self).__init__(parent)
        self.port_type = port_type
        self.port_truth = port_truth
        # BASIC SETTINGS
        self.setAcceptHoverEvents(True)
        self.setFlags(self.ItemSendsScenePositionChanges | self.ItemIsSelectable)
        self.setZValue(constants.Z_VAL_PORT)

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
        """
        Return the node which contains this port.

        """

        return self.parentItem()

    def add_pipes(self, pipe_widget):
        """
        Add pipes in this storage.

        Args:
            pipe_widget: The added pipe widget.

        """

        self.pipes.append(pipe_widget)

    def remove_pipes(self, pipe_widget):
        """
        Delete pipes from this storage.

        Args:
            pipe_widget: The deleted pipe widget.

        """

        if pipe_widget in self.pipes:
            self.pipes.remove(pipe_widget)

    def update_pipes_position(self):
        """
        Update the geometry of pipes.

        """

        for pipe in self.pipes:
            if pipe:
                pipe.update_position()
            else:
                self.pipes.remove(pipe)

    def start_pipes_animation(self):
        """
        Turn on rolling ball effect by ctrl 0.

        """

        for pipe in self.pipes:
            pipe.perform_evaluation_feedback()

    def end_pipes_animation(self):
        """
        Turn off rolling ball effect by ctrl 0.

        """

        for pipe in self.pipes:
            pipe.end_evaluation_feedback()

    def sizeHint(self, which: QtCore.Qt.SizeHint, constraint: QtCore.QSizeF = ...) -> QtCore.QSizeF:
        # Width init
        if self.scene():
            if hasattr(self.scene(), "port_style_width") and self.scene().port_style_width and not self.width_flag:
                self.width = self.scene().port_style_width
        return QtCore.QSizeF(self.width, self.width)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        """
        Draw port widget.

        Args:
            painter: Draw pen.
            option: None.
            widget: None.

        """

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

        # Size init
        if self.scene().port_style_width and not self.width_flag:
            self.width = self.scene().port_style_width
            self.setMaximumSize(self.width, self.width)
            self.updateGeometry()

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

    def serialize(self, port_serialization=None):
        """
        Serialization.

        Args:
            port_serialization: Google protobuff object.

        """

        # port
        port_serialization.port_id = self.id
        port_serialization.port_type = self.port_type
        port_serialization.port_truth = self.port_truth

        # pipes
        for pipe_widget in self.pipes:
            if pipe_widget:
                port_serialization.pipes_id.append(pipe_widget.id)
            else:
                self.pipes.remove(pipe_widget)

        # ui
        port_serialization.port_width = self.width
        port_serialization.port_color.append(self.color.rgba())
        port_serialization.port_color.append(self.border_color.rgba())
        port_serialization.port_color.append(self.hovered_color.rgba())
        port_serialization.port_color.append(self.hovered_border_color.rgba())
        port_serialization.port_color.append(self.activated_color.rgba())
        port_serialization.port_color.append(self.activated_border_color.rgba())

        # flag
        port_serialization.port_flag.append(self.width_flag)
        port_serialization.port_flag.append(self.color_flag)
        port_serialization.port_flag.append(self.border_color_flag)
        port_serialization.port_flag.append(self.hovered_color_flag)
        port_serialization.port_flag.append(self.hovered_border_color_flag)
        port_serialization.port_flag.append(self.activated_color_flag)
        port_serialization.port_flag.append(self.activated_border_color_flag)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        """
        Deserialization.

        Args:
            data: Google protobuff object.
            hashmap: Hashmap.
            view: The manager.
            flag: two times Deserialization.

        """

        if flag:
            # id and hashmap
            self.id = data.port_id
            hashmap[data.port_id] = self

            # style
            self.width = data.port_width

            self.color = QtGui.QColor()
            self.color.setRgba(data.port_color[0])

            self.border_color = QtGui.QColor()
            self.border_color.setRgba(data.port_color[1])

            self.hovered_color = QtGui.QColor()
            self.hovered_color.setRgba(data.port_color[2])

            self.hovered_border_color = QtGui.QColor()
            self.hovered_border_color.setRgba(data.port_color[3])

            self.activated_color = QtGui.QColor()
            self.activated_color.setRgba(data.port_color[4])

            self.activated_border_color = QtGui.QColor()
            self.activated_border_color.setRgba(data.port_color[5])

            # flag
            self.width_flag = data.port_flag[0]
            self.color_flag = data.port_flag[1]
            self.border_color_flag = data.port_flag[2]
            self.hovered_color_flag = data.port_flag[3]
            self.hovered_border_color_flag = data.port_flag[4]
            self.activated_color_flag = data.port_flag[5]
            self.activated_border_color_flag = data.port_flag[6]

        else:
            # deserialize pipes
            pass
