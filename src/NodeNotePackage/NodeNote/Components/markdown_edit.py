from PyQt5 import QtCore, QtWebEngineWidgets, QtGui

from ..Model.constants import DEBUG_MARKDOWN


class MarkdownView(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, mainwindow, parent=None) -> None:
        super().__init__(parent=parent)
        self.mainwindow = mainwindow
        self.dict_id = dict()

    def set_id(self, dict_id):
        self.dict_id = dict_id


class MarkdownDocument(QtCore.QObject):
    save_text_signal = QtCore.pyqtSignal(dict, str)
    change_js_markdown_signal = QtCore.pyqtSignal(str)

    def __init__(self, page, parent=None) -> None:
        super().__init__(parent=parent)
        self.page = page

    @QtCore.pyqtSlot(dict)
    def return_text(self, dict_id):
        self.page.runJavaScript(f"returnText({dict_id});")
    
    @QtCore.pyqtSlot("QJsonObject", str)
    def save_text(self, dict_id: "QtCore.QJsonObject", text: str):
        if "old_focus_item" in dict_id.keys() and "new_focus_item" in dict_id.keys():
            dict_id["old_focus_item"] = int(dict_id["old_focus_item"].toDouble())
            dict_id["new_focus_item"] = int(dict_id["new_focus_item"].toDouble())

            if DEBUG_MARKDOWN:
                print(f"Write 2.show_text->{dict_id}, {text}")

            self.save_text_signal.emit(dict_id, text)
