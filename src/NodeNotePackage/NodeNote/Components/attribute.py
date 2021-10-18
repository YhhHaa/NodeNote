"""
attribute.py - Create many components which can be used in the scene.
"""

import re
import os
import io
import time
import validators
import matplotlib.pyplot as plt
from PIL import Image, ImageOps, ImageQt
import numpy as np
from PyQt5 import QtCore, QtWidgets, QtGui, sip
from ..Model import constants, stylesheet, serializable
from ..Components import port, pipe

__all__ = ["InputTextField", "SimpleTextField",
           "LogicWidget", "AttributeWidget", "AttributeFile"]


class SizeDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        """
        Used to change the image size in a InputTextField.

        Args:
            parent: Parent item.
        """

        super(SizeDialog, self).__init__(parent)
        self.resize(100, 80)
        self.setWindowTitle("Set Image Width and Height")
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                    "../Resources/Plane.png"))))
        self.num_width = QtWidgets.QLineEdit(parent=self)
        self.num_width.setValidator(QtGui.QDoubleValidator())
        self.num_height = QtWidgets.QLineEdit(parent=self)
        self.num_height.setValidator(QtGui.QDoubleValidator())
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel("Width: ", parent=self), 0, 0, 1, 1)
        grid.addWidget(QtWidgets.QLabel("Height: ", parent=self), 1, 0, 1, 1)
        grid.addWidget(self.num_width, 0, 1, 1, 1)
        grid.addWidget(self.num_height, 1, 1, 1, 1)

        button_box = QtWidgets.QDialogButtonBox(parent=self)
        button_box.setOrientation(QtCore.Qt.Horizontal)
        button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel |
                                      QtWidgets.QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(grid)
        spacerItem = QtWidgets.QSpacerItem(20, 48, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addItem(spacerItem)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Close Message',
                                               "Are you sure to quit?", QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def format(color, style=''):
    """Return a QTextCharFormat with the given attributes.
    """
    _color = QtGui.QColor()
    _color.setNamedColor(color)

    _format = QtGui.QTextCharFormat()
    _format.setForeground(_color)
    if 'bold' in style:
        _format.setFontWeight(QtGui.QFont.Bold)
    if 'italic' in style:
        _format.setFontItalic(True)

    return _format


# Syntax styles that can be shared by all languages
STYLES = {
    'keyword': format('blue'),
    'operator': format('red'),
    'brace': format('black'),
    'defclass': format('black', 'bold'),
    'string': format('magenta'),
    'string2': format('darkMagenta'),
    'comment': format('darkGreen', 'italic'),
    'self': format('black', 'italic'),
    'numbers': format('brown'),
}


class PythonHighlighter(QtGui.QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'and', 'assert', 'break', 'class', 'continue', 'def',
        'del', 'elif', 'else', 'except', 'exec', 'finally',
        'for', 'from', 'global', 'if', 'import', 'in',
        'is', 'lambda', 'not', 'or', 'pass', 'print',
        'raise', 'return', 'try', 'while', 'yield',
        'None', 'True', 'False',
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]

    def __init__(self, document):
        QtGui.QSyntaxHighlighter.__init__(self, document)

        self.tri_single = (QtCore.QRegExp("'''"), 1, STYLES['string2'])
        self.tri_double = (QtCore.QRegExp('"""'), 2, STYLES['string2'])

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, STYLES['keyword'])
                  for w in PythonHighlighter.keywords]
        rules += [(r'%s' % o, 0, STYLES['operator'])
                  for o in PythonHighlighter.operators]
        rules += [(r'%s' % b, 0, STYLES['brace'])
                  for b in PythonHighlighter.braces]

        # All other rules
        rules += [
            # 'self'
            (r'\bself\b', 0, STYLES['self']),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, STYLES['string']),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, STYLES['string']),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, STYLES['defclass']),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, STYLES['defclass']),

            # From '#' until a newline
            (r'#[^\n]*', 0, STYLES['comment']),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, STYLES['numbers']),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0, STYLES['numbers']),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QtCore.QRegExp(pat), index, fmt)
                      for (pat, index, fmt) in rules]

    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, font_format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, font_format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            self.match_multiline(text, *self.tri_double)

    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False


class SimpleTextField(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, parent):
        """
        Simple text field.

        Args:
            text: The default text.
            parent: Parent item.
        """

        super(SimpleTextField, self).__init__(text, parent)
        self.setFlags(QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges | QtWidgets.QGraphicsWidget.ItemIsSelectable)

    def mouseDoubleClickEvent(self, event) -> None:
        super(SimpleTextField, self).mouseDoubleClickEvent(event)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIsFocusable, True)
        self.setFocus()
        if not self.hasFocus():
            activate = QtCore.QEvent(QtCore.QEvent.WindowActivate)
            self.scene().view.mainwindow.app.sendEvent(self.scene(), activate)
            self.setFocus(QtCore.Qt.MouseFocusReason)

    def mousePressEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        self.parentItem().mousePressEvent(event)

    def focusInEvent(self, event) -> None:
        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        super(SimpleTextField, self).focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textCursor().clearSelection()
        super(SimpleTextField, self).focusOutEvent(event)


