import re
import os
import struct
import json
import code
import random
import subprocess

import socket

from .util import randstring, FUNCS_TO_INJECT

from . import commands
from .commands.base import MaernCommands

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg.encode()
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]

    print("ML", msglen)
    # Read the message data
    return recvall(sock, msglen).decode()

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


class Modes(object):
    NormalSingle = 0
    NormalMulti = 1
    CommandMode = 2

class PathEnv(list):
    def append(self, path_str):
        pass
    
    def __add__(self, rhs):
        pass

class Environment(object):
    def __init___(self):
        self.env = os.env.copy()

    def set_path_env(self, value):
        pass
    
    def get_path_env(self):
        return self.env['path']

    def __setitem__(self, item, value):
        lower_item = item.lower()

        if hasattr(self, 'set_{0}_env'.format(lower_item)):
            getattr(self, 'set_{0}_env'.format(lower_item))(value)
        else:
            self.env[item] = value
    
    def __getitem__(self, item):
        lower_item = item.lower()

        if hasattr(self, 'get_{0}_env'.format(lower_item)):
            return getattr(self, 'get_{0}_env'.format(lower_item))()
        else:
            return self.env[item]

class Process(object):
    def __init__(self):
        self.pid = None
        self.status = None
        self.output = None
        self.input = None
        self.error = None

    def kill(self):
        pass

class Buffer(object):
    def __init__(self):
        self.buffer_limit = 10000
        self.buffer = []


class Session(object):
    def __init__(self):
        self.buffer = Buffer()

    @property
    def environment(self):
        pass
    
    @property
    def processes(self):
        pass


class MyI(code.InteractiveInterpreter):
    latest = None
    full = []

    def write(self, data):
        print(data)
        self.latest = data
        self.full.append(data)

import contextlib
from io import StringIO
@contextlib.contextmanager
def capture():
    import sys
    oldout,olderr = sys.stdout, sys.stderr
    try:
        out=[StringIO(), StringIO()]
        sys.stdout,sys.stderr = out
        yield out
    finally:
        sys.stdout,sys.stderr = oldout, olderr
        out[0] = out[0].getvalue()
        out[1] = out[1].getvalue()

rem = re.compile("\<(.*)\>")

def parse_command(command):
    matches = rem.search(command)

    in_string_pos = []

    quote_match = ''
    prev_char = ''
    in_quotes = 0
    index = 0
    quote_started_at = -1
    for c in command:
        if c in "\"'" and prev_char != '\\':
            if in_quotes and quote_match == c:
                in_quotes = False
                quote_match = ''
                in_string_pos.append((quote_started_at, index))
            else:
                in_quotes = True
                quote_match = c
                quote_started_at = index

        prev_char = c
        index += 1
    
    if matches is not None:
        ret = []
        ind = 0
        for v in matches.groups():
            ret.append({
                'mode': 'cmd',
                'index': ind,
                'match': matches.span(ind),
                'in_string': any([x[0] < matches.start(ind) < x[1] for x in in_string_pos]),
                'command': v.strip()
            })
            ind += 1
        ret.append({
            'mode': 'python',
            'command': command
        })

        return ret
    else:
        return [{'mode': 'python', 'command': command}]

def start_server():
    host = '127.0.0.1'
    port = 5000

    srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv_socket.bind((host, port))

    srv_socket.listen(1)

    conn, addr = srv_socket.accept()

    ii = MyI()
    imports_c = code.compile_command('import os')
    ii.runcode(imports_c)

    for fname, fnc in FUNCS_TO_INJECT.items():
        ii.locals[fname] = fnc

    while True:
        data = recv_msg(conn)

        if not data:
            break
        
        #print("RECEIVED", data)
        data_obj = json.loads(data)

        command = data_obj['command']

        if data_obj['mode'] == Modes.CommandMode:
            if command.startswith('cd'):
                command = '<%s>' % command.strip('\r\n')
            else:
                command = 'print("""<%s>""")' % command.strip('\r\n')

        results = parse_command(command)

        """cmd_map = {
            'ls': ls.execute,
            'dir': ls,
            'cd': cd
        }"""

        cmd_results = []
        for result in results:
            if result['mode'] == 'cmd':
                if result['command'].split(' ')[0] in MaernCommands:
                    fn = MaernCommands[result['command'].split(' ')[0]].execute
                    pre, post = fn(*[r.lstrip('-') for r in result['command'].split(' ')], as_string=result['in_string'])

                    _cobj = code.compile_command(pre)
                    ii.runcode(_cobj)

                    if result['in_string']:
                        post = ii.locals[post]

                    #cmd_results.append(post.replace('\\\\n', '\\\\\\\\n').replace('\\\\r', '\\\\\\\\r'))
                    cmd_results.append(post.replace('\\n', '\\\\n').replace('\\r', '\\\\r'))
                else:
                    cr = subprocess.run(result['command'].split(' '), shell=True, stdout=subprocess.PIPE) #obv needs work LOL
                    cmd_results.append(cr.stdout.decode('utf-8').replace('\n', '\\\\\\\\n').replace('\r', '\\\\\\\\r'))
            elif result['mode'] == 'python':
                pcm = result['command']
                rcm = pcm

                for r in cmd_results:
                    rcm = rem.sub(r, rcm, count=1)
                
                try:
                    cobj = code.compile_command(rcm.replace('\\\\r','\\r').replace('\\\\n', '\\n').replace(':\\', ':\\\\'))
                except SyntaxError as e:
                    prepped_response = {
                        'result': e.msg,
                        'cwd': os.getcwd()
                    }
                else:
                    with capture() as out:
                        ii.runcode(cobj)

                        res = out

                    print("OUT", res)

                    prepped_response = {
                        'result': res[0] if res[0] is not None else ' ',
                        'cwd': os.getcwd()
                    }

                send_msg(conn, json.dumps(prepped_response))

    conn.close()


if __name__ == '__main__':
    start_server()