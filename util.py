import random
import platform

OS = {
    'darwin': 'osx',
    'windows': 'windows',
    'linux': 'linux'
}.get(platform.system().lower(), 'linux')

def randstring(len):
    r = []

    for i in range(len):
        r.append(random.choice('abcdefghijklmnopqrstuvwxyz1234567890'))
    
    return ''.join(r)

FUNCS_TO_INJECT = {}

def inject_func(fnc):
    FUNCS_TO_INJECT[fnc.__name__] = fnc
    def inner(*args, **kwargs):
        return fnc(*args, **kwargs)
    return inner

def format_args_for_py(**kwargs):
    return ','.join(['%s=%s' % (k,v) for k,v in kwargs.items()])