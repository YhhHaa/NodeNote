"""
Stylesheet ui.
"""

import os

STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    margin-top: 1px;
    padding-top: 10px;
    padding-bottom: 2px;
    padding-left: 5px;
    padding-right: 5px;
    font-size: 8pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(0, 0, 0, 180);
    padding: 0px;
    left:-4px;
}
'''


STYLE_QCOMBOBOX = '''
QComboBox {
    color: white;
    font: 20px;
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 4px;
    padding-right: 4px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 255, 255, 80);
}
QComboBox:editable {
    background: white;
}
QComboBox:!editable, QComboBox::drop-down:editable {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                 stop: 0 #005AA7, stop: 1.0 #FFFDE4);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #C6FFDD, stop: 0.4 #FBD786, stop: 1.0 #f7797d);
}
QComboBox::drop-down {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #C6FFDD, stop: 0.4 #FBD786, stop: 1.0 #f7797d);
    border-left: 1px solid rgba(80, 80, 80, 255);
    width: 20px;
}
QComboBox::down-arrow {
    image: url(%s);
}
QComboBox::down-arrow:on {
    /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}''' % os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/down_arrow.png")).replace('\\', r'/')

STYLE_QCOMBOBOX_LOGIC = '''
QComboBox {
    color: white;
    font: 12px;
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 4px;
    padding-right: 4px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 255, 255, 80);
}
QComboBox:editable {
    background: white;
}
QComboBox:!editable, QComboBox::drop-down:editable {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                 stop: 0 #005AA7, stop: 1.0 #FFFDE4);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #C6FFDD, stop: 0.4 #FBD786, stop: 1.0 #f7797d);
}
QComboBox::drop-down {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #C6FFDD, stop: 0.4 #FBD786, stop: 1.0 #f7797d);
    border-left: 1px solid rgba(80, 80, 80, 255);
    width: 20px;
}
QComboBox::down-arrow {
    image: url(%s);
}
QComboBox::down-arrow:on {
    /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}''' % os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/down_arrow.png")).replace('\\', r'/')

STYLE_QLISTVIEW = '''
QListView {
    background: rgba(80, 80, 80, 255);
    border: 0px solid rgba(0, 0, 0, 0);
}
QListView::item {
    color: rgba(255, 255, 255, 120);
    background: rgba(60, 60, 60, 255);
    border-bottom: 1px solid rgba(0, 0, 0, 0);
    border-radius: 0px;
    margin: 0px;
    padding: 2px;
}
QListView::item:selected {
    color: rgba(98, 68, 10, 255);
    background: rgba(219, 158, 0, 255);
    border-bottom: 1px solid rgba(255, 255, 255, 5);
    border-radius: 0px;
    margin:0px;
    padding: 2px;
}
'''

STYLE_QDOUBLESPINBOX = '''
QDoubleSpinBox {
    color: black;
    selection-background-color: black;
    border: 2px solid blue;
    border-radius: 5px;
    padding-left: 2px;
    padding-top: 2px;
}
'''

STYLE_QCHECKBOX = '''
QCheckBox {
    color: rgba(0, 0, 0, 255);
    background-color: transparent;
    font-size: 12px;
    spacing: 5px 5px;
    padding-top: 8px;
    padding-bottom: 0px;
    height: 8px;
}
QCheckBox::indicator {
    width: 12px;
    height: 12px;
}
QCheckBox::indicator:checked {
image: url(%s);
}
QCheckBox::indicator:unchecked {
image: url(%s);
}
''' % (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/True.png")).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/False.png")).replace('\\', r'/')
)

STYLE_QTEXTEDIT = '''
QTextEdit {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 5px;
    color: rgba(255, 255, 255, 150);
    background: rgba(0, 0, 0, 80);
    selection-background-color: rgba(255, 198, 10, 155);
}
'''

STYLE_QMENU = '''
QMenu {
    background-color: rgba(153, 230, 255, 128); /* sets background of the menu */
    border: 1px solid black;
}
QMenu::item {
    background-color: transparent;
}
QMenu::item:selected {
    background-color: rgba(0, 115, 153, 255);
}
'''

STYLE_HSCROLLBAR = '''
                QScrollBar:horizontal {
                    border: 2px solid grey;
                    background: #FFC6BF;
                    height: 8px;
                    margin: 0px 20px 0 20px;
                }
                QScrollBar::handle:horizontal {
                    background: #FF7FAE;
                    min-width: 20px;
                }
                QScrollBar::add-line:horizontal {
                    border: 2px solid grey;
                    background: #8333E9;
                    width: 20px;
                    subcontrol-position: right;
                    subcontrol-origin: margin;
                }
                
                QScrollBar::sub-line:horizontal {
                    border: 2px solid grey;
                    background: #8333E9;
                    width: 20px;
                    subcontrol-position: left;
                    subcontrol-origin: margin;
                }

                QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                 border: 2px solid grey;
                 width: 3px;
                 height: 3px;
                 background: white;
             }
