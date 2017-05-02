MaernCommands = {}

class MaernCommandMetaClass(type):
    def __new__(*args, **kwargs):
        obj = type.__new__(*args, **kwargs)
        if hasattr(obj, 'command') and obj.command is not None:
            MaernCommands[obj.command] = obj
        return obj

class MaernCommand(metaclass=MaernCommandMetaClass):
    def __init__(self):
        pass
