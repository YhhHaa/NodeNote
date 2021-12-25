from PyQt5 import QtCore

from ..Model.constants import DEBUG_MARKDOWN


class MarkdownDocument(QtCore.QObject):
    text_changed_signal = QtCore.pyqtSignal(dict, str)
    change_js_markdown_signal = QtCore.pyqtSignal(str)

    def __init__(self, page, parent=None) -> None:
        super().__init__(parent=parent)
        self.page = page

    @QtCore.pyqtSlot(dict)
    def emit_save_flag(self, dict_id):
        if DEBUG_MARKDOWN:
            print(f"2 MarkdownDocument told js to return dict_id:{dict_id} and markdown text.")
        self.page.runJavaScript(f"returnText({dict_id});")
    
    @QtCore.pyqtSlot("QJsonObject", str)
    def save_text(self, dict_id: "QtCore.QJsonObject", text: str):
        dict_id["old_focus_item"] = int(dict_id["old_focus_item"].toDouble())
        dict_id["new_focus_item"] = int(dict_id["new_focus_item"].toDouble())

        if DEBUG_MARKDOWN:
            print(f"3 MarkdownDocument receive dict_id{dict_id} and {text} from js and send them to view")

        self.text_changed_signal.emit(dict_id, text)
