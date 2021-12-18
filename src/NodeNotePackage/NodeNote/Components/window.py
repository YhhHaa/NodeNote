import math
import time
import os

from PyQt5 import QtWidgets, QtCore, QtGui
from ..Components.effect_snow import EffectSkyWidget
from ..Components import attribute, pipe, port, draw, todo
from ..Model import stylesheet
from ..GraphicsView.view import View

__all__ = ["NoteWindow"]


class NoteWindow(QtWidgets.QMainWindow):
    """
    Main window of the application:
        - Sidebar.
        - View manager.

    """

    def __init__(self, argv, app=None):
        """
        Create sidebar and view manager.
        Args:
            argv: The command parameter file path.
            app: The Qt event loop application.
        """

        super(NoteWindow, self).__init__()
        self.argv = argv
        self.app = app
        self.app._window = self

        #   Window Init
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                    '../Resources/cloudy.png'))))  # set icon
        self.setWindowTitle("My Beautiful life")  # set title
        self.resize(1200, 1000)  # set size
        self.move(  # set geometry
            (QtWidgets.QDesktopWidget().screenGeometry().width() - self.geometry().width()) // 2,
            (QtWidgets.QDesktopWidget().screenGeometry().height() - self.geometry().height()) // 2
        )

        # Tool bar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setStyleSheet(stylesheet.STYLE_QTOOLBAR)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self.tab_widget = QtWidgets.QTabWidget()
        self.toolbar.addWidget(self.tab_widget)
        self.toolbar.setVisible(False)

        # Scene list widget
        self.scene_thumbnails = QtWidgets.QWidget()
        self.scene_thumbnails_layout = QtWidgets.QVBoxLayout()
        self.scene_thumbnails_layout.setSpacing(0)
        self.scene_thumbnails.setLayout(self.scene_thumbnails_layout)

        self.scene_list_bottom = QtWidgets.QWidget(self.scene_thumbnails)
        self.scene_list_bottom_layout = QtWidgets.QVBoxLayout()
        self.scene_list_bottom.setLayout(self.scene_list_bottom_layout)
        self.scene_thumbnails_layout.addWidget(self.scene_list_bottom)

        self.scene_list_scroll = QtWidgets.QScrollArea(self.scene_list_bottom)
        self.scene_list_scroll.setWidgetResizable(True)
        self.scene_list_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scene_list_bottom_layout.addWidget(self.scene_list_scroll)

        self.scene_list = QtWidgets.QTreeWidget()
        self.scene_list.setSortingEnabled(True)
        self.scene_list.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.scene_list.setStyleSheet(stylesheet.STYLE_QTREEWIDGET)
        self.scene_list.setAlternatingRowColors(True)
        self.scene_list.setHeaderLabel("Scene List")
        self.scene_list.setIndentation(8)
        self.scene_list_scroll.setWidget(self.scene_list)
        self.tab_widget.addTab(self.scene_thumbnails, "Scene")

        # Style list widget
        self.style_list_bottom = QtWidgets.QWidget()
        self.style_list_bottom_layout = QtWidgets.QVBoxLayout()
        self.style_list_bottom.setLayout(self.style_list_bottom_layout)

        self.style_list_scroll = QtWidgets.QScrollArea(self.style_list_bottom)
        self.style_list_scroll.setWidgetResizable(True)
        self.style_list_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.style_list_bottom_layout.addWidget(self.style_list_scroll)

        self.style_list = QtWidgets.QWidget()
        self.style_list_layout = QtWidgets.QGridLayout()
        self.style_list_scroll.setWidget(self.style_list)
        self.style_list.setLayout(self.style_list_layout)

        self.tab_widget.addTab(self.style_list_bottom, "Style")
        #   Switch widget
        self.style_switch_combox = QtWidgets.QComboBox()
        self.style_switch_combox.addItems(("All Scene", "Current Scene", "Selected Items"))
        self.style_switch_combox.setStyleSheet(stylesheet.STYLE_QCOMBOBOX)
        self.style_list_layout.addWidget(self.style_switch_combox, 0, 0, 1, -1)
        self.style_switch_combox.setStyleSheet(stylesheet.STYLE_QCOMBOBOX)
        #   Attribute widgets
        #       Color and font
        self.attribute_style_font = None
        self.attribute_style_font_color = None
        self.attribute_style_background_color = None
        self.attribute_style_selected_background_color = None
        self.attribute_style_border_color = None
        self.attribute_style_selected_border_color = None
        #       Label Widgets
        #           init
        self.attribute_style_label = QtWidgets.QLabel("Attribute Widgets")
        self.attribute_style_font_label = QtWidgets.QLabel("Font")
        self.attribute_style_font_color_label = QtWidgets.QLabel("Font Color")
        self.attribute_style_background_color_label = QtWidgets.QLabel("Background Color")
        self.attribute_style_selected_background_color_label = QtWidgets.QLabel("Selected Background Color")
        self.attribute_style_border_color_label = QtWidgets.QLabel("Border Color")
        self.attribute_style_selected_border_color_label = QtWidgets.QLabel("Selected Border Color")
        #           added
        self.style_list_layout.addWidget(self.attribute_style_label, 1, 0, 1, -1)
        self.style_list_layout.addWidget(self.attribute_style_font_label, 2, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_font_color_label, 3, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_background_color_label, 4, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_background_color_label, 5, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_border_color_label, 6, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_border_color_label, 7, 1, 1, 1)
        #           stylesheet
        self.attribute_style_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.attribute_style_font_label.setStyleSheet(stylesheet.STYLE_QLABEL_COMMON)
        self.attribute_style_font_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.attribute_style_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.attribute_style_selected_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.attribute_style_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.attribute_style_selected_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        #       Pushbutton Widgets
        #           init
        self.attribute_style_font_button = QtWidgets.QPushButton("Change Font")
        self.attribute_style_font_color_button = QtWidgets.QPushButton("Change Font Color")
        self.attribute_style_background_color_button = QtWidgets.QPushButton("Change Background Color")
        self.attribute_style_selected_background_color_button = QtWidgets.QPushButton(
            "Change Selected Background Color")
        self.attribute_style_border_color_button = QtWidgets.QPushButton("Change Border Color")
        self.attribute_style_selected_border_color_button = QtWidgets.QPushButton("Change Selected Border Color")
        #           added
        self.style_list_layout.addWidget(self.attribute_style_font_button, 2, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_font_color_button, 3, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_background_color_button, 4, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_background_color_button, 5, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_border_color_button, 6, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_border_color_button, 7, 0, 1, 1)
        #           stylesheet
        self.attribute_style_font_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.attribute_style_font_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.attribute_style_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.attribute_style_selected_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.attribute_style_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.attribute_style_selected_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)

        #   Logic widgets
        #       Color
        self.logic_style_background_color = None
        self.logic_style_selected_background_color = None
        self.logic_style_border_color = None
        self.logic_style_selected_border_color = None
        #       label widgets
        #           init
        self.logic_style_label = QtWidgets.QLabel("Logic Widgets")
        self.logic_style_background_color_label = QtWidgets.QLabel("Background Color")
        self.logic_style_selected_background_color_label = QtWidgets.QLabel("Selected Background Color")
        self.logic_style_border_color_label = QtWidgets.QLabel("Border Color")
        self.logic_style_selected_border_color_label = QtWidgets.QLabel("Selected Border Color")
        #           added
        self.style_list_layout.addWidget(self.logic_style_label, 8, 0, 1, -1)
        self.style_list_layout.addWidget(self.logic_style_background_color_label, 9, 1)
        self.style_list_layout.addWidget(self.logic_style_selected_background_color_label, 10, 1)
        self.style_list_layout.addWidget(self.logic_style_border_color_label, 11, 1)
        self.style_list_layout.addWidget(self.logic_style_selected_border_color_label, 12, 1)
        #           stylesheet
        self.logic_style_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.logic_style_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.logic_style_selected_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.logic_style_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.logic_style_selected_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        #       button widgets
        #           init
        self.logic_style_background_color_button = QtWidgets.QPushButton("Change Background Color")
        self.logic_style_selected_background_color_button = QtWidgets.QPushButton("Change Selected Background Color")
        self.logic_style_border_color_button = QtWidgets.QPushButton("Change Border Color")
        self.logic_style_selected_border_color_button = QtWidgets.QPushButton("Change Selected Border Color")
        #           added
        self.style_list_layout.addWidget(self.logic_style_background_color_button, 9, 0)
        self.style_list_layout.addWidget(self.logic_style_selected_background_color_button, 10, 0)
        self.style_list_layout.addWidget(self.logic_style_border_color_button, 11, 0)
        self.style_list_layout.addWidget(self.logic_style_selected_border_color_button, 12, 0)
        #           stylesheet
        self.logic_style_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.logic_style_selected_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.logic_style_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.logic_style_selected_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)

        #   Pipe widgets
        #       Color and width
        self.pipe_style_width = None
        self.pipe_style_background_color = None
        self.pipe_style_selected_background_color = None
        #       Label widgets
        #           init
        self.pipe_style_label = QtWidgets.QLabel("Pipe Widgets")
        self.pipe_style_width_label = QtWidgets.QLabel("Width")
        self.pipe_style_background_color_label = QtWidgets.QLabel("Background Color")
        self.pipe_style_selected_background_color_label = QtWidgets.QLabel("Selected Background Color")
        #           added
        self.style_list_layout.addWidget(self.pipe_style_label, 13, 0, 1, -1)
        self.style_list_layout.addWidget(self.pipe_style_width_label, 14, 1)
        self.style_list_layout.addWidget(self.pipe_style_background_color_label, 15, 1)
        self.style_list_layout.addWidget(self.pipe_style_selected_background_color_label, 16, 1)
        #           stylesheet
        self.pipe_style_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.pipe_style_width_label.setStyleSheet(stylesheet.STYLE_QLABEL_COMMON)
        self.pipe_style_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.pipe_style_selected_background_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        #       Pushbutton widgets
        #           init
        self.pipe_style_width_button = QtWidgets.QPushButton("Change Width")
        self.pipe_style_background_color_button = QtWidgets.QPushButton("Change Background Color")
        self.pipe_style_selected_background_color_button = QtWidgets.QPushButton("Change Selected Background Color")
        #           added
        self.style_list_layout.addWidget(self.pipe_style_width_button, 14, 0)
        self.style_list_layout.addWidget(self.pipe_style_background_color_button, 15, 0)
        self.style_list_layout.addWidget(self.pipe_style_selected_background_color_button, 16, 0)
        #           stylesheet
        self.pipe_style_width_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.pipe_style_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.pipe_style_selected_background_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)

        #   Port Widgets
        #       Width and Color
        self.port_style_width = None
        self.port_style_color = None
        self.port_style_border_color = None
        self.port_style_hovered_color = None
        self.port_style_hovered_border_color = None
        self.port_style_activated_color = None
        self.port_style_activated_border_color = None
        #       Label widgets
        #           init
        self.port_style_label = QtWidgets.QLabel("Port Widgets")
        self.port_style_width_label = QtWidgets.QLabel("Width")
        self.port_style_color_label = QtWidgets.QLabel("Background Color")
        self.port_style_border_color_label = QtWidgets.QLabel("Border Color")
        self.port_style_hovered_color_label = QtWidgets.QLabel("Hovered Background Color")
        self.port_style_hovered_border_color_label = QtWidgets.QLabel("Hovered Border Color")
        self.port_style_activated_color_label = QtWidgets.QLabel("Activated Background Color")
        self.port_style_activated_border_color_label = QtWidgets.QLabel("Activated Border Color")
        #           added
        self.style_list_layout.addWidget(self.port_style_label, 17, 0, 1, -1)
        self.style_list_layout.addWidget(self.port_style_width_label, 18, 1)
        self.style_list_layout.addWidget(self.port_style_color_label, 19, 1)
        self.style_list_layout.addWidget(self.port_style_border_color_label, 20, 1)
        self.style_list_layout.addWidget(self.port_style_hovered_color_label, 21, 1)
        self.style_list_layout.addWidget(self.port_style_hovered_border_color_label, 22, 1)
        self.style_list_layout.addWidget(self.port_style_activated_color_label, 23, 1)
        self.style_list_layout.addWidget(self.port_style_activated_border_color_label, 24, 1)
        #           stylesheet
        self.port_style_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.port_style_width_label.setStyleSheet(stylesheet.STYLE_QLABEL_COMMON)
        self.port_style_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.port_style_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.port_style_hovered_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.port_style_hovered_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.port_style_activated_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        self.port_style_activated_border_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        #       Pushbutton widgets
        #           init
        self.port_style_width_button = QtWidgets.QPushButton("Change Width")
        self.port_style_color_button = QtWidgets.QPushButton("Change Background Color")
        self.port_style_border_color_button = QtWidgets.QPushButton("Change Border Color")
        self.port_style_hovered_color_button = QtWidgets.QPushButton("Change Hovered Background Color")
        self.port_style_hovered_border_color_button = QtWidgets.QPushButton("Change Hovered Border Color")
        self.port_style_activated_color_button = QtWidgets.QPushButton("Change Activated Background Color")
        self.port_style_activated_border_color_button = QtWidgets.QPushButton("Change Activated Border Color")
        #           added
        self.style_list_layout.addWidget(self.port_style_width_button, 18, 0)
        self.style_list_layout.addWidget(self.port_style_color_button, 19, 0)
        self.style_list_layout.addWidget(self.port_style_border_color_button, 20, 0)
        self.style_list_layout.addWidget(self.port_style_hovered_color_button, 21, 0)
        self.style_list_layout.addWidget(self.port_style_hovered_border_color_button, 22, 0)
        self.style_list_layout.addWidget(self.port_style_activated_color_button, 23, 0)
        self.style_list_layout.addWidget(self.port_style_activated_border_color_button, 24, 0)
        #           stylesheet
        self.port_style_width_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_hovered_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_hovered_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_activated_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.port_style_activated_border_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)

        #   Container widgets
        #       Label widgets
        #           init
        self.draw_style_label = QtWidgets.QLabel("Draw Widgets")
        self.draw_style_width_label = QtWidgets.QLabel("Width")
        self.draw_style_color_label = QtWidgets.QLabel("Color")
        #           added
        self.style_list_layout.addWidget(self.draw_style_label, 25, 0, 1, -1)
        self.style_list_layout.addWidget(self.draw_style_width_label, 26, 1)
        self.style_list_layout.addWidget(self.draw_style_color_label, 27, 1)
        #           stylesheet
        self.draw_style_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.draw_style_width_label.setStyleSheet(stylesheet.STYLE_QLABEL_COMMON)
        self.draw_style_color_label.setStyleSheet(stylesheet.STYLE_QLABEL_CHANGED)
        #       Pushbutton widgets
        #           init
        self.draw_style_width_button = QtWidgets.QPushButton("Change Width")
        self.draw_style_color_button = QtWidgets.QPushButton("Change Color")
        #           added
        self.style_list_layout.addWidget(self.draw_style_width_button, 26, 0)
        self.style_list_layout.addWidget(self.draw_style_color_button, 27, 0)
        #           stylesheet
        self.draw_style_width_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.draw_style_color_button.setStyleSheet(stylesheet.STYLE_QPUSHBUTTON)
        self.draw_init_flag = True

        # Text editor
        #       widgets
        self.text_editor_label = QtWidgets.QLabel("Text Editor(All scene)")
        self.text_editor_length_label = QtWidgets.QLabel("Set Fixed Width Or Not")
        self.text_editor_length_box = QtWidgets.QDoubleSpinBox()
        self.text_editor_length_box.setRange(-1, math.inf)
        self.text_editor_length_box.setSingleStep(100)
        self.text_editor_length_box.setValue(-1)
        #       added
        self.style_list_layout.addWidget(self.text_editor_label, 28, 0, 1, -1)
        self.style_list_layout.addWidget(self.text_editor_length_box, 29, 0)
        self.style_list_layout.addWidget(self.text_editor_length_label, 29, 1)
        #       stylesheet
        self.text_editor_label.setStyleSheet(stylesheet.STYLE_QLABEL_TITLE)
        self.text_editor_length_label.setStyleSheet(stylesheet.STYLE_QLABEL_COMMON)
        self.text_editor_length_box.setStyleSheet(stylesheet.STYLE_QDOUBLESPINBOX)
        #       slot
        self.text_editor_length_box.valueChanged.connect(self.text_width_changed)

        #   Slots Controller
        self.style_switch_combox.currentIndexChanged.connect(self.init_style)
        self.init_style(current_index=self.style_switch_combox.currentIndex())

        # Widget Init
        self.central_widget = QtWidgets.QWidget()  # central widget
        self.view_widget = View(self, self.central_widget)  # view widget
        self.scene_list.itemClicked.connect(self.view_widget.change_current_scene)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)  # layout contains two widgets
        self.sky_widget = EffectSkyWidget(self.view_widget, self.central_widget)  # snow falling widget
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view_widget)
        self.central_widget.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setCentralWidget(self.central_widget)

        # time clock
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.time_update)
        self.timer.start(180000)

        # thumbnails
        self.thumbnails = QtWidgets.QLabel()
        self.thumbnails.setMinimumSize(self.style_list.sizeHint().width(), 200)
        self.thumbnails.setMaximumSize(self.style_list.sizeHint().width(), 200)
        self.thumbnails.setStyleSheet("border:1px solid red")
        self.scene_thumbnails_layout.addWidget(self.thumbnails)
        self.time_id = 0

    def time_update(self):
        """
        Auto save file.

        """

        if self.view_widget.filename:
            self.view_widget.save_to_file()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        if self.view_widget.filename:
            todo.Todo.close_flag = True
            self.view_widget.save_to_file()

    @staticmethod
    def color_label_changed(label, color):
        """
        Change the colorful label.

        Args:
            label: QLabel.
            color: QColor.

        """
        if color:
            color_style = '''
             QLabel {
                 background-color: #%s;
                 border-style: outset;
                 border-width: 1px;
                 border-radius: 10px;
                 border-color: beige;
                 font: bold 8px;
                 padding: 6px;
             }
             ''' % str(hex(color.rgba()))[2:]
            label.setStyleSheet(color_style)

    @staticmethod
    def font_label_changed(label: QtWidgets.QLabel, font: QtGui.QFont):
        """
        Change the font info in label.

        Args:
            label: The label need to be changed.
            font: The up to date font.

        """

        label.setText("Font: %s %d" % (font.family(), font.pointSize()))

    @staticmethod
    def width_label_changed(label: QtWidgets.QLabel, width):
        """
        Change the width info in label.

        Args:
            label: The label need to be changed.
            width: The up to date width.

        """

        label.setText("Width: %s" % str(width))

    def color_changed(self, widget_type, current_index):
        """
        Change the color of the widgets of all or of scene or of selected items.

        Args:
            widget_type: Different widget type.
            current_index: The current drop-down box index on the top of the style list.

        """

        if widget_type == "Attribute_font_color":
            font_color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                         QtWidgets.QColorDialog.ShowAlphaChannel)
            if font_color:
                if current_index == 0:
                    for item in self.view_widget.attribute_widgets:
                        if not item.scene().attribute_style_font_color and \
                                not item.attribute_widget.label_item.font_color_flag:
                            attribute.InputTextField.font_color = font_color
                            item.attribute_widget.label_item.setDefaultTextColor(font_color)
                            item.update()
                    self.color_label_changed(self.attribute_style_font_color_label, attribute.InputTextField.font_color)

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_font_color = font_color
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget) \
                                and not item.attribute_widget.label_item.font_color_flag:
                            item.attribute_widget.label_item.setDefaultTextColor(font_color)
                            item.update()
                    self.color_label_changed(self.attribute_style_font_color_label,
                                             self.view_widget.current_scene.attribute_style_font_color)

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.attribute_widget.label_item.font_color = font_color
                            item.attribute_widget.label_item.setDefaultTextColor(font_color)
                            item.attribute_widget.label_item.font_color_flag = True
                            item.update()
                            self.color_label_changed(self.attribute_style_font_color_label,
                                                     font_color)

        elif widget_type == "Attribute_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.AttributeWidget.color = color
                    self.color_label_changed(self.attribute_style_background_color_label,
                                             attribute.AttributeWidget.color)
                    for item in self.view_widget.attribute_widgets:
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_background_color = color
                    self.color_label_changed(self.attribute_style_background_color_label,
                                             self.view_widget.current_scene.attribute_style_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.color = color
                            item.color_flag = True
                            self.color_label_changed(self.attribute_style_background_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Attribute_selected_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.AttributeWidget.selected_color = color
                    self.color_label_changed(self.attribute_style_selected_background_color_label,
                                             attribute.AttributeWidget.selected_color)
                    for item in self.view_widget.attribute_widgets:
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_selected_background_color = color
                    self.color_label_changed(self.attribute_style_selected_background_color_label,
                                             self.view_widget.current_scene.attribute_style_selected_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.selected_color = color
                            item.selected_color_flag = True
                            self.color_label_changed(self.attribute_style_selected_background_color_label,
                                                     color)
                            item.update()


        elif widget_type == "Attribute_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.AttributeWidget.border_color = color
                    self.color_label_changed(self.attribute_style_border_color_label,
                                             attribute.AttributeWidget.border_color)
                    for item in self.view_widget.attribute_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_border_color = color
                    self.color_label_changed(self.attribute_style_border_color_label,
                                             self.view_widget.current_scene.attribute_style_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.border_color = color
                            item.border_flag = True
                            self.color_label_changed(self.attribute_style_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Attribute_selected_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.AttributeWidget.selected_border_color = color
                    self.color_label_changed(self.attribute_style_selected_border_color_label,
                                             attribute.AttributeWidget.selected_border_color)
                    for item in self.view_widget.attribute_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_selected_border_color = color
                    self.color_label_changed(self.attribute_style_selected_border_color_label,
                                             self.view_widget.current_scene.attribute_style_selected_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.selected_border_color = color
                            item.selected_border_flag = True
                            self.color_label_changed(self.attribute_style_selected_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Logic_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.LogicWidget.background_color = color
                    self.color_label_changed(self.logic_style_background_color_label,
                                             attribute.LogicWidget.background_color)
                    for item in self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.logic_style_background_color = color
                    self.color_label_changed(self.logic_style_background_color_label,
                                             self.view_widget.current_scene.logic_style_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.LogicWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.LogicWidget):
                            item.background_color = color
                            item.background_color_flag = True
                            self.color_label_changed(self.logic_style_background_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Logic_selected_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.LogicWidget.selected_background_color = color
                    self.color_label_changed(self.logic_style_selected_background_color_label,
                                             attribute.LogicWidget.selected_background_color)
                    for item in self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.logic_style_selected_background_color = color
                    self.color_label_changed(self.logic_style_selected_background_color_label,
                                             self.view_widget.current_scene.logic_style_selected_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.LogicWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.LogicWidget):
                            item.selected_background_color = color
                            item.selected_background_color_flag = True
                            self.color_label_changed(self.logic_style_selected_background_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Logic_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.LogicWidget.border_color = color
                    self.color_label_changed(self.logic_style_border_color_label, attribute.LogicWidget.border_color)
                    for item in self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.logic_style_border_color = color
                    self.color_label_changed(self.logic_style_border_color_label,
                                             self.view_widget.current_scene.logic_style_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.LogicWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.LogicWidget):
                            item.border_color = color
                            item.border_color_flag = True
                            self.color_label_changed(self.logic_style_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Logic_selected_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    attribute.LogicWidget.selected_border_color = color
                    self.color_label_changed(self.logic_style_selected_border_color_label,
                                             attribute.LogicWidget.selected_border_color)
                    for item in self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.logic_style_selected_border_color = color
                    self.color_label_changed(self.logic_style_selected_border_color_label,
                                             self.view_widget.current_scene.logic_style_selected_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.LogicWidget):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.LogicWidget):
                            item.selected_border_color = color
                            item.selected_border_color_flag = True
                            self.color_label_changed(self.logic_style_selected_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Pipe_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    pipe.Pipe.color = color
                    self.color_label_changed(self.pipe_style_background_color_label, pipe.Pipe.color)
                    for item in self.view_widget.pipes: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.pipe_style_background_color = color
                    self.color_label_changed(self.pipe_style_background_color_label,
                                             self.view_widget.current_scene.pipe_style_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, pipe.Pipe):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, pipe.Pipe):
                            item.color = color
                            item.color_flag = True
                            self.color_label_changed(self.pipe_style_background_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Pipe_selected_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    pipe.Pipe.selected_color = color
                    self.color_label_changed(self.pipe_style_selected_background_color_label, pipe.Pipe.selected_color)
                    for item in self.view_widget.pipes: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.pipe_style_selected_background_color = color
                    self.color_label_changed(self.pipe_style_selected_background_color_label,
                                             self.view_widget.current_scene.pipe_style_selected_background_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, pipe.Pipe):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, pipe.Pipe):
                            item.selected_color = color
                            item.selected_color_flag = True
                            self.color_label_changed(self.pipe_style_selected_background_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.color = color
                    self.color_label_changed(self.port_style_color_label, port.Port.color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_color = color
                    self.color_label_changed(self.port_style_color_label,
                                             self.view_widget.current_scene.port_style_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.color = color
                            item.color_flag = True
                            self.color_label_changed(self.port_style_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.border_color = color
                    self.color_label_changed(self.port_style_border_color_label, port.Port.border_color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_border_color = color
                    self.color_label_changed(self.port_style_border_color_label,
                                             self.view_widget.current_scene.port_style_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.border_color = color
                            item.border_color_flag = True
                            self.color_label_changed(self.port_style_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_hovered_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.hovered_color = color
                    self.color_label_changed(self.port_style_hovered_color_label, port.Port.hovered_color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_hovered_color = color
                    self.color_label_changed(self.port_style_hovered_color_label,
                                             self.view_widget.current_scene.port_style_hovered_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.hovered_color = color
                            item.hovered_color_flag = True
                            self.color_label_changed(self.port_style_hovered_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_hovered_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.hovered_border_color = color
                    self.color_label_changed(self.port_style_hovered_border_color_label, port.Port.hovered_border_color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_hovered_border_color = color
                    self.color_label_changed(self.port_style_hovered_border_color_label,
                                             self.view_widget.current_scene.port_style_hovered_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.hovered_border_color = color
                            item.hovered_border_color_flag = True
                            self.color_label_changed(self.port_style_hovered_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_activated_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.activated_color = color
                    self.color_label_changed(self.port_style_activated_color_label, port.Port.activated_color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_activated_color = color
                    self.color_label_changed(self.port_style_activated_color_label,
                                             self.view_widget.current_scene.port_style_activated_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.activated_color = color
                            item.activated_color_flag = True
                            self.color_label_changed(self.port_style_activated_color_label,
                                                     color)
                            item.update()

        elif widget_type == "Port_activated_border_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    port.Port.activated_border_color = color
                    self.color_label_changed(self.port_style_activated_border_color_label,
                                             port.Port.activated_border_color)
                    for item in self.view_widget.attribute_widgets + self.view_widget.logic_widgets: 
                        item.update()

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_activated_border_color = color
                    self.color_label_changed(self.port_style_activated_border_color_label,
                                             self.view_widget.current_scene.port_style_activated_border_color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, (attribute.AttributeWidget, attribute.LogicWidget)):
                            item.update()

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.activated_border_color = color
                            item.activated_border_color_flag = True
                            self.color_label_changed(self.port_style_activated_border_color_label,
                                                     color)
                            item.update()

        elif widget_type == "draw_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color")
            if color:
                draw.Draw.color = color
                self.color_label_changed(self.draw_style_color_label, color)

    def font_changed(self, widget_type, current_index):
        """
        Change the font of widgets of all or current scene or selected items.

        Args:
            widget_type: Different widget type.
            current_index: The current drop-down box index on the top of the style list.

        Returns:

        """
        if widget_type == "Attribute":
            font_type, ok = QtWidgets.QFontDialog.getFont()
            if font_type and ok:
                if current_index == 0:
                    for item in self.view_widget.attribute_widgets:
                        attribute.InputTextField.font = font_type
                        if not item.scene().attribute_style_font and not item.attribute_widget.label_item.font_flag:
                            item.attribute_widget.label_item.document().setDefaultFont(font_type)
                            item.text_change_node_shape()
                    self.font_label_changed(self.attribute_style_font_label, attribute.InputTextField.font)

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_font = font_type
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget) \
                                and not item.attribute_widget.label_item.font_flag:
                            item.attribute_widget.label_item.document().setDefaultFont(font_type)
                            item.text_change_node_shape()
                            item.resize(20, 10)
                    self.font_label_changed(self.attribute_style_font_label,
                                            self.view_widget.current_scene.attribute_style_font)

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.attribute_widget.label_item.document().setDefaultFont(font_type)
                            item.text_change_node_shape()
                            item.attribute_widget.label_item.font_flag = True
                            self.font_label_changed(self.attribute_style_font_label,
                                                    font_type)

    def width_changed(self, widget_type, current_index):
        """
        Change the width of the widgets of all or current scene or selected items.

        Args:
            widget_type: Different widget type.
            current_index: The current drop-down box index on the top of the style list.

        """

        if widget_type == "Pipe_width":
            width, ok = QtWidgets.QInputDialog.getDouble(self, "Get Double Width",
                                                         "Width", 2, 0.1, 15.0, 2, QtCore.Qt.WindowFlags(), 0.5)
            if width and ok:
                if current_index == 0:
                    pipe.Pipe.width = width
                    self.width_label_changed(self.pipe_style_width_label, pipe.Pipe.width)

                elif current_index == 1:
                    self.view_widget.current_scene.pipe_style_width = width
                    self.width_label_changed(self.pipe_style_width_label,
                                             self.view_widget.current_scene.pipe_style_width)

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, pipe.Pipe):
                            item.width = width
                            item.width_flag = True
                            self.width_label_changed(self.pipe_style_width_label, width)

        elif widget_type == "Port_width":
            width, ok = QtWidgets.QInputDialog.getDouble(self, "Get Double Width",
                                                         "Width", 22, 8, 40, 2, QtCore.Qt.WindowFlags(), 2)
            if width and ok:
                if current_index == 0:
                    port.Port.width = width
                    self.width_label_changed(self.port_style_width_label, port.Port.width)

                elif current_index == 1:
                    self.view_widget.current_scene.port_style_width = width
                    self.width_label_changed(self.port_style_width_label,
                                             self.view_widget.current_scene.port_style_width)

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, port.Port):
                            item.width = width
                            item.width_flag = True
                            self.width_label_changed(self.port_style_width_label, width)

                for item in self.view_widget.current_scene.items():
                    if isinstance(item, port.Port):
                        item.setMaximumSize(width, width)
                        item.updateGeometry()
                        item.update()

        elif widget_type == "draw_width":
            width, ok = QtWidgets.QInputDialog.getDouble(self, "Get Double Width",
                                                         "Width", 10.0, 0.1, 50.0, 2, QtCore.Qt.WindowFlags(), 0.2)
            if width and ok:
                draw.Draw.pen_width = width
                self.width_label_changed(self.draw_style_width_label, width)

    def init_attribute(self, current_index):
        """
        Init the attribute style label.

        Args:
            current_index: The current drop-down box index on the top of the style list.

        """

        if current_index == 0:
            #   change current parameters
            #       font
            self.font_label_changed(self.attribute_style_font_label, attribute.InputTextField.font)
            #       color
            self.color_label_changed(self.attribute_style_font_color_label, attribute.InputTextField.font_color)
            self.color_label_changed(self.attribute_style_background_color_label, attribute.AttributeWidget.color)
            self.color_label_changed(self.attribute_style_selected_background_color_label,
                                     attribute.AttributeWidget.selected_color)
            self.color_label_changed(self.attribute_style_border_color_label, attribute.AttributeWidget.border_color)
            self.color_label_changed(self.attribute_style_selected_border_color_label,
                                     attribute.AttributeWidget.selected_border_color)
            #   change slots
            #       font
            self.attribute_style_font_button.disconnect()
            self.attribute_style_font_button.clicked.connect(
                lambda x: self.font_changed("Attribute", current_index))

            #       color
            self.attribute_style_font_color_button.disconnect()
            self.attribute_style_font_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_font_color", current_index))

            self.attribute_style_background_color_button.disconnect()
            self.attribute_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_color", current_index))

            self.attribute_style_selected_background_color_button.disconnect()
            self.attribute_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_color", current_index))

            self.attribute_style_border_color_button.disconnect()
            self.attribute_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_border_color", current_index))

            self.attribute_style_selected_border_color_button.disconnect()
            self.attribute_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_border_color", current_index))

        elif current_index == 1:
            #   change current parameters
            #       font
            if self.view_widget.current_scene.attribute_style_font:
                self.font_label_changed(self.attribute_style_font_label,
                                        self.view_widget.current_scene.attribute_style_font)
            else:
                self.font_label_changed(self.attribute_style_font_label, attribute.InputTextField.font)
            #       color
            if self.view_widget.current_scene.attribute_style_font_color:
                self.color_label_changed(self.attribute_style_font_color_label,
                                         self.view_widget.current_scene.attribute_style_font_color)
            else:
                self.color_label_changed(self.attribute_style_font_color_label, attribute.InputTextField.font_color)
            if self.view_widget.current_scene.attribute_style_background_color:
                self.color_label_changed(self.attribute_style_background_color_label,
                                         self.view_widget.current_scene.attribute_style_background_color)
            else:
                self.color_label_changed(self.attribute_style_background_color_label, attribute.AttributeWidget.color)
            if self.view_widget.current_scene.attribute_style_selected_background_color:
                self.color_label_changed(self.attribute_style_selected_background_color_label,
                                         self.view_widget.current_scene.attribute_style_selected_background_color)
            else:
                self.color_label_changed(self.attribute_style_selected_background_color_label,
                                         attribute.AttributeWidget.selected_color)
            if self.view_widget.current_scene.attribute_style_border_color:
                self.color_label_changed(self.attribute_style_border_color_label,
                                         self.view_widget.current_scene.attribute_style_border_color)
            else:
                self.color_label_changed(self.attribute_style_border_color_label,
                                         attribute.AttributeWidget.border_color)
            if self.view_widget.current_scene.attribute_style_selected_border_color:
                self.color_label_changed(self.attribute_style_selected_border_color_label,
                                         self.view_widget.current_scene.attribute_style_selected_border_color)
            else:
                self.color_label_changed(self.attribute_style_selected_border_color_label,
                                         attribute.AttributeWidget.selected_border_color)
            #   change slots
            #       font
            self.attribute_style_font_button.disconnect()
            self.attribute_style_font_button.clicked.connect(
                lambda x: self.font_changed("Attribute", current_index))
            #       color
            self.attribute_style_font_color_button.disconnect()
            self.attribute_style_font_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_font_color", current_index))
            self.attribute_style_background_color_button.disconnect()
            self.attribute_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_color", current_index))
            self.attribute_style_selected_background_color_button.disconnect()
            self.attribute_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_color", current_index))
            self.attribute_style_border_color_button.disconnect()
            self.attribute_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_border_color", current_index))
            self.attribute_style_selected_border_color_button.disconnect()
            self.attribute_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_border_color", current_index))

        elif current_index == 2:
            #   change slots
            #       font
            self.attribute_style_font_button.disconnect()
            self.attribute_style_font_button.clicked.connect(
                lambda x: self.font_changed("Attribute", current_index))
            #       color
            self.attribute_style_font_color_button.disconnect()
            self.attribute_style_font_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_font_color", current_index))
            self.attribute_style_background_color_button.disconnect()
            self.attribute_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_color", current_index))
            self.attribute_style_selected_background_color_button.disconnect()
            self.attribute_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_color", current_index))
            self.attribute_style_border_color_button.disconnect()
            self.attribute_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_border_color", current_index))
            self.attribute_style_selected_border_color_button.disconnect()
            self.attribute_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Attribute_selected_border_color", current_index))

    def init_logic(self, current_index):
        """
        Init the logic label style.

        Args:
            current_index: The current drop-down box index on the top of the style list.

        """
        if current_index == 0:
            #   change current parameters
            #       color
            self.color_label_changed(self.logic_style_background_color_label, attribute.LogicWidget.background_color)
            self.color_label_changed(self.logic_style_selected_background_color_label,
                                     attribute.LogicWidget.selected_background_color)
            self.color_label_changed(self.logic_style_border_color_label, attribute.LogicWidget.border_color)
            self.color_label_changed(self.logic_style_selected_border_color_label,
                                     attribute.LogicWidget.selected_border_color)
            #   change slots
            self.logic_style_background_color_button.disconnect()
            self.logic_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_color", current_index))

            self.logic_style_selected_background_color_button.disconnect()
            self.logic_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_color", current_index))

            self.logic_style_border_color_button.disconnect()
            self.logic_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_border_color", current_index))

            self.logic_style_selected_border_color_button.disconnect()
            self.logic_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_border_color", current_index))

        elif current_index == 1:
            #   change current parameters
            #       color
            if not self.view_widget.current_scene.logic_style_background_color:
                self.color_label_changed(self.logic_style_background_color_label,
                                         attribute.LogicWidget.background_color)
            else:
                self.color_label_changed(self.logic_style_background_color_label,
                                         self.view_widget.current_scene.logic_style_background_color)

            if not self.view_widget.current_scene.logic_style_selected_background_color:
                self.color_label_changed(self.logic_style_selected_background_color_label,
                                         attribute.LogicWidget.selected_background_color)
            else:
                self.color_label_changed(self.logic_style_selected_background_color_label,
                                         self.view_widget.current_scene.logic_style_selected_background_color)

            if not self.view_widget.current_scene.logic_style_border_color:
                self.color_label_changed(self.logic_style_border_color_label, attribute.LogicWidget.border_color)
            else:
                self.color_label_changed(self.logic_style_border_color_label,
                                         self.view_widget.current_scene.logic_style_selected_background_color)

            if not self.view_widget.current_scene.logic_style_selected_border_color:
                self.color_label_changed(self.logic_style_selected_border_color_label,
                                         attribute.LogicWidget.selected_border_color)
            else:
                self.color_label_changed(self.logic_style_selected_border_color_label,
                                         self.view_widget.current_scene.logic_style_selected_border_color)

            #   change slots
            self.logic_style_background_color_button.disconnect()
            self.logic_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_color", current_index))

            self.logic_style_selected_background_color_button.disconnect()
            self.logic_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_color", current_index))

            self.logic_style_border_color_button.disconnect()
            self.logic_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_border_color", current_index))

            self.logic_style_selected_border_color_button.disconnect()
            self.logic_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_border_color", current_index))

        elif current_index == 2:
            #   change slots
            self.logic_style_background_color_button.disconnect()
            self.logic_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_color", current_index))

            self.logic_style_selected_background_color_button.disconnect()
            self.logic_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_color", current_index))

            self.logic_style_border_color_button.disconnect()
            self.logic_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_border_color", current_index))

            self.logic_style_selected_border_color_button.disconnect()
            self.logic_style_selected_border_color_button.clicked.connect(
                lambda x: self.color_changed("Logic_selected_border_color", current_index))

    def init_pipe(self, current_index):
        """
        Init the pipe widget label style.

        Args:
            current_index: The current drop-down box index on the top of the style list.

        """

        if current_index == 0:
            #   change current parameters
            self.width_label_changed(self.pipe_style_width_label, pipe.Pipe.width)
            self.color_label_changed(self.pipe_style_background_color_label, pipe.Pipe.color)
            self.color_label_changed(self.pipe_style_selected_background_color_label, pipe.Pipe.selected_color)
            #   change slots
            #       width
            self.pipe_style_width_button.disconnect()
            self.pipe_style_width_button.clicked.connect(lambda x: self.width_changed("Pipe_width", current_index))
            #       color
            self.pipe_style_background_color_button.disconnect()
            self.pipe_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_color", current_index))

            self.pipe_style_selected_background_color_button.disconnect()
            self.pipe_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_selected_color", current_index))

        elif current_index == 1:
            #   change current parameters
            #       width
            if self.view_widget.current_scene.pipe_style_width:
                self.width_label_changed(self.pipe_style_width_label, self.view_widget.current_scene.pipe_style_width)
            else:
                self.width_label_changed(self.pipe_style_width_label, pipe.Pipe.width)
            #       color
            if self.view_widget.current_scene.pipe_style_background_color:
                self.color_label_changed(self.pipe_style_background_color_label,
                                         self.view_widget.current_scene.pipe_style_background_color)
            else:
                self.color_label_changed(self.pipe_style_background_color_label, pipe.Pipe.color)

            if self.view_widget.current_scene.pipe_style_selected_background_color:
                self.color_label_changed(self.pipe_style_background_color_label,
                                         self.view_widget.current_scene.pipe_style_selected_background_color)
            else:
                self.color_label_changed(self.pipe_style_selected_background_color_label, pipe.Pipe.selected_color)

            #   change slots
            #       width
            self.pipe_style_width_button.disconnect()
            self.pipe_style_width_button.clicked.connect(lambda x: self.width_changed("Pipe_width", current_index))
            #       color
            self.pipe_style_background_color_button.disconnect()
            self.pipe_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_color", current_index))

            self.pipe_style_selected_background_color_button.disconnect()
            self.pipe_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_selected_color", current_index))

        elif current_index == 2:
            #   change slots
            #       width
            self.pipe_style_width_button.disconnect()
            self.pipe_style_width_button.clicked.connect(lambda x: self.width_changed("Pipe_width", current_index))
            #       color
            self.pipe_style_background_color_button.disconnect()
            self.pipe_style_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_color", current_index))

            self.pipe_style_selected_background_color_button.disconnect()
            self.pipe_style_selected_background_color_button.clicked.connect(
                lambda x: self.color_changed("Pipe_selected_color", current_index))

    def init_port(self, current_index):
        """
        Init port widget label style.

        Args:
            current_index: The current drop-down box index on the top of the style list.

        """

        if current_index == 0:
            #   change current parameters
            #       width
            self.width_label_changed(self.port_style_width_label, port.Port.width)
            #       color
            self.color_label_changed(self.port_style_color_label, port.Port.color)
            self.color_label_changed(self.port_style_border_color_label, port.Port.border_color)
            self.color_label_changed(self.port_style_hovered_color_label, port.Port.hovered_color)
            self.color_label_changed(self.port_style_hovered_border_color_label, port.Port.hovered_border_color)
            self.color_label_changed(self.port_style_activated_color_label, port.Port.activated_color)
            self.color_label_changed(self.port_style_activated_border_color_label, port.Port.activated_border_color)
            #   change slots
            #       width
            self.port_style_width_button.disconnect()
            self.port_style_width_button.clicked.connect(lambda x: self.width_changed("Port_width", current_index))
            #       color
            self.port_style_color_button.disconnect()
            self.port_style_color_button.clicked.connect(
                lambda x: self.color_changed("Port_color", current_index))

            self.port_style_border_color_button.disconnect()
            self.port_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_border_color", current_index))

            self.port_style_hovered_color_button.disconnect()
            self.port_style_hovered_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_color", current_index))

            self.port_style_hovered_border_color_button.disconnect()
            self.port_style_hovered_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_border_color", current_index))

            self.port_style_activated_color_button.disconnect()
            self.port_style_activated_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_color", current_index))

            self.port_style_activated_border_color_button.disconnect()
            self.port_style_activated_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_border_color", current_index))

        elif current_index == 1:
            #   change current parameters
            #       width
            if not self.view_widget.current_scene.port_style_width:
                self.width_label_changed(self.port_style_width_label, port.Port.width)
            else:
                self.width_label_changed(self.port_style_width_label, self.view_widget.current_scene.port_style_width)
            #       color
            if not self.view_widget.current_scene.port_style_color:
                self.color_label_changed(self.port_style_color_label, port.Port.color)
            else:
                self.color_label_changed(self.port_style_color_label, self.view_widget.current_scene.port_style_color)

            if not self.view_widget.current_scene.port_style_border_color:
                self.color_label_changed(self.port_style_border_color_label, port.Port.border_color)
            else:
                self.color_label_changed(self.port_style_border_color_label,
                                         self.view_widget.current_scene.port_style_border_color)

            if not self.view_widget.current_scene.port_style_hovered_color:
                self.color_label_changed(self.port_style_hovered_color_label, port.Port.hovered_color)
            else:
                self.color_label_changed(self.port_style_hovered_color_label,
                                         self.view_widget.current_scene.port_style_hovered_color)

            if not self.view_widget.current_scene.port_style_hovered_border_color:
                self.color_label_changed(self.port_style_hovered_border_color_label, port.Port.hovered_border_color)
            else:
                self.color_label_changed(self.port_style_hovered_border_color_label,
                                         self.view_widget.current_scene.port_style_hovered_border_color)

            if not self.view_widget.current_scene.port_style_activated_color:
                self.color_label_changed(self.port_style_activated_color_label, port.Port.activated_color)
            else:
                self.color_label_changed(self.port_style_activated_color_label,
                                         self.view_widget.current_scene.port_style_activated_color)

            if not self.view_widget.current_scene.port_style_activated_border_color:
                self.color_label_changed(self.port_style_activated_border_color_label, port.Port.activated_border_color)
            else:
                self.color_label_changed(self.port_style_activated_border_color_label,
                                         self.view_widget.current_scene.port_style_activated_border_color)

            #   change slots
            #       width
            self.port_style_width_button.disconnect()
            self.port_style_width_button.clicked.connect(lambda x: self.width_changed("Port_width", current_index))
            #       color
            self.port_style_color_button.disconnect()
            self.port_style_color_button.clicked.connect(
                lambda x: self.color_changed("Port_color", current_index))

            self.port_style_border_color_button.disconnect()
            self.port_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_border_color", current_index))

            self.port_style_hovered_color_button.disconnect()
            self.port_style_hovered_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_color", current_index))

            self.port_style_hovered_border_color_button.disconnect()
            self.port_style_hovered_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_border_color", current_index))

            self.port_style_activated_color_button.disconnect()
            self.port_style_activated_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_color", current_index))

            self.port_style_activated_border_color_button.disconnect()
            self.port_style_activated_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_border_color", current_index))

        elif current_index == 2:
            #   change slots
            #       width
            self.port_style_width_button.disconnect()
            self.port_style_width_button.clicked.connect(lambda x: self.width_changed("Port_width", current_index))
            #       color
            self.port_style_color_button.disconnect()
            self.port_style_color_button.clicked.connect(
                lambda x: self.color_changed("Port_color", current_index))

            self.port_style_border_color_button.disconnect()
            self.port_style_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_border_color", current_index))

            self.port_style_hovered_color_button.disconnect()
            self.port_style_hovered_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_color", current_index))

            self.port_style_hovered_border_color_button.disconnect()
            self.port_style_hovered_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_hovered_border_color", current_index))

            self.port_style_activated_color_button.disconnect()
            self.port_style_activated_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_color", current_index))

            self.port_style_activated_border_color_button.disconnect()
            self.port_style_activated_border_color_button.clicked.connect(
                lambda x: self.color_changed("Port_activated_border_color", current_index))

    def init_draw(self):
        """
        init draw widget style label.

        """

        #   change current parameters
        #       width
        self.width_label_changed(self.draw_style_width_label, draw.Draw.pen_width)
        #       color
        self.color_label_changed(self.draw_style_color_label, draw.Draw.color)
        #   chang slots
        #       width
        if self.draw_init_flag:
            self.draw_style_width_button.clicked.connect(
                lambda x: self.width_changed("draw_width", 0))
            #       color
            self.draw_style_color_button.clicked.connect(
                lambda x: self.color_changed("draw_color", 0))
            self.draw_init_flag = False

    def text_width_changed(self, value: float):
        attribute.AttributeWidget.width_flag = value
        for attribute_item in self.view_widget.attribute_widgets:
            attribute_item.attribute_widget.label_item.setTextWidth(attribute.AttributeWidget.width_flag)
            attribute_item.resize(0, 0)
            if not attribute_item.parentItem():
                attribute_item.text_change_node_shape()

    def init_style(self, current_index):
        """
        Init widgets of all type style.

        Args:
            current_index: The current drop-down box index on the top of the style list.

        """

        self.init_attribute(current_index)
        self.init_logic(current_index)
        self.init_pipe(current_index)
        self.init_port(current_index)
        self.init_draw()

    def resizeEvent(self, a0) -> None:
        super(NoteWindow, self).resizeEvent(a0)
        self.sky_widget.resize(self.width(), self.height())

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key_B and int(a0.modifiers()) & QtCore.Qt.ControlModifier:
            if self.toolbar.isVisible():
                self.toolbar.setVisible(False)
                self.view_widget.run_thumbnails.wait()
                self.view_widget.run_thumbnails.killTimer(self.time_id)
                self.thumbnails.hide()
            else:
                self.toolbar.setVisible(True)
                self.view_widget.run_thumbnails.run()
                self.time_id = self.view_widget.run_thumbnails.startTimer(500, timerType=QtCore.Qt.VeryCoarseTimer)
                self.thumbnails.show()
        if a0.key() == QtCore.Qt.Key_Delete and len(self.scene_list.selectedItems()) == 1:
            self.view_widget.delete_sub_scene(self.scene_list.selectedItems()[0])
        super(NoteWindow, self).keyPressEvent(a0)

    def load_data(self, splash: QtWidgets.QSplashScreen):
        """
        Load the filename while loading splash screen.

        Args:
            splash: The splash screen.

        """

        if self.view_widget.filename:
            self.view_widget.load_from_file()
            self.view_widget.first_open = False
        splash.showMessage("loading", QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)
        QtWidgets.qApp.processEvents()
