"""
The Serialization base class
"""


class Serializable:
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data, hashmap: dict, view=None, flag=True):
        raise NotImplemented()
