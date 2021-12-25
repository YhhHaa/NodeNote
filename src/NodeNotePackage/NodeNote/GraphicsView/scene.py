"""
Sets the scene stylesheet and serialization .
"""

import os

from PyQt5 import QtWidgets, QtCore, QtGui
from ..Components import effect_background, effect_cutline, attribute, pipe, draw, port
from ..Model import serializable, constants, history

__all__ = ["Scene"]


class Scene(QtWidgets.QGraphicsScene, serializable.Serializable):
    """
    Store the scene serialization and create the basic widget.

    """

    def __init__(self, sub_scene_flag, view, attribute_widget=None, parent=None):
        """
        Create the scene which contains many widgets.

        Args:
            sub_scene_flag: Scene list item
            view: The manager.
            attribute_widget: whether is the sub scene of an attribute widget.
            parent: Parent item.
        """

        super(Scene, self).__init__(parent)
        self.view = view
        self.attribute_widget = attribute_widget
        self.scene_rect = QtCore.QRectF(-1000, -1000, 2000, 2000)
        self.setSceneRect(self.scene_rect)
        self.sub_scene_flag = sub_scene_flag

        # History
        self.history = history.History(self.view)

        # background image
        self.background_image_flag = False
        self.background_image = effect_background.EffectBackground(self.view)
        self.background_image.resize(self.view.size().width(), self.view.size().width())
        self.background_image.setPos(self.view.mapToScene(0, 0).x(), self.view.mapToScene(0, 0).y())
        self.addItem(self.background_image)
        # self.background_image.setFlag(QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

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
        #       font
        self.pipe_style_font_type = None
        self.pipe_style_font_color = None

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
        self.draw_image = QtGui.QImage(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                    "../Resources/common_background_image.png")))

        # show markdown text
        self.focusItemChanged.connect(self.change_markdown)
    
    def change_markdown(self, new_focus_item, old_focus_item, reason):
        """
        change markdown whenever focus of attribute widget changed.

        """

        if self.view.mainwindow.markdown_toolbar.isVisible():
            send_id = dict()

            # data
            if isinstance(old_focus_item, attribute.AttributeWidget):
                send_id["old_focus_item"] = old_focus_item.id
            else:
                send_id["old_focus_item"] = 0
            if isinstance(new_focus_item, attribute.AttributeWidget):
                send_id["new_focus_item"] = new_focus_item.id
            else:
                send_id["new_focus_item"] = 0

            # send data to js
            if constants.DEBUG_MARKDOWN:
                print(f"1 Scene send send_id{send_id} to MarkdownDocument emit_save_flag")

            self.view.mainwindow.markdown_document.emit_save_flag(send_id)

    def get_id_attribute(self, attribute_id) -> attribute.AttributeWidget:
        """
        For Serialization to get attribute widget.

        Args:
            attribute_id: attribute id.

        """

        for item in self.items():
            if isinstance(item, attribute.AttributeWidget):
                if item.id == attribute_id:
                    return item

    def get_id_logic(self, logic_id) -> attribute.LogicWidget:
        """
         For Serialization to get logic widget.

         Args:
             logic_id: logic id.

         """

        for item in self.items():
            if isinstance(item, attribute.LogicWidget):
                if item.id == logic_id:
                    return item

    def get_id_port(self, port_id) -> port.Port:
        """
         For Serialization to get port widget.

         Args:
             port_id: port id.

         """

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
        """
        For Serialization to get pipe widget.

        Args:
            pipe_id: pipe id.

        """

        for item in self.items():
            if isinstance(item, pipe.Pipe):
                if item.id == pipe_id:
                    return item

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        #   Background
        super(Scene, self).drawBackground(painter, rect)
        painter.drawImage(self.scene_rect, self.draw_image)

    def serialize(self, scene_serialization=None):
        """
        Serialization.

        Args:
            scene_serialization: The protobuff object.

        """
        # scene id
        scene_serialization.scene_id = self.id

        # items
        for item in self.items():
            if isinstance(item, attribute.AttributeWidget):
                item.serialize(scene_serialization.attr_serialization.add())
            elif isinstance(item, attribute.LogicWidget):
                item.serialize(scene_serialization.logic_serialization.add())
            elif isinstance(item, pipe.Pipe):
                if item.start_port and item.end_port:
                    item.serialize(scene_serialization.pipe_serialization.add())
            elif isinstance(item, draw.Draw):
                item.serialize(scene_serialization.draw_serialization.add())

        # ui serialization
        scene_serialization.background_image_flag = self.background_image_flag
        scene_serialization.background_image = self.background_image.name

        # attribute widget ui
        if self.attribute_style_font:
            scene_serialization.scene_attr_font_family = self.attribute_style_font.family()
            scene_serialization.scene_attr_font_size = self.attribute_style_font.pointSize()
        if self.attribute_style_font_color:
            scene_serialization.scene_attr_style_font_color = self.attribute_style_font_color.rgba()
        if self.attribute_style_background_color:
            scene_serialization.scene_attr_style_background_color = self.attribute_style_background_color.rgba()
        if self.attribute_style_selected_background_color:
            scene_serialization.scene_attr_style_selected_background_color = \
                self.attribute_style_selected_background_color.rgba()
        if self.attribute_style_border_color:
            scene_serialization.scene_attr_style_border_color = self.attribute_style_border_color.rgba()
        if self.attribute_style_selected_border_color:
            scene_serialization.scene_attr_style_selected_border_color = \
                self.self.attribute_style_selected_border_color.rgba()

        # logic widget ui
        if self.logic_style_background_color:
            scene_serialization.scene_logic_style_background_color = self.logic_style_background_color.rgba()
        if self.logic_style_selected_background_color:
            scene_serialization.scene_logic_style_selected_background_color = \
                self.logic_style_selected_background_color.rgba()
        if self.logic_style_border_color:
            scene_serialization.scene_logic_style_border_color = self.logic_style_border_color.rgba()
        if self.logic_style_selected_border_color:
            scene_serialization.scene_logic_style_selected_border_color = self.logic_style_selected_border_color.rgba()

        # pipe widget ui
        if self.pipe_style_width:
            scene_serialization.scene_pipe_width = self.pipe_style_width
        if self.pipe_style_background_color:
            scene_serialization.scene_pipe_style_background_color = self.pipe_style_background_color.rgba()
        if self.pipe_style_selected_background_color:
            scene_serialization.scene_pipe_style_selected_background_color = \
                self.pipe_style_selected_background_color.rgba()
        if self.pipe_style_font_color:
            scene_serialization.scene_pipe_font_color = self.pipe_style_font_color.rgba()
        if self.pipe_style_font_type:
            scene_serialization.scene_pipe_font_family = self.pipe_style_font_type.family()
            scene_serialization.scene_pipe_font_size = self.pipe_style_font_type.pointSize()

        # port widget ui
        if self.port_style_width:
            scene_serialization.scene_port_width = self.port_style_width
        if self.port_style_color:
            scene_serialization.scene_port_style_color = self.port_style_color.rgba()
        if self.port_style_border_color:
            scene_serialization.scene_port_style_border_color = self.port_style_border_color.rgba()
        if self.port_style_hovered_color:
            scene_serialization.scene_port_style_hovered_color = self.port_style_hovered_color.rgba()
        if self.port_style_hovered_border_color:
            scene_serialization.scene_port_style_hovered_border_color = self.port_style_hovered_border_color.rgba()
        if self.port_style_activated_color:
            scene_serialization.scene_port_style_activated_color = self.port_style_activated_color.rgba()
        if self.port_style_activated_border_color:
            scene_serialization.scene_port_style_activated_border_color = self.port_style_activated_border_color.rgba()

        # rect
        scene_serialization.x = self.sceneRect().x()
        scene_serialization.y = self.sceneRect().y()
        scene_serialization.width = self.sceneRect().width()
        scene_serialization.height = self.sceneRect().height()

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        """
        Deserialization.

        Args:
            data: The protobuff object.
            hashmap: hashmap.
            view: The manager.
            flag: different Times to deserialize.

        """

        if flag is True:
            # deserialize id
            self.id = data.scene_id
            hashmap[data.scene_id] = self

            # size
            self.scene_rect = QtCore.QRectF(data.x, data.y, data.width, data.height)
            self.setSceneRect(self.scene_rect)

            # deserialize attribute widgets with (id, geometry)
            for attribute_data in data.attr_serialization:
                attribute.AttributeWidget().deserialize(attribute_data, hashmap, view, flag=True)
            # deserialize logic widgets with (id, geometry)
            for logic_data in data.logic_serialization:
                attribute.LogicWidget().deserialize(logic_data, hashmap, view, flag=True)
            # deserialize pipe widgets with all
            for pipe_data in data.pipe_serialization:
                start_port = self.get_id_port(pipe_data.pipe_port_id[0])
                if constants.DEBUG_DESERIALIZE:
                    print("find start port: ", start_port,
                          "\nstart port id: ", pipe_data.pipe_port_id[0])
                end_port = self.get_id_port(pipe_data.pipe_port_id[1])
                pipe.Pipe(start_port, end_port, None).deserialize(pipe_data, hashmap, view, flag=True)
                start_port.update_pipes_position()
                if end_port:
                    end_port.update_pipes_position()
            # deserialize container widgets with all
            for draw_data in data.draw_serialization:
                draw.Draw().deserialize(draw_data, hashmap, view, flag)
            # background image
            if data.HasField("background_image_flag"):
                self.background_image_flag = data.background_image_flag
            self.background_image.change_svg(data.background_image)
            # style
            if data.scene_attr_font_family and data.scene_attr_font_size:
                font = QtGui.QFont()
                font.setFamily(data.scene_attr_font_family)
                font.setPointSize(data.scene_attr_font_size)
                self.attribute_style_font = font
            else:
                self.attribute_style_font = None

            if data.scene_attr_style_font_color:
                self.attribute_style_font_color = QtGui.QColor()
                self.attribute_style_font_color.setRgba(data.scene_attr_style_font_color)
            else:
                self.attribute_style_font_color = None

            if data.scene_attr_style_background_color:
                self.attribute_style_background_color = QtGui.QColor()
                self.attribute_style_background_color.setRgba(data.scene_attr_style_background_color)
            else:
                self.attribute_style_background_color = None

            if data.scene_attr_style_selected_background_color:
                self.attribute_style_selected_background_color = QtGui.QColor()
                self.attribute_style_selected_background_color.setRgba(data.scene_attr_style_selected_background_color)
            else:
                self.attribute_style_selected_background_color = None

            if data.scene_attr_style_border_color:
                self.attribute_style_border_color = QtGui.QColor()
                self.attribute_style_border_color.setRgba(data.scene_attr_style_border_color)
            else:
                self.attribute_style_border_color = None

            if data.scene_attr_style_selected_border_color:
                self.attribute_style_selected_border_color = QtGui.QColor()
                self.attribute_style_selected_border_color.setRgba(data.scene_attr_style_selected_border_color)
            else:
                self.attribute_style_selected_border_color = None

            if data.scene_logic_style_background_color:
                self.logic_style_background_color = QtGui.QColor()
                self.logic_style_background_color.setRgba(data.scene_logic_style_background_color)
            else:
                self.logic_style_background_color = None

            if data.scene_logic_style_selected_background_color:
                self.logic_style_selected_background_color = QtGui.QColor()
                self.logic_style_selected_background_color.setRgba(data.scene_logic_style_selected_background_color)
            else:
                self.logic_style_selected_background_color = None

            if data.scene_logic_style_border_color:
                self.logic_style_border_color = QtGui.QColor()
                self.logic_style_border_color.setRgba(data.scene_logic_style_border_color)
            else:
                self.logic_style_border_color = None

            if data.scene_logic_style_selected_border_color:
                self.logic_style_selected_border_color = QtGui.QColor()
                self.logic_style_selected_border_color.setRgba(data.scene_logic_style_selected_border_color)
            else:
                self.logic_style_selected_border_color = None

            if data.scene_pipe_width:
                self.pipe_style_width = data.scene_pipe_width
            else:
                self.pipe_style_width = None

            if data.scene_pipe_style_background_color:
                self.pipe_style_background_color = QtGui.QColor()
                self.pipe_style_background_color.setRgba(data.scene_pipe_style_background_color)
            else:
                self.pipe_style_background_color = None

            if data.scene_pipe_style_selected_background_color:
                self.pipe_style_selected_background_color = QtGui.QColor()
                self.pipe_style_selected_background_color.setRgba(data.scene_pipe_style_selected_background_color)
            else:
                self.pipe_style_selected_background_color = None
            
            if data.scene_pipe_font_color:
                self.pipe_style_font_color = QtGui.QColor()
                self.pipe_style_font_color.setRgba(data.scene_pipe_font_color)
            else:
                self.pipe_style_font_color = None
            
            if data.scene_pipe_font_family and data.scene_pipe_font_size:
                self.pipe_style_font_type = QtGui.QFont()
                self.pipe_style_font_type.setFamily(data.scene_pipe_font_family)
                self.pipe_style_font_type.setPointSize(data.scene_pipe_font_size)
            else:
                self.pipe_style_font_type = None

            if data.scene_port_width:
                self.port_style_width = data.scene_port_width
            else:
                self.port_style_width = None

            if data.scene_port_style_color:
                self.port_style_color = QtGui.QColor()
                self.port_style_color.setRgba(data.scene_port_style_color)
            else:
                self.port_style_color = None

            if data.scene_port_style_border_color:
                self.port_style_border_color = QtGui.QColor()
                self.port_style_border_color.setRgba(data.scene_port_style_border_color)
            else:
                self.port_style_border_color = None

            if data.scene_port_style_hovered_color:
                self.port_style_hovered_color = QtGui.QColor()
                self.port_style_hovered_color.setRgba(data.scene_port_style_hovered_color)
            else:
                self.port_style_hovered_color = None

            if data.scene_port_style_hovered_border_color:
                self.port_style_hovered_border_color = QtGui.QColor()
                self.port_style_hovered_border_color.setRgba(data.scene_port_style_hovered_border_color)
            else:
                self.port_style_hovered_border_color = None

            if data.scene_port_style_activated_color:
                self.port_style_activated_color = QtGui.QColor()
                self.port_style_activated_color.setRgba(data.scene_port_style_activated_color)
            else:
                self.port_style_activated_color = None

            if data.scene_port_style_activated_border_color:
                self.port_style_activated_border_color = QtGui.QColor()
                self.port_style_activated_border_color.setRgba(data.scene_port_style_activated_border_color)
            else:
                self.port_style_activated_border_color = None

        elif flag is False:
            for item in self.items():
                # deserialize attribute widgets second time
                if isinstance(item, attribute.AttributeWidget):
                    # deserialize attribute widgets with attribute sub widgets
                    for attribute_widget_data in data.attr_serialization:
                        if item.id == attribute_widget_data.attr_id:
                            # deserialize sub attribute widgets
                            for attribute_sub_id in attribute_widget_data.sub_attr:
                                sub_attribute_widget = self.get_id_attribute(attribute_sub_id)
                                item.attribute_sub_widgets.append(sub_attribute_widget)
                                item.attribute_layout.addItem(sub_attribute_widget,
                                                              sub_attribute_widget.item_row,
                                                              sub_attribute_widget.item_column)
                            from ..Components.sub_view import ProxyView
                            from ..Components.todo import Todo
                            for attribute_sub_file in attribute_widget_data.file_serialization:
                                attribute_sub = attribute.AttributeFile(item)
                                attribute_sub.deserialize(attribute_sub_file, hashmap, view, flag)
                                item.attribute_sub_widgets.append(attribute_sub)
                                item.attribute_layout.addItem(attribute_sub,
                                                              attribute_sub.item_row,
                                                              attribute_sub.item_column)
                            for attribute_sub_todo in attribute_widget_data.todo_serialization:
                                attribute_sub = Todo(item)
                                attribute_sub.deserialize(attribute_sub_todo, hashmap, view, flag)
                                item.attribute_sub_widgets.append(attribute_sub)
                                item.attribute_layout.addItem(attribute_sub,
                                                              attribute_sub.item_row,
                                                              attribute_sub.item_column)
                            for attribute_sub_view in attribute_widget_data.subview_serialization:
                                attribute_sub = ProxyView(self.view.mainwindow)
                                attribute_sub.deserialize(attribute_sub_view, hashmap,
                                                          attribute_sub.sub_view_widget_view, flag=True)
                                self.view.mainwindow.view_widget.children_view[attribute_sub.id] = attribute_sub
                                item.attribute_sub_widgets.append(attribute_sub)
                                item.attribute_layout.addItem(attribute_sub,
                                                              attribute_sub.item_row,
                                                              attribute_sub.item_column)
                            for attribute_none_widget in attribute_widget_data.none_serialization:
                                attribute_none = attribute.NoneWidget(attribute_none_widget.none_pos[0],
                                                                      attribute_none_widget.none_pos[1],
                                                                      item)
                                attribute_none.deserialize(attribute_none_widget, hashmap, view, flag)
                                item.attribute_sub_widgets.append(attribute_none)
                                item.attribute_layout.addItem(attribute_none,
                                                              attribute_none.item_row,
                                                              attribute_none.item_column)

                            item.text_change_node_shape()
                            # deserialize attribute widgets with attribute next widgets
                            for attribute_next_id in attribute_widget_data.next_attr_id:
                                next_attribute_widget = self.get_id_attribute(attribute_next_id)
                                item.next_attribute.append(next_attribute_widget)
                                if constants.DEBUG_DESERIALIZE:
                                    print("deserialize attribute widget: ", item,
                                          "add next attribute: ", next_attribute_widget,
                                          "current next attribute: ", item.next_attribute)
                            # deserialize attribute widgets with attribute last widgets
                            for attribute_last_id in attribute_widget_data.last_attr_id:
                                last_attribute_widget = self.get_id_attribute(attribute_last_id)
                                item.last_attribute.append(last_attribute_widget)
                                if constants.DEBUG_DESERIALIZE:
                                    print("deserialize attribute widget: ", item,
                                          "add last attribute: ", last_attribute_widget,
                                          "current last attribute: ", item.last_attribute)
                            # deserialize attribute widgets with logic next widgets
                            for logic_next_id in attribute_widget_data.next_logic_id:
                                next_logic_widget = self.get_id_logic(logic_next_id)
                                item.next_logic.append(next_logic_widget)
                            # deserialize attribute widgets with logic next widgets
                            for logic_last_id in attribute_widget_data.last_logic_id:
                                last_logic_widget = self.get_id_logic(logic_last_id)
                                item.last_logic.append(last_logic_widget)
                            # deserialize attribute widgets with pipes
                            for pipe_id in attribute_widget_data.attr_port[0].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.true_input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data.attr_port[1].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.false_input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data.attr_port[2].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.true_output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in attribute_widget_data.attr_port[3].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.false_output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                # deserialize logic widgets second time
                elif isinstance(item, attribute.LogicWidget):
                    for logic_widget_data in data.logic_serialization:
                        # traverse list and find right logic
                        if item.id == logic_widget_data.logic_id:
                            # deserialize logic widgets with attribute next widgets
                            for attribute_next_id in logic_widget_data.logic_next_attr:
                                next_attribute_widget = self.get_id_attribute(attribute_next_id)
                                item.next_attribute.append(next_attribute_widget)
                            # deserialize logic widgets with attribute last widgets
                            for attribute_last_id in logic_widget_data.logic_last_attr:
                                last_attribute_widget = self.get_id_attribute(attribute_last_id)
                                item.last_attribute.append(last_attribute_widget)
                            # deserialize logic widgets with logic next widgets
                            for logic_next_id in logic_widget_data.logic_next_logic:
                                next_logic_widget = self.get_id_logic(logic_next_id)
                                item.next_logic.append(next_logic_widget)
                            # deserialize logic widgets with logic last widgets
                            for logic_last_id in logic_widget_data.logic_last_logic:
                                last_logic_widget = self.get_id_logic(logic_last_id)
                                item.last_logic.append(last_logic_widget)
                            # deserialize logic widgets with ports
                            for pipe_id in logic_widget_data.logic_port[0].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.input_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
                            for pipe_id in logic_widget_data.logic_port[1].pipes_id:
                                pipe_widget = self.get_id_pipe(pipe_id)
                                item.output_port.pipes.append(pipe_widget)
                                item.update_pipe_position()
        return True
