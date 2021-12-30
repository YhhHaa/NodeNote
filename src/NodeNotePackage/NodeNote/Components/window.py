import math
import os

from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets, QtWebChannel

from ..Components.effect_snow import EffectSkyWidget
from ..Components import attribute, pipe, port, draw, todo, effect_background, markdown_edit
from ..GraphicsView.view import View
from ..Model import constants


class SceneList(QtWidgets.QTreeWidget):
    def __init__(self, mainwindow, parent=None) -> None:
        super().__init__(parent=parent)
        self.mainwindow = mainwindow
    
    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        context_menu = QtWidgets.QMenu(self)
        delete_scene = context_menu.addAction(QtCore.QCoreApplication.translate("SceneList", "delete this scene"))
        delete_scene.setIcon(QtGui.QIcon(
                os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/sidebar_delete.png"))))

        action = context_menu.exec_(a0.globalPos())
        if action == delete_scene and len(self.selectedItems()) >= 1:
                self.mainwindow.view_widget.delete_sub_scene(self.selectedItems()[0])

        a0.accept()


class FileView(QtWidgets.QTreeView):
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.clicked.connect(self.load_new_file)

    def contextMenuEvent(self, a0: QtGui.QContextMenuEvent) -> None:
        context_menu = QtWidgets.QMenu(self)
        create_dir = context_menu.addAction(QtCore.QCoreApplication.translate("FileView", "create new dir"))
        create_dir.setIcon(QtGui.QIcon(
            os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/file_view_create.png"))))
        delete_dir_file = context_menu.addAction(QtCore.QCoreApplication.translate("FileView", "delete file"))
        delete_dir_file.setIcon(QtGui.QIcon(
            os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/file_view_delete.png"))))
        create_new_note = context_menu.addAction(QtCore.QCoreApplication.translate("FileView", "create new note"))
        create_new_note.setIcon(QtGui.QIcon(
            os.path.abspath(os.path.join(constants.work_dir, "Resources/Images/create_new_note.png"))))
        
        action = context_menu.exec_(a0.globalPos())
        if action == delete_dir_file:
            if self.mainwindow.file_model.type(self.currentIndex()) == "Directory":
                self.mainwindow.file_model.rmdir(self.currentIndex())
            else:
                self.mainwindow.file_model.remove(self.currentIndex())
        elif action == create_dir:
            self.mainwindow.file_model.mkdir(self.currentIndex(), "new dir")
        elif action == create_new_note:
            if self.mainwindow.file_model.isDir(self.currentIndex()):
                self.mainwindow.load_window.new_note_file(self.mainwindow.file_model.filePath(self.currentIndex()))
            else:
                 self.mainwindow.load_window.new_note_file(self.mainwindow.file_model.filePath(self.currentIndex().parent()))
    
    def load_new_file(self, model_index: QtCore.QModelIndex):
        if not self.mainwindow.file_model.isDir(model_index) and self.mainwindow.file_model.fileName(model_index).endswith(".note"):
            self.mainwindow.load_window.load_from_file(self.mainwindow.file_model.filePath(model_index))


class NoteWindow(QtWidgets.QMainWindow):
    """
    Main window of the application:
        - Sidebar.
        - View manager.

    """

    def __init__(self, argv, app=None, load_window=None):
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
        self.load_window = load_window

        #   Window Init
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(constants.work_dir,
                                                                    'Resources/Images/cloudy.png'))))  # set icon
        self.setWindowTitle("My Beautiful life")  # set title
        self.resize(1200, 1000)  # set size
        self.move(  # set geometry
            (QtWidgets.QDesktopWidget().screenGeometry().width() - self.geometry().width()) // 2,
            (QtWidgets.QDesktopWidget().screenGeometry().height() - self.geometry().height()) // 2
        )
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        # Tool bar
        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolbar)
        self.tab_widget = QtWidgets.QTabWidget()
        self.toolbar.addWidget(self.tab_widget)
        self.toolbar.setVisible(False)

        # dir view
        #   model
        self.file_model = QtWidgets.QFileSystemModel()
        self.file_model.setReadOnly(False)
        #   view
        self.file_view = FileView(self)
        self.file_view.setModel(self.file_model)
        self.file_view.setRootIndex(self.file_model.setRootPath(constants.work_dir))
        #       layout
        self.file_view.setAnimated(False)
        self.file_view.setIndentation(20)
        self.file_view.setSortingEnabled(True)
        self.file_view.resize(self.file_view.screen().availableGeometry().size() / 2)
        self.file_view.setColumnWidth(0, self.file_view.width() / 3)
        self.tab_widget.addTab(self.file_view, QtCore.QCoreApplication.translate("NoteWindow", "Work Dir"))

        # Scene list widget
        self.scene_list_scroll = QtWidgets.QScrollArea(self)
        self.scene_list_scroll.setWidgetResizable(True)
        self.scene_list_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scene_list_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.scene_list = SceneList(self)
        self.scene_list.setObjectName("scene_list")
        self.scene_list.setSortingEnabled(True)
        self.scene_list.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.scene_list.setAlternatingRowColors(True)
        self.scene_list.setHeaderLabel(QtCore.QCoreApplication.translate("NoteWindow", "Scene List"))
        self.scene_list.setIndentation(8)
        self.scene_list_scroll.setWidget(self.scene_list)
        self.tab_widget.addTab(self.scene_list_scroll, QtCore.QCoreApplication.translate("NoteWindow", "Scene"))

        # Style list widget
        self.style_list_scroll = QtWidgets.QScrollArea(self)
        self.style_list_scroll.setWidgetResizable(True)
        self.style_list_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        self.style_list = QtWidgets.QWidget()
        self.style_list_layout = QtWidgets.QGridLayout()
        self.style_list_scroll.setWidget(self.style_list)
        self.style_list.setLayout(self.style_list_layout)

        self.tab_widget.addTab(self.style_list_scroll, QtCore.QCoreApplication.translate("NoteWindow", "Style"))
        #   Switch widget
        self.style_switch_combox = QtWidgets.QComboBox()
        self.style_switch_combox.addItems((QtCore.QCoreApplication.translate("NoteWindow", "All Scene"), QtCore.QCoreApplication.translate("NoteWindow", "Current Scene"), QtCore.QCoreApplication.translate("NoteWindow", "Selected Items")))
        self.style_list_layout.addWidget(self.style_switch_combox, 0, 0, 1, -1)
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
        self.attribute_style_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Attribute Widgets"))
        self.attribute_style_label.setObjectName("title_label")
        self.attribute_style_font_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Font"))
        self.attribute_style_font_label.setObjectName("font_label")
        self.attribute_style_font_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Font Color"))
        self.attribute_style_font_color_label.setObjectName("color_label")
        self.attribute_style_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Background Color"))
        self.attribute_style_background_color_label.setObjectName("color_label")
        self.attribute_style_selected_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Selected Background Color"))
        self.attribute_style_selected_background_color_label.setObjectName("color_label")
        self.attribute_style_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Border Color"))
        self.attribute_style_border_color_label.setObjectName("color_label")
        self.attribute_style_selected_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Selected Border Color"))
        self.attribute_style_selected_border_color_label.setObjectName("color_label")
        #           added
        self.style_list_layout.addWidget(self.attribute_style_label, 1, 0, 1, -1)
        self.style_list_layout.addWidget(self.attribute_style_font_label, 2, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_font_color_label, 3, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_background_color_label, 4, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_background_color_label, 5, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_border_color_label, 6, 1, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_border_color_label, 7, 1, 1, 1)
        #       Pushbutton Widgets
        #           init
        self.attribute_style_font_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Font"))
        self.attribute_style_font_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Font Color"))
        self.attribute_style_background_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Background Color"))
        self.attribute_style_selected_background_color_button = QtWidgets.QPushButton(
            QtCore.QCoreApplication.translate("NoteWindow", "Change Selected Background Color"))
        self.attribute_style_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Border Color"))
        self.attribute_style_selected_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Selected Border Color"))
        #           added
        self.style_list_layout.addWidget(self.attribute_style_font_button, 2, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_font_color_button, 3, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_background_color_button, 4, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_background_color_button, 5, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_border_color_button, 6, 0, 1, 1)
        self.style_list_layout.addWidget(self.attribute_style_selected_border_color_button, 7, 0, 1, 1)

        #   Logic widgets
        #       Color
        self.logic_style_background_color = None
        self.logic_style_selected_background_color = None
        self.logic_style_border_color = None
        self.logic_style_selected_border_color = None
        #       label widgets
        #           init
        self.logic_style_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Logic Widgets"))
        self.logic_style_label.setObjectName("title_label")
        self.logic_style_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Background Color"))
        self.logic_style_background_color_label.setObjectName("color_label")
        self.logic_style_selected_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Selected Background Color"))
        self.logic_style_selected_background_color_label.setObjectName("color_label")
        self.logic_style_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Border Color"))
        self.logic_style_border_color_label.setObjectName("color_label")
        self.logic_style_selected_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Selected Border Color"))
        self.logic_style_selected_border_color_label.setObjectName("color_label")
        #           added
        self.style_list_layout.addWidget(self.logic_style_label, 8, 0, 1, -1)
        self.style_list_layout.addWidget(self.logic_style_background_color_label, 9, 1)
        self.style_list_layout.addWidget(self.logic_style_selected_background_color_label, 10, 1)
        self.style_list_layout.addWidget(self.logic_style_border_color_label, 11, 1)
        self.style_list_layout.addWidget(self.logic_style_selected_border_color_label, 12, 1)
        #       button widgets
        #           init
        self.logic_style_background_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Background Color"))
        self.logic_style_selected_background_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Selected Background Color"))
        self.logic_style_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Border Color"))
        self.logic_style_selected_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Selected Border Color"))
        #           added
        self.style_list_layout.addWidget(self.logic_style_background_color_button, 9, 0)
        self.style_list_layout.addWidget(self.logic_style_selected_background_color_button, 10, 0)
        self.style_list_layout.addWidget(self.logic_style_border_color_button, 11, 0)
        self.style_list_layout.addWidget(self.logic_style_selected_border_color_button, 12, 0)

        #   Pipe widgets
        #       Color and width
        self.pipe_style_width = None
        self.pipe_style_background_color = None
        self.pipe_style_selected_background_color = None
        self.pipe_style_font_type = None
        self.pipe_style_font_color = None
        #       Label widgets
        #           init
        self.pipe_style_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Pipe Widgets"))
        self.pipe_style_label.setObjectName("title_label")
        self.pipe_style_width_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Width"))
        self.pipe_style_width_label.setObjectName("font_label")
        self.pipe_style_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Background Color"))
        self.pipe_style_background_color_label.setObjectName("color_label")
        self.pipe_style_selected_background_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Selected Background Color"))
        self.pipe_style_selected_background_color_label.setObjectName("color_label")
        self.pipe_style_font_type_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Font Type"))
        self.pipe_style_font_type_label.setObjectName("font_label")
        self.pipe_style_font_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Font Color"))
        self.pipe_style_font_color_label.setObjectName("color_label")
        #           added
        self.style_list_layout.addWidget(self.pipe_style_label, 13, 0, 1, -1)
        self.style_list_layout.addWidget(self.pipe_style_width_label, 14, 1)
        self.style_list_layout.addWidget(self.pipe_style_background_color_label, 15, 1)
        self.style_list_layout.addWidget(self.pipe_style_selected_background_color_label, 16, 1)
        self.style_list_layout.addWidget(self.pipe_style_font_type_label, 17, 1)
        self.style_list_layout.addWidget(self.pipe_style_font_color_label, 18, 1)
        #       Pushbutton widgets
        #           init
        self.pipe_style_width_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Width"))
        self.pipe_style_background_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Background Color"))
        self.pipe_style_selected_background_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Selected Background Color"))
        self.pipe_style_font_type_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Font Type"))
        self.pipe_style_font_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Font Color"))
        #           added
        self.style_list_layout.addWidget(self.pipe_style_width_button, 14, 0)
        self.style_list_layout.addWidget(self.pipe_style_background_color_button, 15, 0)
        self.style_list_layout.addWidget(self.pipe_style_selected_background_color_button, 16, 0)
        self.style_list_layout.addWidget(self.pipe_style_font_type_button, 17, 0)
        self.style_list_layout.addWidget(self.pipe_style_font_color_button, 18, 0)

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
        self.port_style_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Port Widgets"))
        self.port_style_label.setObjectName("title_label")
        self.port_style_width_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Width"))
        self.port_style_width_label.setObjectName("font_label")
        self.port_style_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Background Color"))
        self.port_style_color_label.setObjectName("color_label")
        self.port_style_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Border Color"))
        self.port_style_border_color_label.setObjectName("color_label")
        self.port_style_hovered_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Hovered Background Color"))
        self.port_style_hovered_color_label.setObjectName("color_label")
        self.port_style_hovered_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Hovered Border Color"))
        self.port_style_hovered_border_color_label.setObjectName("color_label")
        self.port_style_activated_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Activated Background Color"))
        self.port_style_activated_color_label.setObjectName("color_label")
        self.port_style_activated_border_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Activated Border Color"))
        self.port_style_activated_border_color_label.setObjectName("color_label")
        #           added
        self.style_list_layout.addWidget(self.port_style_label, 19, 0, 1, -1)
        self.style_list_layout.addWidget(self.port_style_width_label, 20, 1)
        self.style_list_layout.addWidget(self.port_style_color_label, 21, 1)
        self.style_list_layout.addWidget(self.port_style_border_color_label, 22, 1)
        self.style_list_layout.addWidget(self.port_style_hovered_color_label, 23, 1)
        self.style_list_layout.addWidget(self.port_style_hovered_border_color_label, 24, 1)
        self.style_list_layout.addWidget(self.port_style_activated_color_label, 25, 1)
        self.style_list_layout.addWidget(self.port_style_activated_border_color_label, 26, 1)
        #       Pushbutton widgets
        #           init
        self.port_style_width_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Width"))
        self.port_style_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Background Color"))
        self.port_style_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Border Color"))
        self.port_style_hovered_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Hovered Background Color"))
        self.port_style_hovered_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Hovered Border Color"))
        self.port_style_activated_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Activated Background Color"))
        self.port_style_activated_border_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Activated Border Color"))
        #           added
        self.style_list_layout.addWidget(self.port_style_width_button, 20, 0)
        self.style_list_layout.addWidget(self.port_style_color_button, 21, 0)
        self.style_list_layout.addWidget(self.port_style_border_color_button, 22, 0)
        self.style_list_layout.addWidget(self.port_style_hovered_color_button, 23, 0)
        self.style_list_layout.addWidget(self.port_style_hovered_border_color_button, 24, 0)
        self.style_list_layout.addWidget(self.port_style_activated_color_button, 25, 0)
        self.style_list_layout.addWidget(self.port_style_activated_border_color_button, 26, 0)

        #   Container widgets
        #       Label widgets
        #           init
        self.draw_style_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Draw Widgets"))
        self.draw_style_label.setObjectName("title_label")
        self.draw_style_width_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Width"))
        self.draw_style_width_label.setObjectName("font_label")
        self.draw_style_color_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Color"))
        self.draw_style_color_label.setObjectName("color_label")
        #           added
        self.style_list_layout.addWidget(self.draw_style_label, 27, 0, 1, -1)
        self.style_list_layout.addWidget(self.draw_style_width_label, 28, 1)
        self.style_list_layout.addWidget(self.draw_style_color_label, 29, 1)
        #       Pushbutton widgets
        #           init
        self.draw_style_width_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Width"))
        self.draw_style_color_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Color"))
        #           added
        self.style_list_layout.addWidget(self.draw_style_width_button, 28, 0)
        self.style_list_layout.addWidget(self.draw_style_color_button, 29, 0)
        self.draw_init_flag = True

        # Background image
        #       widgets
        self.background_image_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Background Image"))
        self.background_image_label.setObjectName("title_label")
        self.background_image_path_label = QtWidgets.QLabel()
        self.background_image_path_label.setObjectName("font_label")
        self.background_image_path_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Image"))
        #       added
        self.style_list_layout.addWidget(self.background_image_label, 30, 0, 1, -1)
        self.style_list_layout.addWidget(self.background_image_path_label, 31, 1)
        self.style_list_layout.addWidget(self.background_image_path_button, 31, 0)

        # Text editor
        #       widgets
        self.text_editor_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Text Editor(All scene)"))
        self.text_editor_label.setObjectName("title_label")
        self.text_editor_length_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Set Fixed Width Or Not"))
        self.text_editor_length_label.setObjectName("font_label")
        self.text_editor_length_box = QtWidgets.QDoubleSpinBox()
        self.text_editor_length_box.setRange(-1, math.inf)
        self.text_editor_length_box.setSingleStep(100)
        self.text_editor_length_box.setValue(-1)
        #       added
        self.style_list_layout.addWidget(self.text_editor_label, 32, 0, 1, -1)
        self.style_list_layout.addWidget(self.text_editor_length_box, 33, 0)
        self.style_list_layout.addWidget(self.text_editor_length_label, 33, 1)
        #       slot
        self.text_editor_length_box.valueChanged.connect(self.text_width_changed)

        # stylesheet
        self.runtime_style = self.load_window.runtime_style
        #   widgets
        self.stylesheet_label = QtWidgets.QLabel(QtCore.QCoreApplication.translate("NoteWindow", "Window Stylesheet"))
        self.stylesheet_label.setObjectName("title_label")
        self.stylesheet_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("NoteWindow", "Change Window Style"))
        self.stylesheet_path_label = QtWidgets.QLabel()
        self.stylesheet_path_label.setObjectName("font_label")
        #   added
        self.style_list_layout.addWidget(self.stylesheet_label, 34, 0, 1, -1)
        self.style_list_layout.addWidget(self.stylesheet_button, 35, 0)
        self.style_list_layout.addWidget(self.stylesheet_path_label, 35, 1)

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

        # thumbnails
        self.thumbnails = QtWidgets.QLabel(self.view_widget)
        self.thumbnails.setGeometry(0, 0, 300, 300)
        self.thumbnails.hide()
        self.time_id = 0

        # markdown
        #   tool bar
        self.markdown_toolbar = QtWidgets.QToolBar()
        self.addToolBar(QtCore.Qt.RightToolBarArea, self.markdown_toolbar)

        #   web engine
        #       view
        self.markdown_view = markdown_edit.MarkdownView(self)
        self.markdown_view.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.markdown_view.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.markdown_toolbar.addWidget(self.markdown_view)
        #       page
        self.markdown_page = QtWebEngineWidgets.QWebEnginePage()
        self.markdown_view.setPage(self.markdown_page)
        #       document
        self.markdown_document = markdown_edit.MarkdownDocument(self.markdown_page)
        #       channel
        self.markdown_chanel = QtWebChannel.QWebChannel()
        self.markdown_chanel.registerObject("saveSignal", self.markdown_document)
        self.markdown_page.setWebChannel(self.markdown_chanel)
        #       slots
        self.markdown_document.save_text_signal.connect(self.load_window.save_markdown)
        #       show
        self.markdown_view.load(QtCore.QUrl.fromLocalFile(os.path.abspath(os.path.join(constants.work_dir, "Resources/Editor/markdown.html"))))
        self.markdown_view.focusProxy().installEventFilter(self)

    def eventFilter(self, a0: 'QtCore.QObject', a1: 'QtCore.QEvent') -> bool:
        if a0 is self.markdown_view.focusProxy() and a1.type() == QtCore.QEvent.FocusOut:
            self.markdown_document.return_text(self.markdown_view.dict_id)
        
        if a0 is self.markdown_view.focusProxy() and a1.type() == QtCore.QEvent.FocusIn:
            self.view_widget.focusOutEvent(QtGui.QFocusEvent(QtCore.QEvent.FocusOut))

        return super().eventFilter(a0, a1)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:

        self.view_widget.run_thumbnails.killTimer(self.time_id) 
        self.view_widget.run_thumbnails.exit(0)
        
        self.load_window.closeEvent(a0)

    def color_label_changed(self, label: QtWidgets.QLabel, color):
        """
        Change the colorful label.

        Args:
            label: QLabel.
            color: QColor.

        """
        if color:
            label.setStyleSheet(f"QLabel{{background-color:#{str(hex(color.rgba()))[2:]};}}")
           

    @staticmethod
    def font_label_changed(label: QtWidgets.QLabel, font: QtGui.QFont):
        """
        Change the font info in label.

        Args:
            label: The label need to be changed.
            font: The up to date font.

        """

        label.setText(QtCore.QCoreApplication.translate("NoteWindow", "Font: "))
        label.setText(label.text() + font.family() + str(font.pointSize()))

    @staticmethod
    def width_label_changed(label: QtWidgets.QLabel, width):
        """
        Change the width info in label.

        Args:
            label: The label need to be changed.
            width: The up to date width.

        """

        label.setText(QtCore.QCoreApplication.translate("NoteWindow", "Width: "))
        label.setText(label.text() + str(width))

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
        
        elif widget_type == "Pipe_font_color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                if current_index == 0:
                    pipe.Pipe.font_color = color
                    self.color_label_changed(self.pipe_style_font_color_label, color)
                    for item in self.view_widget.pipes:
                        item.update()
                elif current_index == 1:
                    self.view_widget.current_scene.pipe_style_font_color = color
                    self.color_label_changed(self.pipe_style_font_color_label, color)
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, pipe.Pipe):
                            item.update()
                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, pipe.Pipe):
                            item.font_color = color
                            item.font_color_flag = True
                            self.color_label_changed(self.pipe_style_font_color_label, color)
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

                elif current_index == 1:
                    self.view_widget.current_scene.attribute_style_font = font_type
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, attribute.AttributeWidget) \
                                and not item.attribute_widget.label_item.font_flag:
                            item.attribute_widget.label_item.document().setDefaultFont(font_type)
                            item.text_change_node_shape()
                            item.resize(20, 10)

                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, attribute.AttributeWidget):
                            item.attribute_widget.label_item.document().setDefaultFont(font_type)
                            item.text_change_node_shape()
                            item.attribute_widget.label_item.font_flag = True
                
                self.font_label_changed(self.attribute_style_font_label, font_type)
        elif widget_type == "Pipe_font":
            font_type, ok = QtWidgets.QFontDialog.getFont()
            if font_type and ok:
                if current_index == 0:
                    pipe.Pipe.font = font_type
                    for item in self.view_widget.pipes:
                        if not item.scene().pipe_style_font_type and not item.font_type_flag:
                            item.edit.setFont(font_type)
                elif current_index == 1:
                    self.view_widget.current_scene.pipe_style_font_type = font_type
                    for item in self.view_widget.current_scene.items():
                        if isinstance(item, pipe.Pipe) and not item.font_type_flag:
                            item.edit.setFont(font_type)
                elif current_index == 2:
                    for item in self.view_widget.current_scene.selectedItems():
                        if isinstance(item, pipe.Pipe):
                            item.font_type_flag = True
                            item.font = font_type
                            item.edit.setFont(font_type)
                self.font_label_changed(self.pipe_style_font_type_label, font_type)
                    

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
    
    def path_changed(self, current_index=0, window_style=False):
        """
        Update background image path.

        """
        if not window_style:
            filename, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                "Select background image", constants.work_dir,
                                                                "Svg background image (*.svg)")
            if filename and ok:
                    if current_index == 0:
                        effect_background.EffectBackground.name = os.path.relpath(filename, constants.work_dir)
                        # sub view
                        for sub_view in self.view_widget.children_view.values():
                            if not sub_view.sub_view_widget_view.current_scene.background_image_flag:
                                sub_view.sub_view_widget_view.current_scene.background_image.change_svg(os.path.relpath(filename, constants.work_dir))
                        # scene
                        iterator = QtWidgets.QTreeWidgetItemIterator(self.scene_list)
                        while iterator.value():
                            scene_flag = iterator.value()
                            iterator += 1
                            scene = scene_flag.data(0, QtCore.Qt.ToolTipRole)
                            if not scene.background_image_flag:
                                scene.background_image.change_svg(os.path.relpath(filename, constants.work_dir))

                    elif current_index == 1:
                        self.view_widget.current_scene.background_image_flag = True
                        self.view_widget.current_scene.background_image.name = os.path.relpath(filename, constants.work_dir)
                        self.view_widget.current_scene.background_image.change_svg(os.path.relpath(filename, constants.work_dir))

                    self.background_image_path_label.setText(os.path.basename(filename))
        else:
            filename, ok = QtWidgets.QFileDialog.getOpenFileName(self,
                                                                "Select qss", constants.work_dir,
                                                                "qss stylesheet (*.qss)")
            if filename and ok:
                self.runtime_style.path = os.path.relpath(filename, constants.work_dir)
                self.stylesheet_path_label.setText(os.path.basename(filename))
                self.runtime_style.load_stylesheet(self.runtime_style.path)

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
            self.font_label_changed(self.pipe_style_font_type_label, pipe.Pipe.font)
            self.color_label_changed(self.pipe_style_font_color_label, pipe.Pipe.font_color)
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
            
            #       font
            self.pipe_style_font_type_button.disconnect()
            self.pipe_style_font_type_button.clicked.connect(lambda x: self.font_changed("Pipe_font", current_index))

            self.pipe_style_font_color_button.disconnect()
            self.pipe_style_font_color_button.clicked.connect(lambda x: self.color_changed("Pipe_font_color", current_index))

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
            
            #       font
            if self.view_widget.current_scene.pipe_style_font_type:
                self.font_label_changed(self.pipe_style_font_type_label, self.view_widget.current_scene.pipe_style_font_type)
            else:
                self.font_label_changed(self.pipe_style_font_type_label, pipe.Pipe.font)
            
            if self.view_widget.current_scene.pipe_style_font_color:
                self.color_label_changed(self.pipe_style_font_color_label, self.view_widget.current_scene.pipe_style_font_color)
            else:
                self.color_label_changed(self.pipe_style_font_color_label, pipe.Pipe.font_color)

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
            #       font
            self.pipe_style_font_type_button.disconnect()
            self.pipe_style_font_type_button.clicked.connect(lambda x: self.font_changed("Pipe_font", current_index))
            self.pipe_style_font_color_button.disconnect()
            self.pipe_style_font_color_button.clicked.connect(lambda x: self.color_changed("Pipe_font_color", current_index))

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
            #       font
            self.pipe_style_font_type_button.disconnect()
            self.pipe_style_font_type_button.clicked.connect(lambda x: self.font_changed("Pipe_font", current_index))
            self.pipe_style_font_color_button.disconnect()
            self.pipe_style_font_color_button.clicked.connect(lambda x: self.color_changed("Pipe_font_color", current_index))

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
    
    def init_background(self, current_index):
        """
        Init background image.

        Args:
            current_index: The current drop-down box index on the top of the style list.
        """

        if current_index == 0:
            self.background_image_path_label.setText(os.path.basename(os.path.join(constants.work_dir, effect_background.EffectBackground.name)))
        elif current_index == 1:
            self.background_image_path_label.setText(os.path.basename(os.path.join(constants.work_dir, self.view_widget.current_scene.background_image.name)))

        self.background_image_path_button.disconnect()
        self.background_image_path_button.clicked.connect(lambda x: self.path_changed(current_index))

    def init_window_style(self):
        """
        init window stylesheet

        """

        # change current parameters
        self.stylesheet_path_label.setText(os.path.basename(os.path.join(constants.work_dir, self.runtime_style.path)))
        self.runtime_style.load_stylesheet(self.runtime_style.path)
        # slot
        self.stylesheet_button.disconnect()
        self.stylesheet_button.clicked.connect(lambda x: self.path_changed(window_style=True))
        
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
            if not attribute_item.mouse_flag:
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
        self.init_background(current_index)
        self.init_window_style()

    def redirect_last_scene(self):
        self.scene_list.clearSelection()

        temp_scene = self.view_widget.current_scene
        temp_sceen_flag = self.view_widget.current_scene_flag

        self.view_widget.current_scene = self.view_widget.last_scene
        self.view_widget.current_scene_flag = self.view_widget.last_scene_flag
        self.view_widget.setScene(self.view_widget.current_scene)
        self.view_widget.current_scene_flag.setSelected(True)
        self.view_widget.background_image = self.view_widget.current_scene.background_image
        self.view_widget.cutline = self.view_widget.current_scene.cutline

        self.view_widget.last_scene = temp_scene
        self.view_widget.last_scene_flag = temp_sceen_flag
    
    def rediect_parent_scene(self):
        self.scene_list.clearSelection()

        parent_flag = self.view_widget.current_scene_flag.parent()
        if parent_flag:
            self.view_widget.change_current_scene(parent_flag)
            parent_flag.setSelected(True)

    def resizeEvent(self, a0) -> None:
        super(NoteWindow, self).resizeEvent(a0)
        self.sky_widget.resize(self.width(), self.height())

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == QtCore.Qt.Key_X and int(a0.modifiers()) & QtCore.Qt.AltModifier:
            self.rediect_parent_scene()
        if a0.key() == QtCore.Qt.Key_Z and int(a0.modifiers()) & QtCore.Qt.AltModifier:
            self.redirect_last_scene()
            return
        if a0.key() == QtCore.Qt.Key_B and int(a0.modifiers()) & QtCore.Qt.ShiftModifier:
            if self.thumbnails.isVisible():
                self.view_widget.run_thumbnails.wait()
                self.view_widget.run_thumbnails.killTimer(self.time_id)
                self.thumbnails.hide()
            else:
                self.view_widget.run_thumbnails.run()
                self.time_id = self.view_widget.run_thumbnails.startTimer(500, timerType=QtCore.Qt.VeryCoarseTimer)
                self.thumbnails.show()
            return
        if a0.key() == QtCore.Qt.Key_B and int(a0.modifiers()) & QtCore.Qt.ControlModifier:
            if self.toolbar.isVisible():
                self.toolbar.setVisible(False)
            else:
                self.toolbar.setVisible(True)
            return
        # if a0.key() == QtCore.Qt.Key_Delete and len(self.scene_list.selectedItems()) == 1:
        #     self.view_widget.delete_sub_scene(self.scene_list.selectedItems()[0])
        super(NoteWindow, self).keyPressEvent(a0)
