"""
Stylesheet ui.
"""

import os


STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border: 2px solid rgba(0, 0, 0, 255);
    margin-top: 1px;
    padding-top: $PADDING_TOP;
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
    color: rgba(255, 255, 255, 150);
    background: rgba(10, 10, 10, 80);
}
QComboBox:!editable,
QComboBox::drop-down:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(80, 80, 80, 80);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: rgba(150, 150, 150, 150);
}
QComboBox::drop-down {
    background: rgba(80, 80, 80, 80);
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
}''' % os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/down_arrow.png")).replace('\\', r'/')

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
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/True.png")).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/False.png")).replace('\\', r'/')
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
                    background: #32CC99;
                    height: 8px;
                    margin: 0px 20px 0 20px;
                }
                QScrollBar::handle:horizontal {
                    background: rgba(204, 255, 255, 200);
                    min-width: 20px;
                }
                QScrollBar::add-line:horizontal {
                    border: 2px solid grey;
                    background: #32CC99;
                    width: 20px;
                    subcontrol-position: right;
                    subcontrol-origin: margin;
                }
                
                QScrollBar::sub-line:horizontal {
                    border: 2px solid grey;
                    background: #32CC99;
                    width: 20px;
                    subcontrol-position: left;
                    subcontrol-origin: margin;
                }
'''

STYLE_VSCROLLBAR = '''
             QScrollBar:vertical {
                 border: 2px solid grey;
                 background: #32CC99;
                 width: 8px;
                 margin: 22px 0 22px 0;
             }
             QScrollBar::handle:vertical {
                 background: rgba(204, 255, 255, 200);
                 min-height: 20px;
             }
             QScrollBar::add-line:vertical {
                 border: 2px solid grey;
                 background: #32CC99;
                 height: 20px;
                 subcontrol-position: bottom;
                 subcontrol-origin: margin;
             }
            
             QScrollBar::sub-line:vertical {
                 border: 2px solid grey;
                 background: #32CC99;
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

STYLE_QTOOLBAR = '''
QToolBar {
    background: rgba(204, 255, 255, 100);
    spacing: 3px;
}

QToolBar::handle {
    image: url(%s);
}
''' % os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/Flowers.png")).replace('\\', r'/')

STYLE_QTREEWIDGET = '''
QTreeWidget {
    alternate-background-color: yellow;
    background-color: rgba(204, 255, 255, 100);
}

QTreeWidget {
    show-decoration-selected: 1;
}

QTreeWidget::item {
     border: 1px solid #d9d9d9;
    border-top-color: transparent;
    border-bottom-color: transparent;
}

QTreeWidget::item:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);
    border: 1px solid #bfcde4;
}

QTreeWidget::item:selected {
    border: 1px solid #567dbc;
}

QTreeWidget::item:selected:active{
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
}

QTreeWidget::item:selected:!active {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);
}

QTreeWidget::branch {
        background: palette(base);
}

QTreeWidget::branch:has-siblings:!adjoins-item {
        background: cyan;
}

QTreeWidget::branch:has-siblings:adjoins-item {
        background: red;
}

QTreeWidget::branch:!has-children:!has-siblings:adjoins-item {
        background: blue;
}

QTreeWidget::branch:closed:has-children:has-siblings {
        background: pink;
}

QTreeWidget::branch:has-children:!has-siblings:closed {
        background: gray;
}

QTreeWidget::branch:open:has-children:has-siblings {
        background: magenta;
}

QTreeWidget::branch:open:has-children:!has-siblings {
        background: green;
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
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/stylesheet-vline.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/stylesheet-branch-more.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/stylesheet-branch-end.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/stylesheet-branch-closed.png")
                    ).replace('\\', r'/'),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/stylesheet-branch-open.png")
                    ).replace('\\', r'/')
)

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
    background-color: rgba(26, 255, 255, 100);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 8px;
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
    font: bold 12px;
    padding: 6px;
}
'''

STYLE_QLABEL_CHANGED = '''
QLabel {
    background-color: rgba(255, 204, 0, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 8px;
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
    font: bold 8px;
    padding: 6px;
}
'''


STYLE_QLABEL_TITLE = '''
QLabel {
    background-color: rgba(51, 102, 153, 200);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    font: bold 8px;
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
    font: bold 16px;
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
    font: bold 8px;
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