class InputTextField(QtWidgets.QGraphicsTextItem):
    edit_finished = QtCore.pyqtSignal(bool)
    start_editing = QtCore.pyqtSignal()

    font = QtGui.QFont("等距更纱黑体 SC", 8)
    font_color = QtGui.QColor(0, 0, 0, 255)

    def __init__(self, text, node, parent=None, single_line=False):
        """
        Complex text field.

        Args:
            text: The default text.
            node: The attribute widget that contains it self.
            parent: Parent item.
            single_line: Whether the user can change line.
        """

        super(InputTextField, self).__init__(text, parent)
        # input
        self.past_scene = None
        self.last_pos = QtCore.QPointF()
        self.setZValue(constants.Z_VAL_NODE + 1)
        # BASIC SETTINGS
        self.setFlags(QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges | QtWidgets.QGraphicsWidget.ItemIsSelectable)
        self.setOpenExternalLinks(True)
        self.setObjectName("Nothing")
        self.node = node
        self.single_line = single_line
        self.text_before_editing = ""
        self.origMoveEvent = self.mouseMoveEvent
        self.mouseMoveEvent = self.node.mouseMoveEvent
        # DOCUMNET SETTINGS
        self.document().setMetaInformation(QtGui.QTextDocument.DocumentUrl, r"Assets/")
        self.setDefaultTextColor(self.font_color)
        self.document().setIndentWidth(4)
        self.document().setDefaultFont(self.font)
        self.pythonlighter = None
        self.editing_state = False
        self.linkActivated.connect(self.hyper_link)
        self.font_size_editing = True
        # style
        self.font_flag = False
        self.font_color_flag = False
        self.resize_flag = True

    def paint(self, painter: QtGui.QPainter, option, widget=None) -> None:
        super(InputTextField, self).paint(painter, option, widget)
        if self.scene() and self.scene().attribute_style_font and not self.font_flag:
            self.document().setDefaultFont(self.scene().attribute_style_font)
            if self.resize_flag:
                if constants.DEBUG_FONT:
                    print("resize node size case the change of it's font")
                self.node.text_change_node_shape()
                self.node.resize(20, 10)
                self.resize_flag = False
        if self.scene() and self.scene().attribute_style_font_color and not self.font_color_flag:
            self.setDefaultTextColor(self.scene().attribute_style_font_color)

    @staticmethod
    def add_table(cursor):
        """
        Add table.

        Args:
            cursor: Text cursor.

        """

        # create parameters
        table_format = QtGui.QTextTableFormat()

        # set and insert
        table_format.setCellPadding(10)
        table_format.setCellSpacing(2)
        table_format.setAlignment(QtCore.Qt.AlignCenter)
        table_format.setBackground(QtGui.QBrush(QtGui.QColor(229, 255, 255, 255)))
        cursor.insertTable(1, 1, table_format)

    @staticmethod
    def table_insert_column(table, cursor):
        """
        Insert column in a table.

        Args:
            table: The used table.
            cursor: Text cursor.

        """

        column = table.cellAt(cursor).column() + 1
        table.insertColumns(column, 1)

    @staticmethod
    def table_insert_row(table, cursor):
        """
        Insert row in table.

        Args:
            table: The used table.
            cursor: Text cursor.

        """

        row = table.cellAt(cursor).row() + 1
        table.insertRows(row, 1)

    @staticmethod
    def table_delete_column(table, cursor):
        """
        Delete the column in table.

        Args:
            table: The used table.
            cursor: Text cursor.

        """

        column = table.cellAt(cursor).column()
        table.removeColumns(column, 1)

    @staticmethod
    def table_delete_row(table, cursor):
        """
        Delete the row in table.

        Args:
            table: The used table.
            cursor: Text cursor.

        """

        row = table.cellAt(cursor).row()
        table.removeRows(row, 1)

    @staticmethod
    def add_list(cursor):
        """
        Add list in table.

        Args:
            cursor: Text cursor.

        """

        # create parameters
        list_format = QtGui.QTextListFormat()

        # set and insert
        list_format.setIndent(4)
        list_format.setStyle(QtGui.QTextListFormat.ListDecimal)
        cursor.insertList(list_format)

    def indent(self):
        """
        Insert a tab in text.

        """

        cursor = self.textCursor()
        if cursor.hasSelection():
            temp = cursor.blockNumber()
            cursor.setPosition(cursor.anchor())
            diff = cursor.blockNumber() - temp
            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
            for _ in range(abs(diff) + 1):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.insertText("    ")
                cursor.movePosition(direction)
        else:
            cursor.insertText("    ")

    def dedent(self):
        """
        Delete a tab in text.

        """

        cursor = self.textCursor()
        if cursor.hasSelection():
            temp = cursor.blockNumber()
            cursor.setPosition(cursor.anchor())
            diff = cursor.blockNumber() - temp
            direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
            for _ in range(abs(diff) + 1):
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                line = cursor.block().text()
                if line.startswith("    "):
                    for _ in range(4):
                        cursor.deleteChar()
                else:
                    for char in line[:4]:
                        if char != " ":
                            break
                        cursor.deleteChar()
                cursor.movePosition(direction)
        else:
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            line = cursor.block().text()
            if line.startswith("    "):
                for _ in range(4):
                    cursor.deleteChar()
            else:
                for char in line[:4]:
                    if char != " ":
                        break
                    cursor.deleteChar()

    def get_text_maxlength(self):
        """
        For all lines, get the longest line.

        Returns:
            maxlength: the longest line length.
        """

        document = self.document()
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start)
        root = document.rootFrame()
        it = root.begin()
        maxlength = 0
        while it != root.end():
            line_length = self.get_line_length(cursor)
            maxlength = maxlength if maxlength > line_length else line_length
            cursor.movePosition(QtGui.QTextCursor.Down)
            it += 1
        return maxlength

    @staticmethod
    def get_line_length(cursor):
        """
        Calculate the length of this line.

        Args:
            cursor: The text cursor.

        Returns:
            line_point: Line length.
        """

        if constants.DEBUG_RICHTEXT:
            print("cursor postion: ", cursor.position())
        line_type = list()
        for char in cursor.block().text():
            if '\u4e00' <= char <= '\u9fa5':
                line_type.append(1)
                if constants.DEBUG_RICHTEXT:
                    print("Chinese: ", char)
            else:
                line_type.append(0)

        line_position = 0
        line_point = 0
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        while not cursor.atBlockEnd():
            point_size = cursor.charFormat().fontPointSize()
            font_point_size = point_size if point_size != 0 else 8
            if line_type[line_position]:
                font_point_size = font_point_size * 2
            line_point += font_point_size
            line_position += 1
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, 1)
        return line_point

    def align(self, align):
        """
        Align left/right/center/none.

        Args:
            align: alignment.

        """

        max_length = self.get_text_maxlength()
        cursor = self.textCursor()
        if align == "Center":
            self.align("Clean")
            if cursor.hasSelection():
                temp = cursor.blockNumber()
                cursor.setPosition(cursor.anchor())
                diff = cursor.blockNumber() - temp
                direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
                for _ in range(abs(diff) + 1):
                    line_length = self.get_line_length(cursor)
                    blank_number = int(((max_length - line_length) // 2) // 8)
                    if constants.DEBUG_RICHTEXT:
                        print("max length, line length, blank number", max_length, line_length, blank_number)
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    cursor.insertText(" " * blank_number)
                    cursor.movePosition(QtGui.QTextCursor.EndOfLine)
                    cursor.insertText(" " * blank_number)
                    cursor.movePosition(direction)
                    self.setTextCursor(cursor)
            else:
                line_length = self.get_line_length(cursor)
                blank_number = int(((max_length - line_length) // 2) // 8)
                if constants.DEBUG_RICHTEXT:
                    print("max length, line length, blank number", max_length, line_length, blank_number)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                cursor.insertText(" " * blank_number)
                cursor.movePosition(QtGui.QTextCursor.EndOfLine)
                cursor.insertText(" " * blank_number)
                self.setTextCursor(cursor)
        elif align == "Left":
            self.align("Clean")
            if cursor.hasSelection():
                temp = cursor.blockNumber()
                cursor.setPosition(cursor.anchor())
                diff = cursor.blockNumber() - temp
                direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
                for _ in range(abs(diff) + 1):
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    line = cursor.block().text()
                    for char in line[:]:
                        if char != " ":
                            break
                        cursor.deleteChar()
                    cursor.movePosition(direction)
                    self.setTextCursor(cursor)
            else:
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                line = cursor.block().text()
                for char in line:
                    if char != " ":
                        break
                    cursor.deleteChar()
                self.setTextCursor(cursor)
        elif align == "Right":
            self.align("Clean")
            if cursor.hasSelection():
                temp = cursor.blockNumber()
                cursor.setPosition(cursor.anchor())
                diff = cursor.blockNumber() - temp
                direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
                for _ in range(abs(diff) + 1):
                    line_length = self.get_line_length(cursor)
                    blank_number = int((max_length - line_length) // 8)
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    for _ in range(blank_number):
                        cursor.insertText(" ")
                    cursor.movePosition(direction)
                    self.setTextCursor(cursor)
            else:
                line_length = self.get_line_length(cursor)
                blank_number = int((max_length - line_length) // 8)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                for _ in range(blank_number):
                    cursor.insertText(" ")
                self.setTextCursor(cursor)
        elif align == "Clean":
            if cursor.hasSelection():
                temp = cursor.blockNumber()
                cursor.setPosition(cursor.anchor())
                diff = cursor.blockNumber() - temp
                direction = QtGui.QTextCursor.Up if diff > 0 else QtGui.QTextCursor.Down
                for _ in range(abs(diff) + 1):
                    cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                    line = cursor.block().text()
                    for char in line:
                        if char != " ":
                            break
                        cursor.deleteChar()
                        if constants.DEBUG_RICHTEXT:
                            print("line: ", cursor.block().text(), len(cursor.block().text()))
                    index = len(line.strip())
                    if constants.DEBUG_RICHTEXT:
                        print("Before move: ", cursor.position(), index)
                    cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, index)
                    if constants.DEBUG_RICHTEXT:
                        print("After move: ", cursor.position(), index, line.lstrip()[index:])
                    for char in line.lstrip()[index:]:
                        if char != " ":
                            break
                        cursor.deleteChar()
                        if constants.DEBUG_RICHTEXT:
                            print("line: ", cursor.block().text(), len(cursor.block().text()))
                    cursor.movePosition(direction)
                    self.setTextCursor(cursor)
            else:
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                line = cursor.block().text()
                for char in line:
                    if char != " ":
                        break
                    cursor.deleteChar()
                    if constants.DEBUG_RICHTEXT:
                        print("line: ", cursor.block().text(), len(cursor.block().text()))
                index = len(line.strip())
                if constants.DEBUG_RICHTEXT:
                    print("Before move: ", cursor.position(), index)
                cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.MoveAnchor, index)
                if constants.DEBUG_RICHTEXT:
                    print("After move: ", cursor.position(), index, line.lstrip()[index:])
                for char in line.lstrip()[index:]:
                    if char != " ":
                        break
                    cursor.deleteChar()
                    if constants.DEBUG_RICHTEXT:
                        print("line: ", cursor.block().text(), len(cursor.block().text()))
                self.setTextCursor(cursor)

    @staticmethod
    def latex_formula(str_latex):
        """
        math formula image.

        Args:
            str_latex: The LaTeX like "$a_3$"

        Returns: The math formula image.

        """
        fig = plt.figure()
        t = plt.text(0.001, 0.001, str_latex, fontsize=50)

        fig.patch.set_facecolor('white')
        plt.axis('off')
        plt.tight_layout()

        with io.BytesIO() as png_buf:
            plt.savefig(png_buf, bbox_inches='tight', pad_inches=0)
            png_buf.seek(0)

            img = plt.imread(png_buf)
            im = img.mean(axis=2)
            im = ((im - im.min()) / (im.ptp() / 255.0)).astype(np.uint8)
            temp_img = QtGui.QImage(im, im.shape[1], im.shape[0], im.shape[1], QtGui.QImage.Format_Indexed8)

            image = QtGui.QPixmap(temp_img).toImage()
            size = image.size()
            image = image.scaled(size.width() * 0.5, size.height() * 0.5,
                                 QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

            image = Image.open(png_buf)
            image.load()
            inverted_image = ImageOps.invert(image.convert("RGB"))

            cropped = image.crop(inverted_image.getbbox())

            return ImageQt.ImageQt(cropped)

    @staticmethod
    def hyper_link(hyperlink):
        """
        Create hyper link.

        Args:
            hyperlink: The hyper link like "www.baidu.com"

        """

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.PointingHandCursor)
        try:
            validators.url(hyperlink)
            QtGui.QDesktopServices.openUrl(QtCore.QUrl(hyperlink))
        except Exception as e:
            print("Valid hyperlink: ", e)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)

    def font_format(self, font_type):
        """
        Complex text format.

        Args:
            font_type: Rich text format.

        """

        cursor = self.textCursor()
        text_format = QtGui.QTextCharFormat()
        if font_type == "Italic":
            if cursor.charFormat().fontItalic():
                text_format.setFontItalic(False)
            else:
                text_format.setFontItalic(True)
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Blod":
            if cursor.charFormat().fontWeight() == 50:
                text_format.setFontWeight(100)
            else:
                text_format.setFontWeight(50)
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Underline":
            if cursor.charFormat().fontUnderline():
                text_format.setFontUnderline(False)
            else:
                text_format.setFontUnderline(True)
                text_format.setUnderlineColor(QtGui.QColor(133, 255, 255))
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Deleteline":
            if cursor.charFormat().fontStrikeOut():
                text_format.setFontStrikeOut(False)
            else:
                text_format.setFontStrikeOut(True)
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Up":
            if constants.DEBUG_RICHTEXT:
                print("Font size: ", cursor.charFormat().fontPointSize())
            if cursor.charFormat().fontPointSize() == 0:
                font_point_size = 8
            else:
                font_point_size = cursor.charFormat().fontPointSize()
            point_size = font_point_size + 2
            text_format.setFontPointSize(point_size)
            cursor.mergeCharFormat(text_format)
            self.editing_state = True
            self.font_size_editing = True
        elif font_type == "Down":
            if constants.DEBUG_RICHTEXT:
                print("Font size: ", cursor.charFormat().fontPointSize())
            if cursor.charFormat().fontPointSize() == 0:
                font_point_size = 8
            else:
                font_point_size = cursor.charFormat().fontPointSize()
            point_size = font_point_size - 2 if font_point_size - 2 > 0 else 2
            text_format.setFontPointSize(point_size)
            cursor.mergeCharFormat(text_format)
            self.editing_state = True
            self.font_size_editing = True
        elif font_type == "Color":
            color = QtWidgets.QColorDialog.getColor(QtCore.Qt.red, None, "Select Color",
                                                    QtWidgets.QColorDialog.ShowAlphaChannel)
            if color:
                text_format.setForeground(color)
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Hyperlink":
            if not cursor.charFormat().isAnchor():
                text_format.setAnchor(True)
                text_format.setForeground(QtGui.QColor("Blue"))
                text_format.setAnchorHref(cursor.selection().toPlainText())
            else:
                text_format.setAnchor(False)
                text_format.setForeground(QtGui.QColor("Black"))
            cursor.mergeCharFormat(text_format)
            self.editing_state = False
        elif font_type == "Mathjax":
            str_latex = cursor.selection().toPlainText()
            if str_latex.startswith("$") and str_latex.endswith("$") and str_latex.count("$") == 2:
                image = self.latex_formula(str_latex)
                image_folder = "Assets"
                if not os.path.exists(image_folder):
                    os.makedirs(image_folder)
                image_name = os.path.join(image_folder, time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '.png')
                image.save(image_name, quality=50)
                cursor.clearSelection()
                cursor.insertText("\n")
                image_format = QtGui.QTextImageFormat()
                image_format.setName(image_name)
                cursor.insertImage(image_format)
                self.editing_state = False
        elif font_type == "Clear":
            cursor.setCharFormat(text_format)
            self.editing_state = False
        if not self.editing_state:
            cursor.movePosition(QtGui.QTextCursor.EndOfBlock)
            cursor.setCharFormat(QtGui.QTextCharFormat())
            self.setTextCursor(cursor)

    def image_format(self):
        """
        Change the size of the image.

        """

        cursor = self.textCursor()
        image_width = self.get_text_maxlength()
        image_height = 50
        if cursor.hasSelection():
            size_dialog = SizeDialog()
            text = cursor.selection().toHtml(bytes())
            if text.find(r'<img src=') != -1:
                cursor.removeSelectedText()
                if size_dialog.exec_():
                    image_width = size_dialog.num_width.text() if size_dialog.num_width.text() else image_width
                    image_height = size_dialog.num_height.text() if size_dialog.num_height.text() else image_height
                if constants.DEBUG_RICHTEXT:
                    print("image size: ", image_width, image_height)
                pattern = re.compile(r'<img src="(.+?)".+?/>')
                text = pattern.sub(r'<img src="\1" width="%s" height="%s" />' % (image_width, image_height), text)
                if constants.DEBUG_RICHTEXT:
                    print("*****************text***********************\n", text, "\n** \
                                                                                  ************************************")
                cursor.insertHtml(text)
            else:
                cursor.clearSelection()
                self.setTextCursor(cursor)

    def copy(self):
        """
        Ctrl C

        """

        text_cursor = self.textCursor()
        clipboard = QtWidgets.QApplication.clipboard()
        if text_cursor.hasSelection():
            mime_data = QtCore.QMimeData()
            html_data = text_cursor.selection().toHtml(bytes())
            mime_data.setHtml(html_data)
            if mime_data.hasUrls() or mime_data.hasImage():
                clipboard.setMimeData(mime_data)
            else:
                text_data = text_cursor.selection().toPlainText()
                mime_data.setText(text_data)
                clipboard.setMimeData(mime_data)

    @staticmethod
    def paste(cursor):
        """
        Ctrl V

        Args:
            cursor: The text cursor.

        """

        mime_data = QtWidgets.QApplication.clipboard().mimeData()
        if mime_data.hasImage():
            image = QtGui.QImage(mime_data.imageData())
            image_folder = "Assets"
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
            image_name = os.path.join(image_folder, time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '.png')
            image.save(image_name, quality=50)
            image_format = QtGui.QTextImageFormat()
            image_format.setName(image_name)
            cursor.insertImage(image_format)
        elif mime_data.hasUrls():
            for u in mime_data.urls():
                file_ext = os.path.splitext(str(u.toLocalFile()))[1].lower()
                if constants.DEBUG_RICHTEXT:
                    print(file_ext, u.isLocalFile())
                if u.isLocalFile() and file_ext in ('.jpg', '.png', '.bmp', '.icon', '.jpeg', 'gif'):
                    image = QtGui.QImage(u.toLocalFile())
                    image_name = u.toLocalFile()
                    url = u.url()
                    first_index = url.rindex('/')
                    second_index = url[:first_index].rindex('/')
                    if url[second_index + 1: first_index] != "Assets":
                        image_folder = "Assets"
                        if not os.path.exists(image_folder):
                            os.makedirs(image_folder)
                        image_name = os.path.join(
                            image_folder, time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime()) + '.png')
                        image.save(image_name, quality=50)
                    image_format = QtGui.QTextImageFormat()
                    image_format.setName(image_name)
                    cursor.insertImage(image_format)
                else:
                    text = mime_data.text()
                    cursor.insertText(text)

        elif mime_data.hasText():
            text = mime_data.text()
            cursor.insertText(text)
            if constants.DEBUG_RICHTEXT:
                print("PASTE: ", text)
        elif mime_data.hasHtml():
            cursor.insertHtml(mime_data.html())

    def keyPressEvent(self, event) -> None:
        # insert key text into text field.
        current_key = event.key()
        current_cursor = self.textCursor()

        # restore text before editing and return.
        if current_key == QtCore.Qt.Key_Escape:
            self.clearFocus()
            super(InputTextField, self).keyPressEvent(event)
            return
        elif current_key == QtCore.Qt.Key_BracketLeft and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("ALIGN LEFT")
            self.align("Left")
        elif current_key == QtCore.Qt.Key_BracketRight and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("ALIGN RIGHT")
            self.align("Right")
        elif current_key == QtCore.Qt.Key_Backslash and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("ALIGN CENTER")
            self.align("Center")
        elif current_key == QtCore.Qt.Key_P and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("ALIGN Clean")
            self.align("Clean")
        elif current_key == QtCore.Qt.Key_Q and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Italic")
        elif current_key == QtCore.Qt.Key_W and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Blod")
        elif current_key == QtCore.Qt.Key_R and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Underline")
        elif current_key == QtCore.Qt.Key_Slash and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Deleteline")
        elif current_key == QtCore.Qt.Key_G and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Up")
        elif current_key == QtCore.Qt.Key_H and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Down")
        elif current_key == QtCore.Qt.Key_N and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Color")
        elif current_key == QtCore.Qt.Key_M and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Hyperlink")
        elif current_key == QtCore.Qt.Key_I and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Mathjax")
        elif current_key == QtCore.Qt.Key_L and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Title")
            self.font_format("Clear")
        elif current_key == QtCore.Qt.Key_Z and event.modifiers() & QtCore.Qt.ControlModifier:
            self.document().undo()
            event.accept()
        elif current_key == QtCore.Qt.Key_Y and event.modifiers() & QtCore.Qt.ControlModifier:
            self.document().redo()
            event.accept()

        if self.single_line:
            if current_key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                if self.toPlainText() == "":
                    self.setHtml(self.text_before_editing)
                    event.ignore()
                    self.edit_finished.emit(False)
                    self.clearFocus()
                else:
                    event.ignore()
                    self.clearFocus()
            else:
                super(InputTextField, self).keyPressEvent(event)
        else:
            super(InputTextField, self).keyPressEvent(event)

        # table operation
        current_table = current_cursor.currentTable()
        if current_key == QtCore.Qt.Key_1 and event.modifiers() & QtCore.Qt.ControlModifier:
            self.add_table(current_cursor)
        if current_key == QtCore.Qt.Key_T and event.modifiers() & QtCore.Qt.ControlModifier and current_table:
            self.table_insert_column(current_table, current_cursor)
        if current_key == QtCore.Qt.Key_R and event.modifiers() & QtCore.Qt.ControlModifier and current_table:
            self.table_insert_row(current_table, current_cursor)
        if current_key == QtCore.Qt.Key_D and event.modifiers() & QtCore.Qt.ControlModifier and current_table:
            self.table_delete_column(current_table, current_cursor)
        if current_key == QtCore.Qt.Key_M and event.modifiers() & QtCore.Qt.ControlModifier and current_table:
            self.table_delete_row(current_table, current_cursor)

        # list operation
        if current_key == QtCore.Qt.Key_2 and event.modifiers() & QtCore.Qt.ControlModifier:
            self.add_list(current_cursor)

        # image
        if current_key == QtCore.Qt.Key_U and event.modifiers() & QtCore.Qt.ControlModifier:
            if constants.DEBUG_RICHTEXT:
                print("Rich Format: Image")
            self.image_format()

    def sceneEvent(self, event: QtCore.QEvent) -> bool:
        if event.type() == QtCore.QEvent.KeyPress:
            if event.matches(QtGui.QKeySequence.Paste):
                self.paste(self.textCursor())
                return False
            elif event.matches(QtGui.QKeySequence.Copy):
                self.copy()
                return False
            elif event.key() == QtCore.Qt.Key_Tab:
                if event.modifiers() == QtCore.Qt.ControlModifier:
                    if constants.DEBUG_RICHTEXT:
                        print("CTRL + TAB")
                    self.dedent()
                    return False
                else:
                    if constants.DEBUG_RICHTEXT:
                        print("TAB")
                    self.indent()
                    return False
            else:
                return super(InputTextField, self).sceneEvent(event)
        else:
            return super(InputTextField, self).sceneEvent(event)

    def mousePressEvent(self, event) -> None:
        # change focus into node
        if self.objectName() == "MouseLocked":
            super(InputTextField, self).mousePressEvent(event)
        else:
            self.node.mousePressEvent(event)
            self.clearFocus()

    def contextMenuEvent(self, event: 'QtWidgets.QGraphicsSceneContextMenuEvent') -> None:
        # not implementing, debug for right mouse clicked
        self.node.contextMenuEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.objectName() == "MouseLocked":
            super(InputTextField, self).mouseReleaseEvent(event)
        else:
            self.node.mouseReleaseEvent(event)
            self.clearFocus()

    def mouseDoubleClickEvent(self, event) -> None:
        # get focus
        super(InputTextField, self).mouseDoubleClickEvent(event)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemIsFocusable, True)
        self.editing_state = True
        self.start_editing.emit()
        self.setFocus(QtCore.Qt.MouseFocusReason)
        if not self.hasFocus():
            activate = QtCore.QEvent(QtCore.QEvent.WindowActivate)
            self.scene().view.mainwindow.app.sendEvent(self.scene(), activate)
            self.setFocus(QtCore.Qt.MouseFocusReason)

    def focusInEvent(self, event) -> None:
        # remove from past scene and added into root scene
        if not self.scene().view.root_flag:
            self.past_scene = self.node.scene()

            # calculate pos
            root_view = self.scene().view.mainwindow.view_widget
            node_subview_pos = self.scene().view.mapFromScene(self.scenePos())
            subview_pos = root_view.mapFromScene(self.scene().view.proxy_widget.scenePos())
            node_pos = node_subview_pos + subview_pos

            # remove from past scene
            for item in self.node.attribute_widget.childItems():
                item.setParentItem(None)
                item.setParent(None)

            # add into root scene
            self.node.attribute_widget.layout.removeAt(0)
            root_view.current_scene.addItem(self)
            self.setPos(root_view.mapToScene(node_pos))

        self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction | QtCore.Qt.LinksAccessibleByMouse)
        self.setObjectName("MouseLocked")
        self.text_before_editing = self.toHtml()
        self.mouseMoveEvent = self.origMoveEvent
        super(InputTextField, self).focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        if self.past_scene:
            # added into past scene
            self.past_scene.addItem(self)
            graphics_widget = QtWidgets.QGraphicsWidget()
            graphics_widget.setGraphicsItem(self)
            self.setParentItem(self.node.attribute_widget)
            self.setParent(self.node.attribute_widget)
            self.setPos(QtCore.QPointF())
            self.node.attribute_widget.layout.addItem(graphics_widget)

        super(InputTextField, self).focusOutEvent(event)
        self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.setObjectName("Nothing")
        self.editing_state = False
        if constants.DEBUG_RICHTEXT:
            print("Html contents:\n", self.toHtml())
        if not self.editing_state or self.font_size_editing:
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.font_size_editing = False
        self.mouseMoveEvent = self.node.mouseMoveEvent
        self.node.scene().history.store_history("Editing")


class SubConstituteWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, parent=None):
        """
        The manger for input text field.

        Args:
            parent: Parent item.
        """

        super(SubConstituteWidget, self).__init__(parent)
        # SET BASIC FUNCTION
        self.hovered = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)

        # LABEL ITEM
        self.label_item = InputTextField(self.parentItem().name, parent, self,
                                         single_line=False)
        self.label_item.setAcceptHoverEvents(True)
        self.label_item.document().contentsChanged.connect(self.parentItem().text_change_node_shape)
        self.label_item.document().contentsChanged.connect(self.parentItem().update_treelist)
        self.label_item.hoverMoveEvent = self.hoverMoveEvent
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.label_widget = QtWidgets.QGraphicsWidget()
        self.label_widget.setGraphicsItem(self.label_item)
        self.layout.addItem(self.label_widget)
        self.setLayout(self.layout)

    def contextMenuEvent(self, event: 'QtWidgets.QGraphicsSceneContextMenuEvent') -> None:
        self.parentItem().contextMenuEvent(event)

    def hoverEnterEvent(self, event) -> None:
        super(SubConstituteWidget, self).hoverEnterEvent(event)
        self.hovered = True
        self.update()

    def hoverMoveEvent(self, event) -> None:
        self.parentItem().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        super(SubConstituteWidget, self).hoverLeaveEvent(event)
        self.hovered = False
        self.update()

    def sizeHint(self, which=None, constraint=None) -> QtCore.QSizeF:
        width = self.label_item.boundingRect().width()
        height = self.label_item.boundingRect().height() + 2
        return QtCore.QSizeF(width, height)


