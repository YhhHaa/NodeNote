from PyQt5 import QtWidgets, QtGui, QtCore
from ..Model import constants


__all__ = ['EffectCutline']


class EffectCutline(QtWidgets.QGraphicsItem):

    def __init__(self, parent=None):
        """
        Cutline which is used to delete the pipes.
        Delete logic is defined in manager.
        """

        super(EffectCutline, self).__init__(parent)
        self.line_points = []
        self.pen = QtGui.QPen(QtCore.Qt.white, 2)
        self.pen.setDashPattern([3, 2])
        self.setZValue(constants.Z_VAL_CUTLINE)

    def boundingRect(self) -> QtCore.QRectF:
        if self.line_points:
            left_x = float("+inf")
            up_y = float("+inf")
            right_x = float("-inf")
            down_y = float("-inf")

            for point in self.line_points:
                if point.x() <= left_x:
                    left_x = point.x()
                if point.y() <= up_y:
                    up_y = point.y()
                if point.x() >= right_x:
                    right_x = point.y()
                if point.y() >= down_y:
                    down_y = point.y()

            return QtCore.QRectF(QtCore.QPointF(left_x, up_y), QtCore.QPointF(right_x, down_y))

        else:
            return QtCore.QRectF(QtCore.QPointF(0, 0), QtCore.QPointF(1, 1))

    def paint(self, painter, option, widget=None) -> None:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self.pen)

        poly = QtGui.QPolygonF(self.line_points)
        painter.drawPolyline(poly)
