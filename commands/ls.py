import os
from ..util import OS, randstring, inject_func, format_args_for_py

from .base import MaernCommand

@inject_func
def __maern_ls_injected(**options):
    file_list = list(os.scandir(os.getcwd()))

    filtered = []

    for f in file_list:
        if options.get('show_hidden', False):
            pass
        
        filtered.append(f)

    if not options.get('format_json', False)\
        and not options.get('as_string', False):
        return filtered
    elif options.get('format_json', False):
        return [{
            'path': e.path,
            'name': e.name,
            'is_dir': False
        } for e in filtered]
    elif options.get('as_string', False):
        return "File Listing for: {cwd}\n{files}".format(
            cwd = os.getcwd(),
            files = '\n'.join("{f.name:20}{stat.st_size:>10}KB{stat.st_ctime:>25}".format(f=f, stat=f.stat()) for f in filtered)
        )

class ls(MaernCommand):
    command = 'ls'

    help = """
        LS Command: Stop being an idiot you know what ls is godddddd
    """

    options = ['long', 'hidden', 'files', 'dirs', 'json']

    @classmethod
    def execute(cls, *args, as_string=False):
        only_files = 'f' in args or 'files' in args

        formatted_args = format_args_for_py(**dict(
            show_long = 'l' in args or 'long' in args,
            show_hidden = 'h' in args or 'hidden' in args,
            only_files = only_files,
            only_dirs = not only_files and ('d' in args or 'dirs' in args),
            format_json = 'j' in args or 'json' in args,
            as_string = as_string
        ))

        r = randstring(10)
        return '_ls_%s = __maern_ls_injected(%s)' % (r, formatted_args), '_ls_%s' % r