'''

STYLE_VSCROLLBAR = '''
             QScrollBar:vertical {
                 border: 2px solid grey;
                 background: #FFC6BF;
                 width: 8px;
                 margin: 22px 0 22px 0;
             }
             QScrollBar::handle:vertical {
                 background: #FF7FAE;
                 min-height: 20px;
             }
             QScrollBar::add-line:vertical {
                 border: 2px solid grey;
                 background: #8333E9;
                 height: 20px;
                 subcontrol-position: bottom;
                 subcontrol-origin: margin;
             }
            
             QScrollBar::sub-line:vertical {
                 border: 2px solid grey;
                 background: #8333E9;
                 height: 20px;
                 subcontrol-position: top;
                 subcontrol-origin: margin;
             }
             QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                 border: 2px solid grey;
                 width: 3px;
                 height: 3px;
                 background: white;
             }
            
             QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                 background: none;
             }
'''

STYLE_QMAINWIDNOW = '''
QMainWindow {
    background-color: rgba(255, 192, 241, 255);
    margin: 2px;
    spacing: 3px;
}
QMainWindow::separator {
    background: yellow;
    width: 10px;
    height: 10px;
}

QMainWindow::separator:hover {
    background: red;
}
'''

STYLE_QTOOLBAR = '''
QToolBar {
    background-color: rgba(246, 237, 170, 255);
    margin: 2px;
    padding: 2px;
    border: 5px solid rgba(253, 248, 147, 255);
    /* border-radius: 25px; */
    spacing: 3px;
}

QToolBar::handle {
    image: url(%s);
    spacing: 3px;
}
''' % os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/horse.png")).replace('\\', r'/')

STYLE_QTABWIDGET = '''
QTabWidget::pane {
    border: 4px solid rgba(254, 210, 190, 255);
    border-radius: 10px;
}

QTabWidget::tab-bar {
    left: 10px;
}

QTabBar::tab {
    border: 2px solid #FCA53C;
    border-bottom-color: rgba(254, 210, 190, 255); /* same as the pane color */
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    min-width: 8ex;
    padding: 2px;
    border-radius: 15px;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0.8, y2: 1,
                                stop: 0 #FFD2B6, stop: 0.4 #FCA52C,
                                stop: 0.2 #FEFBC8, stop: 1.0 #F6EDAB);
}

QTabBar::tab:selected {
    border-color: rgba(255, 192, 241, 255);
    border-bottom-color: rgba(254, 210, 190, 255); /* same as pane color */
}

QTabBar::tab:!selected {
    margin-top: 2px; /* make non-selected tabs look smaller */
}
'''

STYLE_SCENE_THUMBNAILS = '''
QWidget {
    background-color: #F6EDAB;
    boder: 2px solid #F6EDAB;
    border-radius: 6px;
}
'''

STYLE_QTREEWIDGET = '''
QTreeWidget {
    alternate-background-color: rgba(240, 251, 158, 180);
    background-color: rgba(245, 250, 199, 255);
    show-decoration-selected: 1;
}

QTreeWidget::item {
    border: 1px solid #FCD554;
    border-top-color: transparent;
    border-bottom-color: transparent;

}

QTreeWidget::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0.8, y2: 1,
                                stop: 0 #FFD2B6, stop: 0.4 #FCA52C,
                                stop: 0.2 #FEFBC8, stop: 1.0 #F6EDAB);
    border: 1px solid #bfcde4;
}

