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
        history_stamp = {
            'desc': desc,
            'snapshot': self.view.serialize()
        }
        return history_stamp

    def restore_history_stamp(self, history_stamp):
        self.view.deserialize(history_stamp['snapshot'], hashmap={}, view=self.view, flag=True)
