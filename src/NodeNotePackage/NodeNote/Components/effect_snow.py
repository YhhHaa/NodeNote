import random
import os

from PyQt5 import QtCore, QtGui, QtWidgets, sip
from ..Model.constants import DEBUG_EFFECT_SNOW


__all__ = ["EffectSkyWidget"]


class EffectSkyWidget(QtWidgets.QWidget):
    timer = QtCore.QTimer()

    def __init__(self, view_widget, parent=None):
        """
        Create the sky contains flowing image.

        Args:
            view_widget: The manager.
            parent: Parent item.
        """

        super(EffectSkyWidget, self).__init__(parent)
        self.view_widget = view_widget
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        self.path_list = list()
        self.index = 0
        self.timer.timeout.connect(self.snow_create)
        self.timer.start(6000)

    def snow_create(self):
        """
        Create flowing image.

        """

        # DEBUG
        if DEBUG_EFFECT_SNOW:
            print("1-Debug:    snow_create function running")
        # create snow widget and its path
        snow_widget = SnowWidget(self)
        opacity_snow = QtWidgets.QGraphicsOpacityEffect(snow_widget)
        run_path = QtCore.QPropertyAnimation(snow_widget, b"pos")
        opacity_path = QtCore.QPropertyAnimation(opacity_snow, b"opacity")
        self.path_list.append(QtCore.QParallelAnimationGroup())
        self.snow_falling(snow_widget, run_path, opacity_path, self.path_list[self.index])
        self.index += 1

    def snow_falling(self, snow_widget, run_path, opacity_path, path_group):
        """
        Falling image.

        Args:
            snow_widget: The flowing image.
            run_path: The flowing path.
            opacity_path: The opacity.
            path_group: The start object.

        """

        # DEBUG
        if DEBUG_EFFECT_SNOW:
            print("2-Debug:    snow_falling function running")
        # pos and size
        start_x = random.randint(0, int(self.width()))
        start_y = random.randint(0, int(self.height()))
        random_size = random.randint(0, 9)
        width = 24 if random_size >= 6 else (18 if random_size >= 3 else 12)
        height = 24 if random_size >= 6 else (18 if random_size >= 3 else 12)
        snow_widget.setGeometry(start_x, start_y, width, height)
        snow_widget.setVisible(True)

        # fall speed
        fall_time_run_path = random.randint(25000, 30000)
        fall_time_opacity_path = random.randint(25000, 30000)
        run_path.setStartValue(QtCore.QPoint(start_x, start_y))
        run_path.setEndValue(QtCore.QPoint(start_x, self.height()))
        run_path.setDuration(fall_time_run_path)
        run_path.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        opacity_path.setStartValue(1)
        opacity_path.setEndValue(0)
        opacity_path.setDuration(fall_time_opacity_path)
        path_group.addAnimation(run_path)
        path_group.addAnimation(opacity_path)

        # falling
        path_group.start()
        path_group.finished.connect(lambda: self.snow_end(snow_widget, path_group))

    def snow_end(self, snow_widget, path_group):
        """
        Delete the finished image.

        Args:
            snow_widget:
            path_group:

        Returns:

        """
        sip.delete(snow_widget)
        self.index -= 1
        self.path_list.remove(path_group)
        if DEBUG_EFFECT_SNOW:
            print("3-Debug:    delete snow widget successfully")


class SnowWidget(QtWidgets.QWidget):
    image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Resources/flower.png'))

    def __init__(self, parent=None):
        """
        Create flowing image.

        Args:
            parent: Parent item.
        """

        super(SnowWidget, self).__init__(parent)

    def change_image_path(self, path):
        """
        Change the flowing image.

        Args:
            path: The flowing image path.

        """

        self.image_path = path
        self.update()

    def paintEvent(self, event):
        """
        Draw the flowing image.

        Args:
            event: QPaintevent.

        """

        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), QtGui.QPixmap(self.image_path), QtCore.QRect())
