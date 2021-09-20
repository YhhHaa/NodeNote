from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore, QtGui
from GraphicsView import view
from Model import constants, serializable


class ProxyView(QtWidgets.QGraphicsProxyWidget, serializable.Serializable):
    def __init__(self, root_window, parent=None):
        super(ProxyView, self).__init__(parent)

        # input method
        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, True)
        self.setAttribute(QtCore.Qt.WA_KeyCompression, True)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

        # new widgets
        self.root_window = root_window
        self.sub_view_widget = QtWidgets.QWidget()
        self.sub_view_widget_layout = QtWidgets.QVBoxLayout()
        self.sub_view_widget_view = view.View(self.root_window, None, False, self)
        # connections
        # init layout
        self.sub_view_widget_layout.setContentsMargins(0, 0, 0, 0)
        self.sub_view_widget_layout.setSpacing(0)
        # init sub view widget
        self.sub_view_widget_layout.addWidget(self.sub_view_widget_view)
        self.sub_view_widget.setLayout(self.sub_view_widget_layout)
        # init proxy widget
        self.setWidget(self.sub_view_widget)
        self.setZValue(constants.Z_VAL_NODE)

        # index
        self.item_row = 0
        self.item_column = 0

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        super(ProxyView, self).mousePressEvent(event)
        self.root_window.view_widget.current_scene.clearSelection()
        self.scene().clearSelection()


    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('size', (self.size().width(), self.size().height())),
            ('row', self.item_row),
            ('column', self.item_column),
            ('sub view', self.sub_view_widget_view.serialize())
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        self.id = data['id']
        self.resize(data['size'][0], data['size'][1])
        self.item_row = data['row']
        self.item_column = data['column']
        self.sub_view_widget_view.deserialize(data['sub view'], hashmap, view, flag)
