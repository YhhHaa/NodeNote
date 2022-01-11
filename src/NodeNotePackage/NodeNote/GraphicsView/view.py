"""
View.py - Control components logic.
"""

import time
import re
import os
import sqlite3

from PyQt5 import QtGui, QtCore, QtWidgets, sip

from .scene import Scene
from ..Components import effect_water, attribute, port, pipe, effect_cutline, effect_background, effect_snow, \
    draw, todo, sub_view
from ..Model import constants, serializable, serialize_pb2


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    Define the comparative method for scene list order.
    """

    def __lt__(self, other):
        """
        The comparative method.

        Args:
            other: Text input.

        Returns:
            bool: whether key1 < key2.
        """

        column = self.treeWidget().sortColumn()
        key_1 = self.natural_sort_key(self.text(column))
        key_2 = self.natural_sort_key(other.text(column))
        if isinstance(key_1, int) and isinstance(key_2, int) or isinstance(key_1, str) and isinstance(key_2, str):
            return key_1 < key_2
        else:
            return str(key_1) < str(key_2)

    @staticmethod
    def natural_sort_key(key):
        """
        Only support the format like this "1. 2. ..." and "a. b. c. ..."

        Args:
            key: Text or number.

        Returns:
            the comparable text

        """

        text = re.match(r'(.+?)\..*', key, re.M)
        if text:
            text = text.group(1)
            if text.isdigit():
                return int(text)
            elif text:
                return text
        else:
            return 0


class DisplayThumbnailsThread(QtCore.QThread):
    def __init__(self, view, parent=None) -> None:
        super().__init__(parent=parent)
        self.view = view


    def run(self):
        """
        Draw thumbnails to index the scene quickly.

        """
        pass
    
    def timerEvent(self, a0: 'QtCore.QTimerEvent') -> None:
        area = self.view.mainwindow.view_widget.current_scene.scene_rect
        image = QtGui.QImage(self.view.mainwindow.thumbnails.size() - QtCore.QSize(10, 10) , QtGui.QImage.Format_ARGB32)
        painter = QtGui.QPainter(image)
        self.view.mainwindow.view_widget.current_scene.render(
            painter, 
            QtCore.QRectF(
                0, 0,
                image.size().width(), image.size().height()
            ),
            area,
            QtCore.Qt.IgnoreAspectRatio)
        painter.end()
        self.view.mainwindow.thumbnails.setPixmap(QtGui.QPixmap.fromImage(image))
        for item in self.view.mainwindow.view_widget.current_scene.items():
            item.update()
        return super().timerEvent(a0)


class View(QtWidgets.QGraphicsView, serializable.Serializable):
    """
    Class used for managing components.
        - Delete and create components.
        - Zoom in and Zoom out.
        - Gpu acceleration.
        - ui settings.
        - cutline to delete pipes.
        - Serach widget.
        - Serialization and deserialization.
    """

    tablet_used = False

    def __init__(self, mainwindow, parent=None, root_flag=True, proxy_widget=None):
        """
        Create a manager for components.

        Args:
            mainwindow: The main window.
            parent: Parent item.
            root_flag: whether it is the root manager.
            proxy_widget: Used for the embedded sub view widget(Components.subview.ProxyWidget).

        """
        self.root_flag = root_flag
        self.mainwindow = mainwindow
        self.proxy_widget = proxy_widget
        super(View, self).__init__(parent)
        if self.root_flag:
            self.line_flag = constants.view_line_flag
            self.copy_attribute_widget = dict()
        self.undo_flag = constants.view_undo_flag
        # BASIC SETTINGS
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform)
        if self.root_flag:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

        if self.root_flag:
            self.root_scene = Scene(self.mainwindow.scene_list, self)
        else:
            self.root_scene = Scene(self.mainwindow.view_widget.current_scene_flag, self)
        self.setScene(self.root_scene)
        self.background_image = self.root_scene.background_image
        self.cutline = self.root_scene.cutline

        # TIME
        self.start_time = None
        self.last_time = 0

        # SCALE FUNCTION
        self.zoomInFactor = 1.25
        self.zoomOutFactor = 0.8
        self.zoom = 5
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        # SCROLLBAR
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.horizontal_scrollbar = QtWidgets.QScrollBar()
        self.setHorizontalScrollBar(self.horizontal_scrollbar)
        self.vertical_scrollbar = QtWidgets.QScrollBar()
        self.setVerticalScrollBar(self.vertical_scrollbar)

        # DRAW LINE
        self.drag_pipe = None
        self.item = None
        self.mode = constants.MODE_NOOP

        # STORE
        self.attribute_widgets = list()
        self.logic_widgets = list()
        self.pipes = list()
        self.draw_widgets = list()

        # Temp for indexing
        if self.root_flag:
            self.children_view = dict()

        # SUB SCENE
        if self.root_flag:
            self.root_scene_flag = TreeWidgetItem(self.mainwindow.scene_list,
                                                  ("Root Scene",))
            self.root_scene_flag.setData(0, QtCore.Qt.ToolTipRole, self.root_scene)
        else:
            self.root_scene_flag = self.mainwindow.view_widget.current_scene_flag

        self.root_scene.sub_scene_flag = self.root_scene_flag
        self.current_scene = self.root_scene
        self.current_scene_flag = self.root_scene_flag

        # Last scene
        self.last_scene = self.root_scene
        self.last_scene_flag = self.root_scene_flag

        # Search
        self.search_widget = QtWidgets.QWidget(self)
        self.search_widget.setVisible(False)
        self.text_widget = QtWidgets.QLineEdit(self.search_widget)
        self.label_widget = QtWidgets.QLabel("Search: ", self.search_widget)
        self.search_button = QtWidgets.QPushButton("Search", self.search_widget)
        self.next_button = QtWidgets.QPushButton("Next", self.search_widget)
        self.last_button = QtWidgets.QPushButton("Last", self.search_widget)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_widget.setLayout(search_layout)
        search_layout.addWidget(self.label_widget)
        search_layout.addWidget(self.text_widget)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.last_button)
        search_layout.addWidget(self.next_button)

        self.search_button.clicked.connect(lambda: self.search(self.text_widget.text(), self.label_widget))
        self.next_button.clicked.connect(lambda: self.next_search(self.label_widget))
        self.last_button.clicked.connect(lambda: self.last_search(self.label_widget))

        self.search_list = list()
        self.search_position = -1
        self.search_result = False
        self.text_format = {}

        # file
        if len(self.mainwindow.argv) == 2:
            self.filename = self.mainwindow.argv[1]
        else:
            self.filename = None
        self.first_open = True

        # image
        self.image_path = None

        # control
        self.pipe_true_item = None

        # tablet
        self.mouse_effect = True
        self.setAttribute(QtCore.Qt.WA_TabletTracking)

        # thumbnails
        self.run_thumbnails = DisplayThumbnailsThread(self)

        # flowing image
        self.flowing_flag = constants.view_flowing_flag

        # markdown in sub view
        if not self.root_flag:
            activate = QtCore.QEvent(QtCore.QEvent.WindowActivate)
            self.mainwindow.app.sendEvent(self.current_scene, activate)

    def magic(self):
        """
        Magic for debugging

        """

        temp = self.scene().scene_rect.adjusted(0, 0, 1, 1)
        self.scene().setSceneRect(temp)
        self.scene().setSceneRect(temp.adjusted(0, 0, -1, -1))

    def expand(self, expand_flag: str):
        if expand_flag == "left":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(-200, 0, 0, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif expand_flag == "right":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, 0, 200, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif expand_flag == "top":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, -200, 0, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif expand_flag == "bottom":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, 0, 0, 200)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)

    def narrow(self, narrow_flag: str):
        if narrow_flag == "left":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(200, 0, 0, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif narrow_flag == "right":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, 0, -200, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif narrow_flag == "top":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, 200, 0, 0)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
        elif narrow_flag == "bottom":
            self.current_scene.scene_rect = self.current_scene.scene_rect.adjusted(0, 0, 0, -200)
            self.current_scene.setSceneRect(self.current_scene.scene_rect)
    
    def align(self, align_flag: str):
        """
        align selected widgets.

        Args:
            align_flag: align direction.

        """

        # get seletced items.
        selected_widgets = []
        for item in self.current_scene.selectedItems():
            if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)) and item.parentItem() == None:
                selected_widgets.append(item)

        # align widgets.
        if len(selected_widgets) >= 2:
            selected_geo = [[item.scenePos(), item.size()] for item in selected_widgets]

            if align_flag == "left":
                left_x = min([geo[0].x() for geo in selected_geo])

                for item in selected_widgets:
                    item.setPos(left_x, item.scenePos().y())

            elif align_flag == "right":
                right_x = max([geo[0].x() + geo[1].width() for geo in selected_geo])

                for item in selected_widgets:
                    item.setPos(right_x - item.size().width(), item.scenePos().y())

            elif align_flag == "up":
                up_y = min([geo[0].y() for geo in selected_geo])

                for item in selected_widgets:
                    item.setPos(item.scenePos().x(), up_y)

            elif align_flag == "down":
                down_y = max([geo[0].y() + geo[1].height() for geo in selected_geo])

                for item in selected_widgets:
                    item.setPos(item.scenePos().x(), down_y - item.size().height())
            
            if self.undo_flag:
                self.current_scene.history.store_history("change alignment.")
    
    def tanslation_expand(self, translation_flag: str):
        """
        tanslate items

        Args:
            translation_flag: translation direction.

        """

        for item in self.current_scene.items():
            if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget, draw.Draw)) and not item.parentItem():
                if translation_flag == "left" and item.scenePos().x() < self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).x():
                    item.setPos(item.scenePos().x() - 50, item.scenePos().y())
                    item.update()
                elif translation_flag == "right" and item.scenePos().x() > self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).x():
                    item.setPos(item.scenePos().x() + 50, item.scenePos().y())
                    item.update()
                elif translation_flag == "up" and item.scenePos().y() < self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).y():
                    item.setPos(item.scenePos().x(), item.scenePos().y() - 50)
                    item.update()
                elif translation_flag == "down" and item.scenePos().y() > self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).y():
                    item.setPos(item.scenePos().x(), item.scenePos().y() + 50)
                    item.update()
    
    def tanslation_narrow(self, translation_flag: str):
        """
        tanslate items

        Args:
            translation_flag: translation direction.

        """

        for item in self.current_scene.items():
            if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget, draw.Draw)) and not item.parentItem():
                if translation_flag == "left" and item.scenePos().x() < self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).x():
                    item.setPos(item.scenePos().x() + 50, item.scenePos().y())
                    item.update()
                elif translation_flag == "right" and item.scenePos().x() > self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).x():
                    item.setPos(item.scenePos().x() - 50, item.scenePos().y())
                    item.update()
                elif translation_flag == "up" and item.scenePos().y() < self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).y():
                    item.setPos(item.scenePos().x(), item.scenePos().y() - 50)
                    item.update()
                elif translation_flag == "down" and item.scenePos().y() > self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())).y():
                    item.setPos(item.scenePos().x(), item.scenePos().y() + 50)
                    item.update()

    def set_leftbtn_beauty(self, event):
        """
        Set the left mouse button effect.

        Args:
            event: QMouseevent

        """

        water_drop = effect_water.EffectWater()
        property_water_drop = QtWidgets.QGraphicsProxyWidget()
        property_water_drop.setWidget(water_drop)
        self.current_scene.addItem(property_water_drop)
        water_drop.move(self.mapToScene(event.pos()))
        water_drop.show()
        super(View, self).mousePressEvent(event)

    def change_svg_image(self):
        """
        - Change the background image whose format is "SVG".
        - The default image is a girl.

        """

        image_name, image_type = QtWidgets.QFileDialog.getOpenFileName(self, "select svg", constants.work_dir, "*.svg")
        if image_name != "":
            self.current_scene.background_image_flag = True
            self.background_image.change_svg(os.path.abspath(image_name))

    def change_flowing_image(self, close=False):
        """
        - Change the flowing image whose format is "PNG".
        - the default image is the flower.

        """
        if not close:
            image_name, image_type = QtWidgets.QFileDialog.getOpenFileName(self, "select png", constants.work_dir, "*.png")
            if image_name != "":
                image_name = os.path.relpath(image_name, constants.work_dir)
                self.image_path = image_name
                effect_snow.SnowWidget.image_path = image_name
        else:
            if self.mainwindow.sky_widget.isVisible():
                self.mainwindow.sky_widget.hide()
                self.flowing_flag = False
            else:
                self.mainwindow.sky_widget.show()
                self.flowing_flag = True

    def change_scale(self, event):
        """
        Press Ctrl + or Ctrl - to change the zoom.

        Args:
            event: QKeyevent

        """
        if constants.DEBUG_VIEW_CHANGE_SCALE:
            print("View is zooming! Current zoom: ", self.zoom)
        if event.key() == QtCore.Qt.Key_Equal and event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom += self.zoomStep
            if self.zoom <= self.zoomRange[1]:
                self.scale(self.zoomInFactor, self.zoomInFactor)
            else:
                self.zoom = self.zoomRange[1]
        elif event.key() == QtCore.Qt.Key_Minus and event.modifiers() & QtCore.Qt.ControlModifier:
            self.zoom -= self.zoomStep
            if self.zoom >= self.zoomRange[0]:
                self.scale(self.zoomOutFactor, self.zoomOutFactor)
            else:
                self.zoom = self.zoomRange[0]

    def view_update_pipe_animation(self):
        """
        Update the scrolling ball animation of pipes.

        """

        if len(self.current_scene.selectedItems()) == 1:
            item = self.current_scene.selectedItems()[0]
            if isinstance(item, attribute.AttributeWidget) or isinstance(item, attribute.LogicWidget):
                if not item.attribute_animation:
                    item.start_pipe_animation()
                else:
                    item.end_pipe_animation()

        if len(self.current_scene.selectedItems()) >= 1:
            for item in self.current_scene.selectedItems():
                if isinstance(item, pipe.Pipe):
                    if item.timeline.state() == QtCore.QTimeLine.NotRunning:
                        item.perform_evaluation_feedback()
                    elif item.timeline.state() == QtCore.QTimeLine.Running:
                        item.end_evaluation_feedback()
        if self.undo_flag:
            self.current_scene.history.store_history("update pipe animation")

    def python_highlighter(self):
        """
        Turn on Python syntax highlighting of the selected attribute widget items.

        """

        for item in self.current_scene.selectedItems():
            if isinstance(item, attribute.AttributeWidget):
                item.attribute_widget.label_item.pythonlighter = \
                    attribute.PythonHighlighter(item.attribute_widget.label_item.document())

    def search_text(self):
        """
        Press Ctrl F to call search widget.

        """

        # widget
        if not self.search_widget.isVisible():
            self.search_widget.setGeometry(self.size().width() // 2 - 250, 0, 500, 50)
            self.search_widget.setVisible(True)
            self.text_widget.setFocus()
        else:
            self.search_widget.setVisible(False)

            for item_id in self.text_format:
                # clear format in root view
                for item in self.attribute_widgets:
                    if item.id == item_id:
                        if item.attribute_widget.label_item:
                            cursor = item.attribute_widget.label_item.textCursor()
                            for text_format in self.text_format[item_id]:
                                cursor.setPosition(text_format[0])
                                cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                                cursor.setCharFormat(text_format[1])
                # clear format in sub view
                for sub_view in self.children_view.values():
                    for item in sub_view.sub_view_widget_view.attribute_widgets:
                        if item.id == item_id:
                            cursor = item.attribute_widget.label_item.textCursor()
                            for text_format in self.text_format[item_id]:
                                cursor.setPosition(text_format[0])
                                cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                                cursor.setCharFormat(text_format[1])

            self.search_list = list()
            self.search_position = -1
            self.search_result = False
            self.text_format = {}

    def search(self, search_text, label_widget):
        """
        Input the text to search for and search in all scene.

        Args:
            search_text: Input text.
            label_widget: The search result.

        """

        # search
        self.search_list = list()
        self.search_position = -1
        self.search_result = False

        for item_id in self.text_format:
            for item in self.attribute_widgets:
                if item.id == item_id:
                    cursor = item.attribute_widget.label_item.textCursor()
                    for text_format in self.text_format[item_id]:
                        cursor.setPosition(text_format[0])
                        cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                        cursor.setCharFormat(text_format[1])
        self.text_format = {}

        if search_text:
            for item in self.attribute_widgets:
                if isinstance(item, attribute.AttributeWidget):

                    # search in node.
                    text = item.attribute_widget.label_item.toPlainText()
                    cursor = item.attribute_widget.label_item.textCursor()

                    text_format = QtGui.QTextCharFormat()
                    text_format.setBackground(QtGui.QBrush(QtGui.QColor(255, 153, 153, 200)))

                    regex = QtCore.QRegExp(search_text)
                    pos = 0
                    index = regex.indexIn(text, pos)
                    while index != -1:
                        cursor.setPosition(index)
                        cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                        last_format = cursor.charFormat()
                        cursor.mergeCharFormat(text_format)

                        if item.id not in self.text_format:
                            self.text_format[item.id] = list()
                            self.text_format[item.id].append((index, last_format))

                        pos = index + regex.matchedLength()
                        index = regex.indexIn(text, pos)
                        self.search_result = True

                    if self.search_result:
                        self.search_list.append(item)
                    self.search_result = False

                    # search in sub view                  
                    for sub_view_widget in self.children_view.values():
                        for item in sub_view_widget.sub_view_widget_view.attribute_widgets:
                            if isinstance(item, attribute.AttributeWidget):
                                text = item.attribute_widget.label_item.toPlainText()
                                cursor = item.attribute_widget.label_item.textCursor()

                                text_format = QtGui.QTextCharFormat()
                                text_format.setBackground(QtGui.QBrush(QtGui.QColor(255, 153, 153, 200)))

                                regex = QtCore.QRegExp(search_text)
                                pos = 0
                                index = regex.indexIn(text, pos)
                                while index != -1:
                                    cursor.setPosition(index)
                                    cursor.movePosition(QtGui.QTextCursor.EndOfWord, 1)
                                    last_format = cursor.charFormat()
                                    cursor.mergeCharFormat(text_format)

                                    if item.id not in self.text_format:
                                        self.text_format[item.id] = list()
                                        self.text_format[item.id].append((index, last_format))

                                    pos = index + regex.matchedLength()
                                    index = regex.indexIn(text, pos)
                                    self.search_result = True

                                if self.search_result and item not in self.search_list:
                                    self.search_list.append(item)
                                self.search_result = False

                self.next_search(label_widget)

                if not self.search_list:
                    self.label_widget.setText("Result 0/0")

        else:
            self.label_widget.setText("Result 0/0")

    def next_search(self, label_widget):
        """
        Start the next search.

        Args:
            label_widget: The search result.

        """

        if self.search_list:
            self.mainwindow.scene_list.clearSelection()

            self.search_position += 1
            if self.search_position > len(self.search_list) - 1:
                self.search_position = len(self.search_list) - 1

            at_scene = self.search_list[self.search_position].scene()

            self.search_item(at_scene, label_widget)

    def last_search(self, label_widget):
        """
        Go back to the last search.

        Args:
            label_widget: The search result.

        """

        if self.search_list:
            self.mainwindow.scene_list.clearSelection()

            self.search_position -= 1
            if self.search_position < 0:
                self.search_position = 0

            at_scene = self.search_list[self.search_position].scene()
            
            self.search_item(at_scene, label_widget)
            
    
    def search_item(self, at_scene, label_widget):
        # if not sub view
        if at_scene.view.root_flag:
            self.mainwindow.view_widget.last_scene = self.mainwindow.view_widget.current_scene
            self.mainwindow.view_widget.last_scene_flag = self.mainwindow.view_widget.current_scene_flag

            self.current_scene = at_scene

            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole).id == at_scene.id:
                    self.current_scene_flag = scene_flag
                    scene_flag.setSelected(True)
                    break

            self.background_image = at_scene.background_image
            self.cutline = at_scene.cutline
            self.setScene(at_scene)
            self.centerOn(self.search_list[self.search_position])
            label_widget.setText("Result %d/%d" % (self.search_position + 1, len(self.search_list)))
        # if sub view
        else:
            # 1. set last scene
            self.mainwindow.view_widget.last_scene = self.mainwindow.view_widget.current_scene
            self.mainwindow.view_widget.last_scene_flag = self.mainwindow.view_widget.current_scene_flag

            # 2. set current scene
            self.current_scene = at_scene.view.proxy_widget.scene()

            # 3. set scene flag selected
            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole).id == self.current_scene.id:
                    self.current_scene_flag = scene_flag
                    scene_flag.setSelected(True)
                    break
            
            # 4. change item
            self.background_image = self.current_scene.background_image
            self.cutline = self.current_scene.cutline
            self.setScene(self.current_scene)

            # 5. focus on item
            self.centerOn(at_scene.view.proxy_widget)
            at_scene.view.centerOn(self.search_list[self.search_position])
            label_widget.setText("Result %d/%d" % (self.search_position + 1, len(self.search_list)))

    def delete_connections(self, item):
        """
        When you delete the pipes, this function help you
        delete the connections in their ports.

        Args:
            item: The pipe needs to be deleted.

        """

        if isinstance(item, attribute.AttributeWidget):
            for pipe_widget in item.true_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)
            for pipe_widget in item.true_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)
        elif isinstance(item, attribute.LogicWidget):
            for pipe_widget in item.input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)
            for pipe_widget in item.output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                if pipe_widget in self.pipes:
                    self.pipes.remove(pipe_widget)

    def delete_attr_widget(self, item: attribute.AttributeWidget):
        for sub_attr_widget in item.attribute_sub_widgets:
            if isinstance(sub_attr_widget, attribute.AttributeWidget):
                self.delete_attr_widget(sub_attr_widget)

        self.delete_connections(item)

        for next_widget in item.next_attribute:
            next_widget.remove_last_attribute(item)
        for next_widget in item.next_logic:
            next_widget.remove_last_attribute(item)
        for last_widget in item.last_attribute:
            if constants.DEBUG_DESERIALIZE:
                print("last widget: ", last_widget,
                        "next attribute widgets: ", last_widget.next_attribute,
                        "remove widget: ", item)
            last_widget.remove_next_attribute(item)
        for last_widget in item.last_logic:
            last_widget.remove_next_attribute(item)

        # delete sub view from view dict
        from ..Components.sub_view import ProxyView
        for sub_item in item.attribute_sub_widgets:
            if isinstance(sub_item, ProxyView):
                self.mainwindow.view_widget.children_view.pop(sub_item.id, 'not found')

        if item.sub_scene:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole) is item.sub_scene:
                    self.delete_sub_scene(scene_flag)
                    break

        if item.parentItem():
            parent_item = item.parentItem()
            parent_item.delete_subwidget(item)
            self.remove_attribute_widget(item)

        else:
            self.remove_attribute_widget(item)

    def delete_widgets(self, event, history_flag=False):
        """
        Delete the selected items.

        Args:
            event: QKeyevent.
            history_flag: To control whether store the serialization.

        """
        from ..Components.todo import Todo
        if event.key() == QtCore.Qt.Key_Delete:
            selected_items = list(self.current_scene.selectedItems())
            for item in selected_items:
                if isinstance(item, attribute.AttributeWidget):
                    self.delete_attr_widget(item)

                elif isinstance(item, attribute.LogicWidget):
                    self.delete_connections(item)
                    for next_widget in item.next_attribute:
                        next_widget.remove_last_logic(item)
                    for next_widget in item.next_logic:
                        next_widget.remove_last_logic(item)
                    for last_widget in item.last_attribute:
                        last_widget.remove_next_logic(item)
                    for last_widget in item.last_logic:
                        last_widget.remove_next_logic(item)
                    self.remove_logic_widget(item)
                elif isinstance(item, pipe.Pipe):
                    if item in self.current_scene.items() and item.start_port and item.end_port:
                        self.delete_pipe(item)
                elif isinstance(item, draw.Draw):
                    self.current_scene.removeItem(item)
                    self.draw_widgets.remove(item)
                elif isinstance(item, (attribute.AttributeFile, Todo, attribute.NoneWidget)):
                    item.parent_item.attribute_layout.removeItem(item)
                    item.parent_item.attribute_sub_widgets.remove(item)
                    sip.delete(item)

                    item.parent_item.text_change_node_shape()
                    item.parent_item.update_pipe_position()

            if not history_flag and self.undo_flag:
                self.current_scene.history.store_history("Delete Widgets")
            
            # Restore scene.
            self.magic()

    def delete_pipe(self, item: pipe.Pipe):
        """
        Delete selected pipes.

        Args:
            item: Pipes.

        """

        end_node = item.get_input_node()
        start_node = item.get_output_node()
        if isinstance(end_node, attribute.AttributeWidget):
            start_node.remove_next_attribute(end_node)
        else:
            start_node.remove_next_logic(end_node)
        if isinstance(start_node, attribute.AttributeWidget):
            end_node.remove_last_attribute(start_node)
        else:
            end_node.remove_last_logic(start_node)

        input_port = item.get_input_type_port()
        output_port = item.get_output_type_port()
        input_port.remove_pipes(item)
        output_port.remove_pipes(item)

        self.current_scene.removeItem(item)
        self.magic()
        if item in self.pipes:
            self.pipes.remove(item)

    def add_attribute_widget(self, event=None, pos=None):
        """
        Create attribute widget.

        Args:
            event: QContextMenuevent.

        """

        basic_widget = attribute.AttributeWidget()
        self.current_scene.addItem(basic_widget)
        if event:
            basic_widget.setPos(self.mapToScene(event.pos()))
        elif pos:
            basic_widget.setPos(self.mapToScene(self.mapFromGlobal(pos)))
        self.attribute_widgets.append(basic_widget)
        if self.undo_flag:
            self.current_scene.history.store_history("Add Attribute Widget")

    def add_truth_widget(self, event=None, pos=None):
        """
        Create logic widget.

        Args:
            event: QContextMenuevent.

        """

        basic_widget = attribute.LogicWidget()
        self.current_scene.addItem(basic_widget)
        if event:
            basic_widget.setPos(self.mapToScene(event.pos()))
        elif pos:
            basic_widget.setPos(self.mapToScene(self.mapFromGlobal(pos)))
        self.logic_widgets.append(basic_widget)
        if self.undo_flag:
            self.current_scene.history.store_history("Add Truth Widget")

    def add_draw_widget(self, event=None, pos=None):
        """
        Create draw widget.

        Args:
            event: QContextMenuevent.

        """

        canvas = draw.Draw()
        self.current_scene.addItem(canvas)
        if event:
            canvas.setPos(self.mapToScene(event.pos()))
        elif pos:
            canvas.setPos(self.mapToScene(self.mapFromGlobal(pos)))
        self.draw_widgets.append(canvas)
        if self.undo_flag:
            self.current_scene.history.store_history("Add Canvas Widget")

    def open_file(self, item):
        """
        Open the file link in attribute file widgte which is embedded in attribute widget.

        Args:
            item: attribute.AttributeFile.

        """

        if not item.file_url:
            item.file_url, _ = QtWidgets.QFileDialog.getOpenFileName(self, "select files", "",
                                                                     "any file (*.*)")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl().fromLocalFile(os.path.join(constants.work_dir, item.file_url)))
        if self.undo_flag:
            self.current_scene.history.store_history("Add File")

    def add_drag_pipe(self, port_widget, pipe_widget):
        """
        Create pipe widget.

        Args:
            port_widget: The port which contains pipes.
            pipe_widget: Added pipe widget.

        """

        port_widget.add_pipes(pipe_widget)
        self.pipes.append(pipe_widget)
        self.current_scene.addItem(pipe_widget)

    def remove_attribute_widget(self, widget):
        """
        Delete attribute widget.

        Args:
            widget: attribute.AttributeWidget.

        """

        self.current_scene.removeItem(widget)
        if widget in self.attribute_widgets:
            self.attribute_widgets.remove(widget)

    def remove_logic_widget(self, widget):
        """
        Delete logic widget.

        Args:
            widget: attribute.LogicWIdget.

        """

        self.current_scene.removeItem(widget)
        self.logic_widgets.remove(widget)

    def get_all_children(self, parent_flag):
        """
        Put all sub attribute widgets into dict.

        Args:
            attribute_widget: Parent widget.
            copy_empty_scene: For serialization.

        """
        copy_empty_scene = serialize_pb2.ViewSerialization().scene_serialization.add()

        # Find chidren of parent attribute widget.
        for item in parent_flag.attribute_sub_widgets:
            if isinstance(item, attribute.AttributeWidget):
                copy_attribute_widget = copy_empty_scene.attr_serialization.add()
                item.serialize(copy_attribute_widget)
                self.mainwindow.view_widget.copy_attribute_widget[item.id] = copy_attribute_widget
                self.get_all_children(item)

    def copy_item(self):
        """
        Used to copy selected item.

        """

        self.mainwindow.view_widget.copy_attribute_widget = dict()
        copy_empty_scene = serialize_pb2.ViewSerialization().scene_serialization.add()
        parent_flag = None

        # Find parent attribute widget.
        selected_items = list(self.current_scene.selectedItems())
        for item in self.current_scene.selectedItems():
            if isinstance(item, attribute.AttributeWidget):
                if not parent_flag and not item.parentItem():
                    copy_attribute_widget = copy_empty_scene.attr_serialization.add()
                    item.serialize(copy_attribute_widget)
                    self.mainwindow.view_widget.copy_attribute_widget[0] = copy_attribute_widget
                    parent_flag = item
                    break
                elif not parent_flag and item.parentItem():
                    parent = item.parentItem()
                    if parent not in selected_items:
                        copy_attribute_widget = copy_empty_scene.attr_serialization.add()
                        item.serialize(copy_attribute_widget)
                        self.mainwindow.view_widget.copy_attribute_widget[0] = copy_attribute_widget
                        parent_flag = item
                        break
        
        if parent_flag:
            self.get_all_children(parent_flag)


    def create_attribute_from_data(self, data):
        """
        Used to create attribute from serialization to paste item.

        Args:
            data: Serialization of attribute widget.

        """
        node_widget = attribute.AttributeWidget()

        # Added into current scene and view
        self.current_scene.addItem(node_widget)
        self.attribute_widgets.append(self)

        # position
        pos = self.mapToScene(self.mapFromGlobal(QtGui.QCursor().pos()))
        size = QtCore.QSizeF(data.size[0], data.size[1])
        node_widget.setGeometry(QtCore.QRectF(pos, size))

        # content
        node_widget.attribute_widget.label_item.setHtml(data.contents)

        # layout
        node_widget.item_row = data.attr_location[0]
        node_widget.item_column = data.attr_location[1]
        node_widget.current_row = data.next_location[0]
        node_widget.current_column = data.next_location[1]

        # highlighter
        if data.highlighter:
            node_widget.attribute_widget.label_item.pythonlighter = \
                attribute.PythonHighlighter(node_widget.attribute_widget.label_item.document())
        
        # style
        font = QtGui.QFont()
        font.setFamily(data.self_attr_font_family)
        font.setPointSize(data.self_attr_font_size)
        node_widget.attribute_widget.label_item.font = font
        node_widget.attribute_widget.label_item.document().setDefaultFont(font)

        node_widget.attribute_widget.label_item.font_color = QtGui.QColor()
        node_widget.attribute_widget.label_item.font_color.setRgba(data.self_attr_color[0])
        node_widget.attribute_widget.label_item.setDefaultTextColor(node_widget.attribute_widget.label_item.font_color)

        node_widget.color = QtGui.QColor()
        node_widget.color.setRgba(data.self_attr_color[1])

        node_widget.selected_color = QtGui.QColor()
        node_widget.selected_color.setRgba(data.self_attr_color[2])

        node_widget.border_color = QtGui.QColor()
        node_widget.border_color.setRgba(data.self_attr_color[3])

        node_widget.selected_border_color = QtGui.QColor()
        node_widget.selected_border_color.setRgba(data.self_attr_color[4])

        node_widget.attribute_widget.label_item.font_flag = data.attr_flag[0]
        node_widget.attribute_widget.label_item.font_color_flag = data.attr_flag[1]

        node_widget.color_flag = data.attr_flag[2]
        node_widget.selected_color_flag = data.attr_flag[3]
        node_widget.border_flag = data.attr_flag[4]
        node_widget.selected_border_flag = data.attr_flag[5]

        # text width
        node_widget.mouse_flag = data.mouse_flag
        if node_widget.mouse_flag:
            node_widget.attribute_widget.label_item.setTextWidth(data.mouse_text_width)
            node_widget.text_change_node_shape()
            node_widget.resize(0, node_widget.size().height())

        # sub items
        for attribute_sub_id in data.sub_attr:
            sub_attribute_widget = self.create_attribute_from_data(self.mainwindow.view_widget.copy_attribute_widget.get(attribute_sub_id))
            node_widget.attribute_sub_widgets.append(sub_attribute_widget)
            node_widget.attribute_layout.addItem(sub_attribute_widget,
                                            sub_attribute_widget.item_row,
                                            sub_attribute_widget.item_column)
        for attribute_sub_file in data.file_serialization:
            attribute_sub = attribute.AttributeFile(node_widget)
            temp_id = attribute_sub.id
            attribute_sub.deserialize(attribute_sub_file, hashmap={}, view=self, flag=True)
            attribute_sub.id = temp_id
            node_widget.attribute_sub_widgets.append(attribute_sub)
            node_widget.attribute_layout.addItem(attribute_sub,
                                            attribute_sub.item_row,
                                            attribute_sub.item_column)
        for attribute_sub_todo in data.todo_serialization:
            attribute_sub = todo.Todo(node_widget)
            temp_id = attribute_sub.id
            attribute_sub.deserialize(attribute_sub_todo, hashmap={}, view=None, flag=True)
            attribute_sub.id = temp_id
            node_widget.attribute_sub_widgets.append(attribute_sub)
            node_widget.attribute_layout.addItem(attribute_sub,
                                            attribute_sub.item_row,
                                            attribute_sub.item_column)
        for attribute_sub_view in data.subview_serialization:
            attribute_sub = sub_view.ProxyView(self.mainwindow)
            temp_id = attribute_sub.id
            attribute_sub.deserialize(attribute_sub_view, hashmap={},
                                        view=attribute_sub.sub_view_widget_view, flag=True)
            attribute_sub.id = temp_id
            node_widget.attribute_sub_widgets.append(attribute_sub)
            node_widget.attribute_layout.addItem(attribute_sub,
                                            attribute_sub.item_row,
                                            attribute_sub.item_column)
        for attribute_none_widget in data.none_serialization:
            attribute_none = attribute.NoneWidget(attribute_none_widget.none_pos[0],
                                                    attribute_none_widget.none_pos[1],
                                                    node_widget)
            temp_id = attribute_none.id
            attribute_none.deserialize(attribute_none_widget, hashmap={}, view=None, flag=True)
            attribute_none.id = temp_id
            node_widget.attribute_sub_widgets.append(attribute_none)
            node_widget.attribute_layout.addItem(attribute_none,
                                            attribute_none.item_row,
                                            attribute_none.item_column)

        node_widget.text_change_node_shape()

        return node_widget

    def paste_item(self):
        """
        Used to paste selected items.

        """
        if self.mainwindow.view_widget.copy_attribute_widget:
            # Deserialize parent attribute widget.
            data = self.mainwindow.view_widget.copy_attribute_widget[0]
            self.create_attribute_from_data(data)

    def remove_drag_pipe(self, port_widget, pipe_widget):
        """
        Delete pipes in port widget.

        Args:
            port_widget: port.Port.
            pipe_widget: pipe.Pipe.

        """

        port_widget.remove_pipes(pipe_widget)
        if pipe_widget in self.pipes:
            self.pipes.remove(pipe_widget)
        self.current_scene.removeItem(pipe_widget)

    def drag_pipe_press(self, event):
        """
        Double mouse press to create pipe.

        Args:
            event: QMouseevent.

        """

        if self.mode == constants.MODE_NOOP:
            self.item = self.itemAt(event.pos())
            if constants.DEBUG_DRAW_PIPE:
                print("mouse double pressed at", self.item)
            if isinstance(self.item, port.Port):
                if constants.DEBUG_DRAW_PIPE:
                    print("enter the drag mode and set input port: ", self.item)
                self.mode = constants.MODE_PIPE_DRAG
                self.drag_pipe = pipe.Pipe(start_port=self.item, end_port=None, node=self.item.parentItem())
                self.add_drag_pipe(self.item, self.drag_pipe)
                return
            if isinstance(self.item, pipe.Pipe):
                self.mode = constants.MODE_PIPE_DRAG
                if constants.DEBUG_DRAW_PIPE:
                    print("delete the output port and drag again")
                self.drag_pipe = self.item
                self.item.delete_input_type_port(self.mapToScene(event.pos()))
                return
        if self.mode == constants.MODE_PIPE_DRAG:
            self.mode = constants.MODE_NOOP
            item = self.itemAt(event.pos())

            if constants.DEBUG_DRAW_PIPE:
                print("end the drag mode and set output port or not: ", item)
            self.drag_pipe_release(item)

    def drag_pipe_release(self, item):
        """
        Mouse released to create pipe.

        Args:
            item: The relevant widget to create pipe.

        """

        if (self.drag_pipe.start_flag == constants.OUTPUT_NODE_START) or \
                (self.drag_pipe.start_flag == constants.INPUT_NODE_START and self.drag_pipe.start_port):
            self.item = self.drag_pipe.start_port
        else:
            self.item = self.drag_pipe.end_port

        if isinstance(item, port.Port):
            if item.port_type != self.item.port_type and not self.judge_same_pipe(item):

                if self.drag_pipe.start_port:
                    self.drag_pipe.end_port = item
                else:
                    self.drag_pipe.start_port = item
                item.add_pipes(self.drag_pipe)
                self.drag_pipe.update_position()

                if item.get_node() is self.drag_pipe.get_output_node():
                    output_node = item.get_node()
                    input_node = self.item.get_node()
                else:
                    output_node = self.item.get_node()
                    input_node = item.get_node()
                if isinstance(output_node, attribute.AttributeWidget) \
                        and isinstance(input_node, attribute.AttributeWidget):
                    output_node.add_next_attribute(input_node)
                    input_node.add_last_attribute(output_node)
                elif isinstance(output_node, attribute.AttributeWidget) \
                        and isinstance(input_node, attribute.LogicWidget):
                    output_node.add_next_logic(input_node)
                    input_node.add_last_attribute(output_node)
                elif isinstance(output_node, attribute.LogicWidget) \
                        and isinstance(input_node, attribute.AttributeWidget):
                    output_node.add_next_attribute(input_node)
                    input_node.add_last_logic(output_node)
                elif isinstance(output_node, attribute.LogicWidget) \
                        and isinstance(input_node, attribute.LogicWidget):
                    output_node.add_next_logic(input_node)
                    input_node.add_last_logic(output_node)

                if output_node.attribute_animation:
                    output_node.start_pipe_animation()
                if self.undo_flag:
                    self.current_scene.history.store_history("Create Pipe")
            else:
                if constants.DEBUG_DRAW_PIPE:
                    print("delete drag pipe case 1")
                self.remove_drag_pipe(self.item, self.drag_pipe)

                self.magic()
                self.item = None
        elif not isinstance(item, port.Port):
            if constants.DEBUG_DRAW_PIPE:
                print("delete drag pipe case 2 from port: ", self.item)
            self.remove_drag_pipe(self.item, self.drag_pipe)
            self.item = None

            # Restore scene.
            self.magic()

    def judge_same_pipe(self, item):
        """
        To judge whether item has the pipe which is same as the pipe in self.item.

        Args:
            item: Port widget contains many pipes.

        Returns: bool

        """
        for same_pipe in item.pipes:
            if same_pipe in self.item.pipes:
                return True
        return False

    def cut_interacting_edges(self):
        """
        To judge whether cutline touched pipes.

        """

        if constants.DEBUG_CUT_LINE:
            print("All pipes: ", self.pipes)
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]
            for pipe_widget in self.pipes:
                if pipe_widget.intersect_with(p1, p2):
                    if constants.DEBUG_CUT_LINE:
                        print("Delete pipe", pipe_widget)
                    self.delete_pipe(pipe_widget)

    def cutline_pressed(self):
        """
        Press ctrl Lmb to create cutline while change the cursor.

        """

        self.mode = constants.MODE_PIPE_CUT
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def cutline_released(self):
        """
        If cutline touched pipes, delete pipes.

        """

        self.cut_interacting_edges()
        self.cutline.line_points = list()
        self.cutline.prepareGeometryChange()
        self.cutline.update()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        self.mode = constants.MODE_NOOP

    def new_sub_scene(self, attribute_widget):
        """
        Press Alt + LMB to enter the attribute widget sub scene.

        Args:
            attribute_widget: attribute.AttributeWidget which is pressed.

        """
        self.mainwindow.scene_list.clearSelection()

        if not attribute_widget.sub_scene:
            sub_scene_flag = TreeWidgetItem(self.current_scene_flag,
                                            (attribute_widget.attribute_widget.label_item.toPlainText(),))
            self.current_scene_flag.setExpanded(True)
            sub_scene = Scene(sub_scene_flag, self, attribute_widget)
            if self.root_flag:
                self.background_image = sub_scene.background_image
                self.cutline = sub_scene.cutline
            else:
                self.mainwindow.view_widget.background_image = sub_scene.background_image
                self.mainwindow.view_widget.cutline = sub_scene.cutline

            attribute_widget.set_sub_scene(sub_scene)

            sub_scene_flag.setData(0, QtCore.Qt.ToolTipRole, sub_scene)

            if self.root_flag:
                self.last_scene = self.current_scene
                self.last_scene_flag = self.current_scene_flag

                self.current_scene.clearSelection()
                self.setScene(sub_scene)
                self.current_scene = sub_scene
                self.current_scene_flag = sub_scene.sub_scene_flag
                self.current_scene_flag.setSelected(True)
            else:
                self.mainwindow.view_widget.last_scene = self.mainwindow.view_widget.current_scene
                self.mainwindow.view_widget.last_scene_flag = self.mainwindow.view_widget.current_scene_flag

                self.current_scene.clearSelection()
                self.mainwindow.view_widget.current_scene.clearSelection()
                self.mainwindow.view_widget.setScene(sub_scene)
                self.mainwindow.view_widget.current_scene = sub_scene
                self.mainwindow.view_widget.current_scene_flag = sub_scene.sub_scene_flag
                self.mainwindow.view_widget.current_scene_flag.setSelected(True)
        else:

            sub_scene = attribute_widget.sub_scene

            if self.root_flag:
                self.last_scene = self.current_scene
                self.last_scene_flag = self.current_scene_flag

                self.current_scene.clearSelection()
                self.setScene(sub_scene)
                self.current_scene = sub_scene
                self.current_scene_flag = sub_scene.sub_scene_flag
                self.current_scene_flag.setSelected(True)
                self.background_image = self.current_scene.background_image
                self.cutline = self.current_scene.cutline
            else:
                self.mainwindow.view_widget.last_scene = self.mainwindow.view_widget.current_scene
                self.mainwindow.view_widget.last_scene_flag = self.mainwindow.view_widget.current_scene_flag

                self.current_scene.clearSelection()
                self.mainwindow.view_widget.current_scene.clearSelection()
                self.mainwindow.view_widget.setScene(sub_scene)
                self.mainwindow.view_widget.current_scene = sub_scene
                self.mainwindow.view_widget.current_scene_flag = sub_scene.sub_scene_flag
                self.mainwindow.view_widget.current_scene_flag.setSelected(True)
                self.mainwindow.view_widget.background_image = self.mainwindow.view_widget.current_scene.background_image
                self.mainwindow.view_widget.cutline = self.mainwindow.view_widget.current_scene.cutline

        # Style init
        self.mainwindow.style_switch_combox.setCurrentIndex(0)
        self.mainwindow.style_switch_combox.setCurrentIndex(1)

        if self.undo_flag:
            self.current_scene.history.store_history("Create Sub Scene")

    def change_current_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem, remove_flag=False):
        """
        Enter different sub scene in different attribute widget.

        Args:
            sub_scene_item: The item in scene list.
            remove_flag: Whether delete sub scene.

        """
        self.mainwindow.scene_list.clearSelection()

        if self.root_flag:
            if not remove_flag:
                self.last_scene = self.current_scene
                self.last_scene_flag = self.current_scene_flag
            else:
                self.last_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
                self.last_scene_flag = sub_scene_item

            self.current_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
            self.current_scene_flag = sub_scene_item
            self.current_scene_flag.setSelected(True)
            self.setScene(self.current_scene)
            self.background_image = self.current_scene.background_image
            self.cutline = self.current_scene.cutline
        else:
            self.mainwindow.view_widget.last_scene = self.mainwindow.view_widget.current_scene
            self.mainwindow.view_widget.last_scene_flag = self.mainwindow.view_widget.current_scene_flag

            self.mainwindow.view_widget.current_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
            self.mainwindow.view_widget.current_scene_flag = sub_scene_item
            self.mainwindow.view_widget.current_scene_flag.setSelected(True)
            self.mainwindow.view_widget.setScene(self.mainwindow.view_widget.current_scene)
            self.mainwindow.view_widget.background_image = self.mainwindow.view_widget.current_scene.background_image
            self.mainwindow.view_widget.cutline = self.mainwindow.view_widget.current_scene.cutline

        self.mainwindow.style_switch_combox.setCurrentIndex(0)
        self.mainwindow.style_switch_combox.setCurrentIndex(1)

    def delete_sub_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem):
        """
        Delete sub scene in attribute widget

        Args:
            sub_scene_item: The item in scene list.


        """

        parent_flag = sub_scene_item.parent()

        if parent_flag:
            # change current scene
            self.change_current_scene(parent_flag, remove_flag=True)
            # delete
            parent_flag.removeChild(sub_scene_item)
            sub_scene_item.data(0, QtCore.Qt.ToolTipRole).attribute_widget.sub_scene = None

    def print_item(self, part: str):
        """
        Generate images which contains the selected or all items in current scene.

        Args:
            part: Flag to control generation logic.

        """

        if part == "Scene":
            pic = QtGui.QPixmap(self.current_scene.sceneRect().width(), self.current_scene.sceneRect().height())
            painter = QtGui.QPainter(pic)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            self.current_scene.draw_image = QtGui.QImage(os.path.abspath(os.path.join(constants.work_dir,
                                                    "Resources/Images/scene_background.png")))
            self.current_scene.removeItem(self.background_image)
            self.current_scene.render(painter)
            self.current_scene.draw_image = QtGui.QImage(os.path.abspath(os.path.join(constants.work_dir,
                                                    "Resources/Images/common_background_image.png")))
            self.current_scene.addItem(self.background_image)
            painter.end()
            name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "./"+str(time.time())+".png", "Image type(*.png *.jpg)")
            if name and ok:
                pic.save(name)
        elif part == "Items":
            if self.current_scene.selectedItems():
                left = float("+inf")
                right = float("-inf")
                top = float("+inf")
                bottom = float("-inf")
                for item in self.current_scene.selectedItems():
                    if item.scenePos().x() <= left:
                        left = item.scenePos().x() - 20
                    if item.scenePos().x() + item.boundingRect().width() >= right:
                        right = item.scenePos().x() + item.boundingRect().width() + 20
                    if item.scenePos().y() <= top:
                        top = item.scenePos().y() - 20
                    if item.scenePos().y() + item.boundingRect().height() >= bottom:
                        bottom = item.scenePos().y() + item.boundingRect().height() + 20

                pic = QtGui.QPixmap(abs(right - left), abs(bottom - top))
                painter = QtGui.QPainter(pic)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)
                self.current_scene.removeItem(self.background_image)
                self.current_scene.clearSelection()
                self.current_scene.render(painter,
                                          target=QtCore.QRectF(),
                                          source=QtCore.QRectF(left, top, right - left, bottom - top))
                self.current_scene.addItem(self.background_image)
                painter.end()
                name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "./"+str(time.time())+".png", "Image type(*.png *.jpg)")
                if name and ok:
                    pic.save(name)
    
    def export_current_scene(self, include=True):
        """
        export current scene to .note file

        Args:
            include: if include sub scene.
        """
        if self.root_flag:
            if include:
                attribute.AttributeWidget.export_sub_scene_flag = True
                filename, ok = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                    "Export current scene including sub scene to note file", os.path.join(constants.work_dir, ".note"),
                                                                    "note (*.note)")
                if filename and ok:
                    with open(filename, 'wb') as file:
                        file.write(self.serialize(export_current_scene=True))   
            else:
                attribute.AttributeWidget.export_sub_scene_flag = False

                filename, ok = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                        "Export current scene not including sub scene to note file", os.path.join(constants.work_dir, ".note"),
                                                                        "note (*.note)")
                if filename and ok:
                    with open(filename, 'wb') as file:
                        file.write(self.serialize(export_current_scene=True))
                
                attribute.AttributeWidget.export_sub_scene_flag = True

        
    def tabletEvent(self, a0: QtGui.QTabletEvent) -> None:
        """
        Used for tablet

        Args:
            a0: QtGui.QTabletEvent

        """

        View.tablet_used = False

        # Send to the draw widge
        item = self.itemAt(a0.pos().x(),
                           a0.pos().y())

        # Change style when the pen almost enter
        if a0.type() == QtCore.QEvent.TabletEnterProximity:
            self.mouse_effect = False
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            cursor_style = QtGui.QPixmap(os.path.abspath(os.path.join(constants.work_dir,
                                                      'Resources/Images/point.png'))).scaled(4,
                                                                                        4)
            cursor = QtGui.QCursor(cursor_style, 2, 2)
            QtWidgets.QApplication.setOverrideCursor(cursor)
        
        if isinstance(item, (draw.Canvas, draw.Draw)):
            # Make other mouse events not work
            View.tablet_used = True
            item.tablet_event(a0)

        a0.accept()

    def mousePressEvent(self, event) -> None:
        if not self.tablet_used:

            try:
                temp = self.itemAt(event.pos())
                if temp:
                    temp.scenePos()  # debug for scaling, i don't understand but it works
                
                # debug for sub scene, i don't understand but it works
                if not self.root_flag:
                    self.magic()
            except AttributeError:
                pass
            if constants.DEBUG_DRAW_PIPE:
                print("mouse press at", self.itemAt(event.pos()))
            if self.mode == constants.MODE_PIPE_DRAG:
                item = self.itemAt(event.pos())
                if isinstance(item, port.Port):
                    if item is self.drag_pipe.start_port:
                        self.drag_pipe_release(None)
                        self.mode = constants.MODE_NOOP
                else:
                    self.drag_pipe_release(None)
                    self.mode = constants.MODE_NOOP

            if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.ControlModifier:
                self.cutline_pressed()
                return
            if event.button() == QtCore.Qt.LeftButton and self.mouse_effect:
                self.set_leftbtn_beauty(event)
            item = self.itemAt(event.pos())
            if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.AltModifier:
                if isinstance(item, attribute.AttributeWidget):
                    self.new_sub_scene(item)
                elif isinstance(item, attribute.SubConstituteWidget):
                    self.new_sub_scene(item.parentItem())
                elif isinstance(item, attribute.InputTextField):
                    self.new_sub_scene(item.node)

            # control point
            pipe_item = self.itemAt(event.pos())
            if event.button() == QtCore.Qt.LeftButton and isinstance(pipe_item, pipe.Pipe):
                self.pipe_true_item = pipe_item
                self.pipe_true_item.show_flag = True
            elif event.button() == QtCore.Qt.LeftButton and isinstance(pipe_item, attribute.SimpleTextField):
                self.pipe_true_item = pipe_item.parentItem()
                self.pipe_true_item.show_flag = True
            elif event.button() == QtCore.Qt.LeftButton and \
                    hasattr(pipe_item, "control_point_flag"):
                self.pipe_true_item.show_flag = True
            else:
                for pipe_widget in self.pipes:
                    pipe_widget.show_flag = False

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.tablet_used:
            super(View, self).mouseReleaseEvent(event)
            if self.mode == constants.MODE_PIPE_CUT:
                self.cutline_released()
                return

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.tablet_used:
            super(View, self).mouseDoubleClickEvent(event)
            if event.buttons() == QtCore.Qt.LeftButton:
                self.drag_pipe_press(event)
                item = self.itemAt(event.pos())
                if hasattr(item, 'file_url'):
                    # noinspection PyTypeChecker
                    self.open_file(item)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if not self.tablet_used:
            # change style when no tablet device
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
            self.mouse_effect = True
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)

            super(View, self).mouseMoveEvent(event)
            if self.mode == constants.MODE_PIPE_DRAG:
                self.drag_pipe.prepareGeometryChange()
                self.drag_pipe.update_position(self.mapToScene(event.pos()))
            elif self.mode == constants.MODE_PIPE_CUT:
                self.cutline.line_points.append(self.mapToScene(event.pos()))
                self.cutline.prepareGeometryChange()
                self.cutline.update()

    def keyPressEvent(self, event) -> None:
        super(View, self).keyPressEvent(event)

        from ..Components.attribute import InputTextField
        current_item = self.current_scene.itemAt(self.mapToScene(self.mapFromGlobal(QtGui.QCursor.pos())), QtGui.QTransform())

        if event.key() == QtCore.Qt.Key_R and int(event.modifiers()) & QtCore.Qt.AltModifier and not event.isAccepted():
            self.copy_item()
            event.accept()
            return

        if isinstance(current_item, effect_background.EffectBackground):
            if event.key() == QtCore.Qt.Key_Q and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.add_attribute_widget(pos=QtGui.QCursor.pos())
                return
            if event.key() == QtCore.Qt.Key_W and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.add_truth_widget(pos=QtGui.QCursor.pos())
                return
            if self.root_flag and event.key() == QtCore.Qt.Key_E and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.add_draw_widget(pos=QtGui.QCursor.pos())
                return
            if event.key() == QtCore.Qt.Key_Delete and isinstance(self.scene().focusItem(), InputTextField):
                if self.scene().focusItem().objectName() == 'MouseLocked':
                    return
            if event.key() == QtCore.Qt.Key_T and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.paste_item()
                return
            if event.key() == QtCore.Qt.Key_1 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.expand("left")
                return
            if event.key() == QtCore.Qt.Key_2 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.expand("right")
                return
            if event.key() == QtCore.Qt.Key_3 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.expand("top")
                return
            if event.key() == QtCore.Qt.Key_4 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.expand("bottom")
                return
            if event.key() == QtCore.Qt.Key_5 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.narrow("left")
                return
            if event.key() == QtCore.Qt.Key_6 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.narrow("right")
                return
            if event.key() == QtCore.Qt.Key_7 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.narrow("top")
                return
            if event.key() == QtCore.Qt.Key_8 and int(event.modifiers()) & QtCore.Qt.AltModifier:
                self.narrow("bottom")
                return
            if event.key() == QtCore.Qt.Key_Left and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.align("left")
                return
            if event.key() == QtCore.Qt.Key_Right and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.align("right")
                return
            if event.key() == QtCore.Qt.Key_Up and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.align("up")
                return
            if event.key() == QtCore.Qt.Key_Down and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.align("down")
                return
            if event.key() == QtCore.Qt.Key_1 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_expand("left")
                return
            if event.key() == QtCore.Qt.Key_2 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_expand("right")
                return
            if event.key() == QtCore.Qt.Key_3 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_expand("up")
                return
            if event.key() == QtCore.Qt.Key_4 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_expand("down")
                return
            if event.key() == QtCore.Qt.Key_5 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_narrow("left")
                return
            if event.key() == QtCore.Qt.Key_6 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_narrow("right")
                return
            if event.key() == QtCore.Qt.Key_7 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_narrow("up")
                return
            if event.key() == QtCore.Qt.Key_8 and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
                self.tanslation_narrow("down")
                return

        if self.mode == constants.MODE_PIPE_DRAG and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.drag_pipe_release(None)
            self.mode = constants.MODE_NOOP
            return
        if event.key() == QtCore.Qt.Key_0 and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.view_update_pipe_animation()
            return
        if event.key() == QtCore.Qt.Key_9 and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.python_highlighter()
            return
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_widgets(event)
            return
        if (event.key() == QtCore.Qt.Key_Equal and event.modifiers() & QtCore.Qt.ControlModifier) or \
                (event.key() == QtCore.Qt.Key_Minus and event.modifiers() & QtCore.Qt.ControlModifier):
            self.change_scale(event)
            return
        if event.key() == QtCore.Qt.Key_F and int(event.modifiers()) & QtCore.Qt.ControlModifier and self.root_flag:
            self.search_text()
            return
        if event.key() == QtCore.Qt.Key_Z and int(event.modifiers()) & QtCore.Qt.ControlModifier and not event.isAccepted():
            self.current_scene.history.undo()
            return
        if event.key() == QtCore.Qt.Key_Y and int(event.modifiers()) & QtCore.Qt.ControlModifier and not event.isAccepted():
            self.current_scene.history.redo()
            return
        if event.key() == QtCore.Qt.Key_P and int(event.modifiers()) & QtCore.Qt.ControlModifier and \
                int(event.modifiers()) & QtCore.Qt.AltModifier:
            self.print_item(part="Scene")
            return
        if event.key() == QtCore.Qt.Key_P and int(event.modifiers()) & QtCore.Qt.ControlModifier and \
                int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.print_item(part="Items")
            return
        if event.key() == QtCore.Qt.Key_S and int(event.modifiers()) & QtCore.Qt.AltModifier:
            self.export_current_scene(include=True)
            return
        if event.key() == QtCore.Qt.Key_S and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.export_current_scene(include=False)
            return
        if event.key() == QtCore.Qt.Key_F1 and self.root_flag:
            self.line_flag = not self.line_flag
            return
        if event.key() == QtCore.Qt.Key_F2 and self.root_flag:
            self.undo_flag = not self.undo_flag
            return
        if event.key() == QtCore.Qt.Key_F11:
            self.change_flowing_image(True)
            return

    def contextMenuEvent(self, event: 'QtGui.QContextMenuEvent') -> None:
        super(View, self).contextMenuEvent(event)
        leftbtn_press_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick, event.pos(), event.globalPos(),
                                                QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
        self.mouseDoubleClickEvent(leftbtn_press_event)
        from ..Components.sub_view import ProxyView
        from ..Components.todo import Todo
        if self.root_flag:
            current_item = self.itemAt(event.pos())
        else:
            current_item = self.current_scene.itemAt(self.mapToScene(event.pos()), QtGui.QTransform())
        if isinstance(current_item, effect_background.EffectBackground):
            context_menu = QtWidgets.QMenu(self)
            # context list
            create_attribute_widget = context_menu.addAction(QtCore.QCoreApplication.translate("View", "create attribute widget"))
            create_attribute_widget.setIcon(QtGui.QIcon(os.path.join(constants.work_dir, "Resources/Images/Attribute Widget.png")))
            create_truth_widget = context_menu.addAction(QtCore.QCoreApplication.translate("View", "create truth widget"))
            create_truth_widget.setIcon(
                (QtGui.QIcon(os.path.abspath(os.path.join(constants.work_dir,
                                          "Resources/Images/Truth Widget.png")))))
            if self.root_flag:
                create_canvas_widget = context_menu.addAction(QtCore.QCoreApplication.translate("View", "create canvas widget"))
                create_canvas_widget.setIcon(
                    QtGui.QIcon(os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/draw_widget.png"))))
            change_background_image = context_menu.addAction(QtCore.QCoreApplication.translate("View", "change background image"))
            change_background_image.setIcon(QtGui.QIcon(
                os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/Change Background Image.png"))))
            change_snow_image = context_menu.addAction(QtCore.QCoreApplication.translate("View", "change flowing image"))
            change_snow_image.setIcon(
                QtGui.QIcon(os.path.abspath(os.path.join(constants.work_dir,
                                         "Resources/Images/Change flowing.png"))))

            action = context_menu.exec_(self.mapToGlobal(event.pos()))
            if action == create_attribute_widget:
                self.add_attribute_widget(event)
            elif action == create_truth_widget:
                self.add_truth_widget(event)
            elif self.root_flag and action == create_canvas_widget:
                self.add_draw_widget(event)
            elif action == change_background_image:
                self.change_svg_image()
            elif action == change_snow_image:
                self.change_flowing_image()
        elif isinstance(current_item, (attribute.AttributeWidget, attribute.AttributeFile, Todo)):
            # if self.root_flag:
            current_item.context_flag = True
            current_item.contextMenuEvent(event)
        elif isinstance(current_item, attribute.InputTextField):
            if self.root_flag:
                current_item.node.context_flag = True
                current_item.node.contextMenuEvent(event)
        elif isinstance(current_item, (attribute.SubConstituteWidget, attribute.SimpleTextField)):
            if self.root_flag and not isinstance(current_item.parentItem(), (pipe.Pipe, attribute.AttributeFile)):
                current_item.parentItem().context_flag = True
                current_item.parentItem().contextMenuEvent(event)
        elif isinstance(current_item, ProxyView):
            return

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(View, self).drawBackground(painter, rect)
        if self.zoom - 5 >=0:
            zoom_factor = self.zoomOutFactor ** (self.zoom - 5)
        else:
            zoom_factor = self.zoomInFactor ** (-(self.zoom - 5))
        self.background_image.setPos(self.mapToScene(0, 0).x(), self.mapToScene(0, 0).y())
        self.background_image.resize(self.size().width() * zoom_factor, self.size().height() * zoom_factor)

    def serialize(self, view_serialization=None, export_current_scene=False):
        """
        Serialization.

        Args:
            view_serialization: The protobuff object.

        """

        # root view
        if not view_serialization:
            view_serialization = serialize_pb2.ViewSerialization()
        # root scene
        if not export_current_scene:
            self.root_scene.serialize(view_serialization.scene_serialization.add())
        else:
            self.current_scene.serialize(view_serialization.scene_serialization.add())

        view_serialization.current_scene_id = self.current_scene.id

        # ui serialization
        if self.image_path:
            view_serialization.image_path = self.image_path
        
        view_serialization.style_path = self.mainwindow.load_window.runtime_style.path

        # attribute widget ui
        view_serialization.all_attr_font_family = attribute.InputTextField.font.family()
        view_serialization.all_attr_font_size = attribute.InputTextField.font.pointSize()
        view_serialization.all_attr_color.append(attribute.InputTextField.font_color.rgba())
        view_serialization.all_attr_color.append(attribute.AttributeWidget.color.rgba())
        view_serialization.all_attr_color.append(attribute.AttributeWidget.selected_color.rgba())
        view_serialization.all_attr_color.append(attribute.AttributeWidget.border_color.rgba())
        view_serialization.all_attr_color.append(attribute.AttributeWidget.selected_border_color.rgba())

        # logic widget ui
        view_serialization.all_logic_color.append(attribute.LogicWidget.background_color.rgba())
        view_serialization.all_logic_color.append(attribute.LogicWidget.selected_background_color.rgba())
        view_serialization.all_logic_color.append(attribute.LogicWidget.border_color.rgba())
        view_serialization.all_logic_color.append(attribute.LogicWidget.selected_border_color.rgba())

        # pipe widget ui
        view_serialization.all_pipe_width = pipe.Pipe.width
        view_serialization.all_pipe_color.append(pipe.Pipe.color.rgba())
        view_serialization.all_pipe_color.append(pipe.Pipe.selected_color.rgba())
        view_serialization.all_pipe_color.append(pipe.Pipe.font_color.rgba())
        view_serialization.all_pipe_font_family = pipe.Pipe.font.family()
        view_serialization.all_pipe_font_size = pipe.Pipe.font.pointSize()

        # port widget ui
        view_serialization.all_port_width = port.Port.width
        view_serialization.all_port_color.append(port.Port.color.rgba())
        view_serialization.all_port_color.append(port.Port.border_color.rgba())
        view_serialization.all_port_color.append(port.Port.hovered_color.rgba())
        view_serialization.all_port_color.append(port.Port.hovered_border_color.rgba())
        view_serialization.all_port_color.append(port.Port.activated_color.rgba())
        view_serialization.all_port_color.append(port.Port.activated_border_color.rgba())

        # container widget ui
        view_serialization.all_draw_width = draw.Draw.pen_width
        view_serialization.all_draw_color = draw.Draw.color.rgba()

        # text widget ui
        view_serialization.text_width = attribute.AttributeWidget.width_flag

        # background image
        view_serialization.all_background_image = effect_background.EffectBackground.name

        # flag
        if self.root_flag:
            view_serialization.line_flag = self.line_flag
        view_serialization.undo_flag = self.undo_flag

        # flowing image
        view_serialization.flowing_flag = self.flowing_flag

        return view_serialization.SerializeToString()

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        """
        Deserialization.

        Args:
            data: The protobuf object.
            hashmap: hashmap.
            view: QGraphicsView manager.
            flag: first time deserialization and second time deserialization.

        """

        # clear all contents
        for item in self.root_scene.items():
            from ..Components.sub_view import ProxyView
            if not isinstance(item, (effect_background.EffectBackground, effect_cutline.EffectCutline, ProxyView)):
                self.root_scene.removeItem(item)
        if self.root_flag:
            self.mainwindow.scene_list.clear()
        self.attribute_widgets = list()
        self.logic_widgets = list()
        self.pipes = list()
        self.draw_widgets = list()

        # image path
        if data.image_path:
            effect_snow.SnowWidget.image_path = data.image_path
            self.image_path = data.image_path
        
        if data.HasField("style_path"):
            self.mainwindow.runtime_style.path = data.style_path

        # set root scene
        if self.root_flag:
            self.root_scene_flag = TreeWidgetItem(
                self.mainwindow.scene_list,
                ("Root Scene",))
            self.root_scene_flag.setData(0, QtCore.Qt.ToolTipRole, self.root_scene)
        self.current_scene = self.root_scene
        self.current_scene_flag = self.root_scene_flag
        self.background_image = self.current_scene.background_image
        self.cutline = self.current_scene.cutline
        self.setScene(self.current_scene)

        # style
        #   attribute widget
        attribute.InputTextField.font = QtGui.QFont()
        attribute.InputTextField.font.setFamily(data.all_attr_font_family)
        attribute.InputTextField.font.setPointSize(data.all_attr_font_size)
        attribute.InputTextField.font_color.setRgba(data.all_attr_color[0])

        attribute.AttributeWidget.color.setRgba(data.all_attr_color[1])
        attribute.AttributeWidget.selected_color.setRgba(data.all_attr_color[2])
        attribute.AttributeWidget.border_color.setRgba(data.all_attr_color[3])
        attribute.AttributeWidget.selected_border_color.setRgba(data.all_attr_color[4])

        #   logic widget
        attribute.LogicWidget.background_color.setRgba(data.all_logic_color[0])
        attribute.LogicWidget.selected_background_color.setRgba(data.all_logic_color[1])
        attribute.LogicWidget.border_color.setRgba(data.all_logic_color[2])
        attribute.LogicWidget.selected_border_color.setRgba(data.all_logic_color[3])

        #   pipe widget
        pipe.Pipe.width = data.all_pipe_width
        pipe.Pipe.color.setRgba(data.all_pipe_color[0])
        pipe.Pipe.selected_color.setRgba(data.all_pipe_color[1])
        if len(data.all_pipe_color) == 3:
            pipe.Pipe.font_color.setRgba(data.all_pipe_color[2])
            pipe.Pipe.font = QtGui.QFont()
            pipe.Pipe.font.setFamily(data.all_pipe_font_family)
            pipe.Pipe.font.setPointSize(data.all_pipe_font_size)

        #   port widget
        port.Port.width = data.all_port_width
        port.Port.color.setRgba(data.all_port_color[0])
        port.Port.border_color.setRgba(data.all_port_color[1])
        port.Port.hovered_color.setRgba(data.all_port_color[2])
        port.Port.hovered_border_color.setRgba(data.all_port_color[3])
        port.Port.activated_color.setRgba(data.all_port_color[4])
        port.Port.activated_border_color.setRgba(data.all_port_color[5])

        #   draw widget
        draw.Draw.pen_width = data.all_draw_width
        draw.SideDraw.pen_width = data.all_draw_width
        draw.Draw.color.setRgb(data.all_draw_color)
        draw.SideDraw.color.setRgb(data.all_draw_color)

        #   background image
        if data.HasField("all_background_image"):
            effect_background.EffectBackground.name = data.all_background_image

        #   text widget
        try:
            if data.text_width:
                attribute.AttributeWidget.width_flag = data.text_width
                self.mainwindow.text_editor_length_box.setValue(data.text_width)
        except Exception:
            pass

        # flag
        if self.root_flag and data.line_flag:
            self.line_flag = data.line_flag
        if data.undo_flag:
            self.undo_flag = data.undo_flag

        if data.HasField("flowing_flag"):
            self.flowing_flag = data.flowing_flag
            if not self.flowing_flag:
                self.mainwindow.sky_widget.hide()

        self.mainwindow.style_switch_combox.setCurrentIndex(1)
        self.mainwindow.style_switch_combox.setCurrentIndex(0)

        # create contents
        hashmap = {}
        self.root_scene.deserialize(data.scene_serialization[0], hashmap, view, flag=True)
        self.root_scene.deserialize(data.scene_serialization[0], hashmap, view, flag=False)

        # recover current scene
        if self.root_flag:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole).id == data.current_scene_id:
                    self.current_scene = scene_flag.data(0, QtCore.Qt.ToolTipRole)
                    self.current_scene_flag = scene_flag
                    self.background_image = self.current_scene.background_image
                    self.cutline = self.current_scene.cutline
                    self.setScene(self.current_scene)

                    self.last_scene = self.current_scene
                    self.last_scene_flag = self.current_scene_flag

                    break

            expanded_item = 0
            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1

                if expanded_item < 5:
                    scene_flag.setExpanded(True)
                    expanded_item += 1
                else:
                    break

        return True
