import os

from .base import MaernCommand

from .ls import ls

class cd(MaernCommand):
    command = 'cd'

    @classmethod
    def execute(cls, *args, as_string=False):
        print("CD",args)
        os.chdir(args[1])
        return ls.execute('', as_string=as_string)