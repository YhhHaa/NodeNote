import json
import time
import re
from collections import OrderedDict
from PyQt5 import QtGui, QtCore, QtWidgets, sip
from GraphicsView.scene import Scene
from Components import effect_water, attribute, port, pipe, container, effect_cutline, effect_background, effect_snow
from Model import constants, stylesheet, history, serializable

__all__ = ["View", "TreeWidgetItem"]


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        key_1 = self.natural_sort_key(self.text(column))
        key_2 = self.natural_sort_key(other.text(column))
        if isinstance(key_1, int) and isinstance(key_2, int) or isinstance(key_1, str) and isinstance(key_2, str):
            return key_1 < key_2
        else:
            return str(key_1) < str(key_2)

    @staticmethod
    def natural_sort_key(key):
        text = re.match(r'(.+?)\..*', key, re.M)
        if text:
            text = text.group(1)
            if text.isdigit():
                return int(text)
            elif text:
                return text
        else:
            return 0


class View(QtWidgets.QGraphicsView, serializable.Serializable):
    def __init__(self, mainwindow, parent=None, root_flag=True, proxy_widget = None):
        self.root_flag = root_flag
        self.mainwindow = mainwindow
        self.proxy_widget = proxy_widget
        super(View, self).__init__(parent)
        if self.root_flag:
            self.gpu_format = QtGui.QSurfaceFormat()
            self.gpu_format.setSamples(4)
            self.gpu_format.setSwapInterval(0)
            self.gpu_format.setRenderableType(QtGui.QSurfaceFormat.OpenGL)
            self.gpu_format.setSwapBehavior(QtGui.QSurfaceFormat.DefaultSwapBehavior)
            self.gpu = QtWidgets.QOpenGLWidget()
            self.gpu.setFormat(self.gpu_format)
            self.setViewport(self.gpu)
        # BASIC SETTINGS
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        if self.root_flag:
            self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
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
        self.horizontal_scrollbar.setStyleSheet(stylesheet.STYLE_HSCROLLBAR)
        self.setHorizontalScrollBar(self.horizontal_scrollbar)
        self.vertical_scrollbar = QtWidgets.QScrollBar()
        self.vertical_scrollbar.setStyleSheet(stylesheet.STYLE_VSCROLLBAR)
        self.setVerticalScrollBar(self.vertical_scrollbar)

        # DRAW LINE
        self.drag_pipe = None
        self.item = None
        self.mode = constants.MODE_NOOP

        # STORE
        self.attribute_widgets = list()
        self.logic_widgets = list()
        self.pipes = list()
        self.containers = list()

        # Container
        self.container_widget = None

        # SUB SCENE
        if self.root_flag:
            self.root_scene_flag = TreeWidgetItem(self.mainwindow.scene_list,
                                                ("Root Scene",))
            self.root_scene_flag.setData(0, QtCore.Qt.ToolTipRole, self.root_scene)
            self.root_scene_flag.setExpanded(True)
        else:
            self.root_scene_flag = self.mainwindow.view_widget.current_scene_flag

        self.root_scene.sub_scene_flag = self.root_scene_flag
        self.current_scene = self.root_scene
        self.current_scene_flag = self.root_scene_flag

        # History
        if self.root_flag:
            self.history = history.History(self)
        else:
            self.history = self.mainwindow.view_widget.history

        # Search
        self.search_widget = QtWidgets.QWidget(self)
        self.search_widget.setVisible(False)
        self.text_widget = QtWidgets.QLineEdit(self.search_widget)
        self.text_widget.setStyleSheet(stylesheet.STYLE_QLINEEDIT)
        self.label_widget = QtWidgets.QLabel("Search: ", self.search_widget)
        self.label_widget.setStyleSheet(stylesheet.STYLE_QLABEL)
        self.search_button = QtWidgets.QPushButton("Search", self.search_widget)
        self.search_widget.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.next_button = QtWidgets.QPushButton("Next", self.search_widget)
        self.next_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.last_button = QtWidgets.QPushButton("Last", self.search_widget)
        self.last_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)

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
        self.tablet_used = False
        self.mouse_effect = True
        self.setAttribute(QtCore.Qt.WA_TabletTracking)

    def set_leftbtn_beauty(self, event):
        water_drop = effect_water.EffectWater()
        property_water_drop = QtWidgets.QGraphicsProxyWidget()
        property_water_drop.setWidget(water_drop)
        self.current_scene.addItem(property_water_drop)
        water_drop.move(self.mapToScene(event.pos()))
        water_drop.show()
        super(View, self).mousePressEvent(event)

    def change_svg_image(self):
        image_name, image_type = QtWidgets.QFileDialog.getOpenFileName(self, "select svg", "", "*.svg")
        if image_name != "":
            self.background_image.change_svg(image_name)

    def change_flowing_image(self):
        image_name, image_type = QtWidgets.QFileDialog.getOpenFileName(self, "select png", "", "*.png")
        if image_name != "":
            self.image_path = image_name
            effect_snow.SnowWidget.image_path = image_name

    def change_scale(self, event):
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

        self.history.store_history("update pipe animation")
        if self.filename and not self.first_open:
            self.save_to_file()

    def python_highlighter(self):
        for item in self.current_scene.selectedItems():
            if isinstance(item, attribute.AttributeWidget):
                item.attribute_widget.label_item.pythonlighter = \
                    attribute.PythonHighlighter(item.attribute_widget.label_item.document())

    def search_text(self):
        # widget
        if not self.search_widget.isVisible():
            self.search_widget.setGeometry(self.size().width() // 2 - 250, 0, 500, 50)
            self.search_widget.setVisible(True)
            self.text_widget.setFocus()
        else:
            self.search_widget.setVisible(False)

            for item_id in self.text_format:
                for item in self.attribute_widgets:
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
                from Components.sub_view import ProxyView
                from Components.todo import Todo
                if not isinstance(item, (ProxyView, Todo)):
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

                self.next_search(label_widget)

                if not self.search_list:
                    self.label_widget.setText("Result 0/0")

        else:
            self.label_widget.setText("Result 0/0")

    def next_search(self, label_widget):
        if self.search_list:

            self.search_position += 1
            if self.search_position > len(self.search_list) - 1:
                self.search_position = len(self.search_list) - 1

            at_scene = self.search_list[self.search_position].scene()
            self.current_scene = at_scene
            self.current_scene_flag = at_scene.sub_scene_flag
            self.background_image = at_scene.background_image
            self.cutline = at_scene.cutline
            self.setScene(at_scene)
            self.centerOn(self.search_list[self.search_position])
            label_widget.setText("Result %d/%d" % (self.search_position + 1, len(self.search_list)))

    def last_search(self, label_widget):
        if self.search_list:
            self.search_position -= 1
            if self.search_position < 0:
                self.search_position = 0

            at_scene = self.search_list[self.search_position].scene()
            self.current_scene = at_scene
            self.current_scene_flag = at_scene.sub_scene_flag
            self.background_image = at_scene.background_image
            self.cutline = at_scene.cutline
            self.setScene(at_scene)
            self.centerOn(self.search_list[self.search_position])
            label_widget.setText("Result %d/%d" % (self.search_position + 1, len(self.search_list)))

    def delete_connections(self, item):
        if isinstance(item, attribute.AttributeWidget):
            for pipe_widget in item.true_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.true_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.false_output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
        elif isinstance(item, attribute.LogicWidget):
            for pipe_widget in item.input_port.pipes:
                output_port = pipe_widget.get_output_type_port()
                output_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)
            for pipe_widget in item.output_port.pipes:
                input_port = pipe_widget.get_input_type_port()
                input_port.remove_pipes(pipe_widget)
                self.current_scene.removeItem(pipe_widget)
                self.pipes.remove(pipe_widget)

    def delete_widgets(self, event):
        from Components.todo import Todo
        if event.key() == QtCore.Qt.Key_Delete:
            for item in self.current_scene.selectedItems():
                if item in self.current_scene.selectedItems():
                    if isinstance(item, attribute.AttributeWidget):
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

                        if item.sub_scene:
                            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
                            while iterator.value():
                                scene_flag = iterator.value()
                                iterator += 1
                                if scene_flag.data(0, QtCore.Qt.ToolTipRole) is item.sub_scene:

                                    self.delete_sub_scene(scene_flag)

                        if item.parentItem():
                            parent_item = item.parentItem()
                            parent_item.delete_subwidget(item)
                            self.remove_attribute_widget(item)
                        else:
                            self.remove_attribute_widget(item)

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
                        self.delete_pipe(item)
                    elif isinstance(item, container.Container):
                        self.current_scene.removeItem(item)
                        self.containers.remove(item)
                    elif isinstance(item, (attribute.AttributeFile, Todo)):
                        item.parent_item.attribute_layout.removeItem(item)
                        item.parent_item.attribute_sub_widgets.remove(item)
                        sip.delete(item)

                        item.parent_item.text_change_node_shape()
                        item.parent_item.update_pipe_position()

            self.history.store_history("Delete Widgets")
            if self.filename and not self.first_open:
                self.save_to_file()

    def delete_pipe(self, item):
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
        self.pipes.remove(item)

    def add_attribute_widget(self, event):
        basic_widget = attribute.AttributeWidget()
        self.current_scene.addItem(basic_widget)
        basic_widget.setPos(self.mapToScene(event.pos()))
        self.attribute_widgets.append(basic_widget)
        self.history.store_history("Add Attribute Widget")
        if self.filename and not self.first_open:
            self.save_to_file()

    def add_truth_widget(self, event):
        basic_widget = attribute.LogicWidget()
        self.current_scene.addItem(basic_widget)
        basic_widget.setPos(self.mapToScene(event.pos()))
        self.logic_widgets.append(basic_widget)
        self.history.store_history("Add Truth Widget")
        if self.filename and not self.first_open:
            self.save_to_file()

    def open_file(self, item):
        if not item.file_url:
            item.file_url, _ = QtWidgets.QFileDialog.getOpenFileName(self, "select files", "",
                                                                     "any file (*.*)")
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(item.file_url))
        self.history.store_history("Add File")
        if self.filename and not self.first_open:
            self.save_to_file()

    def add_drag_pipe(self, port_widget, pipe_widget):
        port_widget.add_pipes(pipe_widget)
        self.pipes.append(pipe_widget)
        self.current_scene.addItem(pipe_widget)

    def remove_attribute_widget(self, widget):
        self.current_scene.removeItem(widget)
        self.attribute_widgets.remove(widget)

    def remove_logic_widget(self, widget):
        self.current_scene.removeItem(widget)
        self.logic_widgets.remove(widget)

    def remove_drag_pipe(self, port_widget, pipe_widget):
        port_widget.remove_pipes(pipe_widget)
        if pipe_widget in self.pipes:
            self.pipes.remove(pipe_widget)
        self.current_scene.removeItem(pipe_widget)

    def drag_pipe_press(self, event):
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

                if input_node.attribute_animation or output_node.attribute_animation:
                    input_node.start_pipe_animation()
                    output_node.start_pipe_animation()

                self.history.store_history("Create Pipe")
                if self.filename and not self.first_open:
                    self.save_to_file()
            else:
                if constants.DEBUG_DRAW_PIPE:
                    print("delete drag pipe case 1")
                self.remove_drag_pipe(self.item, self.drag_pipe)
                self.item = None
        elif not isinstance(item, port.Port):
            if constants.DEBUG_DRAW_PIPE:
                print("delete drag pipe case 2 from port: ", self.item)
            self.remove_drag_pipe(self.item, self.drag_pipe)
            self.item = None

    def judge_same_pipe(self, item):
        for same_pipe in item.pipes:
            if same_pipe in self.item.pipes:
                return True
        return False

    def cut_interacting_edges(self):
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
        self.mode = constants.MODE_PIPE_CUT
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)

    def cutline_released(self):
        self.cut_interacting_edges()
        self.cutline.line_points = list()
        self.cutline.prepareGeometryChange()
        self.cutline.update()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
        self.mode = constants.MODE_NOOP

    def container_pressed(self, event):
        self.mode = constants.MODE_CONTAINER
        self.container_widget = container.Container(self.mapToScene(event.pos()))
        self.current_scene.addItem(self.container_widget)
        self.containers.append(self.container_widget)

    def container_released(self):
        self.mode = constants.MODE_NOOP

    def new_sub_scene(self, attribute_widget):
        if not attribute_widget.sub_scene:
            sub_scene_flag = TreeWidgetItem(self.current_scene_flag,
                                            (attribute_widget.attribute_widget.label_item.toPlainText(),))
            sub_scene = Scene(sub_scene_flag, self, attribute_widget)
            if self.root_flag:
                self.background_image = sub_scene.background_image
                self.cutline = sub_scene.cutline
            else:
                self.mainwindow.view_widget.background_image = sub_scene.background_image
                self.mainwindow.view_widget.cutline = sub_scene.cutline

            attribute_widget.set_sub_scene(sub_scene)

            sub_scene_flag.setData(0, QtCore.Qt.ToolTipRole, sub_scene)
            sub_scene_flag.setExpanded(True)

            if self.root_flag:
                self.current_scene.clearSelection()
                self.setScene(sub_scene)
                self.current_scene = sub_scene
                self.current_scene_flag = sub_scene.sub_scene_flag
            else:
                self.current_scene.clearSelection()
                self.mainwindow.view_widget.current_scene.clearSelection()
                self.mainwindow.view_widget.setScene(sub_scene)
                self.mainwindow.view_widget.current_scene = sub_scene
                self.mainwindow.view_widget.current_scene_flag = sub_scene.sub_scene_flag
        else:

            sub_scene = attribute_widget.sub_scene

            if self.root_flag:
                self.current_scene.clearSelection()
                self.setScene(sub_scene)
                self.current_scene = sub_scene
                self.current_scene_flag = sub_scene.sub_scene_flag
                self.background_image = self.current_scene.background_image
                self.cutline = self.current_scene.cutline
            else:
                self.current_scene.clearSelection()
                self.mainwindow.view_widget.current_scene.clearSelection()
                self.mainwindow.view_widget.setScene(sub_scene)
                self.mainwindow.view_widget.current_scene = sub_scene
                self.mainwindow.view_widget.current_scene_flag = sub_scene.sub_scene_flag
                self.mainwindow.view_widget.background_image = self.mainwindow.view_widget.current_scene.background_image
                self.mainwindow.view_widget.cutline = self.mainwindow.view_widget.current_scene.cutline

        # Style init
        self.mainwindow.style_switch_combox.setCurrentIndex(0)
        self.mainwindow.style_switch_combox.setCurrentIndex(1)

        self.history.store_history("Create Sub Scene")
        if self.filename and not self.first_open:
            self.save_to_file()

    def change_current_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem):
        if self.root_flag:
            self.current_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
            self.current_scene_flag = sub_scene_item
            self.setScene(self.current_scene)
            self.background_image = self.current_scene.background_image
            self.cutline = self.current_scene.cutline
        else:
            self.mainwindow.view_widget.current_scene = sub_scene_item.data(0, QtCore.Qt.ToolTipRole)
            self.mainwindow.view_widget.current_scene_flag = sub_scene_item
            self.mainwindow.view_widget.setScene(self.mainwindow.view_widget.current_scene)
            self.mainwindow.view_widget.background_image = self.mainwindow.view_widget.current_scene.background_image
            self.mainwindow.view_widget.cutline = self.mainwindow.view_widget.current_scene.cutline

        self.mainwindow.style_switch_combox.setCurrentIndex(0)
        self.mainwindow.style_switch_combox.setCurrentIndex(1)

        self.mainwindow.scene_list.selectionModel().clearSelection()

        if self.filename and not self.first_open:
            self.save_to_file()

    def delete_sub_scene(self, sub_scene_item: QtWidgets.QTreeWidgetItem):
        parent_flag = sub_scene_item.parent()

        if parent_flag:
            # change current scene
            self.change_current_scene(parent_flag)
            # delete
            parent_flag.removeChild(sub_scene_item)
            sub_scene_item.data(0, QtCore.Qt.ToolTipRole).attribute_widget.sub_scene = None

    def print_item(self, part: str):
        if part == "Scene":
            pic = QtGui.QPixmap(self.current_scene.sceneRect().width(), self.current_scene.sceneRect().height())
            painter = QtGui.QPainter(pic)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            self.current_scene.removeItem(self.background_image)
            self.current_scene.render(painter)
            self.current_scene.addItem(self.background_image)
            painter.end()
            name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "./", "Images (*.png *.jpg)")
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
                        left = item.scenePos().x()
                    if item.scenePos().x() + item.boundingRect().width() >= right:
                        right = item.scenePos().x() + item.boundingRect().width()
                    if item.scenePos().y() <= top:
                        top = item.scenePos().y()
                    if item.scenePos().y() + item.boundingRect().height() >= bottom:
                        bottom = item.scenePos().y() + item.boundingRect().height()

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
                name, ok = QtWidgets.QFileDialog.getSaveFileName(self, "Save Image", "./", "Images (*.png *.jpg)")
                if name and ok:
                    pic.save(name)

    def tabletEvent(self, a0: QtGui.QTabletEvent) -> None:

        self.tablet_used = True

        if a0.deviceType() == QtGui.QTabletEvent.Stylus:

            # change style when the pen almost enter
            if a0.type() == QtCore.QEvent.TabletEnterProximity:
                self.mouse_effect = False
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                cursor_style = QtGui.QPixmap('Resources/point.png').scaled(20, 20)
                cursor = QtGui.QCursor(cursor_style, 10, 10)
                QtWidgets.QApplication.setOverrideCursor(cursor)

            # draw line when the pen is on the tablet
            if a0.type() == QtCore.QEvent.TabletPress:
                self.container_pressed(a0)
            elif a0.type() == QtCore.QEvent.TabletMove and self.mode == constants.MODE_CONTAINER:
                self.container_widget.next_point = self.mapToScene(a0.pos())
                self.container_widget.update()
            elif a0.type() == QtCore.QEvent.TabletRelease:
                self.container_released()

        a0.accept()

    def mousePressEvent(self, event) -> None:
        if not self.tablet_used:

            try:
                self.itemAt(event.pos()).scenePos()  # debug for scale, i don't understand but it works
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
            if event.button() == QtCore.Qt.LeftButton and int(event.modifiers()) & QtCore.Qt.AltModifier and \
                    isinstance(item, attribute.AttributeWidget):
                self.new_sub_scene(item)

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
        from Components.attribute import InputTextField
        if event.key() == QtCore.Qt.Key_Delete and isinstance(self.scene().focusItem(), InputTextField):
            if self.scene().focusItem().objectName() == 'MouseLocked':
                return
        if self.mode == constants.MODE_PIPE_DRAG and int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.drag_pipe_release(None)
            self.mode = constants.MODE_NOOP
        if event.key() == QtCore.Qt.Key_0 and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.view_update_pipe_animation()
        if event.key() == QtCore.Qt.Key_6 and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.python_highlighter()
        if event.key() == QtCore.Qt.Key_Delete:
            self.delete_widgets(event)
        if (event.key() == QtCore.Qt.Key_Equal and event.modifiers() & QtCore.Qt.ControlModifier) or \
                (event.key() == QtCore.Qt.Key_Minus and event.modifiers() & QtCore.Qt.ControlModifier):
            self.change_scale(event)
        if event.key() == QtCore.Qt.Key_F and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.search_text()
        if event.key() == QtCore.Qt.Key_Z and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            if not event.isAccepted():
                self.history.undo()
                if self.filename and not self.first_open:
                    self.save_to_file()
        if event.key() == QtCore.Qt.Key_Y and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            if not event.isAccepted():
                self.history.redo()
                if self.filename and not self.first_open:
                    self.save_to_file()
        if event.key() == QtCore.Qt.Key_S and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.save_to_file()
        if event.key() == QtCore.Qt.Key_O and int(event.modifiers()) & QtCore.Qt.ControlModifier:
            self.load_from_file()
        if event.key() == QtCore.Qt.Key_P and int(event.modifiers()) & QtCore.Qt.ControlModifier and \
                int(event.modifiers()) & QtCore.Qt.AltModifier:
            self.print_item(part="Scene")
        if event.key() == QtCore.Qt.Key_P and int(event.modifiers()) & QtCore.Qt.ControlModifier and \
                int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.print_item(part="Items")
        if event.key() == QtCore.Qt.Key_I and int(event.modifiers()) & QtCore.Qt.ControlModifier and \
                int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.mainwindow.time_start()

    def contextMenuEvent(self, event: 'QtGui.QContextMenuEvent') -> None:
        super(View, self).contextMenuEvent(event)
        leftbtn_press_event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonDblClick, event.pos(), event.globalPos(),
                                                QtCore.Qt.LeftButton, QtCore.Qt.NoButton, event.modifiers())
        self.mouseDoubleClickEvent(leftbtn_press_event)
        from Components.sub_view import ProxyView
        current_item = self.itemAt(event.pos())
        if isinstance(current_item, effect_background.EffectBackground):
            context_menu = QtWidgets.QMenu(self)
            # context list
            create_attribute_widget = context_menu.addAction("Create Attribute Widget")
            create_attribute_widget.setIcon(QtGui.QIcon("Resources/ViewContextMenu/Attribute Widget.png"))
            create_truth_widget = context_menu.addAction("Create Truth Widget")
            create_truth_widget.setIcon((QtGui.QIcon("Resources/ViewContextMenu/Truth Widget.png")))
            change_background_image = context_menu.addAction("Change Background Image")
            change_background_image.setIcon(QtGui.QIcon("Resources/ViewContextMenu/Change Background Image.png"))
            change_snow_image = context_menu.addAction("Change flowing Image")
            change_snow_image.setIcon(QtGui.QIcon("Resources/ViewContextMenu/Change flowing.png"))

            action = context_menu.exec_(self.mapToGlobal(event.pos()))
            if action == create_attribute_widget:
                self.add_attribute_widget(event)
            elif action == create_truth_widget:
                self.add_truth_widget(event)
            elif action == change_background_image:
                self.change_svg_image()
            elif action == change_snow_image:
                self.change_flowing_image()
        elif isinstance(current_item, ProxyView):
            return
        elif isinstance(current_item, attribute.AttributeWidget):
            current_item.context_flag = True
            current_item.contextMenuEvent(event)
        elif isinstance(current_item, attribute.InputTextField):
            current_item.node.context_flag = True
            current_item.node.contextMenuEvent(event)
        elif isinstance(current_item, attribute.SubConstituteWidget):
            current_item.parentItem().context_flag = True
            current_item.parentItem().contextMenuEvent(event)


    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        super(View, self).drawBackground(painter, rect)
        self.background_image.setPos(self.mapToScene(0, 0).x(), self.mapToScene(0, 0).y())
        self.background_image.resize(self.size().width(), self.size().height())

    def save_to_file(self):
        if self.root_flag:
            if not self.filename:
                filename, ok = QtWidgets.QFileDialog.getSaveFileName(self,
                                                                     "Save serialization json file", "./", "json (*.json)")
                if filename and ok:
                    self.filename = filename
                    with open(filename, "w", encoding='utf-8') as file:
                        file.write(json.dumps(self.serialize(), indent=4))
                    self.mainwindow.setWindowTitle(filename + "-Life")
            else:
                with open(self.filename, "w", encoding='utf-8') as file:
                    file.write(json.dumps(self.serialize(), indent=4))
                self.mainwindow.setWindowTitle(self.filename + "-Life")

    def load_from_file(self):
        if self.root_flag:
            if not self.filename:
                filename, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                     "Open serialization json file", "./", "json (*.json)")
                if filename and ok:
                    with open(filename, "r", encoding='utf-8') as file:
                        data = json.loads(file.read())
                        self.deserialize(data, {}, self, True)
                        self.filename = filename
                        self.mainwindow.setWindowTitle(filename + "-Life")
            else:
                with open(self.filename, "r", encoding='utf-8') as file:
                    data = json.loads(file.read())
                    self.deserialize(data, {}, self, True)
                    self.mainwindow.setWindowTitle(self.filename + "-Life")

            self.first_open = False

    def serialize(self):
        return OrderedDict([
            ('root scene', self.root_scene.serialize()),
            ('current scene', self.current_scene.id),
            ('use time', self.start_time),
            ('last time', self.last_time),
            ('image path', self.image_path),
            ('attribute font family', attribute.InputTextField.font.family()),
            ('attribute font size', attribute.InputTextField.font.pointSize()),
            ('attribute font color', attribute.InputTextField.font_color.rgba()),
            ('attribute color', attribute.AttributeWidget.color.rgba()),
            ('attribute selected color', attribute.AttributeWidget.selected_color.rgba()),
            ('attribute border color', attribute.AttributeWidget.border_color.rgba()),
            ('attribute selected border color', attribute.AttributeWidget.selected_border_color.rgba()),
            ('logic color', attribute.LogicWidget.background_color.rgba()),
            ('logic selected color', attribute.LogicWidget.selected_background_color.rgba()),
            ('logic border color', attribute.LogicWidget.border_color.rgba()),
            ('logic selected border color', attribute.LogicWidget.selected_border_color.rgba()),
            ('pipe width', pipe.Pipe.width),
            ('pipe color', pipe.Pipe.color.rgba()),
            ('pipe selected color', pipe.Pipe.selected_color.rgba()),
            ('port width', port.Port.width),
            ('port color', port.Port.color.rgba()),
            ('port border color', port.Port.border_color.rgba()),
            ('port hovered color', port.Port.hovered_color.rgba()),
            ('port hovered border color', port.Port.hovered_border_color.rgba()),
            ('port activated color', port.Port.activated_color.rgba()),
            ('port activated border color', port.Port.activated_border_color.rgba()),
            ('container width', container.Container.width),
            ('container color', container.Container.color.rgba()),
            ('container selected color', container.Container.selected_color.rgba())
        ])

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # clear all contents
        for item in self.root_scene.items():
            from Components.sub_view import ProxyView
            if not isinstance(item, (effect_background.EffectBackground, effect_cutline.EffectCutline, ProxyView)):
                self.root_scene.removeItem(item)
        if self.root_flag:
            self.mainwindow.scene_list.clear()
        self.attribute_widgets = list()
        self.logic_widgets = list()
        self.pipes = list()
        self.containers = list()

        # use time
        current_day = time.strftime("%Y/%m/%d", time.localtime(time.time()))
        last_day = time.strftime("%Y/%m/%d", time.localtime(data['use time']))
        if current_day == last_day:
            self.start_time = data['use time']
            self.last_time = data['last time']
        else:
            self.start_time = None
            self.last_time = 0
        day_time = self.last_time
        day_time_hour = int(day_time // 60 // 60)
        day_time_min = int((day_time // 60) - 60 * day_time_hour)
        day_time_sec = int(day_time - 60 * day_time_min - 60 * 60 * day_time_hour)

        # image path
        if data['image path']:
            effect_snow.SnowWidget.image_path = data['image path']
            self.image_path = data['image path']

        # set root scene
        if self.root_flag:
            self.root_scene_flag = TreeWidgetItem(
                self.mainwindow.scene_list,
                ("Root Scene",))
            self.root_scene_flag.setData(0, QtCore.Qt.ToolTipRole, self.root_scene)
            self.root_scene_flag.setExpanded(True)
        self.current_scene = self.root_scene
        self.current_scene_flag = self.root_scene_flag
        self.background_image = self.current_scene.background_image
        self.cutline = self.current_scene.cutline
        self.setScene(self.current_scene)

        # style
        #   attribute widget
        attribute.InputTextField.font = QtGui.QFont()
        attribute.InputTextField.font.setFamily(data['attribute font family'])
        attribute.InputTextField.font.setPointSize(data['attribute font size'])
        attribute.InputTextField.font_color.setRgba(data['attribute font color'])

        attribute.AttributeWidget.color.setRgba(data['attribute color'])
        attribute.AttributeWidget.selected_color.setRgba(data['attribute selected color'])
        attribute.AttributeWidget.border_color.setRgba(data['attribute border color'])
        attribute.AttributeWidget.selected_border_color.setRgba(data['attribute selected border color'])

        #   logic widget
        attribute.LogicWidget.background_color.setRgba(data['logic color'])
        attribute.LogicWidget.selected_background_color.setRgba(data['logic selected color'])
        attribute.LogicWidget.border_color.setRgba(data['logic border color'])
        attribute.LogicWidget.selected_border_color.setRgba(data['logic selected border color'])

        #   pipe widget
        pipe.Pipe.width = data['pipe width']
        pipe.Pipe.color.setRgba(data['pipe color'])
        pipe.Pipe.selected_color.setRgba(data['pipe selected color'])

        #   port widget
        port.Port.width = data['port width']
        port.Port.color.setRgba(data['port color'])
        port.Port.border_color.setRgba(data['port border color'])
        port.Port.hovered_color.setRgba(data['port hovered color'])
        port.Port.hovered_border_color.setRgba(data['port hovered border color'])
        port.Port.activated_color.setRgba(data['port activated color'])
        port.Port.activated_border_color.setRgba(data['port activated border color'])

        #   container widget
        container.Container.width = data['container width']
        container.Container.color.setRgba(data['container color'])
        container.Container.selected_color.setRgba(data['container selected color'])

        self.mainwindow.style_switch_combox.setCurrentIndex(1)
        self.mainwindow.style_switch_combox.setCurrentIndex(0)

        # create contents
        hashmap = {}
        self.root_scene.deserialize(data['root scene'], hashmap, view, flag=True)
        self.root_scene.deserialize(data['root scene'], hashmap, view, flag=False)

        # recover current scene
        if self.root_flag:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole).id == data['current scene']:
                    self.current_scene = scene_flag.data(0, QtCore.Qt.ToolTipRole)
                    self.current_scene_flag = scene_flag
                    self.background_image = self.current_scene.background_image
                    self.cutline = self.current_scene.cutline
                    self.setScene(self.current_scene)
                    break

        return True
