import warnings
from collections import OrderedDict
from PyQt5 import QtWidgets, QtCore, QtGui
from Components import effect_background, effect_cutline, attribute, pipe, container, port
from Model import serializable, constants

__all__ = ["Scene"]


class Scene(QtWidgets.QGraphicsScene, serializable.Serializable):
    def __init__(self, sub_scene_flag, view, attribute_widget=None, parent=None):
        super(Scene, self).__init__(parent)
        self.view = view
        self.attribute_widget = attribute_widget
        self.setSceneRect(QtCore.QRectF())
        self.sub_scene_flag = sub_scene_flag

        # background image
        self.background_image = effect_background.EffectBackground(self.view)
        self.background_image.resize(self.view.size().width(), self.view.size().width())
        self.background_image.setPos(self.view.mapToScene(0, 0).x(), self.view.mapToScene(0, 0).y())
        self.addItem(self.background_image)
        self.background_image.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

        # CUT LINE
        self.cutline = effect_cutline.EffectCutline()
        self.addItem(self.cutline)

        #   =============== attribute widget========================
        #       font
        self.attribute_style_font = None
        self.attribute_style_font_color = None
        #       color
        self.attribute_style_background_color = None
        self.attribute_style_selected_background_color = None
        self.attribute_style_border_color = None
        self.attribute_style_selected_border_color = None
        #   =================================================

        #   =============== logic widget==========================
        #       color
        self.logic_style_background_color = None
        self.logic_style_selected_background_color = None
        self.logic_style_border_color = None
        self.logic_style_selected_border_color = None
        #   =================================================

        #   =============== pipe widget==========================
        #       width
        self.pipe_style_width = None
        #       color
        self.pipe_style_background_color = None
        self.pipe_style_selected_background_color = None
        #   =================================================

        #   =============== port widget==========================
        #       width
        self.port_style_width = None
        #       color
        self.port_style_color = None
        self.port_style_border_color = None
        self.port_style_hovered_color = None
        self.port_style_hovered_border_color = None
        self.port_style_activated_color = None
        self.port_style_activated_border_color = None
        #   =================================================

        #   =============== container widget========================
        self.container_style_width = None
        self.container_style_color = None
        self.container_style_selected_color = None
        #   =================================================

        #   Background
        self.brush = QtGui.QBrush(QtGui.QImage("Resources/Background/scene_background.png"))
        self.setBackgroundBrush(self.brush)

    def get_id_attribute(self, attribute_id) -> attribute.AttributeWidget:
        for item in self.items():
            if isinstance(item, attribute.AttributeWidget):
                if item.id == attribute_id:
                    return item

    def get_id_logic(self, logic_id) -> attribute.LogicWidget:
        for item in self.items():
            if isinstance(item, attribute.LogicWidget):
                if item.id == logic_id:
                    return item

    def get_id_port(self, port_id) -> port.Port:
        for item in self.items():
            if isinstance(item, attribute.AttributeWidget):
                if item.true_input_port.id == port_id:
                    return item.true_input_port
                elif item.false_input_port.id == port_id:
                    return item.false_input_port
                elif item.true_output_port.id == port_id:
                    return item.true_output_port
                elif item.false_output_port.id == port_id:
                    return item.false_output_port
            elif isinstance(item, attribute.LogicWidget):
                if item.input_port.id == port_id:
                    return item.input_port
                elif item.output_port.id == port_id:
                    return item.output_port

    def get_id_pipe(self, pipe_id) -> pipe.Pipe:
        for item in self.items():
            if isinstance(item, pipe.Pipe):
                if item.id == pipe_id:
                    return item

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(Scene, self).drawBackground(painter, rect)

    def serialize(self):
        attribute_widgets = list()
        logic_widgets = list()
        pipe_widgets = list()
        container_widgets = list()

        for item in self.items():
            if isinstance(item, attribute.AttributeWidget):
                attribute_widgets.append(item.serialize())
            elif isinstance(item, attribute.LogicWidget):
                logic_widgets.append(item.serialize())
            elif isinstance(item, pipe.Pipe):
                pipe_widgets.append(item.serialize())
            elif isinstance(item, container.Container):
                container_widgets.append(item.serialize())

        return OrderedDict([
            ('id', self.id),

            ('attribute widgets', attribute_widgets),
            ('logic widgets', logic_widgets),
            ('pipe widgets', pipe_widgets),
            ('container widgets', container_widgets),

            ('background image', self.background_image.name),

            ('attribute font family', self.attribute_style_font.family() if self.attribute_style_font else None),
            ('attribute font size', self.attribute_style_font.pointSize() if self.attribute_style_font else None),
            ('attribute font color', self.attribute_style_font_color.rgba()
            if self.attribute_style_font_color else None),
            ('attribute color', self.attribute_style_background_color.rgba()
            if self.attribute_style_background_color else None),
            ('attribute selected color', self.attribute_style_selected_background_color.rgba()
            if self.attribute_style_selected_background_color else None),
            ('attribute border color', self.attribute_style_border_color.rgba()
            if self.attribute_style_border_color else None),
            ('attribute selected border color', self.attribute_style_selected_border_color.rgba()
            if self.attribute_style_selected_border_color else None),
            ('logic color', self.logic_style_background_color.rgba()
            if self.logic_style_background_color else None),
            ('logic selected color', self.logic_style_selected_background_color.rgba()
            if self.logic_style_selected_background_color else None),
            ('logic border color', self.logic_style_border_color.rgba()
            if self.logic_style_border_color else None),
            ('logic selected border color', self.logic_style_selected_border_color.rgba()
            if self.logic_style_selected_border_color else None),
            ('pipe width', self.pipe_style_width if self.pipe_style_width else None),
            ('pipe color', self.pipe_style_background_color.rgba() if self.pipe_style_background_color else None),
            ('pipe selected color', self.pipe_style_selected_background_color.rgba()
            if self.pipe_style_selected_background_color else None),
            ('port width', self.port_style_width if self.port_style_width else None),
            ('port color', self.port_style_color.rgba() if self.port_style_color else None),
            ('port border color', self.port_style_border_color.rgba() if self.port_style_border_color else None),
            ('port hovered color', self.port_style_hovered_color.rgba() if self.port_style_hovered_color else None),
            ('port hovered border color', self.port_style_hovered_border_color.rgba()
            if self.port_style_hovered_border_color else None),
            ('port activated color', self.port_style_activated_color.rgba()
            if self.port_style_activated_color else None),
            ('port activated border color', self.port_style_activated_border_color.rgba()
            if self.port_style_activated_border_color else None),
            ('container width', self.container_style_width if self.container_style_width else None),
            ('container color', self.container_style_color.rgba() if self.container_style_color else None),
            ('container selected color', self.container_style_selected_color.rgba()
            if self.container_style_selected_color else None)
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        if flag is True:
            # deserialize id
            self.id = data['id']
            hashmap[data['id']] = self
            # deserialize attribute widgets with (id, geometry)
            for attribute_data in data['attribute widgets']:
                attribute.AttributeWidget().deserialize(attribute_data, hashmap, view, flag=True)
            # deserialize logic widgets with (id, geometry)
            for logic_data in data['logic widgets']:
                attribute.LogicWidget().deserialize(logic_data, hashmap, view, flag=True)
            # deserialize pipe widgets with all
            for pipe_data in data['pipe widgets']:
                start_port = self.get_id_port(pipe_data['start port'])
                if constants.DEBUG_DESERIALIZE:
                    print("find start port: ", start_port,
                          "\nstart port id: ", pipe_data['start port'])
                end_port = self.get_id_port(pipe_data['end port'])
                pipe.Pipe(start_port, end_port, None).deserialize(pipe_data, hashmap, view, flag=True)
                start_port.update_pipes_position()
                end_port.update_pipes_position()
            # deserialize container widgets with all
            for container_data in data['container widgets']:
                container.Container(QtCore.QPointF(container_data['points'][0][0], container_data['points'][0][1])). \
                    deserialize(container_data, hashmap, view, flag)
            # background image
            self.background_image.change_svg(data['background image'])
            # style
            if data['attribute font family'] and data['attribute font size']:
                font = QtGui.QFont()
                font.setFamily(data['attribute font family'])
                font.setPointSize(data['attribute font size'])
                self.attribute_style_font = font
            else:
                self.attribute_style_font = None

            if data['attribute font color']:
                self.attribute_style_font_color = QtGui.QColor()
                self.attribute_style_font_color.setRgba(data['attribute font color'])
            else:
                self.attribute_style_font_color = None

            if data['attribute color']:
                self.attribute_style_background_color = QtGui.QColor()
                self.attribute_style_background_color.setRgba(data['attribute color'])
            else:
                self.attribute_style_background_color = None

            if data['attribute selected color']:
                self.attribute_style_selected_background_color = QtGui.QColor()
                self.attribute_style_selected_background_color.setRgba(data['attribute selected color'])
            else:
                self.attribute_style_selected_background_color = None

            if data['attribute border color']:
                self.attribute_style_border_color = QtGui.QColor()
                self.attribute_style_border_color.setRgba(data['attribute border color'])
            else:
                self.attribute_style_border_color = None

            if data['attribute selected border color']:
                self.attribute_style_selected_border_color = QtGui.QColor()
                self.attribute_style_selected_border_color.setRgba(data['attribute selected border color'])
            else:
                self.attribute_style_selected_border_color = None

            if data['logic color']:
                self.logic_style_background_color = QtGui.QColor()
                self.logic_style_background_color.setRgba(data['logic color'])
            else:
                self.logic_style_background_color = None

            if data['logic selected color']:
                self.logic_style_selected_background_color = QtGui.QColor()
                self.logic_style_selected_background_color.setRgba(data['logic selected color'])
            else:
                self.logic_style_selected_background_color = None

            if data['logic border color']:
                self.logic_style_border_color = QtGui.QColor()
                self.logic_style_border_color.setRgba(data['logic border color'])
            else:
                self.logic_style_border_color = None

            if data['logic selected border color']:
                self.logic_style_selected_border_color = QtGui.QColor()
                self.logic_style_selected_border_color.setRgba(data['logic selected border color'])
            else:
                self.logic_style_selected_border_color = None

            if data['pipe width']:
                self.pipe_style_width = data['pipe width']
            else:
                self.pipe_style_width = None

            if data['pipe color']:
                self.pipe_style_background_color = QtGui.QColor()
                self.pipe_style_background_color.setRgba(data['pipe color'])
            else:
                self.pipe_style_background_color = None

            if data['pipe selected color']:
                self.pipe_style_selected_background_color = QtGui.QColor()
                self.pipe_style_selected_background_color.setRgba(data['pipe selected color'])
            else:
                self.pipe_style_selected_background_color = None

            if data['port width']:
                self.port_style_width = data['port width']
            else:
                self.port_style_width = None

            if data['port color']:
                self.port_style_color = QtGui.QColor()
                self.port_style_color.setRgba(data['port color'])
            else:
                self.port_style_color = None

            if data['port border color']:
                self.port_style_border_color = QtGui.QColor()
                self.port_style_border_color.setRgba(data['port border color'])
            else:
                self.port_style_border_color = None

            if data['port hovered color']:
                self.port_style_hovered_color = QtGui.QColor()
                self.port_style_hovered_color.setRgba(data['port hovered color'])
            else:
                self.port_style_hovered_color = None

            if data['port hovered border color']:
                self.port_style_hovered_border_color = QtGui.QColor()
                self.port_style_hovered_border_color.setRgba(data['port hovered border color'])
            else:
                self.port_style_hovered_border_color = None

            if data['port activated color']:
                self.port_style_activated_color = QtGui.QColor()
                self.port_style_activated_color.setRgba(data['port activated color'])
            else:
                self.port_style_activated_color = None

            if data['port activated border color']:
                self.port_style_activated_border_color = QtGui.QColor()
                self.port_style_activated_border_color.setRgba(data['port activated border color'])
            else:
                self.port_style_activated_border_color = None

            if data['container width']:
                self.container_style_width = data['container width']
            else:
                self.container_style_width = None

            if data['container color']:
                self.container_style_color = QtGui.QColor()
                self.container_style_color.setRgba(data['container color'])
            else:
                self.container_style_color = None

            if data['container selected color']:
                self.container_style_selected_color = QtGui.QColor()
                self.container_style_selected_color.setRgba(data['container selected color'])
            else:
                self.container_style_selected_color = None

        elif flag is False:
            for item in self.items():
                # deserialize attribute widgets second time
                if isinstance(item, attribute.AttributeWidget):
                    # deserialize attribute widgets with attribute sub widgets
                    for attribute_widget_data in data['attribute widgets']:
                        if item.id == attribute_widget_data['id']:
                            # deserialize sub attribute widgets
                            for attribute_sub_id in attribute_widget_data['attribute sub widgets']:
                                if isinstance(attribute_sub_id, int):
                                    sub_attribute_widget = self.get_id_attribute(attribute_sub_id)
                                    item.attribute_sub_widgets.append(sub_attribute_widget)
                                    item.attribute_layout.addItem(sub_attribute_widget,
                                                                  sub_attribute_widget.item_row,
                                                                  sub_attribute_widget.item_column)
                                elif isinstance(attribute_sub_id, dict):
                                    from Components.sub_view import ProxyView
                                    from Components.todo import Todo
                                    if 'file' in attribute_sub_id:
                                        attribute_sub = attribute.AttributeFile(item)
                                        attribute_sub.deserialize(attribute_sub_id, hashmap, view, flag)
                                    elif 'task' in attribute_sub_id:
                                        attribute_sub = Todo(item)
                                        attribute_sub.deserialize(attribute_sub_id, hashmap, view, flag)
                                    else:
                                        attribute_sub = ProxyView(self.view.mainwindow)
                                        attribute_sub.deserialize(attribute_sub_id, hashmap,
                                                                  attribute_sub.sub_view_widget_view, flag=True)
                                    item.attribute_sub_widgets.append(attribute_sub)
                                    item.attribute_layout.addItem(attribute_sub,
                                                                  attribute_sub.item_row,
                                                                  attribute_sub.item_column)
                            item.text_change_node_shape()
                            # deserialize attribute widgets with attribute next widgets
                            for attribute_next_id in attribute_widget_data['next attribute widgets']:
                                next_attribute_widget = self.get_id_attribute(attribute_next_id)
                                item.next_attribute.append(next_attribute_widget)
                                if constants.DEBUG_DESERIALIZE:
                                    print("deserialize attribute widget: ", item,
                                          "add next attribute: ", next_attribute_widget,
                                          "current next attribute: ", item.next_attribute)
                            # deserialize attribute widgets with attribute last widgets
                            for attribute_last_id in attribute_widget_data['last attribute widgets']:
                                last_attribute_widget = self.get_id_attribute(attribute_last_id)
                                item.last_attribute.append(last_attribute_widget)
                                if constants.DEBUG_DESERIALIZE:
                                    print("deserialize attribute widget: ", item,
                                          "add last attribute: ", last_attribute_widget,
                                          "current last attribute: ", item.last_attribute)
                            # deserialize attribute widgets with logic next widgets
                            for logic_next_id in attribute_widget_data['next logic widgets']:
                                next_logic_widget = self.get_id_logic(logic_next_id)
                                item.next_logic.append(next_logic_widget)
                            # deserialize attribute widgets with logic next widgets
                            for logic_last_id in attribute_widget_data['last logic widgets']:
                                last_logic_widget = self.get_id_logic(logic_last_id)
                                item.last_logic.append(last_logic_widget)
                            # deserialize attribute widgets with pipes
                            for pipe_id in attribute_widget_data['input true port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.true_input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data['input false port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.false_input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data['output true port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.true_output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data['output false port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.false_output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                # deserialize logic widgets second time
                elif isinstance(item, attribute.LogicWidget):
                    for logic_widget_data in data['logic widgets']:
                        # traverse list and find right logic
                        if item.id == logic_widget_data['id']:
                            # deserialize logic widgets with attribute next widgets
                            for attribute_next_id in logic_widget_data['next attribute widgets']:
                                next_attribute_widget = self.get_id_attribute(attribute_next_id)
                                item.next_attribute.append(next_attribute_widget)
                            # deserialize logic widgets with attribute last widgets
                            for attribute_last_id in logic_widget_data['last attribute widgets']:
                                last_attribute_widget = self.get_id_attribute(attribute_last_id)
                                item.last_attribute.append(last_attribute_widget)
                            # deserialize logic widgets with logic next widgets
                            for logic_next_id in logic_widget_data['next logic widgets']:
                                next_logic_widget = self.get_id_logic(logic_next_id)
                                item.next_logic.append(next_logic_widget)
                            # deserialize logic widgets with logic last widgets
                            for logic_last_id in logic_widget_data['last logic widgets']:
                                last_logic_widget = self.get_id_logic(logic_last_id)
                                item.last_logic.append(last_logic_widget)
                            # deserialize logic widgets with ports
                            for pipe_id in logic_widget_data['input port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in logic_widget_data['output port']['pipes']:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
        return True
