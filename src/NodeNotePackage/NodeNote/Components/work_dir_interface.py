import os
import time
import shutil
import sys
import json
import traceback
import sqlite3
import shutil

from PyQt5 import QtWidgets, QtCore, QtGui

from NodeNotePackage.NodeNote.Components import draw

from ..Model import constants, serialize_pb2
from ..Components.window import NoteWindow
from ..Components.attribute import AttributeWidget
from ..Components.todo import Todo
from ..GraphicsView.scene import Scene


class ReadOnlyDeletgate(QtWidgets.QItemDelegate):
    def createEditor(self, parent: QtWidgets.QWidget, option: 'QtGui.QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtWidgets.QWidget:
        return None


class RuntimeStylesheets():

    path = constants.style_path

    def __init__(self, app) -> None:
        self.app = app
        self.load_stylesheet(self.path)
    
    def load_stylesheet(self, stylesheet_path=""):
        """
        load stylesheet into app.

        Args:
            stylesheet_path: relative path of stylesheet file.

        """

        try:
            with open(os.path.join(constants.work_dir, stylesheet_path), 'r', encoding='utf-8') as qss_file:
                style = qss_file.read()
            self.app.setStyleSheet(style)

        except Exception:
            pass


class WorkDirInterface(QtWidgets.QWidget):
    def __init__(self, app, trans) -> None:
        super().__init__()
        self.app = app
        self.trans = trans

        #   Window Init
        self.setWindowTitle(QtCore.QCoreApplication.translate("WorkDirInterface", "Work dir"))  # set title
        self.resize(600, 500)  # set size
        self.move(  # set geometry
            (QtWidgets.QDesktopWidget().screenGeometry().width() - self.geometry().width()) // 2,
            (QtWidgets.QDesktopWidget().screenGeometry().height() - self.geometry().height()) // 2
        )
        self.setLayout(QtWidgets.QVBoxLayout())

        # style
        self.setObjectName("work_dir_interface")
        self.runtime_style = RuntimeStylesheets(self.app)
        self.runtime_style.load_stylesheet(self.runtime_style.path)

        # logo
        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setPixmap(QtGui.QPixmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/Images/logo.png"))))
        self.layout().addWidget(self.logo_label)
        self.layout().setAlignment(self.logo_label, QtCore.Qt.AlignCenter)

        # last dir view
        self.dir_model = QtGui.QStandardItemModel()
        self.dir_model.setHorizontalHeaderLabels([QtCore.QCoreApplication.translate("WorkDirInterface", "Last Dirs"),
                                                  QtCore.QCoreApplication.translate("WorkDirInterface", "Opened Time")])
        self.dir_view = QtWidgets.QTreeView()
        self.dir_view.setItemDelegate(ReadOnlyDeletgate(self))
        self.dir_view.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.dir_view.header().setStretchLastSection(True)
        self.dir_view.setModel(self.dir_model)
        self.dir_view.doubleClicked.connect(lambda model_index: self.set_work_dir(model_index.sibling(model_index.row(), 0).data(QtCore.Qt.DisplayRole)))
        self.layout().addWidget(self.dir_view)
        self.load_last_dirs()

        # delete dir context menu
        self.dir_view.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.delete_action = QtWidgets.QAction(QtGui.QIcon(os.path.join(constants.work_dir, "Resources/Images/delete_path.png")), 
                                QtCore.QCoreApplication.translate("WorkDirInterface", "delete this path"))
        self.dir_view.addAction(self.delete_action)
        self.delete_action.triggered.connect(lambda: self.delete_last_dir(self.dir_view.currentIndex().siblingAtColumn(0)))
        

        # open dir button
        self.open_dir_button = QtWidgets.QPushButton(QtCore.QCoreApplication.translate("WorkDirInterface", "Open work dir"))
        self.layout().addWidget(self.open_dir_button)
        self.open_dir_button.clicked.connect(self.set_work_dir)
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(constants.work_dir,
                                                            'Resources/Images/cloudy.png'))))  # set icon
        
        # time clock
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.auto_save)
        self.timer.start(180000)
        self.current_file = ""

        # database
        self.database_connect = None
    
    def delete_last_dir(self, model_index: QtCore.QModelIndex):
        # get path
        path = model_index.data(QtCore.Qt.DisplayRole)

        # read from json
        if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json"))):
            with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "r") as f:
                time_dirs = json.load(f)
        else:
            return
        
        # delete data from json
        for time_dir_index in range(len(time_dirs["dirs"])):
            if time_dirs["dirs"][time_dir_index][1] == path:
                del time_dirs["dirs"][time_dir_index]
                break
        
        # write data into json
        if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json"))):
            with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "w") as f:
                json.dump(time_dirs, f, indent=4, sort_keys=True)
        
        # remove this row from view
        self.dir_model.removeRow(model_index.row())

    def load_last_dirs(self):
        #   create last work dir
        if os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json"))):
            with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "r") as f:
                time_dirs = json.load(f)
                i = 0
                for time_dir in time_dirs["dirs"]:
                    self.dir_model.setItem(i, 0, QtGui.QStandardItem(time_dir[1]))
                    self.dir_model.setItem(i, 1, QtGui.QStandardItem(time.asctime(time.localtime(float(time_dir[0])))))
                    i += 1


    def set_work_dir(self, work_dir=None):

        if not work_dir:
            work_dir = QtWidgets.QFileDialog.getExistingDirectory(self, 
                                                        "Open your work dir", 
                                                        "./", 
                                                        QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
        if work_dir:
            work_dir = os.path.abspath(work_dir)

            # change work dir
            constants.init_path(work_dir)

            # create environment
            try:
                #   create .NODENOTE
                if not os.path.exists(os.path.join(work_dir, ".NODENOTE")):
                    with open(os.path.join(work_dir, ".NODENOTE"), "w", encoding="utf-8") as f:
                        json.dump({"create_dir_time": time.time(), "last_file": ""}, f, indent=4)
                #   create Assets which stores images.
                if not os.path.exists(os.path.join(work_dir, "Assets")):
                    os.mkdir(os.path.join(work_dir, "Assets"))
                #   create Attachments which stores attachments.
                if not os.path.exists(os.path.join(work_dir, "Attachments")):
                    os.mkdir(os.path.join(work_dir, "Attachments"))
                #   create Documents which stores markdown documents.
                if not os.path.exists(os.path.join(work_dir, "Documents")):
                    os.mkdir(os.path.join(work_dir, "Documents"))
                #   create database to store markdown text.
                if self.database_connect:
                    self.database_connect.commit()
                    self.database_connect.close()
                self.database_connect = sqlite3.connect(os.path.join(os.path.join(constants.work_dir, "Documents"), "markdown.db"))
                database_cursor = self.database_connect.cursor()
                database_cursor.execute('''
                    CREATE TABLE IF NOT EXISTS markdown (
                        id INT PRIMARY KEY NOT NULL,
                        markdown_text TEXT);
                ''')
                database_cursor.close()
                self.database_connect.commit()
                #   create History which stores .note file of history versions.
                if not os.path.exists(os.path.join(work_dir, "History")):
                    os.mkdir(os.path.join(work_dir, "History"))
                #   create Resources which stores resources like stylesheet or background image.
                if not os.path.exists(os.path.join(work_dir, "Resources")):
                    os.mkdir(os.path.join(work_dir, "Resources"))
                #       create Stylesheets dir and move stylesheets.qss
                if not os.path.exists(os.path.join(work_dir, "Resources/Stylesheets")):
                    shutil.copytree(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/Stylesheets")),
                                    os.path.join(work_dir, "Resources/Stylesheets"))
                #       create Images dir and move images
                if not os.path.exists(os.path.join(work_dir, "Resources/Images")):
                    shutil.copytree(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/Images")),
                                    os.path.join(work_dir, "Resources/Images"))
                #       create Vditor
                if not os.path.exists(os.path.join(work_dir, "Resources/Editor")):
                    shutil.copytree(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/Editor")),
                                    os.path.join(work_dir, "Resources/Editor"))
                #   create Notes which stores .note file
                if not os.path.exists(os.path.join(work_dir, "Notes")):
                    os.mkdir(os.path.join(work_dir, "Notes"))

                #   create last work dir
                last_work_dirs = {"dirs": []}
                #       create json
                if not os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json"))):
                    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "w", encoding="utf-8") as f:
                        json.dump(last_work_dirs, f, indent=4, sort_keys=True)
                #       read json
                with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "r", encoding="utf-8") as f:
                    last_work_dirs = json.load(f)
                #       write dir to json
                append_flag = True
                for time_dir in last_work_dirs["dirs"]:
                    if time_dir[1] == work_dir:
                        time_dir[0] = time.time()
                        append_flag = False
                if append_flag:
                    last_work_dirs["dirs"].append([time.time(), work_dir])
                with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/LASTDIR.json")), "w", encoding="utf-8") as f:
                    json.dump(last_work_dirs, f, indent=4, sort_keys=True)
                
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                QtWidgets.QErrorMessage(self).showMessage("Error:\n"+ f"{e}" + f"{exc_type}, {fname}, {exc_tb.tb_lineno}")
            
            # load mainwindow
            self.load_mainwindow()

    def load_mainwindow(self):
        # slash
        splash = QtWidgets.QSplashScreen(QtGui.QPixmap(os.path.join(constants.work_dir,
                                                    "Resources/Images/logo.png")))
        splash.showMessage(QtCore.QCoreApplication.translate("WorkDirInterface", "start loading"), QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)
        splash.setFont(QtGui.QFont("New York Large", 10))
        splash.show()
        self.app.processEvents()

        # main
        try:
            self.hide()
            self.window = NoteWindow(sys.argv, self.app, self)
            self.load_data(splash)
            self.window.show()
            splash.finish(self.window)
            splash.deleteLater()
        except Exception as e:
            self.show()
            QtWidgets.QErrorMessage(self).showMessage(f"{traceback.format_exc()}")
    
    def load_data(self, splash: QtWidgets.QSplashScreen):
        """
        Load the filename while loading splash screen.
        - has last note file
        - has other file
        - no file

        Args:
            splash: The splash screen.

        """

        # load last file
        with open(os.path.join(constants.work_dir, ".NODENOTE"), "r", encoding="utf-8") as f:
            meta_data = json.load(f)
            if meta_data["last_file"]:
                if os.path.exists(os.path.join(constants.work_dir, meta_data["last_file"])):
                    self.load_from_file(os.path.join(constants.work_dir, meta_data["last_file"]))
                    return
        
        # reverse dir to find a accessable .note file
        sub_dirs = os.walk(os.path.join(constants.work_dir, "Notes"))
        for root, _, file_name in sub_dirs:
            for file in file_name:
                if file.endswith(".note"):
                    self.load_from_file(os.path.join(root, file))
                    return

        self.new_note_file()
        
        splash.showMessage(QtCore.QCoreApplication.translate("NoteWindow", "loading"), QtCore.Qt.AlignCenter | QtCore.Qt.AlignBottom, QtCore.Qt.white)
        QtWidgets.qApp.processEvents()

    def new_note_file(self, path=""):
        """
        Create a new note file in path.

        Args:
            path: usual work_dir/Notes.

        Return:
            path: absloute path.

        """

        view_serialization = serialize_pb2.ViewSerialization()

        # scene
        root_scene = Scene(self.window.scene_list, self.window.view_widget)
        root_scene.serialize(view_serialization.scene_serialization.add())
        view_serialization.current_scene_id = root_scene.id

        # style
        view_serialization.style_path = constants.style_path

        # attribute widget ui
        view_serialization.all_attr_font_family = constants.input_text_font.family()
        view_serialization.all_attr_font_size = constants.input_text_font.pointSize()
        view_serialization.all_attr_color.append(constants.input_text_font_color.rgba())
        view_serialization.all_attr_color.append(constants.attribute_color.rgba())
        view_serialization.all_attr_color.append(constants.attribute_selected_color.rgba())
        view_serialization.all_attr_color.append(constants.attribute_border_color.rgba())
        view_serialization.all_attr_color.append(constants.attribute_selected_border_color.rgba())
        # logic widget ui
        view_serialization.all_logic_color.append(constants.logic_background_color.rgba())
        view_serialization.all_logic_color.append(constants.logic_selected_background_color.rgba())
        view_serialization.all_logic_color.append(constants.logic_border_color.rgba())
        view_serialization.all_logic_color.append(constants.logic_selected_border_color.rgba())
        # pipe widget ui
        view_serialization.all_pipe_width = constants.pipe_width
        view_serialization.all_pipe_color.append(constants.pipe_color.rgba())
        view_serialization.all_pipe_color.append(constants.pipe_selected_color.rgba())
        view_serialization.all_pipe_color.append(constants.pipe_font_color.rgba())
        view_serialization.all_pipe_font_family = constants.pipe_font.family()
        view_serialization.all_pipe_font_size = constants.pipe_font.pointSize()
        # port widget ui
        view_serialization.all_port_width = constants.port_width
        view_serialization.all_port_color.append(constants.port_color.rgba())
        view_serialization.all_port_color.append(constants.port_border_color.rgba())
        view_serialization.all_port_color.append(constants.port_hovered_color.rgba())
        view_serialization.all_port_color.append(constants.port_hovered_border_color.rgba())
        view_serialization.all_port_color.append(constants.port_activated_color.rgba())
        view_serialization.all_port_color.append(constants.port_activated_border_color.rgba())
        # draw widget ui
        view_serialization.all_draw_width = constants.draw_pen_width
        view_serialization.all_draw_color = constants.draw_color.rgba()
        # text width
        view_serialization.text_width = constants.attribute_width_flag
        # background image
        view_serialization.all_background_image = constants.background_image_path
        # flag
        if self.window.view_widget.root_flag:
            view_serialization.line_flag = constants.view_line_flag
        view_serialization.undo_flag = constants.view_undo_flag
        # flowing image
        view_serialization.flowing_flag = constants.view_flowing_flag

        if not path:
            with open(os.path.join(os.path.join(constants.work_dir, "Notes"), "NodeNote_" + str(int(time.time())) + ".note"), "wb") as f:
                f.write(view_serialization.SerializeToString())  
        else:
            with open(os.path.join(path, "NodeNote_" + str(int(time.time())) + ".note"), "wb") as f:
                f.write(view_serialization.SerializeToString())  

        # load
        if not path:
            file_path = os.path.relpath(os.path.join(os.path.join(constants.work_dir, "Notes"), "NodeNote_" + str(int(time.time())) + ".note"), constants.work_dir)
        else:
            file_path = os.path.relpath(os.path.join(path, "NodeNote_" + str(int(time.time())) + ".note"), constants.work_dir)
        self.load_from_file(os.path.join(constants.work_dir, file_path))
    
    def load_from_file(self, path=None):
        """
        Load .note file and save last file.

        Args:
            path: absolute path

        """

        # save last file
        if self.current_file:
            self.save_to_file(self.current_file)
        
        # load new file
        with open(path, "rb") as file:
            view_serialization = serialize_pb2.ViewSerialization()
            view_serialization.ParseFromString(file.read())
            self.window.view_widget.deserialize(view_serialization, {}, self.window.view_widget, True)
            self.window.setWindowTitle(path + "-Life")
            self.current_file = path
        
        # save into last opened file
        if not os.path.exists(os.path.join(constants.work_dir, ".NODENOTE")):
            with open(os.path.join(constants.work_dir, ".NODENOTE"), "w", encoding="utf-8") as f:
                json.dump({"create_dir_time": time.time(), "last_file": ""}, f, indent=4)
        with open(os.path.join(constants.work_dir, ".NODENOTE"), "r", encoding="utf-8") as f:
            meta_data = json.load(f)
        with open(os.path.join(constants.work_dir, ".NODENOTE"), "w", encoding="utf-8") as f:
            meta_data["last_file"] = os.path.relpath(path, constants.work_dir)
            json.dump(meta_data, f, indent=4)
    
    def save_to_file(self, path=None):
        """
        Save .note and backup .note

        Args:
            path: absolute path

        """

        # save file
        AttributeWidget.export_sub_scene_flag = True
        with open(path, 'wb') as file:
            file.write(self.window.view_widget.serialize())
        self.window.setWindowTitle(path)

        # backup file
        self.copy_file(path, os.path.join(constants.work_dir, os.path.join("History", f"{time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime(time.time()))}" + "_" + os.path.basename(path))))
    
    def save_markdown(self, dict_id: dict, mark_text: str):
        """
        Save last attr markdown text and load next attr markdown text

        Args:
            dict_id: {last_attr_id, new_attr_id}.
            mark_text: markdown text from html.

        """

        old_item_id = dict_id.get("old_focus_item")

        if self.database_connect and old_item_id != 0:
            # save last attr markdown text
            if mark_text:
                # save database
                database_cursor = self.database_connect.cursor()
                database_cursor.execute(f'''
                    replace into markdown (id, markdown_text) values (?,?)
                ''', (old_item_id, mark_text))
                database_cursor.close()
                self.database_connect.commit()

                # save file
                with open(os.path.join(constants.work_dir, os.path.join("Documents", f"{old_item_id}.md")), 
                            "w", encoding="utf-8") as f:
                    f.write(mark_text)

                if constants.DEBUG_MARKDOWN:
                    print(f"Write 3.save_markdown {mark_text}")
    
    def save_image(self, dict_id: dict, image: draw.Canvas):
        """
        Save attr draw image.

        Args:
            dict_id: {last_attr_id, new_attr_id}.
            image: side bar image.

        """

        old_item_id = dict_id.get("old_focus_item")

        # save image into path
        image.save_to_path(os.path.join("Assets", str(old_item_id) + ".png"))
                
    def show_markdown(self, dict_id: dict):
        new_item_id = dict_id.get("new_focus_item")
        if self.database_connect and new_item_id != 0:
            database_cursor = self.database_connect.cursor()
            markdown_line = database_cursor.execute('''
                SELECT markdown_text
                from markdown
                where id=?
            ''', (new_item_id,)).fetchone()
            if markdown_line:
                markdown_text = markdown_line[0]
            else:
                markdown_text = ""
            database_cursor.close()
            self.database_connect.commit()

            self.window.markdown_document.change_js_markdown_signal.emit(markdown_text)

            if constants.DEBUG_MARKDOWN:
                print(f"Read 2.show_markdown->{markdown_text}")
    
    def show_image(self, dict_id: dict):
        new_item_id = dict_id.get("new_focus_item")
            
        if not os.path.exists(os.path.join(constants.work_dir, os.path.join("Assets", str(new_item_id) + ".png"))):
            self.window.side_draw.canvas_item = draw.Canvas(300, 900, QtCore.Qt.transparent)
        else:
            self.window.side_draw.canvas_item.load_from_path(os.path.join("Assets", str(new_item_id) + ".png"))

        self.window.side_draw.change_width(self.window.side_draw.canvas_item.width(), self.window.side_draw.canvas_item.height())
        self.window.side_draw.update()

    def auto_save(self):
        """
        Save .note and backup .note

        """

        if self.current_file:
            self.save_to_file(self.current_file)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.current_file:
            Todo.close_flag = True
            self.save_to_file(self.current_file)
        if self.database_connect:
            self.database_connect.commit()
            self.database_connect.close()
        return super().closeEvent(a0)
    
    def copy_file(self, src_path, des_path):
        if src_path != des_path:
            try:
                shutil.copyfile(src_path, des_path)
            except Exception as e:
                QtWidgets.QErrorMessage(self).showMessage(f"Wrong:\n{e}")

