import time
import os

from PyQt5 import QtCore, QtGui, QtWidgets, sip
from ..Model import constants, serializable


class Canvas(QtGui.QPixmap):
    def __init__(self, width: int = 0, height: int = 0, eraser_color=QtCore.Qt.transparent):
        """
        Create the draw canvas.

        Args:
            width: The canvas width.
            height: The canvas height.
            eraser_color: QtCore.Qt.transparent.
        """

        super(Canvas, self).__init__(width, height)

        # Transparent color
        self.fill(eraser_color)

        # Pixmap path
        self.path = ""

    def save_to_path(self, path) -> bool:
        """
        Save image

        Args:
            path: rel path with work dir

        """

        return self.save(os.path.join(constants.work_dir, path))

    def load_from_path(self, path) -> bool:
        """
        Load image

        Args:
            path: rel path with work dir

        """

        return self.load(os.path.join(constants.work_dir, path))


class Draw(QtWidgets.QGraphicsWidget, serializable.Serializable):
    z_value = constants.Z_VAL_CONTAINERS
    color = constants.draw_color
    pen_width = constants.draw_pen_width

    def __init__(self):
        """
        Create the manager of the draw canvas.
            - Pen width.
            - Pen color.
        """

        super(Draw, self).__init__(parent=None)

        # Size settings
        self.minimum_size = 50
        self.width = 200
        self.height = 200
        self.resize(self.width, self.height)

        # Resize flag
        self.resize_flag = False

        # Interaction settings
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable | QtWidgets.QGraphicsItem.ItemIsMovable |
                      QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges)

        # Draw style and point
        self.device_down = False
        self.last_point = {'pos': QtCore.QPointF(),
                           'pressure': 0.0,
                           'rotation': 0.0}

        self.eraser_color = QtCore.Qt.transparent
        self.brush = QtGui.QBrush(self.color)
        self.pen = QtGui.QPen(self.brush, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)

        # Create canvas
        self.canvas_item = Canvas(self.width, self.height, self.eraser_color)
        self.eraser_flag = False
        self.eraser_rect = QtCore.QSize(10, 10)

    def pressure_to_width(self, pressure: float):
        """
        Translate the pen pressure to pen width.

        Args:
            pressure: The pen pressure.

        Returns:

        """
        return pressure * self.pen_width

    def update_brush(self, event: QtGui.QTabletEvent):
        """
        Update the pen brush according to the tablet event.

        Args:
            event: QtGui.QTabletEvent

        """

        hue, saturation, value, alpha = self.color.getHsv()
        # Set alpha channel
        self.color.setAlphaF(event.pressure())
        # Set color saturation
        self.color.setHsv(hue, int(event.pressure() * 255) if int(event.pressure() * 255) > 200 else 200, value, alpha)
        # Set line width
        self.pen.setWidthF(self.pressure_to_width(event.pressure()))
        # Set color
        if event.pointerType() == QtGui.QTabletEvent.Eraser:
            self.eraser_flag = True

            # Change eraser cursor
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                                      'Resources/Images/eraser.png'))).scaled(20, 20)
            cursor = QtGui.QCursor(cursor_style, 10, 10)
            QtWidgets.QApplication.setOverrideCursor(cursor)

            # Set eraser width
            self.pen.setWidthF(10.0)
        else:
            self.eraser_flag = False

            # Change draw cursor
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                                      'Resources/Images/point.png'))).scaled(10, 10)
            cursor = QtGui.QCursor(cursor_style, 5, 5)
            QtWidgets.QApplication.setOverrideCursor(cursor)

            # Set draw color
            self.brush.setColor(self.color)
            self.pen.setColor(self.color)

    def paint_pixmap(self, painter: QtGui.QPainter, event: QtGui.QTabletEvent):
        """
        Draw pixmap according to the tablet event.

        Args:
            painter: The draw pen.
            event: QtGui.QTabletEvent

        """

        # Draw settings
        max_pen_radius = self.pressure_to_width(1.0)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        # Draw line
        painter.setPen(self.pen)
        painter.drawLine(self.last_point['pos'], self.mapFromScene(self.scene().view.mapToScene(event.pos())))
        self.update(QtCore.QRectF(self.last_point['pos'],
                                  self.mapFromScene(self.scene().view.mapToScene(event.pos()))).
                    normalized().adjusted(-max_pen_radius, -max_pen_radius, max_pen_radius, max_pen_radius))

    def paint(self, painter: QtGui.QPainter, option=None, widget=None) -> None:
        # Set painter render hint.
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        # set ZValue
        self.setZValue(self.z_value)

        # Draw border
        painter.setPen(QtGui.QColor(255, 255, 255, 255) if not self.isSelected() else QtGui.QColor(255, 0, 0, 255))
        painter.drawRect(self.boundingRect())

        # Draw pixmap
        painter.drawPixmap(self.boundingRect(), self.canvas_item, self.boundingRect())

    def tablet_event(self, event: QtGui.QTabletEvent):
        """
        Custom tablet event which is given by the manager.

        Args:
            event: The manager tablet event.

        """

        if event.deviceType() == QtGui.QTabletEvent.Stylus:

            if event.type() == QtCore.QEvent.TabletPress:
                self.device_down = True
                self.last_point['pos'] = self.mapFromScene(self.scene().view.mapToScene(event.pos()))
                self.last_point['pressure'] = event.pressure()
                self.last_point['rotation'] = event.rotation()

            elif event.type() == QtCore.QEvent.TabletMove:
                if self.device_down:
                    # Update draw style
                    self.update_brush(event)

                    # Draw pixmap
                    painter = QtGui.QPainter(self.canvas_item)
                    if self.eraser_flag:
                        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
                    self.paint_pixmap(painter, event)

                    # Store current info
                    self.last_point['pos'] = self.mapFromScene(self.scene().view.mapToScene(event.pos()))
                    self.last_point['pressure'] = event.pressure()
                    self.last_point['rotation'] = event.rotation()

            elif event.type() == QtCore.QEvent.TabletRelease:
                if self.device_down and event.buttons() == QtCore.Qt.NoButton:
                    self.device_down = False
                self.update()

    def mousePressEvent(self, event) -> None:
        if not self.scene().view.tablet_used:
            # Start resizing
            if int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                super(Draw, self).mousePressEvent(event)
                self.resize_flag = True
                self.setCursor(QtCore.Qt.SizeAllCursor)

    def mouseMoveEvent(self, event) -> None:
        if not self.scene().view.tablet_used:
            # Resizing
            if self.resize_flag:
                past_pos = self.scenePos()
                past_width = self.size().width()
                past_height = self.size().height()
                current_pos = self.mapToScene(event.pos())
                current_width = current_pos.x() - past_pos.x() if current_pos.x() >= past_pos.x() else past_width
                current_height = current_pos.y() - past_pos.y() if current_pos.y() >= past_pos.y() else past_height
                if current_width >= self.minimum_size and current_height >= self.minimum_size:
                    self.resize(current_width, current_height)
                    new_canvas = Canvas(current_width, current_height, self.eraser_color)
                    painter = QtGui.QPainter(new_canvas)
                    painter.drawPixmap(QtCore.QRectF(0, 0, self.canvas_item.width(), self.canvas_item.height()),
                                       self.canvas_item,
                                       QtCore.QRectF(0, 0, self.canvas_item.width(), self.canvas_item.height()))
                    sip.delete(self.canvas_item)
                    self.canvas_item = new_canvas
            else:
                super(Draw, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if not self.scene().view.tablet_used:
            super(Draw, self).mouseReleaseEvent(event)
            if self.resize_flag:
                self.resize_flag = False
                self.setCursor(QtCore.Qt.ArrowCursor)

    def serialize(self, draw_serialization=None):
        # Path
        if not self.canvas_item.path:
            if not os.path.exists(os.path.join(constants.work_dir, "Assets")):
                os.makedirs(os.path.join(constants.work_dir, "Assets"))
            self.canvas_item.path = os.path.relpath(os.path.join(os.path.join(constants.work_dir, "Assets"),
                                                 time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '.png'), constants.work_dir)
        self.canvas_item.save_to_path(self.canvas_item.path)
        draw_serialization.path = self.canvas_item.path

        # Geometry
        draw_serialization.draw_id = self.id
        draw_serialization.draw_size.append(self.size().width())
        draw_serialization.draw_size.append(self.size().height())
        draw_serialization.draw_pos.append(self.scenePos().x())
        draw_serialization.draw_pos.append(self.scenePos().y())

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # Added
        view.current_scene.addItem(self)
        view.draw_widgets.append(self)

        # Geometry
        self.id = data.draw_id
        self.resize(data.draw_size[0], data.draw_size[1])
        self.setPos(data.draw_pos[0], data.draw_pos[1])

        # Path
        self.canvas_item.path = data.path
        self.canvas_item.load_from_path(self.canvas_item.path)
        self.update()


class SideDraw(QtWidgets.QWidget):
    color = constants.draw_color
    pen_width = constants.draw_pen_width

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


        # Focus setting
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Size settings
        self.minimum_size = 50
        self.width = self.width()
        self.height = self.height()

        # Draw style and point
        self.device_down = False
        self.last_point = {'pos': QtCore.QPointF(),
                           'pressure': 0.0,
                           'rotation': 0.0}

        self.eraser_color = QtCore.Qt.transparent
        self.brush = QtGui.QBrush(self.color)
        self.pen = QtGui.QPen(self.brush, 1, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin)

        # Create canvas
        self.canvas_item = Canvas(self.width, self.height, QtCore.Qt.darkYellow)
        self.eraser_flag = False
        self.eraser_rect = QtCore.QSize(10, 10)
    
    def pressure_to_width(self, pressure: float):
        """
        Translate the pen pressure to pen width.

        Args:
            pressure: The pen pressure.

        Returns:

        """
        return pressure * self.pen_width

    def update_brush(self, event: QtGui.QTabletEvent):
        """
        Update the pen brush according to the tablet event.

        Args:
            event: QtGui.QTabletEvent

        """

        hue, saturation, value, alpha = self.color.getHsv()
        # Set alpha channel
        self.color.setAlphaF(event.pressure())
        # Set color saturation
        self.color.setHsv(hue, int(event.pressure() * 255) if int(event.pressure() * 255) > 200 else 200, value, alpha)
        # Set line width
        self.pen.setWidthF(self.pressure_to_width(event.pressure()))
        # Set color
        if event.pointerType() == QtGui.QTabletEvent.Eraser:
            self.eraser_flag = True

            # Change eraser cursor
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                                      'Resources/Images/eraser.png'))).scaled(20, 20)
            cursor = QtGui.QCursor(cursor_style, 10, 10)
            QtWidgets.QApplication.setOverrideCursor(cursor)

            # Set eraser width
            self.pen.setWidthF(10.0)
        else:
            self.eraser_flag = False

            # Change draw cursor
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                                      'Resources/Images/point.png'))).scaled(10, 10)
            cursor = QtGui.QCursor(cursor_style, 5, 5)
            QtWidgets.QApplication.setOverrideCursor(cursor)

            # Set draw color
            self.brush.setColor(self.color)
            self.pen.setColor(self.color)
    
    def paint_pixmap(self, painter: QtGui.QPainter, event: QtGui.QTabletEvent):
        """
        Draw pixmap according to the tablet event.

        Args:
            painter: The draw pen.
            event: QtGui.QTabletEvent

        """

        # Draw settings
        max_pen_radius = self.pressure_to_width(1.0)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        # Draw line
        painter.setPen(self.pen)
        painter.drawLine(self.last_point['pos'], event.pos())
        self.update(QtCore.QRect(self.last_point['pos'],
                                  event.pos()).
                    normalized().adjusted(-max_pen_radius, -max_pen_radius, max_pen_radius, max_pen_radius))
    
    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

        # Draw pixmap
        painter.drawPixmap(self.rect(), self.canvas_item, self.rect())
        return super().paintEvent(a0)
    
    def tabletEvent(self, event: QtGui.QTabletEvent) -> None:
        # Change style when the pen almost enter
        if event.type() == QtCore.QEvent.TabletEnterProximity:
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                      'Resources/Images/point.png'))).scaled(10,
                                                                                        10)
            cursor = QtGui.QCursor(cursor_style, 5, 5)
            QtWidgets.QApplication.setOverrideCursor(cursor)

        if event.deviceType() == QtGui.QTabletEvent.Stylus:

            if event.type() == QtCore.QEvent.TabletPress:
                self.device_down = True
                self.last_point['pos'] = event.pos()
                self.last_point['pressure'] = event.pressure()
                self.last_point['rotation'] = event.rotation()

            elif event.type() == QtCore.QEvent.TabletMove:
                if self.device_down:
                    # Update draw style
                    self.update_brush(event)

                    # Draw pixmap
                    painter = QtGui.QPainter(self.canvas_item)
                    if self.eraser_flag:
                        painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
                    self.paint_pixmap(painter, event)

                    # Store current info
                    self.last_point['pos'] = event.pos()
                    self.last_point['pressure'] = event.pressure()
                    self.last_point['rotation'] = event.rotation()

            elif event.type() == QtCore.QEvent.TabletRelease:
                if self.device_down and event.buttons() == QtCore.Qt.NoButton:
                    self.device_down = False

            self.update()

        return super().tabletEvent(event)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key_W and self.height - 50 > 0:
            self.height -= 50
            self.resize(self.width, self.height)
            self.change_width(self.width, self.height)
        elif a0.key() == QtCore.Qt.Key_S:
            self.height += 50
            self.resize(self.width, self.height)
            self.change_width(self.width, self.height)
        elif a0.key() == QtCore.Qt.Key_A and self.width - 50 > 0:
            self.width -= 50
            self.resize(self.width, self.height)
            self.change_width(self.width, self.height)
        elif a0.key() == QtCore.Qt.Key_D:
            self.width += 50
            self.resize(self.width, self.height)
            self.change_width(self.width, self.height)
        return super().keyPressEvent(a0)

    def change_width(self, width, height):
        new_canvas = Canvas(width, height, self.eraser_color)
        painter = QtGui.QPainter(new_canvas)
        painter.drawPixmap(QtCore.QRectF(0, 0, self.canvas_item.width(), self.canvas_item.height()),
                            self.canvas_item,
                            QtCore.QRectF(0, 0, self.canvas_item.width(), self.canvas_item.height()))
        sip.delete(self.canvas_item)
        self.canvas_item = new_canvas

        self.update()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        self.change_width(a0.size().width(), a0.size().height())
        return super().resizeEvent(a0)
