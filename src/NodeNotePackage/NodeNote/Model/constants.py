"""
The model parameters.
"""

import os

from PyQt5.QtWidgets import QGraphicsItem
from PyQt5 import QtWidgets, QtGui, QtCore

# === DIR ===
work_dir = os.path.join(os.path.dirname(__file__), "../")

# === UI ===
# attribute widget ui
input_text_font = QtWidgets.QApplication([]).font()
input_text_font_color = QtGui.QColor(0, 0, 0, 255)
attribute_color = QtGui.QColor(252, 165, 44, 255)
attribute_selected_color = QtGui.QColor(255, 255, 255, 30)
attribute_border_color = QtGui.QColor(46, 57, 66, 255)
attribute_selected_border_color = QtGui.QColor(254, 207, 42, 255)
attribute_width_flag = -1
# logic widget ui
logic_background_color = QtGui.QColor(240, 251, 158, 255)
logic_selected_background_color = QtGui.QColor(255, 255, 255, 30)
logic_border_color = QtGui.QColor(46, 57, 66, 255)
logic_selected_border_color = QtGui.QColor(254, 207, 42, 255)
# pipe widget ui
pipe_width = 2
pipe_color = QtGui.QColor(225, 192, 241, 255)
pipe_selected_color = QtGui.QColor(0, 153, 121, 255)
pipe_font = QtWidgets.QApplication([]).font()
pipe_font_color = QtGui.QColor(0, 0, 0, 255)
# port widget ui
port_width = 10.0
port_color = QtGui.QColor(245, 237, 171, 255)
port_border_color = QtGui.QColor(118, 184, 182, 255)
port_hovered_color = QtGui.QColor(118, 184, 182, 255)
port_hovered_border_color = QtGui.QColor(99, 180, 255, 255)
port_activated_color = QtGui.QColor(14, 45, 59, 255)
port_activated_border_color = QtGui.QColor(107, 166, 193, 255)
# draw widget ui
draw_color = QtGui.QColor(QtCore.Qt.red)
draw_pen_width = 10
# background image
background_image_path = os.path.abspath(os.path.join(work_dir, "Resources/Images/background_tree.svg"))
# view flag
view_line_flag = True
view_undo_flag = True
view_flowing_flag = True
# scene flag
scene_background_image_flag = False
# style
style_path = os.path.abspath(os.path.join(work_dir, "Resources/Stylesheets/cute_style.qss"))

# === DEBUG ===
DEBUG_EFFECT_SNOW = False
DEBUG_TUPLE_NODE_SCALE = False
DEBUG_VIEW_CHANGE_SCALE = False
DEBUG_DRAW_PIPE = False
DEBUG_TEXT_CHANGED = False
DEBUG_PYTHON_SYNTAXHIGHTLIGHTER = False
DEBUG_RICHTEXT = False
DEBUG_CUT_LINE = False
DEBUG_COLLIDING = False
DEBUG_HISTORY = False
DEBUG_DESERIALIZE = False
DEBUG_FONT = False
DEBUG_FILE_SAVE = False
DEBUG_ATTRIBUTE_INDEX = False
DEBUG_MARKDOWN = False

# === DRAW STACK ORDER ===
Z_VAL_PIPE = 2
Z_VAL_PIPE_DONE = 4
Z_VAL_NODE = 3
Z_VAL_PORT = 3
Z_VAL_CUTLINE = 5
Z_VAL_CONTAINERS = 6

# === NODE ===
NODE_WIDTH = 150
NODE_HEIGHT = 70
NODE_LAYOUT_MARGINS = 5
NODE_ICON_SIZE = 24
NODE_SEL_COLOR = (255, 255, 255, 30)
NODE_SEL_BORDER_COLOR = (254, 207, 42, 255)

# === ITEM CACHE MODE ===
ITEM_CACHE_MODE = QGraphicsItem.DeviceCoordinateCache

# === NODE TYPE ===
INPUT_NODE_TYPE = 0
OUTPUT_NODE_TYPE = 1

# === DRAW LINE ===
MODE_NOOP = 1
MODE_PIPE_DRAG = 2
MODE_PIPE_CUT = 3
MODE_CONTAINER = 4

# === PIPE ===
PIPE_STATUS_NEW = 0
PIPE_STATUS_CHANGE = 1

# === PIPE START STATUS ===
INPUT_NODE_START = 0
OUTPUT_NODE_START = 1

# === COLLIDING ===
COLLIDING_ATTRIBUTE = 0
COLLIDING_PIPE = 1
COLLIDING_NONE = 2

# === PIPE MOVE ===
PIPE_FIRST = 0
PIPE_MOVEING = 1
PIPE_COMMON = 2
PIPE_UPDATE = 3

# === MOVE ===
down = 0
up = 1
left = 2
right = 3


def init_path(path):
    """
    Init work dir

    Agrs:
        paht: work dir.

    """
    global work_dir
    global background_image_path
    global style_path

    work_dir = path
    background_image_path = os.path.abspath(os.path.join(work_dir, "Resources/Images/background_tree.svg"))
    style_path = os.path.abspath(os.path.join(work_dir, "Resources/Stylesheets/cute_style.qss"))
