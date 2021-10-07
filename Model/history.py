from Model import serialize_pb2
from PyQt5 import QtGui, QtCore


class History:
    def __init__(self, view):
        self.view = view

        self.history_stack = []
        self.history_current_step = -1
        self.history_limit = 50

    def undo(self):
        if self.history_current_step > 0:
            self.history_current_step -= 1
            self.restore_history()

    def redo(self):
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_current_step += 1
            self.restore_history()

    def store_history(self, desc):
        if self.history_current_step + 1 < len(self.history_stack):
            self.history_stack = self.history_stack[0: self.history_current_step]

        if self.history_current_step + 1 >= self.history_limit:
            self.history_stack = self.history_stack[1:]
            self.history_current_step -= 1

        hs = self.create_history_stamp(desc)
        self.history_stack.append(hs)
        self.history_current_step += 1

    def restore_history(self):
        self.restore_history_stamp(self.history_stack[self.history_current_step])

    def create_history_stamp(self, desc):
        view_serialization = serialize_pb2.ViewSerialization()
        current_scene_serialization = view_serialization.scene_serialization.add()
        self.view.current_scene.serialize(current_scene_serialization)
        history_stamp = {
            'desc': desc,
            'snapshot': current_scene_serialization
        }
        return history_stamp

    def restore_history_stamp(self, history_stamp):
        # Delete items
        for item in self.view.current_scene.items():
            item.setSelected(True)
        self.view.delete_widgets(QtGui.QKeyEvent(QtGui.QKeyEvent.KeyPress, QtCore.Qt.Key_Delete, QtCore.Qt.NoModifier),
                                 history_flag=True)

        # Serialization
        self.view.current_scene.deserialize(history_stamp['snapshot'], hashmap={}, view=self.view, flag=True)
        self.view.current_scene.deserialize(history_stamp['snapshot'], hashmap={}, view=self.view, flag=False)