QTreeWidget::item:selected {
    border: 1px solid #567dbc;
    background: qlineargradient(x1: 0, y1: 0, x2: 0.8, y2: 1,
                                stop: 0 #F29627, stop: 0.4 #FCA52C,
                                stop: 0.2 #FEFBC8, stop: 1.0 #F6EDAB);
}

QTreeWidget::item:selected:active{
    background: qlineargradient(x1: 0, y1: 0, x2: 0.8, y2: 1,
                                stop: 0 #F0FB9E, stop: 0.4 #E6C1BD,
                                stop: 0.2 #FCD554, stop: 1.0 #FFD2B6);
}

QTreeWidget::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
}

QTreeWidget::branch {
        background: #FFD2B6;
}

QTreeWidget::branch:has-siblings:!adjoins-item {
        background: #E2D14E;
}

QTreeWidget::branch:has-siblings:adjoins-item {
        background: #76B8B6;
}

QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
        background: #B9D644;
}

QTreeWidget::branch:closed:has-children:has-siblings {
        background: #FCD554;
}

QTreeWidget::branch:has-children:!has-siblings:closed {
        background: #DAC3A4;
}

QTreeWidget::branch:open:has-children:has-siblings {
        background: #E0EEB3;
}

QTreeWidget::branch:open:has-children:!has-siblings {
        background: #949D6F;
}
QTreeWidget::branch:has-siblings:!adjoins-item {
    border-image: url(%s) 0;
}

QTreeWidget::branch:has-siblings:adjoins-item {
    border-image: url(%s) 0;
}

QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
    border-image: url(%s) 0;
}

QTreeWidget::branch:has-children:!has-siblings:closed,
QTreeWidget::branch:closed:has-children:has-siblings {
        border-image: none;
        image: url(%s);
}

QTreeWidget::branch:open:has-children:!has-siblings,
QTreeWidget::branch:open:has-children:has-siblings  {
        border-image: none;
        image: url(%s);
}
''' % (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/stylesheet-vline.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/stylesheet-branch-more.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/stylesheet-branch-end.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/stylesheet-branch-closed.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Resources/stylesheet-branch-open.png")
                    ).replace('\\', r'/')
)

STYLE_QLABEL_THUMBNAILS = '''
QLabel {
    border-style: ridge;
    border-width: 4px;
    border-radius: 2px;
    border-color: rgba(255, 153, 153, 255);
}
'''

STYLE_QTOOLBUTTON = '''
QToolButton {
    background-color: rgba(26, 255, 255, 100);
    border-style: outset;
    border-width: 1px;
    border-radius: 0px;
    border-color: beige;
    font: bold 8px;
    padding: 6px;
}

QToolButton:pressed {
    background-color: rgb(224, 0, 0);
    border-style: inset;
}
'''

STYLE_QPUSHBUTTON = '''
QPushButton {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #C6FFDD, stop: 0.4 #FBD786, stop: 1.0 #f7797d);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}

QPushButton:pressed {
    background-color: rgb(224, 0, 0);
    border-style: inset;
}
'''

STYLE_QLABEL = '''
QLabel {
    background-color: rgba(200, 200, 200, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 0px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}
'''

STYLE_QLABEL_CHANGED = '''
QLabel {
    background-color: rgba(255, 204, 0, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 1px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}
'''

STYLE_QLABEL_COMMON = '''
QLabel {
    background-color: rgba(153, 0, 255, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}
'''


STYLE_QLABEL_TITLE = '''
QLabel {
    color: white;
    background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                stop: 0 #2980B9, stop: 0.4 #6DD5FA, stop: 1.0 #FFFFFF);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 14px italic large;
    padding: 6px;
}
'''

STYLE_QLABEL_TITLE_TIME = '''
QLabel {
    background-color: rgba(51, 102, 153, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}
'''


STYLE_QLABEL_FILE = '''
QLabel {
    background-color: rgba(200, 200, 200, 100);
    border-style: outset;
    border-width: 1px;
    border-radius: 5px;
    border-color: beige;
    font: bold 12px italic large;
    padding: 6px;
}
'''


STYLE_QLINEEDIT = '''
QLineEdit {
    border: 2px solid gray;
    border-radius: 0px;
    padding: 0 8px;
    background: beige;
    selection-background-color: darkgray;
}
'''


