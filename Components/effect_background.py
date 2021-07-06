from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg


__all__ = ["EffectBackground"]


class EffectBackground(QtSvg.QGraphicsSvgItem):
    def __init__(self, view, parent=None):
        super(EffectBackground, self).__init__(parent)
        self.view = view
        self.width = 1080
        self.height = 900
        self.name = "Resources/Background/soft.svg"
        self.svg = QtSvg.QSvgRenderer(self.name)
        self.setSharedRenderer(self.svg)

    def resize(self, width, height):
        self.width = width
        self.height = height

    def change_svg(self, path):
        self.name = path
        self.svg = QtSvg.QSvgRenderer(path)
        self.setSharedRenderer(self.svg)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        painter.save()
        self.renderer().render(painter, self.boundingRect())
        painter.restore()
