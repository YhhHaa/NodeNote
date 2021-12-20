"""
pipe.py - The connection between attribute widget and logci widget.
"""


import os

from PyQt5 import QtGui, QtCore, QtWidgets
from ..Model import constants, serializable
from ..Components import attribute

__all__ = ["Pipe", "ControlPoint"]


class Pipe(QtWidgets.QGraphicsPathItem, serializable.Serializable):
    """
    A pipe with:
        - Rolling ball effect.
        - Controller point.
        - Text.
    """

    width = 2
    color = QtGui.QColor(225, 192, 241, 255)
    selected_color = QtGui.QColor(0, 153, 121, 255)
    font = QtWidgets.QApplication([]).font()
    font.setPointSize(6)
    font_color = QtGui.QColor(0, 0, 0, 255)

    def __init__(self, start_port=None, end_port=None, node=None):
        """
        Create a pipe.

        Args:
            start_port: The source port widget.
            end_port: The destination port widget.
            node: The attribute widget.
        """

        super(Pipe, self).__init__()
        self.node = node
        self.start_port = start_port
        self.end_port = end_port
        self.start_flag = constants.OUTPUT_NODE_START if self.start_port.port_type == constants.OUTPUT_NODE_TYPE else \
            constants.INPUT_NODE_START

        # BASIC SETTINGS
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setZValue(constants.Z_VAL_PIPE)

        # POS
        self.pos_source = self.start_port.parentItem().get_port_position(self.start_port.port_type,
                                                                         self.start_port.port_truth)
        self.pos_destination = self.pos_source
        self.status = constants.PIPE_STATUS_NEW

        # ANIMATION
        self.timeline = QtCore.QTimeLine(2000)
        self.timeline.frameChanged.connect(self.timeline_frame_changed)
        self.timeline.setLoopCount(0)

        ellips_size = QtCore.QRectF(-5, -5, 10, 10)
        ellips_color = QtGui.QColor(255, 153, 153, 200)
        ellips_thickness = 2
        ellips_pen = QtGui.QPen(ellips_color, ellips_thickness, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap,
                                QtCore.Qt.RoundJoin)
        self.ellips_item = QtWidgets.QGraphicsEllipseItem(ellips_size, self)
        self.ellips_item.setBrush(ellips_color)
        self.ellips_item.setPen(ellips_pen)
        if start_port.port_type == constants.OUTPUT_NODE_TYPE:
            self.ellips_item.setPos(self.path().pointAtPercent(0.0))
            self.timeline.setFrameRange(0, 100)
        else:
            self.ellips_item.setPos(self.path().pointAtPercent(1))
            self.timeline.setFrameRange(100, 0)
        self.ellips_item.hide()

        # EDIT
        self.edit = attribute.SimpleTextField("info", self)
        self.edit.setFont(self.font)
        self.edit.setDefaultTextColor(self.font_color)
        bound_rect_width, bound_rect_height = self.edit.boundingRect().width(), self.edit.boundingRect().height()
        self.edit.setPos(self.path().pointAtPercent(0.5).x() - (bound_rect_width // 2),
                         self.path().pointAtPercent(0.5).y() - (bound_rect_height // 2))

        # CONTROL
        self.choose_first = True

        self.source_item = ControlPoint(self)
        self.destination_item = ControlPoint(self)
        self.show_flag = False
        self.control_line_color = QtGui.QColor(128, 205, 255)

        # Style init
        self.width_flag = False
        self.color_flag = False
        self.selected_color_flag = False
        self.font_type_flag = False
        self.font_color_flag = False

    def perform_evaluation_feedback(self):
        """
        Turn on rolling ball effect.

        """

        if self.timeline.state() == QtCore.QTimeLine.NotRunning:
            self.ellips_item.show()
            self.timeline.start()

    def end_evaluation_feedback(self):
        """
        Turn off rolling ball effect.

        """

        if self.timeline.state() == QtCore.QTimeLine.Running:
            self.ellips_item.hide()
            self.timeline.stop()

    def timeline_frame_changed(self, frame_num):
        """
        Set the position of the rolling ball.

        Args:
            frame_num: Effect number.

        """

        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            point = self.path().pointAtPercent(float(frame_num) / float(self.timeline.endFrame()))
        else:
            point = self.path().pointAtPercent(float(frame_num) / float(self.timeline.startFrame()))
        self.ellips_item.setPos(point)

    def get_input_node(self):
        """
        Get the input node.

        Returns: Input node.

        """

        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            return self.end_port.get_node()
        else:
            return self.start_port.get_node()

    def get_output_node(self):
        """
        Get the output node.

        Returns: Output node.

        """

        if self.start_port.port_type == constants.INPUT_NODE_TYPE:
            return self.end_port.get_node()
        else:
            return self.start_port.get_node()

    def get_output_type_port(self):
        """
        Get output type port

        Returns: Output type port.

        """

        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            return self.start_port
        else:
            return self.end_port

    def get_input_type_port(self):
        """
        Get input type port.

        Returns: Input type port.

        """

        if self.start_port.port_type == constants.INPUT_NODE_TYPE:
            return self.start_port
        else:
            return self.end_port

    def delete_input_type_port(self, pos_destination=None):
        """
        Delete the connections in input type port.

        Args:
            pos_destination: The destination pos.

        """

        if self.start_flag == constants.OUTPUT_NODE_START:

            self.end_port.remove_pipes(self)

            output_node = self.start_port.parentItem()
            input_node = self.end_port.parentItem()
            if isinstance(output_node, attribute.AttributeWidget):
                input_node.remove_last_attribute(output_node)
            else:
                input_node.remove_last_logic(output_node)
            if isinstance(input_node, attribute.AttributeWidget):
                output_node.remove_next_attribute(input_node)
            else:
                output_node.remove_next_logic(input_node)

            self.end_port = None

        elif self.start_flag == constants.INPUT_NODE_START:

            self.start_port.remove_pipes(self)

            output_node = self.end_port.parentItem()
            input_node = self.start_port.parentItem()
            if isinstance(output_node, attribute.AttributeWidget):
                input_node.remove_last_attribute(output_node)
            else:
                input_node.remove_last_logic(output_node)
            if isinstance(input_node, attribute.AttributeWidget):
                output_node.remove_next_attribute(input_node)
            else:
                output_node.remove_next_logic(input_node)

            self.start_port = None

        self.update_position(pos_destination)

    def intersect_with(self, p1, p2):
        """
        Judge whether path intersects self.

        Args:
            p1: The point 1 (cutline point)
            p2: The point 2 (cutline point)

        Returns:
            bool

        """
        cut_path = QtGui.QPainterPath(p1)
        cut_path.lineTo(p2)
        if constants.DEBUG_CUT_LINE:
            print(self, ": ", cut_path.intersects(self.path()))
        return cut_path.intersects(self.path())

    def update_position(self, pos_destination=None):
        """
        Update the pipe position.

        Args:
            pos_destination: The pipe position.

        """

        # source pos
        if self.start_port:
            self.pos_source = self.start_port.parentItem().get_port_position(self.start_port.port_type,
                                                                             self.start_port.port_truth)
        else:
            self.pos_source = self.end_port.parentItem().get_port_position(self.end_port.port_type,
                                                                           self.end_port.port_truth)

        # destination pos
        if self.end_port is not None and self.start_port is not None:
            self.pos_destination = self.end_port.parentItem().get_port_position(self.end_port.port_type,
                                                                                self.end_port.port_truth)
        elif pos_destination is not None:
            self.pos_destination = pos_destination
        else:
            self.pos_destination = self.pos_source

        self.prepareGeometryChange()
        self.start_port.parentItem().layout.activate()
        if self.end_port:
            self.end_port.parentItem().layout.activate()
        self.update()

    # def boundingRect(self) -> QtCore.QRectF:
    #     return QtCore.QRectF(
    #         min(self.pos_source.x(), self.pos_destination.x()),
    #         min(self.pos_source.y(), self.pos_destination.y()),
    #         abs(self.pos_source.x() - self.pos_destination.x()),
    #         abs(self.pos_source.y() - self.pos_destination.y()),
    #     )

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        """
        Draw widget.

        Args:
            painter: Draw pen.
            option: None
            widget: None

        """

        # Width and color init
        if self.scene():
            if self.scene().pipe_style_width and not self.width_flag:
                self.width = self.scene().pipe_style_width
            if self.scene().pipe_style_background_color and not self.color_flag:
                self.color = self.scene().pipe_style_background_color
            if self.scene().pipe_style_selected_background_color and not self.selected_color_flag:
                self.selected_color = self.scene().pipe_style_selected_background_color
            if self.scene().pipe_style_font_type and not self.font_type_flag:
                self.font = self.scene().pipe_style_font_type
            if self.scene().pipe_style_font_color and not self.font_color_flag:
                self.font_color = self.scene().pipe_style_font_color
        
        # font
        if not self.font.family() == self.edit.font().family() or not self.font.pointSize() == self.edit.font().pointSize():
            self.edit.setFont(self.font)
        if self.edit.defaultTextColor().rgba() != self.font_color.rgba():
            self.edit.setDefaultTextColor(self.font_color)

        # DEFAULT PEN
        pen = QtGui.QPen(self.color if not self.isSelected() else self.selected_color)
        pen.setWidth(self.width)

        # DRAGGING PEN
        dragging_pen = QtGui.QPen(self.color)
        dragging_pen.setStyle(QtCore.Qt.DashLine)
        dragging_pen.setWidth(self.width)

        # PATH
        s = self.pos_source
        d = self.pos_destination
        dist = (d.x() - s.x()) * 0.5
        if self.start_port:
            sspos = self.start_port.port_type
        else:
            sspos = self.end_port.port_type
        s_x = +dist
        s_y = 0
        d_x = -dist
        d_y = 0
        if ((s.x() > d.x()) and sspos == constants.OUTPUT_NODE_TYPE) or \
                ((s.x() < d.x()) and sspos == constants.INPUT_NODE_TYPE):
            s_x *= -1  # > 0, s_y = 0  | < 0
            d_x *= -1  # < 0, d_y = 0  | > 0
        path = QtGui.QPainterPath(self.pos_source)

        # create ellipse item
        if not self.source_item.first_flag and not self.destination_item.first_flag:
            self.source_item.first_flag = True
            self.destination_item.first_flag = True
            self.scene().addItem(self.source_item)
            self.scene().addItem(self.destination_item)

        # control show
        if self.show_flag:
            self.source_item.setVisible(True)
            self.destination_item.setVisible(True)
        else:
            self.source_item.setVisible(False)
            self.destination_item.setVisible(False)

        if not self.source_item.moving:
            self.source_item.setPos(
                s.x() + s_x, s.y() + s_y)
        else:
            self.source_item.setPos(self.start_port.scenePos() + self.source_item.offect)
        if not self.destination_item.moving:
            self.destination_item.setPos(
                d.x() + d_x, d.y() + d_y)
        else:
            self.destination_item.setPos(self.start_port.scenePos() + self.destination_item.offect)

        # PEN
        if self.end_port is None or (self.start_flag == constants.INPUT_NODE_START and self.start_port is None):
            painter.setPen(dragging_pen)
        else:
            painter.setPen(pen)

        # DRAW
        path.lineTo(self.source_item.scenePos())
        path.moveTo(self.source_item.scenePos())
        path.lineTo(self.destination_item.scenePos())
        path.moveTo(self.destination_item.scenePos())
        path.lineTo(self.pos_destination)
        path.moveTo(self.pos_destination)
        self.setPath(path)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(self.path())

        # ARROW
        image = QtGui.QPixmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/arrow.png")))
        image_rectf = QtCore.QRectF(image.rect().x(), image.rect().y(), image.rect().width(), image.rect().height())
        target_rectf = QtCore.QRectF(0, 0, 0, 0)
        if self.start_flag == constants.OUTPUT_NODE_START or (self.start_flag == constants.INPUT_NODE_START and
                                                              self.start_port is None):
            target_rectf = QtCore.QRectF(d.x() - image.width() / 2, d.y() - image.height() / 2,
                                         image.width(), image.height())
        elif self.start_flag == constants.INPUT_NODE_START:
            target_rectf = QtCore.QRectF(s.x() - image.width() / 2, s.y() - image.height() / 2,
                                         image.width(), image.height())
        painter.drawPixmap(target_rectf, image, image_rectf)

        # EDIT
        bound_rect_width, bound_rect_height = self.edit.boundingRect().width(), self.edit.boundingRect().height()
        self.edit.setPos(self.path().pointAtPercent(0.5).x() - (bound_rect_width // 2),
                         self.path().pointAtPercent(0.5).y() - (bound_rect_height // 2))

        # ZVALUE
        if self.start_port and self.end_port:
            self.setZValue(constants.Z_VAL_PIPE_DONE)
        else:
            self.setZValue(constants.Z_VAL_PIPE)

    def serialize(self, pipe_serialization=None):
        """
        Serialization.

        Args:
            pipe_serialization: Google protobuff object.

        """

        pipe_serialization.pipe_id = self.id
        pipe_serialization.pipe_port_id.append(self.start_port.id)
        pipe_serialization.pipe_port_id.append(self.end_port.id)
        pipe_serialization.pipe_text = self.edit.toPlainText()

        # control point
        pipe_serialization.start_point.append(self.source_item.scenePos().x())
        pipe_serialization.start_point.append(self.source_item.scenePos().y())
        pipe_serialization.end_point.append(self.destination_item.scenePos().x())
        pipe_serialization.end_point.append(self.destination_item.scenePos().y())
        pipe_serialization.source_move_status = self.source_item.moving
        pipe_serialization.destination_move_status = self.destination_item.moving
        pipe_serialization.offset_start_point.append(self.source_item.offect.x())
        pipe_serialization.offset_start_point.append(self.source_item.offect.y())
        pipe_serialization.offset_destination_point.append(self.destination_item.offect.x())
        pipe_serialization.offset_destination_point.append(self.destination_item.offect.y())

        # ui
        pipe_serialization.self_pipe_width = self.width
        pipe_serialization.self_pipe_color.append(self.color.rgba())
        pipe_serialization.self_pipe_color.append(self.selected_color.rgba())
        pipe_serialization.self_pipe_color.append(self.font_color.rgba())
        pipe_serialization.pipe_font_family = self.font.family()
        pipe_serialization.pipe_font_size = self.font.pointSize()

        # flag
        pipe_serialization.pipe_flag.append(self.width_flag)
        pipe_serialization.pipe_flag.append(self.color_flag)
        pipe_serialization.pipe_flag.append(self.selected_color_flag)
        pipe_serialization.pipe_flag.append(self.font_type_flag)
        pipe_serialization.pipe_flag.append(self.font_color_flag)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        """
        Deserialization.

        Args:
            data: Google protobuff object.
            hashmap: Hashmap.
            view: The manager.
            flag: Deserialization times.

        """

        # added into current scene and view
        view.current_scene.addItem(self)
        view.pipes.append(self)
        # control point
        self.prepareGeometryChange()
        self.source_item.moving = data.source_move_status
        self.destination_item.moving = data.destination_move_status
        self.source_item.setPos(data.start_point[0], data.start_point[1])
        self.destination_item.setPos(data.end_point[0], data.end_point[1])
        self.source_item.offect = QtCore.QPointF(data.offset_start_point[0], data.offset_start_point[1])
        self.destination_item.offect = QtCore.QPointF(data.offset_destination_point[0],
                                                      data.offset_destination_point[1])
        # id and hashmap
        self.id = data.pipe_id
        hashmap[data.pipe_id] = self
        # text
        self.edit.setPlainText(data.pipe_text)
        # style
        self.width = data.self_pipe_width

        self.color = QtGui.QColor()
        self.color.setRgba(data.self_pipe_color[0])

        self.selected_color = QtGui.QColor()
        self.selected_color.setRgba(data.self_pipe_color[1])

        if len(data.self_pipe_color) == 3:
            self.font_color = QtGui.QColor()
            self.font_color.setRgba(data.self_pipe_color[2])

            self.font = QtGui.QFont()
            self.font.setFamily(data.pipe_font_family)
            self.font.setPointSize(data.pipe_font_size)
            self.font_type_flag = data.pipe_flag[3]
            self.font_color_flag = data.pipe_flag[4]

        # flag
        self.width_flag = data.pipe_flag[0]
        self.color_flag = data.pipe_flag[1]
        self.selected_color_flag = data.pipe_flag[2]

        self.update()
        return True


class ControlPoint(QtWidgets.QGraphicsItem):
    """
    Every pipe item has two control points to change its position.

    """

    control_point_radius = 10
    control_point_color = QtGui.QColor(255, 129, 129)
    control_point_border_color = QtGui.QColor(0, 0, 0)

    def __init__(self, pipe_item: Pipe):
        """
        Create control  points.

        Args:
            pipe_item: The pipe item which contains the control point.
        """

        super(ControlPoint, self).__init__(pipe_item)
        self.moving = False
        self.control_point_flag = True
        self.first_flag = False
        self.pipe_item = pipe_item
        self.offect = QtCore.QPointF()
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable |
                      QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setZValue(constants.Z_VAL_PORT)
        self.setVisible(False)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self.control_point_radius, self.control_point_radius)

    def paint(self, painter, option, widget=None) -> None:
        painter.setBrush(self.control_point_color)
        painter.setPen(self.control_point_border_color)
        painter.drawEllipse(self.boundingRect())

    def mouseMoveEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        super(ControlPoint, self).mouseMoveEvent(event)
        self.moving = True
        self.offect = self.scenePos() - self.pipe_item.start_port.scenePos()

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        super(ControlPoint, self).mouseReleaseEvent(event)
        if self.scene().view.undo_flag:
            self.scene().history.store_history("Change Pipe Control Point")
