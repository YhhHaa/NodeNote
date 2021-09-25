from PyQt5 import QtCore, QtGui, QtWidgets


__all__ = ["EffectWater"]


class EffectWater(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(EffectWater, self).__init__(parent)

        # water ui
        self.water_color = QtGui.QColor("#FF6699FF")
        self.circle_big_size = 10.0
        self.circle_small_size = 0.0
        self.design_ui()

        # water animation
        self.water_animation = QtCore.QVariantAnimation(self)

    def design_ui(self):
        self.setFixedSize(QtCore.QSize(int(self.circle_big_size * 2), int(self.circle_big_size * 2)))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAutoFillBackground(True)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(255, 255, 255, 255))
        self.setPalette(palette)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def move(self, a0) -> None:
        true_pos = a0 - QtCore.QPoint(int(self.circle_big_size), int(self.circle_big_size))
        super(EffectWater, self).move(QtCore.QPoint(true_pos.x(), true_pos.y()))

    def show(self):
        super(EffectWater, self).show()
        self.water_animation.setStartValue(0.0)
        self.water_animation.setEndValue(self.circle_big_size)
        self.water_animation.setDuration(350)
        self.water_animation.valueChanged.connect(self.circle_repaint)
        self.water_animation.finished.connect(self.close)
        self.water_animation.start()

    def circle_repaint(self, value):
        self.circle_small_size = value
        self.update()

    def paintEvent(self, a0) -> None:
        # painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(self.water_color))
        # paint two circle
        big_circle = QtGui.QPainterPath()
        big_circle.addEllipse(QtCore.QPointF(self.circle_big_size, self.circle_big_size),
                              self.circle_big_size, self.circle_big_size)
        small_circle = QtGui.QPainterPath()
        small_circle.addEllipse(QtCore.QPointF(self.circle_big_size, self.circle_big_size),
                                self.circle_small_size, self.circle_small_size)
        circle = big_circle - small_circle
        painter.drawPath(circle)
