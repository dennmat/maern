import importlib
from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f)]

for a in __all__:
    importlib.import_module('.%s' % a, 'maern.commands')