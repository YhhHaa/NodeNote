# -*- coding: utf-8 -*-
"""
Example.py -  run the application
Copyright 2021 ye tao
Distributed under MPL-2.0 license. See LICENSE for more information

# v2.7.4:
## Debug:
- Restore the scene rect.
- Delete pipes correctly.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../../../../")))
sys.path.insert(0, os.path.abspath(os.path.join(__file__, "../../../")))


from src.NodeNotePackage.NodeNote.Components.window import NoteWindow
from src.NodeNotePackage.NodeNote.GraphicsView.app import TabletApplication
from PyQt5.QtWidgets import QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, qInstallMessageHandler, QTranslator, QLocale


def message_output(msg_type, context, msg):
    try:
        if msg_type >= 2:
            with open("exception_log.txt", "a", encoding="utf-8") as log:
                log.write(f"{msg},{msg_type} from {context.file},{context.function},{context.line}\n")
    except Exception as e:
        pass


if __name__ == '__main__':
    qInstallMessageHandler(message_output)

    app = TabletApplication([])

    # load language
    local = QLocale()
    lan = QLocale.language(local)
    trans = QTranslator()
    if lan == QLocale.Chinese:
        trans.load("../NodeNote/src/NodeNotePackage/NodeNote\Model/MultiLanguages/zh_CN")
        app.installTranslator(trans)

    # slash
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        splash = QSplashScreen(QPixmap(os.path.join(os.path.dirname(__file__),
                                                    "../NodeNote/src/NodeNotePackage/NodeNote/Resources/splash.jpg")))
    else:
        splash = QSplashScreen(QPixmap(os.path.join(os.path.dirname(__file__),
                                                    "../NodeNote/Resources/splash.jpg")))
    splash.showMessage("start loading", Qt.AlignCenter | Qt.AlignBottom, Qt.white)
    splash.setFont(QFont("New York Large", 10))
    splash.show()
    app.processEvents()

    # main
    window = NoteWindow(sys.argv, app, trans)
    window.load_data(splash)
    window.show()
    splash.finish(window)
    splash.deleteLater()

    app.exec_()
