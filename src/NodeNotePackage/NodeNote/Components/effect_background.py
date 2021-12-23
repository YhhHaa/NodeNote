import os

from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg


__all__ = ["EffectBackground"]


class EffectBackground(QtSvg.QGraphicsSvgItem):

    name = os.path.abspath((os.path.join(os.path.dirname(__file__),
                                                        "../Resources/background_tree.svg")))
                                                        
    def __init__(self, view, parent=None):
        """
        Scene svg background image.

        Args:
            view: The manager.
            parent: Parent item.
        """

        super(EffectBackground, self).__init__(parent)
        self.view = view
        self.width = 1080
        self.height = 900
        self.svg = QtSvg.QSvgRenderer(self.name)
        self.setSharedRenderer(self.svg)
        self.setCacheMode(QtWidgets.QGraphicsItem.ItemCoordinateCache)

    def resize(self, width, height):
        """
        Change the size.

        Args:
            width: The manager width.
            height: The manager height.

        """

        self.width = width
        self.height = height

    def change_svg(self, path):
        """
        Change the svg image.

        Args:
            path: Svg image path.

        """

        self.name = path
        self.svg = QtSvg.QSvgRenderer(path)
        self.setSharedRenderer(self.svg)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget=None) -> None:
        super(EffectBackground, self).paint(painter, option, widget)
        painter.save()
        self.renderer().render(painter, self.boundingRect())
        painter.restore()