class GroupWidget(QtWidgets.QGroupBox):
    def __init__(self, label, parent=None):
        """
        Component of logic widget.

        Args:
            label: The default text.
            parent: Parent item.

        """

        super(GroupWidget, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(4)
        self.setTitle(label)

    def setTitle(self, text):
        margin = (0, 0, 0, 0)
        padding_top = '14px'
        if text == '':
            margin = (0, 2, 0, 0)
            padding_top = '2px'
        style = stylesheet.STYLE_QGROUPBOX.replace('$PADDING_TOP', padding_top)
        self.layout().setContentsMargins(*margin)
        self.setStyleSheet(style)
        super(GroupWidget, self).setTitle(text)

    def add_node_widget(self, widget):
        self.layout().addWidget(widget)

    def get_node_widget(self):
        return self.layout().itemAt(0).widget()


class AbstractWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, parent=None):
        """
        The base class which can be resized.

        Args:
            parent: Parent item.
        """

        super(AbstractWidget, self).__init__(parent)
        self.resizing = False

    def mousePressEvent(self, event) -> None:
        if int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.resizing = True
            if constants.DEBUG_TUPLE_NODE_SCALE:
                print("Node is scaling!")
            self.setCursor(QtCore.Qt.SizeAllCursor)
        else:
            super(AbstractWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self.resizing:
            past_pos = self.scenePos()
            past_width = self.size().width()
            past_height = self.size().height()
            current_pos = self.mapToScene(event.pos())
            current_width = current_pos.x() - past_pos.x() if current_pos.x() >= past_pos.x() else past_width
            current_height = current_pos.y() - past_pos.y() if current_pos.y() >= past_pos.y() else past_height
            if current_width >= self.childItems()[0].widget().minimumSize().width() and \
                    current_height >= self.childItems()[0].widget().minimumSize().width():
                self.resize(current_width, current_height)
            if constants.DEBUG_TUPLE_NODE_SCALE:
                print("DEBUG TUPLE NODE SCALE CURRENT SIZE:", current_width, current_height)
        else:
            super(AbstractWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.resizing:
            self.resizing = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            super(AbstractWidget, self).mouseReleaseEvent(event)


class TruthWidget(QtWidgets.QGraphicsWidget):
    def __init__(self, truth=True, parent=None):
        """
        The component of the logic widget.

        Args:
            truth: Nor / and / or.
            parent: Parent item.
        """

        super(TruthWidget, self).__init__(parent)
        # new checkbox
        self.truth_checkbox = QtWidgets.QCheckBox("Truth")
        self.truth_checkbox.setChecked(truth)
        self.truth_checkbox.setStyleSheet(stylesheet.STYLE_QCHECKBOX)

        # set font
        font = self.truth_checkbox.font()
        font.setPointSize(8)
        self.truth_checkbox.setFont(font)

        # add into group
        proxywidget = QtWidgets.QGraphicsProxyWidget()
        proxywidget.setWidget(self.truth_checkbox)
        self.layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addItem(proxywidget)
        self.setLayout(self.layout)

    def sizeHint(self, which=None, constraint=None) -> QtCore.QSizeF:
        width = self.truth_checkbox.width() + 5
        height = self.truth_checkbox.height() + 5
        return QtCore.QSizeF(width, height)

    def boundingRect(self) -> QtCore.QRectF:
        return QtCore.QRectF(0, 0,
                             self.truth_checkbox.width() + 5,
                             self.truth_checkbox.height() + 5)

    def wheelEvent(self, event: 'QtWidgets.QGraphicsSceneWheelEvent') -> None:
        pass


class ComboBox(QtWidgets.QComboBox):
    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        pass


class LogicWidget(QtWidgets.QGraphicsWidget, serializable.Serializable):
    background_color = QtGui.QColor(229, 255, 255, 125)
    selected_background_color = QtGui.QColor(255, 255, 255, 30)
    border_color = QtGui.QColor(46, 57, 66, 255)
    selected_border_color = QtGui.QColor(254, 207, 42, 255)

    def __init__(self, parent=None):
        """
        Logic widget to control the truth of the logic.

        Args:
            parent: Parent item.

        """

        super(LogicWidget, self).__init__(parent)
        self.resizing = False
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsMovable | QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.input_port = port.Port(constants.INPUT_NODE_TYPE, True, self)
        self.output_port = port.Port(constants.OUTPUT_NODE_TYPE, True, self)
        self.setZValue(constants.Z_VAL_NODE)
        self.logic_combobox_input = ComboBox()
        self.logic_combobox_output = ComboBox()
        self.logic_combobox_input.setStyleSheet(stylesheet.STYLE_QCOMBOBOX)
        self.logic_combobox_input.setMaximumHeight(20)
        logic_list_input = QtWidgets.QListView(self.logic_combobox_input)
        logic_list_input.setStyleSheet(stylesheet.STYLE_QLISTVIEW)
        self.logic_combobox_input.setView(logic_list_input)
        self.logic_combobox_input.addItems(("And", "Or", "Not"))
        self.logic_combobox_input.clearFocus()

        self.logic_combobox_output.setStyleSheet(stylesheet.STYLE_QCOMBOBOX)
        self.logic_combobox_output.setMaximumHeight(20)
        logic_list_output = QtWidgets.QListView(self.logic_combobox_output)
        logic_list_output.setStyleSheet(stylesheet.STYLE_QLISTVIEW)
        self.logic_combobox_output.setView(logic_list_output)
        self.logic_combobox_output.addItems(("And", "Or", "Not"))
        self.logic_combobox_output.clearFocus()

        self.group = GroupWidget("Logical Controller")
        self.group.add_node_widget(self.logic_combobox_input)
        self.group.add_node_widget(self.logic_combobox_output)
        self.proxywidget = QtWidgets.QGraphicsProxyWidget()
        self.proxywidget.setWidget(self.group)
        self.layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.layout.addItem(self.input_port)
        self.layout.addItem(self.proxywidget)
        self.layout.addItem(self.output_port)
        self.layout.setSpacing(0)
        self.layout.setAlignment(self.input_port, QtCore.Qt.AlignLeft)
        self.layout.setAlignment(self.output_port, QtCore.Qt.AlignRight)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Animation
        self.next_attribute = list()
        self.last_attribute = list()
        self.next_logic = list()
        self.last_logic = list()
        self.attribute_animation = False

        # Colliding
        self.moving = False
        self.colliding_co = False

        # MOVING
        self.was_moved = False

        # DRAW LINE
        self.vpath = None
        self.hpath = None
        self.hlast = None
        self.vlast = None
        self.hpath_flag = False
        self.vpath_flag = False

        # Style
        self.background_color_flag = False
        self.selected_background_color_flag = False
        self.border_color_flag = False
        self.selected_border_color_flag = False

    def get_port_position(self, port_type, port_truth):
        """
        Return the port position.

        Args:
            port_type: The port type.
            port_truth: The port truth.

        Returns: The port scene position.

        """

        self.layout.activate()
        if port_truth:
            if port_type == constants.INPUT_NODE_TYPE:
                return self.input_port.scenePos() + QtCore.QPointF(0, self.input_port.width / 2)
            else:
                return self.output_port.scenePos() + QtCore.QPointF(self.output_port.width / 2,
                                                                    self.output_port.width / 2)

    def update_pipe_position(self):
        """
        Update pipe position.

        """

        self.input_port.update_pipes_position()
        self.output_port.update_pipes_position()

    def add_next_attribute(self, widget):
        """
        Add the related attribute widget.

        Args:
            widget: attribute widget.

        """

        self.next_attribute.append(widget)

    def add_last_attribute(self, widget):
        """
        Add the related attribute widget.

        Args:
            widget: attribute widget.

        """

        self.last_attribute.append(widget)

    def add_next_logic(self, widget):
        """
        Add the related logic widget.

        Args:
            widget: logic widget.

        """

        self.next_logic.append(widget)

    def add_last_logic(self, widget):
        """
        Add the related logic widget.

        Args:
            widget: logic widget.

        """

        self.last_logic.append(widget)

    def remove_next_attribute(self, widget):
        if widget in self.next_attribute:
            self.next_attribute.remove(widget)

    def remove_last_attribute(self, widget):
        if widget in self.last_attribute:
            self.last_attribute.remove(widget)

    def remove_next_logic(self, widget):
        if widget in self.next_logic:
            self.next_logic.remove(widget)

    def remove_last_logic(self, widget):
        if widget in self.last_logic:
            self.last_logic.remove(widget)

    def start_pipe_animation(self):
        self.output_port.start_pipes_animation()
        self.input_port.start_pipes_animation()
        self.attribute_animation = True

        for node in self.next_attribute:
            if not node.attribute_animation:
                node.start_pipe_animation()

        for node in self.last_attribute:
            if not node.attribute_animation:
                node.start_pipe_animation()

        for logic in self.next_logic:
            if not logic.attribute_animation:
                logic.start_pipe_animation()

        for logic in self.last_logic:
            if not logic.attribute_animation:
                logic.start_pipe_animation()

    def end_pipe_animation(self):
        self.output_port.end_pipes_animation()
        self.input_port.end_pipes_animation()
        self.attribute_animation = False

        for node in self.next_attribute:
            if node.attribute_animation:
                node.end_pipe_animation()

        for node in self.last_attribute:
            if node.attribute_animation:
                node.end_pipe_animation()

        for logic in self.next_logic:
            if logic.attribute_animation:
                logic.end_pipe_animation()

        for logic in self.last_logic:
            if logic.attribute_animation:
                logic.end_pipe_animation()

    @staticmethod
    def colliding_judge_pipe(logic_widget, item):
        for pipe_widget in logic_widget.input_port.pipes:
            if pipe_widget is item:
                return True
        for pipe_widget in logic_widget.output_port.pipes:
            if pipe_widget is item:
                return True
        return False

    def colliding_detection(self):
        colliding_items = self.scene().collidingItems(self, QtCore.Qt.IntersectsItemBoundingRect)
        for colliding_item in colliding_items:
            if isinstance(colliding_item, pipe.Pipe):
                if not self.colliding_judge_pipe(self, colliding_item):
                    self.colliding_co = True
                    self.update()
                    return colliding_item
            self.colliding_co = False
            self.update()

    def colliding_release(self):
        if self.colliding_co:
            pipe_item = self.colliding_detection()

            output_node = pipe_item.get_output_node()
            input_node = pipe_item.get_input_node()
            if isinstance(input_node, AttributeWidget):
                output_node.remove_next_attribute(input_node)
                self.add_next_attribute(input_node)
            else:
                output_node.remove_next_logic(input_node)
                self.add_next_logic(input_node)
            output_node.add_next_logic(self)
            if isinstance(output_node, AttributeWidget):
                input_node.remove_last_attribute(output_node)
                self.add_last_attribute(output_node)
            else:
                input_node.remove_last_logic(output_node)
                self.add_last_logic(output_node)
            input_node.add_last_logic(self)

            input_port = pipe_item.get_input_type_port()
            pipe_widget = pipe.Pipe(self.output_port, input_port, self)
            self.scene().addItem(pipe_widget)
            self.scene().view.pipes.append(pipe_widget)
            pipe_item.end_port = self.input_port

            input_port.remove_pipes(pipe_item)
            input_port.add_pipes(pipe_widget)
            self.input_port.add_pipes(pipe_item)
            self.output_port.add_pipes(pipe_widget)

            self.update_pipe_position()
            input_node.update_pipe_position()
            output_node.update_pipe_position()

            if output_node.attribute_animation:
                self.start_pipe_animation()

        self.moving = False
        self.colliding_co = False

        self.scene().history.store_history("Colliding Release")

    def paint(self, painter, option, widget=None) -> None:
        super(LogicWidget, self).paint(painter, option, widget)
        painter.save()

        #   color init
        if self.scene().logic_style_background_color and not self.background_color_flag:
            self.background_color = self.scene().logic_style_background_color
        if self.scene().logic_style_selected_background_color and not self.selected_background_color_flag:
            self.selected_background_color = self.scene().logic_style_selected_background_color
        if self.scene().logic_style_border_color and not self.border_color_flag:
            self.border_color = self.scene().logic_style_border_color
        if self.scene().logic_style_selected_border_color and not self.selected_border_color_flag:
            self.selected_border_color = self.scene().logic_style_selected_border_color

        if self.colliding_co:
            pen = QtGui.QPen(QtGui.QColor(230, 0, 0, 100), 2)
        elif self.isSelected():
            pen = QtGui.QPen(self.selected_border_color, 2)
        else:
            pen = QtGui.QPen(self.border_color, 1)

        if self.isSelected():
            brush = QtGui.QBrush(self.selected_background_color)
        else:
            brush = QtGui.QBrush(self.background_color)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRoundedRect(0, 0, self.boundingRect().width(), self.boundingRect().height(), 2, 2)

        painter.restore()

    def mouseMoveEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        for item in self.scene().selectedItems():
            if isinstance(item, LogicWidget):
                for pipe_item in item.input_port.pipes + item.output_port.pipes:
                    pipe_item.source_item.setVisible(True)
                    pipe_item.destination_item.setVisible(True)
                    pipe_item.source_item.setSelected(True)
                    pipe_item.destination_item.setSelected(True)
            elif isinstance(item, AttributeWidget):
                for pipe_item in item.true_output_port.pipes + item.true_input_port.pipes + \
                                 item.false_input_port.pipes + item.false_output_port.pipes:
                    pipe_item.source_item.setVisible(True)
                    pipe_item.destination_item.setVisible(True)
                    pipe_item.source_item.setSelected(True)
                    pipe_item.destination_item.setSelected(True)

        self.moving = True
        self.was_moved = True

        # draw line
        #       init
        offect = 5
        line_hitem_up = None
        line_hitem_down = None
        line_vitem_left = None
        line_vitem_right = None
        move_h = None
        move_v = None
        hpath = None
        vpath = None
        line_hdistance_up = float("inf")
        line_hdistance_down = float("inf")
        line_vdistance_left = float("inf")
        line_vdistance_right = float("inf")
        pen = QtGui.QPen(QtGui.QColor(77, 148, 255), 2, QtCore.Qt.CustomDashLine, QtCore.Qt.RoundCap)
        pen.setDashPattern((1, 3, 1, 3))

        #       judge move direction
        if not self.hlast:
            self.hlast = self.scenePos().y()
            move_h = constants.down
        elif self.hlast > self.scenePos().y():
            move_h = constants.up
            self.hlast = self.scenePos().y()
        elif self.hlast <= self.scenePos().y():
            move_h = constants.down
            self.hlast = self.scenePos().y()

        if not self.vlast:
            self.vlast = self.scenePos().x()
            move_v = constants.left
        elif self.vlast > self.scenePos().x():
            move_v = constants.left
            self.vlast = self.scenePos().x()
        elif self.vlast <= self.scenePos().x():
            move_v = constants.right
            self.vlast = self.scenePos().x()

        #       select close item
        for item in self.scene().items():
            if isinstance(item, (AttributeWidget, LogicWidget)):
                if item is not self:
                    #   different move directions
                    if move_h == constants.up:
                        #   find line_hitem_down
                        if item.scenePos().y() + item.boundingRect().height() - offect <= self.scenePos().y():
                            h_distance_down = self.scenePos().y() - (item.scenePos().y() + item.boundingRect().height())
                            if h_distance_down < line_hdistance_down:
                                line_hdistance_down = h_distance_down
                                line_hitem_down = item
                        #   find line_hitem_up
                        if item.scenePos().y() - offect <= self.scenePos().y():
                            h_distance_up = self.scenePos().y() - item.scenePos().y()
                            if h_distance_up < line_hdistance_up:
                                line_hdistance_up = h_distance_up
                                line_hitem_up = item

                    elif move_h == constants.down:
                        #   find line_hitem_up
                        if item.scenePos().y() + offect >= self.scenePos().y() + self.boundingRect().height():
                            h_distance_up = item.scenePos().y() + item.boundingRect().height() - self.scenePos().y()
                            if h_distance_up < line_hdistance_up:
                                line_hdistance_up = h_distance_up
                                line_hitem_up = item
                        #   find line_hitem_down
                        if item.y() + item.boundingRect().height() + offect >= self.y() + self.boundingRect().height():
                            h_distance_down = item.scenePos().y() + item.boundingRect().height() - \
                                              (self.scenePos().y() + self.boundingRect().height())
                            if h_distance_down < line_hdistance_down:
                                line_hdistance_down = h_distance_down
                                line_hitem_down = item

                    if move_v == constants.left:
                        #   find line_vitem_right
                        if item.scenePos().x() + item.boundingRect().width() - offect <= self.scenePos().x():
                            v_distance_right = self.scenePos().x() - (item.scenePos().x() + item.boundingRect().width())
                            if v_distance_right < line_vdistance_right:
                                line_vdistance_right = v_distance_right
                                line_vitem_right = item
                        #   find line_vitem_left
                        if item.x() - offect <= self.scenePos().x():
                            v_distance_left = self.scenePos().x() - item.scenePos().x()
                            if v_distance_left < line_vdistance_left:
                                line_vdistance_left = v_distance_left
                                line_vitem_left = item

                    elif move_v == constants.right:
                        #   find line_vitem_left
                        if item.scenePos().x() + offect >= self.scenePos().x() + self.boundingRect().width():
                            v_distance_left = item.scenePos().x() - (self.scenePos().x() + self.boundingRect().width())
                            if v_distance_left < line_vdistance_left:
                                line_vdistance_left = v_distance_left
                                line_vitem_left = item
                        #   find line_vitem_right
                        if item.scenePos().x() + item.boundingRect().width() + offect >= \
                                self.scenePos().x() + self.boundingRect().width():
                            v_distance_right = item.scenePos().x() + item.boundingRect().width() - \
                                               (self.scenePos().x() + self.boundingRect().width())
                            if v_distance_right < line_vdistance_right:
                                line_vdistance_right = v_distance_right
                                line_vitem_right = item

        #   calculate the closest hitem and vitem
        #       hitem
        if move_h == constants.up:
            if line_hitem_down and line_hitem_up:

                if line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() >= \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                        self.scene().sceneRect().right(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

                elif line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() < \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_up.scenePos().y(),
                        self.scene().sceneRect().right(),
                        line_hitem_up.scenePos().y())

            elif line_hitem_up and not line_hitem_down:

                hpath = QtWidgets.QGraphicsLineItem(
                    self.scene().sceneRect().left(),
                    line_hitem_up.scenePos().y(),
                    self.scene().sceneRect().right(),
                    line_hitem_up.scenePos().y())

        elif move_h == constants.down:
            if line_hitem_down and line_hitem_up:

                if line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() < \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                        self.scene().sceneRect().right(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

                elif line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() >= \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_up.scenePos().y(),
                        self.scene().sceneRect().right(),
                        line_hitem_up.scenePos().y())

            elif line_hitem_down and not line_hitem_up:

                hpath = QtWidgets.QGraphicsLineItem(
                    self.scene().sceneRect().left(),
                    line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                    self.scene().sceneRect().right(),
                    line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

        #       vitem
        if move_v == constants.left:
            if line_vitem_left and line_vitem_right:

                if line_vitem_left.scenePos().x() > \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().top(),
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().bottom())

                elif line_vitem_left.scenePos().x() <= \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().top(),
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().bottom())

            elif line_vitem_left and not line_vitem_right:

                vpath = QtWidgets.QGraphicsLineItem(
                    line_vitem_left.scenePos().x(),
                    self.scene().sceneRect().top(),
                    line_vitem_left.scenePos().x(),
                    self.scene().sceneRect().bottom())

        elif move_v == constants.right:
            if line_vitem_left and line_vitem_right:

                if line_vitem_left.scenePos().x() <= \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().top(),
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().bottom())

                elif line_vitem_left.scenePos().x() > \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().top(),
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().bottom())

            elif line_vitem_right and not line_vitem_left:

                vpath = QtWidgets.QGraphicsLineItem(
                    line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                    self.scene().sceneRect().top(),
                    line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                    self.scene().sceneRect().bottom())

        if hpath:
            if not self.hpath:
                self.hpath = hpath
                self.hpath.setPen(pen)
                self.scene().addItem(self.hpath)
            elif self.hpath is not hpath and self.hpath:
                if self.hpath in self.scene().items():
                    self.scene().removeItem(self.hpath)
                self.hpath = hpath
                self.hpath.setPen(pen)
                self.scene().addItem(self.hpath)
                self.hpath_flag = True
        elif self.hpath_flag:
            if self.hpath in self.scene().items():
                self.scene().removeItem(self.hpath)
                self.hpath = None

        if vpath:
            if not self.vpath:
                self.vpath = vpath
                self.vpath.setPen(pen)
                self.scene().addItem(self.vpath)
            elif self.vpath is not vpath and self.vpath:
                if self.vpath in self.scene().items():
                    self.scene().removeItem(self.vpath)
                self.vpath = vpath
                self.vpath.setPen(pen)
                self.scene().addItem(self.vpath)
                self.vpath_flag = True
        elif self.vpath_flag:
            if self.vpath in self.scene().items():
                self.scene().removeItem(self.vpath)
                self.vpath = None

        super(LogicWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: 'QtWidgets.QGraphicsSceneMouseEvent') -> None:
        if self.was_moved:
            self.was_moved = False
            self.scene().history.store_history("Logic Widget Position Changed")
        if self.scene().view.mode == constants.MODE_NOOP:
            self.colliding_release()

        if self.vpath and self.vpath in self.scene().items():
            self.scene().removeItem(self.vpath)
        if self.hpath and self.hpath in self.scene().items():
            self.scene().removeItem(self.hpath)

        super(LogicWidget, self).mouseReleaseEvent(event)

    def moveEvent(self, event: 'QtWidgets.QGraphicsSceneMoveEvent') -> None:
        super(LogicWidget, self).moveEvent(event)
        if self.moving:
            self.colliding_detection()
        self.update_pipe_position()

    def save_to_file(self):
        pass

    def serialize(self, logic_serialization=None):
        # logic widget
        logic_serialization.logic_id = self.id
        logic_serialization.logic_position.append(self.scenePos().x())
        logic_serialization.logic_position.append(self.scenePos().y())
        logic_serialization.logic_truth.append(self.logic_combobox_input.currentIndex())
        logic_serialization.logic_truth.append(self.logic_combobox_output.currentIndex())

        # port
        self.input_port.serialize(logic_serialization.logic_port.add())
        self.output_port.serialize(logic_serialization.logic_port.add())

        # connections
        for next_attribute_widget in self.next_attribute:
            logic_serialization.logic_next_attr.append(next_attribute_widget.id)
        for next_logic_widget in self.next_logic:
            logic_serialization.logic_next_logic.append(next_logic_widget.id)
        for last_attribute_widget in self.last_attribute:
            logic_serialization.logic_last_attr.append(last_attribute_widget.id)
        for last_logic_widget in self.last_logic:
            logic_serialization.logic_last_logic.append(last_logic_widget.id)

        # ui
        logic_serialization.logic_color.append(self.background_color.rgba())
        logic_serialization.logic_color.append(self.selected_border_color.rgba())
        logic_serialization.logic_color.append(self.border_color.rgba())
        logic_serialization.logic_color.append(self.selected_border_color.rgba())

        # flag
        logic_serialization.logic_flag.append(self.background_color_flag)
        logic_serialization.logic_flag.append(self.selected_background_color_flag)
        logic_serialization.logic_flag.append(self.border_color_flag)
        logic_serialization.logic_flag.append(self.selected_border_color_flag)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        if flag:
            # added into scene and view
            view.current_scene.addItem(self)
            view.logic_widgets.append(self)
            # id and hashmap
            self.id = data.logic_id
            hashmap[data.logic_id] = self
            # geometry and contents
            self.setPos(data.logic_position[0], data.logic_position[1])
            self.logic_combobox_input.setCurrentIndex(data.logic_truth[0])
            self.logic_combobox_output.setCurrentIndex(data.logic_truth[1])
            # ports
            self.input_port.deserialize(data.logic_port[0], hashmap, view, flag=True)
            self.output_port.deserialize(data.logic_port[1], hashmap, view, flag=True)
            # style
            self.background_color = QtGui.QColor()
            self.background_color.setRgba(data.logic_color[0])

            self.selected_border_color = QtGui.QColor()
            self.selected_border_color.setRgba(data.logic_color[1])

            self.border_color = QtGui.QColor()
            self.border_color.setRgba(data.logic_color[2])

            self.selected_border_color = QtGui.QColor()
            self.selected_border_color.setRgba(data.logic_color[3])

            # flag
            self.background_color_flag = data.logic_flag[0]
            self.selected_background_color_flag = data.logic_flag[1]
            self.border_color_flag = data.logic_flag[2]
            self.selected_border_color_flag = data.logic_flag[3]

            return True
        else:
            pass


