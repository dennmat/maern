import os
import json
import time
import struct
import socket

import subprocess

import pyglet

from pyglet2d import Shape

window = pyglet.window.Window(1024, 768, resizable=True)

label = pyglet.text.Label('Hello, world',
                        font_name='Consolas',
                        font_size=12,
                        x=0, y=window.height,
                        multiline=True,
                        width=window.width,
                        anchor_x='left', anchor_y='top')

input_area = Shape.rectangle([[100, 30], [window.width, 0]], color=(50, 50, 50))
mode_area = Shape.rectangle([[0, 30], [100, 0]], color=(104, 209, 250))
text_input = pyglet.text.Label()

mode_label = pyglet.text.Label('Py Mixed',
                                font_name='Consolas',
                                font_size=12,
                                x = 50,
                                y = 17,
                                anchor_x='center', anchor_y='center',
                                bold=True,
                                color=(20, 40, 150, 255))

cwd_label = pyglet.text.Label('',
                            font_name='Consolas',
                            font_size=12,
                            x = window.width - 5,
                            y = window.height- 5,
                            anchor_x='right', anchor_y='top',
                            bold=True,
                            color=(220, 220, 220, 255))

document = pyglet.text.document.FormattedDocument('A')
document.set_style(0,1, dict(font_name='Consolas', font_size=12, color=(240, 240, 240, 240), bold=True))
layout = pyglet.text.layout.IncrementalTextLayout(document, window.width - 10, 25, multiline=True)
layout.x = 110
document.delete_text(0,1)
caret = pyglet.text.caret.Caret(layout, color=(240, 240, 240))
window.push_handlers(caret)


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

@window.event
def on_resize(width, height):
    label.width = width
    label.y = height

    layout.width = width - 10

    input_area = Shape.rectangle([[100, 30], [window.width-100, 0]], color=(50, 50, 50))

@window.event
def on_draw():
    window.clear()
    label.draw()
    input_area.draw()
    mode_area.draw()
    layout.draw()
    cwd_label.draw()
    mode_label.draw()

class Modes(object):
    NormalSingle = 0
    NormalMulti = 1
    CommandMode = 2

class ClockTimer(pyglet.event.EventDispatcher):
    def tick(self):
        self.dispatch_event('on_update')
    
ClockTimer.register_event_type('on_update')

class Observer(object):
    def __init__(self, subject):
        subject.push_handlers(self)
        

class Client(Observer):
    def __init__(self, subject):
        super(Client, self).__init__(subject)
        host = '127.0.0.1'
        port = 5000

        self.history = []
        self.history_index = 0 #0 = new ... 1 = latest 2... older N oldest

        self.mode = Modes.NormalSingle

        self.cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.cl_socket.connect((host, port))
            self.cl_socket.setblocking(0)
        except:
            subprocess.Popen(["python", "server.py"])
            time.sleep(1)
            self.cl_socket.connect((host, port))
            self.cl_socket.setblocking(0)

    def on_update(self):
        try:
            response = recv_msg(self.cl_socket)
        except socket.timeout as e:
            if e.args[0] != 'timed out':
                print("SOCKET ERROR: ", e)
            else:
                pass
        except socket.error as e:
            pass # print ("SOCKET ERROR", e)
        else:
            if len(response) == 0:
                print("SERVER SHUT DOWN!")
            else:
                dataload = json.loads(response)
                label.text = dataload['result']
                cwd_label.text = dataload['cwd']

    def on_key_release(self, symbol, modifiers):
        if symbol == pyglet.window.key.ENTER:
            if self.mode == Modes.NormalMulti and not (modifiers & pyglet.window.key.MOD_CTRL):
                return

            command = document.text

            if self.history_index == 0:
                self.history.append({
                    "command": command.lstrip('\n'),
                    "mode": self.mode
                })
            
            self.history_index = 0
            
            send_msg(self.cl_socket, json.dumps({
                "command": command if command.endswith('\n') else "%s\n" % command,
                "mode": self.mode
            }))

            document.delete_text(0, len(document.text))
        elif symbol == pyglet.window.key.UP:
            if self.mode == Modes.NormalMulti and not (modifiers & pyglet.window.key.MOD_CTRL):
                return
            self.history_index += 1

            if self.history_index > len(self.history):
                self.history_index = 0
                document.text = ""
            else:
                document.text = self.history[-(self.history_index)]['command']
                self.switch_mode(self.history[-(self.history_index)]['mode'])
                caret.position = len(document.text) - 1
        elif symbol == pyglet.window.key.DOWN:
            if self.mode == Modes.NormalMulti and not (modifiers & pyglet.window.key.MOD_CTRL):
                return
            self.history_index -= 1

            if self.history_index < 0:
                self.history_index = 0
                document.text = ""
            else:
                document.text = self.history[-(self.history_index)]['command']
                self.switch_mode(self.history[-(self.history_index)]['mode'])
                caret.position = len(document.text) - 1
        elif symbol == pyglet.window.key.TAB:
            next_mode = Modes.NormalSingle

            if self.mode == Modes.NormalSingle:
                next_mode = Modes.NormalMulti
            elif self.mode == Modes.NormalMulti:
                next_mode = Modes.CommandMode

            self.switch_mode(next_mode)
    
    def ns_switch_mode(self, new_mode):
        global mode_area, input_area
        self.mode = Modes.NormalSingle
        mode_label.text = 'Py Single'
        mode_label.y = 17
        input_area = Shape.rectangle([[100, 30], [window.width, 0]], color=(50, 50, 50))
        layout.y = 0
        layout.height = 25
        mode_area = Shape.rectangle([[0, 30], [100, 0]], color=(104, 209, 250))
    
    def nm_switch_mode(self, new_mode):
        global mode_area, input_area
        self.mode = Modes.NormalMulti
        mode_label.text = 'Py Multi'
        mode_area = Shape.rectangle([[0, 130], [100, 100]], color=(209, 104, 250))
        mode_label.y = 117
        input_area = Shape.rectangle([[100, 130], [window.width, 0]], color=(50, 50, 50))
        layout.y = 0
        layout.height = 125
    
    def cm_switch_mode(self, new_node):
        global mode_area, input_area
        self.mode = Modes.CommandMode
        mode_label.text = '<CMD>'
        mode_label.y = 17
        input_area = Shape.rectangle([[100, 30], [window.width, 0]], color=(50, 50, 50))
        layout.y = 0
        layout.height = 25
        mode_area = Shape.rectangle([[0, 30], [100, 0]], color=(220, 89, 106))
    
    def switch_mode(self, new_mode):
        if new_mode == self.mode:
            return

        if new_mode == Modes.NormalSingle:
            self.ns_switch_mode(new_mode)
        elif new_mode == Modes.NormalMulti:
            self.nm_switch_mode(new_mode)
        elif new_mode == Modes.CommandMode:
            self.cm_switch_mode(new_mode)

    def on_command_send(self):
        pass
    
    def __del__(self):
        self.cl_socket.close()

timer = ClockTimer()

def update(s):
    timer.tick()

pyglet.clock.schedule_interval(update, 1/30.0)

client = Client(timer)

window.push_handlers(client)

pyglet.app.run()