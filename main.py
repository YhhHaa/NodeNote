import sys

from Components.window import NoteWindow
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QEvent, QObject


class TabletApplication(QApplication):
    def __init__(self, argv):
        super(TabletApplication, self).__init__(argv)
        self._window = None

    def event(self, a0: QEvent) -> bool:
        if self._window:
            if a0.type() in (QEvent.TabletEnterProximity, QEvent.TabletLeaveProximity):
                self._window.view_widget.tabletEvent(a0)
                self._window.view_widget.tablet_used = a0.type() == QEvent.TabletEnterProximity

                if a0.type() == QEvent.TabletLeaveProximity:
                    self._window.view_widget.history.store_history("Create Container")
                    if self._window.view_widget.filename and not self._window.view_widget.first_open:
                        self._window.view_widget.save_to_file()

                return True
        return super(TabletApplication, self).event(a0)


if __name__ == '__main__':
    app = TabletApplication([])

    # slash
    splash = QSplashScreen(QPixmap("Resources/splash.jpg"))
    splash.showMessage("start loading", Qt.AlignCenter | Qt.AlignBottom, Qt.white)
    splash.setFont(QFont("New York Large", 10))
    splash.show()
    app.processEvents()

    # main
    window = NoteWindow(sys.argv)
    window.load_data(splash)
    window.show()
    splash.finish(window)
    splash.deleteLater()

    app._window = window
    app.exec_()