class AttributeImage(QtWidgets.QGraphicsWidget):
    def __init__(self, parent=None):
        super(AttributeImage, self).__init__(parent)
        self.video = parent
        self.file_url = None


class ChangeImageOrVideo(QtWidgets.QLabel):
    def __init__(self, label_type: str, parent, text):
        super(ChangeImageOrVideo, self).__init__(text)
        self.label_type = label_type
        self.parent = parent
        self.setStyleSheet(stylesheet.STYLE_QLABEL_FILE)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        super(ChangeImageOrVideo, self).mousePressEvent(ev)
        if self.label_type == "Cover":
            self.parent.turn_image()
        elif self.label_type == "File":
            self.parent.turn_file()


class AttributeFile(QtWidgets.QGraphicsWidget, serializable.Serializable):
    def __init__(self, parent=None):
        """
        Create the file sub widget.

        Args:
            parent: Parent item.
        """

        super(AttributeFile, self).__init__()
        self.parent_item = parent
        self.setZValue(constants.Z_VAL_NODE)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # widget
        self.image = AttributeImage()
        self.image.setMinimumSize(100, 100)
        self.image.setMaximumSize(100, 100)
        self.image.setAutoFillBackground(True)
        palette = self.image.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(
            QtGui.QPixmap(os.path.abspath(os.path.join(os.path.dirname(__file__), "../Resources/video.png"))).scaled(
                self.image.size().width(),
                self.image.size().height(),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation
            )))
        self.image.setPalette(palette)

        self.label_item = SimpleTextField("Description", self)
        self.label_item.setFont(QtGui.QFont("等距更纱黑体 SC", 8))

        self.change_image_text = ChangeImageOrVideo("Cover", self, "Cover")
        self.change_video_text = ChangeImageOrVideo("File", self, "File")
        self.proxy_image_text = QtWidgets.QGraphicsProxyWidget()
        self.proxy_video_text = QtWidgets.QGraphicsProxyWidget()
        self.proxy_image_text.setZValue(constants.Z_VAL_NODE)
        self.proxy_video_text.setZValue(constants.Z_VAL_NODE)
        self.proxy_image_text.setWidget(self.change_image_text)
        self.proxy_video_text.setWidget(self.change_video_text)

        # layout
        self.layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.layout.setSpacing(15)
        self.control_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.control_layout.addItem(self.proxy_image_text)
        self.control_layout.addItem(self.proxy_video_text)
        self.layout.addItem(QtWidgets.QGraphicsWidget(self.label_item))
        self.layout.addItem(self.control_layout)
        self.layout.addItem(self.image)
        self.setLayout(self.layout)

        # store
        self.image_url = os.path.abspath(os.path.join(os.path.dirname(__file__), r"../Resources/video.png"))

        # layout
        self.item_row = 0
        self.item_column = 0

    def paint(self, painter: QtGui.QPainter, option: 'QtWidgets.QStyleOptionGraphicsItem', widget=None) -> None:
        painter.save()

        pen = QtGui.QPen(AttributeWidget.border_color, 0.5)
        selected_pen = QtGui.QPen(AttributeWidget.selected_border_color, 0.5)
        painter.setPen(pen if not self.isSelected() else selected_pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRoundedRect(0, 0, self.size().width(), self.size().height(), 5, 5)

        painter.restore()

    def turn_image(self):
        image_url, _ = QtWidgets.QFileDialog.getOpenFileName(None, "select image", "", "*.png *.jpg")
        if image_url:
            self.image_url = image_url
            palette = self.image.palette()
            palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap(image_url).scaled(
                self.image.size().width(),
                self.image.size().height(),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation
            )))
            self.image.setPalette(palette)

    def turn_file(self):
        file_url, _ = QtWidgets.QFileDialog.getOpenFileName(None, "select files", "", "any file (*.*)")
        if file_url:
            self.image.file_url = file_url

    def serialize(self, file_serialization=None):
        file_serialization.file_id = self.id
        file_serialization.text = self.label_item.toPlainText()
        file_serialization.cover = self.image_url
        if self.image.file_url:
            file_serialization.file = self.image.file_url
        file_serialization.file_location.append(self.item_row)
        file_serialization.file_location.append(self.item_column)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        # id and hashmap
        self.id = data.file_id
        hashmap[data.file_id] = self
        # text
        self.label_item.setPlainText(data.text)
        # image
        self.image_url = data.cover
        palette = self.image.palette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(QtGui.QPixmap(self.image_url).scaled(
            self.image.size().width(),
            self.image.size().height(),
            QtCore.Qt.IgnoreAspectRatio,
            QtCore.Qt.SmoothTransformation
        )))
        self.image.setPalette(palette)
        # file
        if data.file:
            self.image.file_url = data.file
        # layout
        self.item_row = data.file_location[0]
        self.item_column = data.file_location[1]

        return True


class NoneWidget(QtWidgets.QGraphicsWidget, serializable.Serializable):
    def __init__(self, row=0, column=0, parent=None):
        """
        Create the blank item in attribute layout.

        Args:
            row: The row
            column: The column.
            parent: Parent item.
        """

        super(NoneWidget, self).__init__(parent)
        self.parent_item = parent
        self.pixmap = QtGui.QPixmap(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                 "../Resources/blank.png")))

        self.setZValue(constants.Z_VAL_PORT)
        self.setFlags(QtWidgets.QGraphicsItem.ItemIsSelectable)
        self.setMinimumSize(float(self.pixmap.size().width()), float(self.pixmap.size().height()))

        self.item_row = row
        self.item_column = column

    def paint(self, painter: QtGui.QPainter, option=None, widget=None) -> None:
        painter.drawPixmap(self.boundingRect().toRect(), self.pixmap)
        pen = QtGui.QPen(AttributeWidget.border_color if not self.isSelected()
                         else AttributeWidget.selected_border_color)
        painter.setPen(pen)
        painter.drawRoundedRect(self.boundingRect(), 5, 5)

    def serialize(self, nonewidget_serialization=None):
        nonewidget_serialization.none_id = self.id
        nonewidget_serialization.none_pos.extend((self.item_row, self.item_column))

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        self.id = data.none_id
        self.item_row = data.none_pos[0]
        self.item_column = data.none_pos[1]


