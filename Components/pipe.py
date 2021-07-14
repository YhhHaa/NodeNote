from collections import OrderedDict
from PyQt5 import QtGui, QtCore, QtWidgets
from Model import constants, serializable
from Components import attribute, port

__all__ = ["Pipe", "ControlPoint"]


class Pipe(QtWidgets.QGraphicsPathItem, serializable.Serializable):
    width = 2
    color = QtGui.QColor(0, 255, 204, 128)
    selected_color = QtGui.QColor(0, 153, 121, 255)

    def __init__(self, start_port=None, end_port=None, node=None):
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
        self.edit.setFont(QtGui.QFont("LucidaMacBold", 8))
        self.edit.setDefaultTextColor(QtCore.Qt.black)
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

    def perform_evaluation_feedback(self):
        if self.timeline.state() == QtCore.QTimeLine.NotRunning:
            self.ellips_item.show()
            self.timeline.start()

    def end_evaluation_feedback(self):
        if self.timeline.state() == QtCore.QTimeLine.Running:
            self.ellips_item.hide()
            self.timeline.stop()

    def timeline_frame_changed(self, frame_num):
        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            point = self.path().pointAtPercent(float(frame_num) / float(self.timeline.endFrame()))
        else:
            point = self.path().pointAtPercent(float(frame_num) / float(self.timeline.startFrame()))
        self.ellips_item.setPos(point)

    def get_input_node(self):
        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            return self.end_port.get_node()
        else:
            return self.start_port.get_node()

    def get_output_node(self):
        if self.start_port.port_type == constants.INPUT_NODE_TYPE:
            return self.end_port.get_node()
        else:
            return self.start_port.get_node()

    def get_output_type_port(self):
        if self.start_port.port_type == constants.OUTPUT_NODE_TYPE:
            return self.start_port
        else:
            return self.end_port

    def get_input_type_port(self):
        if self.start_port.port_type == constants.INPUT_NODE_TYPE:
            return self.start_port
        else:
            return self.end_port

    def delete_input_type_port(self, pos_destination=None):
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
        cut_path = QtGui.QPainterPath(p1)
        cut_path.lineTo(p2)
        if constants.DEBUG_CUT_LINE:
            print(self, ": ", cut_path.intersects(self.path()))
        return cut_path.intersects(self.path())

    def update_position(self, pos_destination=None):
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

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(
            min(self.pos_source.x(), self.pos_destination.x()),
            min(self.pos_source.y(), self.pos_destination.y()),
            abs(self.pos_source.x() - self.pos_destination.x()),
            abs(self.pos_source.y() - self.pos_destination.y()),
        ).adjusted(-self.width / 2, -self.width / 2, +self.width / 2, +self.width / 2)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        painter.save()
        # Width and color init
        if self.scene():
            if self.scene().pipe_style_width and not self.width_flag:
                self.width = self.scene().pipe_style_width
            if self.scene().pipe_style_background_color and not self.color_flag:
                self.color = self.scene().pipe_style_background_color
            if self.scene().pipe_style_selected_background_color and not self.selected_color_flag:
                self.selected_color = self.scene().pipe_style_selected_background_color
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
        image = QtGui.QPixmap("Resources/Pipe/arrow.png")
        image_rectf = QtCore.QRectF(image.rect().x(), image.rect().y(), image.rect().width(), image.rect().height())
        target_rectf = QtCore.QRectF(0, 0, 0, 0)
        if self.start_flag == constants.OUTPUT_NODE_START or (self.start_flag == constants.INPUT_NODE_START and
                                                              self.start_port is None):
            target_rectf = QtCore.QRectF(d.x() - port.Port.width / 2, d.y() - port.Port.width / 2,
                                         image.width(), image.height())
        elif self.start_flag == constants.INPUT_NODE_START:
            target_rectf = QtCore.QRectF(s.x() - port.Port.width / 2, s.y() - port.Port.width / 2,
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

        painter.restore()

    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('start port', self.start_port.id),
            ('end port', self.end_port.id if self.end_port else None),
            ("text", self.edit.toPlainText()),
            # control point
            ('start control point x', self.source_item.scenePos().x()),
            ('start control point y', self.source_item.scenePos().y()),
            ('end control point x', self.destination_item.scenePos().x()),
            ('end control point y', self.destination_item.scenePos().y()),
            ('source moving status', self.source_item.moving),
            ('destination moving status', self.destination_item.moving),
            ('start offect point x', self.source_item.offect.x()),
            ('start offect point y', self.source_item.offect.y()),
            ('destination offect point x', self.destination_item.offect.x()),
            ('destination offect point y', self.destination_item.offect.y()),
            # style
            ('width', self.width),
            ('color', self.color.rgba()),
            ('selected color', self.selected_color.rgba()),
            ('width flag', self.width_flag),
            ('color flag', self.color_flag),
            ('selected color flag', self.selected_color_flag)
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # added into current scene and view
        view.current_scene.addItem(self)
        view.pipes.append(self)
        # control point
        self.prepareGeometryChange()
        self.source_item.moving = data['source moving status']
        self.destination_item.moving = data['destination moving status']
        self.source_item.setPos(data['start control point x'], data['start control point y'])
        self.destination_item.setPos(data['end control point x'], data['end control point y'])
        self.source_item.offect = QtCore.QPointF(data['start offect point x'], data['start offect point y'])
        self.destination_item.offect = QtCore.QPointF(data['destination offect point x'],
                                                      data['destination offect point y'])
        # id and hashmap
        self.id = data['id']
        hashmap[data['id']] = self
        # text
        self.edit.setPlainText(data['text'])
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

        self.update()
        return True


class ControlPoint(QtWidgets.QGraphicsItem):
    control_point_radius = 10
    control_point_color = QtGui.QColor(255, 129, 129)
    control_point_border_color = QtGui.QColor(0, 0, 0)

    def __init__(self, pipe_item: Pipe):
        super(ControlPoint, self).__init__()
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
        self.scene().view.history.store_history("Change Pipe Control Point")
        if self.scene().view.filename and not self.scene().view.first_open:
            self.scene().view.save_to_file()
