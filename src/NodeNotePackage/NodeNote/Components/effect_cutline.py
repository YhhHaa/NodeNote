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
            x__min_point = min([point.x() for point in self.line_points])
            y__min_point = min([point.y() for point in self.line_points])
            x__max_point = max([point.x() for point in self.line_points])
            y__max_point = max([point.y() for point in self.line_points])
            return QtCore.QRectF(x__min_point, y__min_point, x__max_point - x__min_point, y__max_point - y__min_point)
        else:
            return QtCore.QRectF(0, 0, 1, 1)


    def paint(self, painter, option, widget=None) -> None:
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(self.pen)

        poly = QtGui.QPolygonF(self.line_points)
        painter.drawPolyline(poly)