class AttributeWidget(QtWidgets.QGraphicsWidget, serializable.Serializable):
    display_name_changed = QtCore.pyqtSignal(str)
    draw_label = None
    color = QtGui.QColor(229, 255, 255, 125)
    selected_color = QtGui.QColor(255, 255, 255, 30)
    border_color = QtGui.QColor(46, 57, 66, 255)
    selected_border_color = QtGui.QColor(254, 207, 42, 255)

    def __init__(self):
        super(AttributeWidget, self).__init__()
        # SET BASIC FUNCTION.
        self.name = "Node"
        self.setFlags(QtWidgets.QGraphicsWidget.ItemIsSelectable | QtWidgets.QGraphicsWidget.ItemIsFocusable |
                      QtWidgets.QGraphicsWidget.ItemSendsGeometryChanges | QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setCacheMode(QtWidgets.QGraphicsItem.DeviceCoordinateCache)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAcceptHoverEvents(True)
        self.setZValue(constants.Z_VAL_NODE)

        # LAYOUTS

        #   create
        self.layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Horizontal)
        self.input_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.output_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.title_layout = QtWidgets.QGraphicsLinearLayout(QtCore.Qt.Vertical)
        self.attribute_layout = QtWidgets.QGraphicsGridLayout()
        self.current_row = 0
        self.current_column = -1
        self.item_row = 0
        self.item_column = 0
        #   sapcing
        self.layout.setSpacing(0)
        self.input_layout.setSpacing(0)
        self.output_layout.setSpacing(0)
        self.title_layout.setSpacing(0)
        self.attribute_layout.setSpacing(10)
        #   margin
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.title_layout.setContentsMargins(0, 0, 0, 0)
        self.attribute_layout.setContentsMargins(0, 0, 0, 2)

        # WIDGETS
        #   title name widget
        self.attribute_widget = SubConstituteWidget(self)
        #   port widgets
        self.true_input_port = port.Port(constants.INPUT_NODE_TYPE, True, self)
        self.true_output_port = port.Port(constants.OUTPUT_NODE_TYPE, True, self)
        self.false_input_port = port.Port(constants.INPUT_NODE_TYPE, False, self)
        self.false_output_port = port.Port(constants.OUTPUT_NODE_TYPE, False, self)
        self.true_input_port.setMaximumSize(port.Port.width, port.Port.width)
        self.true_output_port.setMaximumSize(port.Port.width, port.Port.width)
        self.false_input_port.setMaximumSize(port.Port.width, port.Port.width)
        self.false_output_port.setMaximumSize(port.Port.width, port.Port.width)

        # IMPLEMENT WIDGETS
        #   layout
        self.setLayout(self.layout)
        self.layout.addItem(self.input_layout)
        self.layout.addItem(self.title_layout)
        self.layout.addItem(self.output_layout)
        #  input layout
        self.input_layout.addItem(self.true_input_port)
        self.input_layout.addStretch(1)
        self.input_layout.addItem(self.false_input_port)
        self.input_layout.setAlignment(self.true_input_port, QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.input_layout.setAlignment(self.false_input_port, QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        # title layout
        self.title_layout.addItem(self.attribute_widget)
        self.title_layout.addItem(self.attribute_layout)
        self.title_layout.setAlignment(self.attribute_widget, QtCore.Qt.AlignCenter)
        self.title_layout.setAlignment(self.attribute_layout, QtCore.Qt.AlignCenter)
        # output layout
        self.output_layout.addItem(self.true_output_port)
        self.output_layout.addStretch(1)
        self.output_layout.addItem(self.false_output_port)
        self.output_layout.setAlignment(self.true_output_port, QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.output_layout.setAlignment(self.false_output_port, QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        # RESIZE
        self.resizing = False

        # MOVE
        self.moving = False
        self.colliding_type = constants.COLLIDING_ATTRIBUTE
        self.colliding_co = False
        self.colliding_parent = False
        self.colliding_child = False
        self.colliding_inside = False

        # ANAMATION
        self.attribute_animation = False
        self.next_attribute = list()
        self.last_attribute = list()
        self.next_logic = list()
        self.last_logic = list()
        self.attribute_sub_widgets = list()

        # SCENE
        self.sub_scene = None

        # MOVING
        self.was_moved = False

        # DRAW LINE
        self.vpath = None
        self.hpath = None
        self.hlast = None
        self.vlast = None
        self.hpath_flag = False
        self.vpath_flag = False

        # Style
        self.color_flag = False
        self.selected_color_flag = False
        self.border_flag = False
        self.selected_border_flag = False

        # context
        self.context_flag = False

    def paint(self, painter, option, widget=None) -> None:
        painter.save()

        # color and width init
        if self.scene().attribute_style_background_color and not self.color_flag:
            self.color = self.scene().attribute_style_background_color
        if self.scene().attribute_style_selected_background_color and not self.selected_color_flag:
            self.selected_color = self.scene().attribute_style_selected_background_color
        if self.scene().attribute_style_border_color and not self.border_flag:
            self.border_color = self.scene().attribute_style_border_color
        if self.scene().attribute_style_selected_border_color and not self.selected_border_flag:
            self.selected_border_color = self.scene().attribute_style_selected_border_color

        # draw border
        bg_border = 1.0
        radius = 2
        rect = QtCore.QRectF(
            0.5 - (bg_border / 2),
            0.5 - (bg_border / 2),
            self.boundingRect().width() + bg_border,
            self.boundingRect().height() + bg_border
        )
        border_color = self.border_color
        path = QtGui.QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # draw background
        rect = self.boundingRect()
        painter.setBrush(self.color if not self.isSelected() else self.selected_color)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # draw border
        border_width = 0.8
        if self.isSelected() and constants.NODE_SEL_BORDER_COLOR:
            border_width = 1.2
            border_color = self.selected_border_color
        border_rect = QtCore.QRectF(rect.left() - (border_width / 2),
                                    rect.top() - (border_width / 2),
                                    rect.width() + border_width,
                                    rect.height() + border_width)
        pen = QtGui.QPen(border_color, border_width)
        path = QtGui.QPainterPath()
        path.addRoundedRect(border_rect, radius, radius)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(pen if not self.colliding_co else
                       QtGui.QPen(QtGui.QColor(230, 0, 0, 100), 2))
        painter.drawPath(path)

        painter.restore()

    def text_change_node_shape(self):
        """
        Update ui.

        """

        # text
        self.attribute_widget.updateGeometry()
        self.attribute_widget.update()
        #  layout
        self.prepareGeometryChange()
        self.layout.invalidate()
        self.layout.activate()
        self.updateGeometry()
        self.update()
        self.title_layout.updateGeometry()
        self.title_layout.invalidate()
        self.attribute_layout.updateGeometry()
        self.attribute_layout.invalidate()
        # pipe position
        self.update_pipe_position()
        self.update_pipe_parent_position()
        # parent
        node = self
        while node.parentItem():
            node = node.parentItem()
        if node is not self:
            node.text_change_node_shape()

    def mouse_update_node_size(self, event):
        """
        Resize and update ui.

        Args:
            event: Qmouseevent.

        """

        if event.type() == QtCore.QEvent.GraphicsSceneMousePress and not self.parentItem():
            self.resizing = True
            self.setCursor(QtCore.Qt.SizeAllCursor)
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseRelease and not self.parentItem():
            self.resizing = False
            self.setCursor(QtCore.Qt.ArrowCursor)
        elif event.type() == QtCore.QEvent.GraphicsSceneMouseMove and not self.parentItem():
            past_pos = self.scenePos()
            past_width = self.size().width()
            past_height = self.size().height()
            current_pos = self.mapToScene(event.pos())
            current_width = current_pos.x() - past_pos.x() if current_pos.x() >= past_pos.x() else past_width
            current_height = current_pos.y() - past_pos.y() if current_pos.y() >= past_pos.y() else past_height
            self.resize(current_width, current_height)
            self.update_pipe_position()

            if constants.DEBUG_TUPLE_NODE_SCALE:
                print(current_width, current_height)

    def get_port_position(self, port_type, port_truth):
        """
        Get the port position.

        Args:
            port_type: The port type.
            port_truth: The port truth.

        Returns:

        """
        pos = QtCore.QPointF(0, 0)
        if port_type == constants.INPUT_NODE_TYPE:
            if port_truth:
                pos = self.true_input_port.scenePos() + QtCore.QPointF(0, self.true_input_port.width / 2)
            else:
                pos = self.false_input_port.scenePos() + QtCore.QPointF(0, self.false_input_port.width / 2)
        elif port_type == constants.OUTPUT_NODE_TYPE:
            if port_truth:
                pos = self.true_output_port.scenePos() + QtCore.QPointF(self.true_output_port.width / 2,
                                                                        self.true_output_port.width / 2)
            else:
                pos = self.false_output_port.scenePos() + QtCore.QPointF(self.false_output_port.width / 2,
                                                                         self.false_output_port.width / 2)
        return pos

    def calculate_last_widget(self, row):
        """
        Returns the reciprocal component of this row.

        Args:
            row: The layout row.

        Returns: Attribute widget.

        """

        for i in range(self.attribute_layout.columnCount() - 1, -1, -1):
            widget = self.attribute_layout.itemAt(row, i)
            if widget:
                return widget

    def calculate_widget_index(self, row):
        """
        Returns the index of the reciprocal component of this row.

        Args:
            row: The layout row.

        Returns: The index.

        """

        number = 0
        for i in range(self.attribute_layout.columnCount() - 1, -1, -1):
            widget = self.attribute_layout.itemAt(row, i)
            if widget:
                number += 1
        return number

    def add_widget(self, widget, line=True):
        """
        Add sub widget

        Args:
            widget: The sub widget.
            line: Change line or not.

        """

        # calculate current pos
        if not line:
            if not (self.current_row == 0 and self.current_column == -1):
                self.current_row += 1
                self.current_column = 0
            else:
                self.current_column = 0
        elif line:
            self.current_column += 1

        # Delete none widget
        if isinstance(self.attribute_layout.itemAt(self.current_row, self.current_column), NoneWidget):
            none_widget = self.attribute_layout.itemAt(self.current_row, self.current_column)
            self.attribute_layout.removeItem(none_widget)
            self.attribute_sub_widgets.remove(none_widget)
            none_widget.setParentItem(None)
            sip.delete(none_widget)

        # Add sub widget
        self.attribute_layout.addItem(widget,
                                      self.current_row,
                                      self.current_column)
        widget.item_row = self.current_row
        widget.item_column = self.current_column

        if constants.DEBUG_ATTRIBUTE_INDEX:
            print("Add sub widget index", self.current_row, self.current_column)

        # Add none widget
        for row in range(self.current_row):
            for column in range(self.current_column + 1):
                if not self.attribute_layout.itemAt(row, column):
                    item = NoneWidget(row, column, self)
                    self.attribute_layout.addItem(item, row, column)
                    self.attribute_sub_widgets.append(item)

    def add_new_subwidget(self, line=True, flag=""):
        """
        Create sub widget and added into layout.

        Args:
            line: Change line or not.
            flag: Different widgets.

        """

        # Create sub widget
        subwidget = None
        if flag == "attr":
            subwidget = AttributeWidget()
            self.scene().view.attribute_widgets.append(subwidget)
        elif flag == "file":
            subwidget = AttributeFile(self)
        elif flag == "view":
            from .sub_view import ProxyView
            subwidget = ProxyView(self.scene().view.mainwindow)
        elif flag == "todo":
            from .todo import Todo
            subwidget = Todo(self)

        # Added into scene
        self.add_widget(subwidget, line)
        self.attribute_sub_widgets.append(subwidget)
        self.text_change_node_shape()
        self.update_pipe_position()

        # Update ui
        parent = self
        while parent.parentItem():
            parent = parent.parentItem()
            parent.text_change_node_shape()
            parent.update_pipe_position()

        # Serialization undo&&redo
        self.scene().history.store_history("Add New Subwidget")

    def add_exist_subwidget(self, subwidget, line=True):
        """
        Add sub widget.

        Args:
            subwidget: The sub widget.
            line: Change line or not.

        """

        self.add_widget(subwidget, line)
        self.attribute_sub_widgets.append(subwidget)
        subwidget.setParentItem(self)
        self.text_change_node_shape()
        self.update_pipe_position()

        parent = self
        while parent.parentItem():
            parent = parent.parentItem()
            parent.text_change_node_shape()
            parent.update_pipe_position()

    def delete_subwidget(self, subwidget):
        """
        Delete the sub widget.

        Args:
            subwidget: The deleted sub widget.

        """

        if constants.DEBUG_ATTRIBUTE_INDEX:
            print("Delete sub widget index", self.current_row, self.current_column)

        # Delete the sub widget
        self.attribute_layout.removeItem(subwidget)
        self.attribute_sub_widgets.remove(subwidget)
        subwidget.setParentItem(None)

        # Added none type widget into blank and update ui
        if not self.attribute_layout.itemAt(subwidget.item_row, subwidget.item_column):
            add_none = NoneWidget(subwidget.item_row, subwidget.item_column, self)
            self.attribute_layout.addItem(add_none, subwidget.item_row, subwidget.item_column)
            self.attribute_sub_widgets.append(add_none)

        # Update
        self.text_change_node_shape()
        self.update_pipe_position()

    def move_up_widget(self, widget):
        """
        Change the index of the widget.

        Args:
            widget: The sub widget.

        """

        if isinstance(widget, SubConstituteWidget):
            widget = widget.parentItem()
        elif isinstance(widget, InputTextField):
            widget = widget.node
        elif isinstance(widget, AttributeFile):
            widget = widget.parent_item
        parent = widget.parentItem()
        if parent:
            row = widget.item_row
            column = widget.item_column
            # can't move up
            if row == 0 and column == 0:
                return
            # can move up
            else:
                # not at first of line
                if column != 0:
                    last_widget = parent.attribute_layout.itemAt(row, column - 1)
                    if last_widget:
                        parent.attribute_layout.removeItem(last_widget)
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row, column - 1)
                        parent.attribute_layout.addItem(last_widget, row, column)
                        widget.item_row = row
                        widget.item_column = column - 1
                        last_widget.item_row = row
                        last_widget.item_column = column
                    else:
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row, column - 1)
                        widget.item_row = row
                        widget.item_column = column - 1
                # at first of line and row != 0
                else:
                    last_widget = parent.caculate_column(row - 1)
                    if last_widget:
                        parent.attribute_layout.removeItem(last_widget)
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row - 1, last_widget.item_column)
                        parent.attribute_layout.addItem(last_widget, row, column)
                        widget.item_row = row - 1
                        widget.item_column = last_widget.item_column
                        last_widget.item_row = row
                        last_widget.item_column = column
                    else:
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row - 1, 0)
                        widget.item_row = row - 1
                        widget.item_column = 0

            parent.text_change_node_shape()

            self.scene().history.store_history("Move up widget")

    def move_down_widget(self, widget):
        """
        Change the index of the widget.

        Args:
            widget: The sub widget.

        """

        if isinstance(widget, SubConstituteWidget):
            widget = widget.parentItem()
        elif isinstance(widget, InputTextField):
            widget = widget.node
        elif isinstance(widget, AttributeFile):
            widget = widget.parent_item
        # find widget
        parent = widget.parentItem()
        if parent:
            row = widget.item_row
            column = widget.item_column
            # move down next line at last
            if row == parent.attribute_layout.rowCount() - 1 and column == parent.attribute_layout.columnCount() - 1:
                parent.attribute_layout.removeItem(widget)
                parent.attribute_layout.addItem(widget, row + 1, 0)
                widget.item_row = row + 1
                widget.item_column = 0
                parent.current_row += 1
                parent.current_column = 0
            # not at last of rows
            else:
                # not at last of line
                if column != parent.attribute_layout.columnCount() - 1:
                    last_widget = parent.attribute_layout.itemAt(row, column + 1)
                    if last_widget:
                        parent.attribute_layout.removeItem(last_widget)
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row, column + 1)
                        parent.attribute_layout.addItem(last_widget, row, column)
                        widget.item_row = row
                        widget.item_column = column + 1
                        last_widget.item_row = row
                        last_widget.item_column = column
                    else:
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row, column + 1)
                        widget.item_row = row
                        widget.item_column = column + 1
                # at last of line
                else:
                    last_widget = parent.attribute_layout.itemAt(row + 1, 0)
                    if last_widget:
                        parent.attribute_layout.removeItem(last_widget)
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row + 1, 0)
                        parent.attribute_layout.addItem(last_widget, row, column)
                        widget.item_row = row + 1
                        widget.item_column = 0
                        last_widget.item_row = row
                        last_widget.item_column = column
                    else:
                        parent.attribute_layout.removeItem(widget)
                        parent.attribute_layout.addItem(widget, row + 1, 0)
                        widget.item_row = row + 1
                        widget.item_column = 0

            parent.text_change_node_shape()

            self.scene().history.store_history("Move down widget")

    def colliding_judge_sub(self, parent_widget, item):
        """
        Judge whether the item is its child.

        Args:
            parent_widget: The parent attribute widget.
            item: The colliding item.

        """

        while parent_widget.attribute_sub_widgets:
            for sub_widget in parent_widget.attribute_sub_widgets:
                if isinstance(sub_widget, AttributeWidget):
                    if sub_widget is item:
                        self.colliding_child = True
                        self.update()
                        return 1
                    parent_widget = sub_widget
                    if self.colliding_judge_sub(parent_widget, item):
                        return 1
            return None

    def colliding_judge_none(self, parent_widget, item):
        """
        Judge whether the item is its child.

        Args:
            parent_widget: The parent attribute widget.
            item: The colliding item.

        """

        while parent_widget.attribute_sub_widgets:
            for sub_widget in parent_widget.attribute_sub_widgets:
                if isinstance(sub_widget, NoneWidget):
                    if sub_widget is item:
                        self.colliding_child = True
                        self.update()
                        return 1
                elif isinstance(sub_widget, AttributeWidget):
                    parent_widget = sub_widget
                    if self.colliding_judge_none(parent_widget, item):
                        return 1
            return None

    def colliding_judge_parent(self, parent_widget, item):
        """
        Judge whether the item is its parent.

        Args:
            parent_widget: The parent attribute widget.
            item: The colliding item.

        """

        while parent_widget.parentItem():
            parent_widget = parent_widget.parentItem()
            if parent_widget is item:
                self.colliding_parent = True
                self.update()
                return 1

    @staticmethod
    def colliding_judge_pipe(attribute_widget, item):
        """
        Judge whether the item is its pipe.

        Args:
            attribute_widget: The parent attribute widget.
            item: The colliding item.

        """

        for pipe_widget in attribute_widget.true_input_port.pipes:
            if pipe_widget is item:
                return True
        for pipe_widget in attribute_widget.true_output_port.pipes:
            if pipe_widget is item:
                return True
        for pipe_widget in attribute_widget.false_input_port.pipes:
            if pipe_widget is item:
                return True
        for pipe_widget in attribute_widget.false_output_port.pipes:
            if pipe_widget is item:
                return True
        for sub_widget in attribute_widget.attribute_sub_widgets:
            from .sub_view import ProxyView
            from .todo import Todo
            if not isinstance(sub_widget, (AttributeFile, ProxyView, Todo, NoneWidget)) and \
                    sub_widget.colliding_judge_pipe(sub_widget, item):
                return True
        return False

    def colliding_detection(self):
        """
        Detect the colliding items.

        Returns:
            The colliding item.

        """

        colliding_items = self.scene().collidingItems(self, QtCore.Qt.IntersectsItemBoundingRect)
        for item in colliding_items:
            if isinstance(item, AttributeWidget):
                self.colliding_type = constants.COLLIDING_ATTRIBUTE
                flag_child = self.colliding_judge_sub(self, item)
                flag_parent = self.colliding_judge_parent(self, item)
                if not flag_parent and not flag_child:
                    self.colliding_co = True
                if flag_parent:
                    self.colliding_inside = True
                self.update()

                flag_pipe = False
                for left_item in colliding_items[colliding_items.index(item):]:
                    if isinstance(left_item, pipe.Pipe):
                        if not self.colliding_judge_pipe(self, left_item):
                            flag_pipe = True
                            continue

                if not flag_child:
                    return item

                if constants.DEBUG_COLLIDING:
                    print("****************attr**************************")
                    print("DEBUG COLLIDING status: ", "\nchild: ", self.colliding_child,
                          "\nparent: ", self.colliding_parent, "\ncommon co: ", self.colliding_co,
                          "\ninside: ", self.colliding_inside, "\nreturn item: ", item,
                          "\ntype: ", self.colliding_type, "\nflag pipe", flag_pipe)
                    print("**********************************************")

            elif isinstance(item, pipe.Pipe):

                if not self.colliding_judge_pipe(self, item):
                    self.colliding_type = constants.COLLIDING_PIPE
                    self.colliding_co = True
                    self.update()

                    if constants.DEBUG_COLLIDING:
                        print("****************pipe**************************")
                        print("DEBUG COLLIDING status: ", "\nchild: ", self.colliding_child,
                              "\nparent: ", self.colliding_parent, "\ncommon co: ", self.colliding_co,
                              "\ninside: ", self.colliding_inside, "\nreturn item: ", item,
                              "\ntype: ", self.colliding_type)
                        print("**********************************************")

                    return item

            elif isinstance(item, NoneWidget):

                if not self.colliding_judge_none(self, item):
                    self.colliding_type = constants.COLLIDING_NONE
                    self.colliding_co = True
                    return item

            else:

                self.colliding_co = False
                self.colliding_type = constants.COLLIDING_ATTRIBUTE
                self.colliding_inside = False

        self.update()

    def colliding_release(self, event):
        """
        According to the colliding items, do sth.

        Args:
            event: Mouse relased event.

        """

        if self.colliding_type == constants.COLLIDING_ATTRIBUTE:
            if self.colliding_co and self.colliding_parent:
                # if target is attribute widget and the parent exists
                source_parent = self.parentItem()
                target_attribute = self.colliding_detection()

                # Delete from source
                self.parentItem().delete_subwidget(self)

                # Added none type widget into blank
                if not source_parent.attribute_layout.itemAt(self.item_row, self.item_column):
                    add_none = NoneWidget(self.item_row, self.item_column, self)
                    source_parent.attribute_layout.addItem(add_none, self.item_row, self.item_column)
                    source_parent.attribute_sub_widgets.append(add_none)
                    source_parent.text_change_node_shape()

                # Added into target
                target_attribute.add_exist_subwidget(self)
                target_attribute.text_change_node_shape()

                if self.scene().view.mode == constants.MODE_NOOP:
                    self.scene().history.store_history("Colliding Add Subwidget")

            elif not self.colliding_co and self.colliding_parent and not self.colliding_inside:

                self.parentItem().delete_subwidget(self)
                self.setPos(event.scenePos())

                self.scene().history.store_history("Colliding Delete Subwidget")

            elif not self.colliding_co and self.colliding_parent and self.colliding_inside:
                self.parentItem().text_change_node_shape()

            elif self.colliding_co and not self.colliding_parent:
                self.colliding_detection().add_exist_subwidget(self)
                if self.scene().view.mode == constants.MODE_NOOP:
                    self.scene().history.store_history("Colliding Add Subwidget")

            self.colliding_co = False
            self.colliding_parent = False
            self.colliding_child = False
            self.colliding_inside = False
            self.moving = False
            self.update()

        elif self.colliding_type == constants.COLLIDING_NONE:
            # Get none type widget
            item = self.colliding_detection()
            source = self.parentItem()

            if source:
                # Remove from current index
                source.delete_subwidget(self)
                self.setPos(event.scenePos())

                if constants.DEBUG_ATTRIBUTE_INDEX:
                    print("Colliding source", self.item_row, self.item_column)

                # update
                source.text_change_node_shape()

            # Delete none type widget from target
            target = item.parentItem()
            target.attribute_layout.removeItem(item)
            target.attribute_sub_widgets.remove(item)
            item.setParentItem(None)
            sip.delete(item)

            if constants.DEBUG_ATTRIBUTE_INDEX:
                print("Colliding none type item", item,
                      target.attribute_layout.itemAt(item.item_row, item.item_column))

            # Added into index of none type widget
            target.attribute_layout.addItem(self, item.item_row, item.item_column)
            target.attribute_sub_widgets.append(self)
            self.setParentItem(target)
            self.item_row = item.item_row
            self.item_column = item.item_column

            if constants.DEBUG_ATTRIBUTE_INDEX:
                print("Colliding target", item.item_row, item.item_column)

            # Recover
            self.colliding_co = False
            self.colliding_parent = False
            self.colliding_child = False
            self.colliding_inside = False
            self.moving = False
            self.colliding_type = constants.COLLIDING_ATTRIBUTE
            self.update()

        elif self.colliding_type == constants.COLLIDING_PIPE and self.scene().view.mode == constants.MODE_NOOP:
            item = self.colliding_detection()

            if self.parentItem():
                self.parentItem().delete_subwidget(self)
                self.setPos(event.scenePos())

            output_node = item.get_output_node()
            input_node = item.get_input_node()
            if isinstance(input_node, AttributeWidget):
                output_node.remove_next_attribute(input_node)
                self.add_next_attribute(input_node)
            else:
                output_node.remove_next_logic(input_node)
                self.add_next_logic(input_node)
            output_node.add_next_attribute(self)
            if isinstance(output_node, AttributeWidget):
                input_node.remove_last_attribute(output_node)
                self.add_last_attribute(output_node)
            else:
                input_node.remove_last_logic(output_node)
                self.add_last_logic(output_node)
            input_node.add_last_attribute(self)

            if isinstance(input_node, AttributeWidget):
                pipe_widget = pipe.Pipe(self.true_output_port, input_node.true_input_port, self)
            else:
                pipe_widget = pipe.Pipe(self.true_output_port, input_node.input_port, self)
            self.scene().addItem(pipe_widget)
            self.scene().view.pipes.append(pipe_widget)

            item.get_input_type_port().add_pipes(pipe_widget)
            item.get_input_type_port().remove_pipes(item)
            self.true_input_port.add_pipes(item)
            self.true_output_port.add_pipes(pipe_widget)
            if item.end_port.port_type == constants.OUTPUT_NODE_TYPE:
                item.start_port = self.true_input_port
                item.update_position()
            else:
                item.end_port = self.true_input_port
                item.update_position()

            self.colliding_co = False
            self.colliding_parent = False
            self.colliding_child = False
            self.colliding_inside = False
            self.moving = False
            self.colliding_type = constants.COLLIDING_ATTRIBUTE
            self.update()
            input_node.update_pipe_position()
            output_node.update_pipe_position()

            if output_node.attribute_animation:
                self.start_pipe_animation()

            pipe_widget.update_position()
            self.scene().history.store_history("Colliding Add Second Pipe")

    def update_scene_rect(self):
        self.scene().setSceneRect(self.scene().itemsBoundingRect())

    def update_pipe_parent_position(self):
        parent_item = self
        while parent_item.parentItem():
            parent_item.parentItem().update_pipe_position()
            parent_item = parent_item.parentItem()

    def update_pipe_position(self):
        self.true_input_port.update_pipes_position()
        self.true_output_port.update_pipes_position()
        self.false_input_port.update_pipes_position()
        self.false_output_port.update_pipes_position()
        for sub_widget in self.attribute_sub_widgets:
            if isinstance(sub_widget, AttributeWidget):
                sub_widget.update_pipe_position()

    def add_next_attribute(self, widget):
        self.next_attribute.append(widget)

    def add_last_attribute(self, widget):
        self.last_attribute.append(widget)

    def add_next_logic(self, widget):
        self.next_logic.append(widget)

    def add_last_logic(self, widget):
        self.last_logic.append(widget)

    def set_sub_scene(self, scene_widget):
        self.sub_scene = scene_widget

    def remove_next_attribute(self, widget):
        if widget in self.next_attribute:
            self.next_attribute.remove(widget)

    def remove_last_attribute(self, widget):
        if widget in self.last_attribute:
            self.last_attribute.remove(widget)

    def remove_next_logic(self, widget):
        if widget in self.next_logic:
            self.next_logic.remove(widget)

    def remove_last_logic(self, widget):
        if widget in self.last_logic:
            self.last_logic.remove(widget)

    def remove_sub_scene(self):
        self.sub_scene = None

    def start_pipe_animation(self):
        self.true_output_port.start_pipes_animation()
        self.false_output_port.start_pipes_animation()
        self.true_input_port.start_pipes_animation()
        self.false_input_port.start_pipes_animation()
        self.attribute_animation = True

        for node in self.next_attribute:
            if not node.attribute_animation:
                node.start_pipe_animation()

        for node in self.last_attribute:
            if not node.attribute_animation:
                node.start_pipe_animation()

        for logic in self.next_logic:
            if not logic.attribute_animation:
                logic.start_pipe_animation()

        for logic in self.last_logic:
            if not logic.attribute_animation:
                logic.start_pipe_animation()

        for sub_node in self.attribute_sub_widgets:
            if isinstance(sub_node, AttributeWidget) and not sub_node.attribute_animation:
                sub_node.start_pipe_animation()

    def end_pipe_animation(self):
        self.true_output_port.end_pipes_animation()
        self.false_output_port.end_pipes_animation()
        self.true_input_port.end_pipes_animation()
        self.false_input_port.end_pipes_animation()
        self.attribute_animation = False

        for node in self.next_attribute:
            if node.attribute_animation:
                node.end_pipe_animation()

        for node in self.last_attribute:
            if node.attribute_animation:
                node.end_pipe_animation()

        for logic in self.next_logic:
            if logic.attribute_animation:
                logic.end_pipe_animation()

        for logic in self.last_logic:
            if logic.attribute_animation:
                logic.end_pipe_animation()

        for sub_node in self.attribute_sub_widgets:
            if isinstance(sub_node, AttributeWidget) and not sub_node.attribute_animation:
                sub_node.end_pipe_animation()

    def update_treelist(self):
        if self.sub_scene:
            iterator = QtWidgets.QTreeWidgetItemIterator(self.scene().view.mainwindow.scene_list)
            while iterator.value():
                scene_flag = iterator.value()
                iterator += 1
                if scene_flag.data(0, QtCore.Qt.ToolTipRole) is self.sub_scene:
                    scene_flag.setText(0, self.attribute_widget.label_item.toPlainText())

    def travers_subitem(self, subitem: list):
        for item in subitem:
            if isinstance(item, AttributeWidget):
                for pipe_item in item.true_output_port.pipes + item.true_input_port.pipes + \
                                 item.false_input_port.pipes + item.false_output_port.pipes:
                    pipe_item.source_item.setVisible(True)
                    pipe_item.destination_item.setVisible(True)
                    pipe_item.source_item.setSelected(True)
                    pipe_item.destination_item.setSelected(True)
                self.travers_subitem(item.attribute_sub_widgets)

    def mousePressEvent(self, event) -> None:
        if int(event.modifiers()) & QtCore.Qt.ShiftModifier:
            self.mouse_update_node_size(event)
        else:
            super(AttributeWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        for item in self.scene().selectedItems():
            if isinstance(item, AttributeWidget):
                for pipe_item in item.true_output_port.pipes + item.true_input_port.pipes + \
                                 item.false_input_port.pipes + item.false_output_port.pipes:
                    pipe_item.source_item.setVisible(True)
                    pipe_item.destination_item.setVisible(True)
                    pipe_item.source_item.setSelected(True)
                    pipe_item.destination_item.setSelected(True)
                self.travers_subitem(self.attribute_sub_widgets)
            elif isinstance(item, LogicWidget):
                for pipe_item in item.input_port.pipes + item.output_port.pipes:
                    pipe_item.source_item.setVisible(True)
                    pipe_item.destination_item.setVisible(True)
                    pipe_item.source_item.setSelected(True)
                    pipe_item.destination_item.setSelected(True)

        self.was_moved = True
        self.moving = True

        # draw line
        #       init
        offect = 5
        line_hitem_up = None
        line_hitem_down = None
        line_vitem_left = None
        line_vitem_right = None
        move_h = None
        move_v = None
        hpath = None
        vpath = None
        line_hdistance_up = float("inf")
        line_hdistance_down = float("inf")
        line_vdistance_left = float("inf")
        line_vdistance_right = float("inf")
        pen = QtGui.QPen(QtGui.QColor(77, 148, 255), 2, QtCore.Qt.CustomDashLine, QtCore.Qt.RoundCap)
        pen.setDashPattern((1, 3, 1, 3))

        #       judge move direction
        if not self.hlast:
            self.hlast = self.scenePos().y()
            move_h = constants.down
        elif self.hlast > self.scenePos().y():
            move_h = constants.up
            self.hlast = self.scenePos().y()
        elif self.hlast <= self.scenePos().y():
            move_h = constants.down
            self.hlast = self.scenePos().y()

        if not self.vlast:
            self.vlast = self.scenePos().x()
            move_v = constants.left
        elif self.vlast > self.scenePos().x():
            move_v = constants.left
            self.vlast = self.scenePos().x()
        elif self.vlast <= self.scenePos().x():
            move_v = constants.right
            self.vlast = self.scenePos().x()

        #       select close item
        for item in self.scene().items():
            if isinstance(item, (AttributeWidget, LogicWidget)):
                if item not in self.attribute_sub_widgets and item is not self:
                    #   different move directions
                    if move_h == constants.up:
                        #   find line_hitem_down
                        if item.scenePos().y() + item.boundingRect().height() - offect <= self.scenePos().y():
                            h_distance_down = self.scenePos().y() - (item.scenePos().y() + item.boundingRect().height())
                            if h_distance_down < line_hdistance_down:
                                line_hdistance_down = h_distance_down
                                line_hitem_down = item
                        #   find line_hitem_up
                        if item.scenePos().y() - offect <= self.scenePos().y():
                            h_distance_up = self.scenePos().y() - item.scenePos().y()
                            if h_distance_up < line_hdistance_up:
                                line_hdistance_up = h_distance_up
                                line_hitem_up = item

                    elif move_h == constants.down:
                        #   find line_hitem_up
                        if item.scenePos().y() + offect >= self.scenePos().y() + self.boundingRect().height():
                            h_distance_up = item.scenePos().y() + item.boundingRect().height() - self.scenePos().y()
                            if h_distance_up < line_hdistance_up:
                                line_hdistance_up = h_distance_up
                                line_hitem_up = item
                        #   find line_hitem_down
                        if item.y() + item.boundingRect().height() + offect >= self.y() + self.boundingRect().height():
                            h_distance_down = item.scenePos().y() + item.boundingRect().height() - \
                                              (self.scenePos().y() + self.boundingRect().height())
                            if h_distance_down < line_hdistance_down:
                                line_hdistance_down = h_distance_down
                                line_hitem_down = item

                    if move_v == constants.left:
                        #   find line_vitem_right
                        if item.scenePos().x() + item.boundingRect().width() - offect <= self.scenePos().x():
                            v_distance_right = self.scenePos().x() - (item.scenePos().x() + item.boundingRect().width())
                            if v_distance_right < line_vdistance_right:
                                line_vdistance_right = v_distance_right
                                line_vitem_right = item
                        #   find line_vitem_left
                        if item.x() - offect <= self.scenePos().x():
                            v_distance_left = self.scenePos().x() - item.scenePos().x()
                            if v_distance_left < line_vdistance_left:
                                line_vdistance_left = v_distance_left
                                line_vitem_left = item

                    elif move_v == constants.right:
                        #   find line_vitem_left
                        if item.scenePos().x() + offect >= self.scenePos().x() + self.boundingRect().width():
                            v_distance_left = item.scenePos().x() - (self.scenePos().x() + self.boundingRect().width())
                            if v_distance_left < line_vdistance_left:
                                line_vdistance_left = v_distance_left
                                line_vitem_left = item
                        #   find line_vitem_right
                        if item.scenePos().x() + item.boundingRect().width() + offect >= \
                                self.scenePos().x() + self.boundingRect().width():
                            v_distance_right = item.scenePos().x() + item.boundingRect().width() - \
                                               (self.scenePos().x() + self.boundingRect().width())
                            if v_distance_right < line_vdistance_right:
                                line_vdistance_right = v_distance_right
                                line_vitem_right = item

        #   calculate the closest hitem and vitem
        #       hitem
        if move_h == constants.up:
            if line_hitem_down and line_hitem_up:

                if line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() >= \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                        self.scene().sceneRect().right(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

                elif line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() < \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_up.scenePos().y(),
                        self.scene().sceneRect().right(),
                        line_hitem_up.scenePos().y())

            elif line_hitem_up and not line_hitem_down:

                hpath = QtWidgets.QGraphicsLineItem(
                    self.scene().sceneRect().left(),
                    line_hitem_up.scenePos().y(),
                    self.scene().sceneRect().right(),
                    line_hitem_up.scenePos().y())

        elif move_h == constants.down:
            if line_hitem_down and line_hitem_up:

                if line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() < \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                        self.scene().sceneRect().right(),
                        line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

                elif line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height() >= \
                        line_hitem_up.scenePos().y():
                    hpath = QtWidgets.QGraphicsLineItem(
                        self.scene().sceneRect().left(),
                        line_hitem_up.scenePos().y(),
                        self.scene().sceneRect().right(),
                        line_hitem_up.scenePos().y())

            elif line_hitem_down and not line_hitem_up:

                hpath = QtWidgets.QGraphicsLineItem(
                    self.scene().sceneRect().left(),
                    line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height(),
                    self.scene().sceneRect().right(),
                    line_hitem_down.scenePos().y() + line_hitem_down.boundingRect().height())

        #       vitem
        if move_v == constants.left:
            if line_vitem_left and line_vitem_right:

                if line_vitem_left.scenePos().x() > \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().top(),
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().bottom())

                elif line_vitem_left.scenePos().x() <= \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().top(),
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().bottom())

            elif line_vitem_left and not line_vitem_right:

                vpath = QtWidgets.QGraphicsLineItem(
                    line_vitem_left.scenePos().x(),
                    self.scene().sceneRect().top(),
                    line_vitem_left.scenePos().x(),
                    self.scene().sceneRect().bottom())

        elif move_v == constants.right:
            if line_vitem_left and line_vitem_right:

                if line_vitem_left.scenePos().x() <= \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().top(),
                        line_vitem_left.scenePos().x(),
                        self.scene().sceneRect().bottom())

                elif line_vitem_left.scenePos().x() > \
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width():
                    vpath = QtWidgets.QGraphicsLineItem(
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().top(),
                        line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                        self.scene().sceneRect().bottom())

            elif line_vitem_right and not line_vitem_left:

                vpath = QtWidgets.QGraphicsLineItem(
                    line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                    self.scene().sceneRect().top(),
                    line_vitem_right.scenePos().x() + line_vitem_right.boundingRect().width(),
                    self.scene().sceneRect().bottom())

        if hpath:
            if not self.hpath:
                self.hpath = hpath
                self.hpath.setPen(pen)
                self.scene().addItem(self.hpath)
            elif self.hpath is not hpath and self.hpath:
                if self.hpath in self.scene().items():
                    self.scene().removeItem(self.hpath)
                self.hpath = hpath
                self.hpath.setPen(pen)
                self.scene().addItem(self.hpath)
                self.hpath_flag = True
        elif self.hpath_flag:
            if self.hpath in self.scene().items():
                self.scene().removeItem(self.hpath)
                self.hpath = None

        if vpath:
            if not self.vpath:
                self.vpath = vpath
                self.vpath.setPen(pen)
                self.scene().addItem(self.vpath)
            elif self.vpath is not vpath and self.vpath:
                if self.vpath in self.scene().items():
                    self.scene().removeItem(self.vpath)
                self.vpath = vpath
                self.vpath.setPen(pen)
                self.scene().addItem(self.vpath)
                self.vpath_flag = True
        elif self.vpath_flag:
            if self.vpath in self.scene().items():
                self.scene().removeItem(self.vpath)
                self.vpath = None

        if self.resizing:
            self.mouse_update_node_size(event)
        else:
            super(AttributeWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.was_moved:
            self.was_moved = False
            if self.scene().view.mode == constants.MODE_NOOP:
                self.scene().history.store_history("Attribute Widget Moved")
        self.colliding_release(event)

        if self.vpath and self.vpath in self.scene().items():
            self.scene().removeItem(self.vpath)
        if self.hpath and self.hpath in self.scene().items():
            self.scene().removeItem(self.hpath)

        if self.resizing:
            self.mouse_update_node_size(event)
            if self.scene().view.mode == constants.MODE_NOOP:
                self.scene().history.store_history("Attribute Widget Size Changed")
        else:
            super(AttributeWidget, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event: 'QtGui.QContextMenuEvent') -> None:
        if self.context_flag:
            menu = QtWidgets.QMenu()
            menu.setStyleSheet(stylesheet.STYLE_QMENU)
            add_line_subwidget = menu.addAction("Add Line Subwidget")
            add_line_subwidget.setIcon(QtGui.QIcon(
                os.path.abspath(os.path.join(os.path.dirname(__file__),
                                             "../Resources/add_line_widget.PNG"))))
            add_subwidget = menu.addAction("Add Subwidget")
            add_subwidget.setIcon(
                QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                         "../Resources/add_widget.png"))))
            add_line_file = menu.addAction("Add Line File")
            add_line_file.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                           "../Resources/add_line_video.png"))))
            add_file = menu.addAction("Add File")
            add_file.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      "../Resources/add_video.png"))))
            add_line_view = menu.addAction("Add Line View")
            add_line_view.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                           "../Resources/sub view.png"))))
            add_view = menu.addAction("Add View")
            add_view.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      "../Resources/sub view.png"))))
            add_todo_line = menu.addAction("Add Todo Inline")
            add_todo_line.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                           "../Resources/Todo.png"))))
            add_todo = menu.addAction("Add Todo")
            add_todo.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                      "../Resources/Todo.png"))))
            move_up = menu.addAction("Move Up")
            move_up.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                     "../Resources/up.png"))))
            move_down = menu.addAction("Move Down")
            move_down.setIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                                       "../Resources/down.png"))))
            result = menu.exec(event.globalPos())

            if result == add_line_subwidget:
                self.add_new_subwidget(line=True, flag="attr")
            elif result == add_subwidget:
                self.add_new_subwidget(line=False, flag="attr")
            elif result == add_line_file:
                self.add_new_subwidget(line=True, flag="file")
            elif result == add_file:
                self.add_new_subwidget(line=False, flag="file")
            elif result == add_line_view:
                self.add_new_subwidget(line=True, flag="view")
            elif result == add_view:
                self.add_new_subwidget(line=False, flag="view")
            elif result == add_todo_line:
                self.add_new_subwidget(line=True, flag="todo")
            elif result == add_todo:
                self.add_new_subwidget(line=False, flag="todo")
            elif result == move_up and (isinstance(self.scene().itemAt(self.scene().view.mapToScene(event.pos()),
                                                                       QtGui.QTransform()),
                                                   (AttributeWidget, AttributeFile, SubConstituteWidget,
                                                    SimpleTextField))):
                self.move_up_widget(self.scene().itemAt(self.scene().view.mapToScene(event.pos()), QtGui.QTransform()))
            elif result == move_down and (isinstance(self.scene().itemAt(self.scene().view.mapToScene(event.pos()),
                                                                         QtGui.QTransform()),
                                                     (AttributeWidget, AttributeFile, SubConstituteWidget,
                                                      SimpleTextField))):
                self.move_down_widget(
                    self.scene().itemAt(self.scene().view.mapToScene(event.pos()), QtGui.QTransform()))
            self.context_flag = False

    def moveEvent(self, event: 'QtWidgets.QGraphicsSceneMoveEvent') -> None:
        super(AttributeWidget, self).moveEvent(event)
        if self.moving:
            self.colliding_detection()
        self.update_pipe_position()

    def serialize(self, attr_serialization=None):

        # attribute widget id
        attr_serialization.attr_id = self.id

        # geometry
        attr_serialization.size.append(self.size().width())
        attr_serialization.size.append(self.size().height())
        attr_serialization.position.append(self.scenePos().x())
        attr_serialization.position.append(self.scenePos().y())

        # contents
        attr_serialization.contents = self.attribute_widget.label_item.toHtml()

        # port
        self.true_input_port.serialize(attr_serialization.attr_port.add())
        self.false_input_port.serialize(attr_serialization.attr_port.add())
        self.true_output_port.serialize(attr_serialization.attr_port.add())
        self.false_output_port.serialize(attr_serialization.attr_port.add())

        # connections
        for next_attribute_widget in self.next_attribute:
            attr_serialization.next_attr_id.append(next_attribute_widget.id)
        for next_logic_widget in self.next_logic:
            attr_serialization.next_logic_id.append(next_logic_widget.id)
        for last_attribute_widget in self.last_attribute:
            attr_serialization.last_attr_id.append(last_attribute_widget.id)
        for last_logic_widget in self.last_logic:
            attr_serialization.last_logic_id.append(last_logic_widget.id)
        for i in range(len(self.attribute_sub_widgets)):
            attribute_sub_widget = self.attribute_layout.itemAt(i)
            from .sub_view import ProxyView
            from .todo import Todo
            if isinstance(attribute_sub_widget, AttributeWidget):
                attr_serialization.sub_attr.append(attribute_sub_widget.id)
            elif isinstance(attribute_sub_widget, AttributeFile):
                attribute_sub_widget.serialize(attr_serialization.file_serialization.add())
            elif isinstance(attribute_sub_widget, ProxyView):
                attribute_sub_widget.serialize(attr_serialization.subview_serialization.add())
            elif isinstance(attribute_sub_widget, Todo):
                attribute_sub_widget.serialize(attr_serialization.todo_serialization.add())
            elif isinstance(attribute_sub_widget, NoneWidget):
                attribute_sub_widget.serialize(attr_serialization.none_serialization.add())

        # sub scene
        if self.sub_scene:
            self.sub_scene.serialize(attr_serialization.sub_scene_serialization.add())

        # highlighter
        attr_serialization.highlighter = True if self.attribute_widget.label_item.pythonlighter else False

        # location
        attr_serialization.attr_location.append(self.item_row)
        attr_serialization.attr_location.append(self.item_column)
        attr_serialization.next_location.append(self.current_row)
        attr_serialization.next_location.append(self.current_column)

        # ui
        attr_serialization.self_attr_font_family = self.attribute_widget.label_item.font.family()
        attr_serialization.self_attr_font_size = self.attribute_widget.label_item.font.pointSize()
        attr_serialization.self_attr_color.append(self.attribute_widget.label_item.font_color.rgba())
        attr_serialization.self_attr_color.append(self.color.rgba())
        attr_serialization.self_attr_color.append(self.selected_color.rgba())
        attr_serialization.self_attr_color.append(self.border_color.rgba())
        attr_serialization.self_attr_color.append(self.selected_border_color.rgba())

        # flag
        attr_serialization.attr_flag.append(self.attribute_widget.label_item.font_flag)
        attr_serialization.attr_flag.append(self.attribute_widget.label_item.font_color_flag)
        attr_serialization.attr_flag.append(self.color_flag)
        attr_serialization.attr_flag.append(self.selected_color_flag)
        attr_serialization.attr_flag.append(self.border_flag)
        attr_serialization.attr_flag.append(self.selected_border_flag)

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        if flag:
            # added into current scene and view
            view.current_scene.addItem(self)
            view.attribute_widgets.append(self)
            # id and hashmap
            self.id = data.attr_id
            hashmap[data.attr_id] = self
            # geometry and contents
            self.setGeometry(data.position[0], data.position[1], data.size[0], data.size[1])
            self.attribute_widget.label_item.setHtml(data.contents)
            # ports
            self.true_input_port.deserialize(data.attr_port[0], hashmap, view, flag=True)
            self.false_input_port.deserialize(data.attr_port[1], hashmap, view, flag=True)
            self.true_output_port.deserialize(data.attr_port[2], hashmap, view, flag=True)
            self.false_output_port.deserialize(data.attr_port[3], hashmap, view, flag=True)
            # layout
            self.item_row = data.attr_location[0]
            self.item_column = data.attr_location[1]
            self.current_row = data.next_location[0]
            self.current_column = data.next_location[1]
            # highlighter
            if data.highlighter:
                self.attribute_widget.label_item.pythonlighter = \
                    PythonHighlighter(self.attribute_widget.label_item.document())
            # style
            font = QtGui.QFont()
            font.setFamily(data.self_attr_font_family)
            font.setPointSize(data.self_attr_font_size)
            self.attribute_widget.label_item.font = font
            self.attribute_widget.label_item.document().setDefaultFont(font)

            self.attribute_widget.label_item.font_color = QtGui.QColor()
            self.attribute_widget.label_item.font_color.setRgba(data.self_attr_color[0])
            self.attribute_widget.label_item.setDefaultTextColor(self.attribute_widget.label_item.font_color)

            self.color = QtGui.QColor()
            self.color.setRgba(data.self_attr_color[1])

            self.selected_color = QtGui.QColor()
            self.selected_color.setRgba(data.self_attr_color[2])

            self.border_color = QtGui.QColor()
            self.border_color.setRgba(data.self_attr_color[3])

            self.selected_border_color = QtGui.QColor()
            self.selected_border_color.setRgba(data.self_attr_color[4])

            self.attribute_widget.label_item.font_flag = data.attr_flag[0]
            self.attribute_widget.label_item.font_color_flag = data.attr_flag[1]

            self.color_flag = data.attr_flag[2]
            self.selected_color_flag = data.attr_flag[3]
            self.border_flag = data.attr_flag[4]
            self.selected_border_flag = data.attr_flag[5]

            # sub scene
            if data.sub_scene_serialization:
                # save scene and flag
                last_scene_flag = view.current_scene_flag
                last_scene = view.current_scene

                # sub scene
                from ..GraphicsView.scene import Scene
                from ..GraphicsView.view import TreeWidgetItem
                sub_scene_flag = TreeWidgetItem(
                    view.current_scene_flag,
                    (self.attribute_widget.label_item.toPlainText(),))
                sub_scene = Scene(sub_scene_flag, view, self)
                self.set_sub_scene(sub_scene)
                sub_scene_flag.setData(0, QtCore.Qt.ToolTipRole, sub_scene)

                view.current_scene = sub_scene
                view.current_scene_flag = sub_scene_flag

                sub_scene.deserialize(data.sub_scene_serialization[0], hashmap, view, True)
                sub_scene.deserialize(data.sub_scene_serialization[0], hashmap, view, False)

                # restore scene and flag
                view.current_scene = last_scene
                view.current_scene_flag = last_scene_flag

        return True
