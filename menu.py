import pyglet
import pyperclip
from tkinter import Tk, filedialog
import json
from collections import OrderedDict

from node import Node
from field import Field
from sub import Sub
from draw import uiGroup


# def copy_nodes(window, data=False):
#     x, y = (0, 0) if data else (window.pointer[0], window.pointer[1])
#     nodes = window.nodes if data else window.selected_nodes
#     buff = []
#     for node in nodes:
#         if isinstance(node, Node):
#             buff.append(OrderedDict({'type': 'node',
#                          'x': node.x - x,
#                          'y': node.y - y,
#                          'size': node.editor_size,
#                          'color': node.color,
#                          'code': node.code,
#                          'connects': node.get_con_id(),
#                          'parent': node.id}))
#         elif isinstance(node, Field):
#             buff.append(OrderedDict({'type': 'field',
#                          'x': node.x - x,
#                          'y': node.y - y,
#                          'size': (node.w, node.h),
#                          'code': node.document.text,
#                          'connects': node.get_con_id(),
#                          'parent': node.id}))
#         elif isinstance(node, Sub):
#             buff.append(OrderedDict({'type': 'sub',
#                          'x': node.x - x,
#                          'y': node.y - y,
#                          'size': node.editor_size,
#                          'color': node.color,
#                          'code': node.code,
#                          'connects': node.get_con_id(),
#                          'parent': node.id}))
#     if data:
#         return json.dumps(buff, indent=4)
#     pyperclip.copy(json.dumps(buff, indent=4))
#     window.info('Copied ' + str(len(buff)) + ' nodes')


# def paste_nodes(window, data=None):
#     x, y = (0, 0) if data else (window.pointer[0], window.pointer[1])
#     buff = []
#     try:
#         data = data if data else pyperclip.paste()
#         try:
#             paste = json.loads(data)
#             #paste = json.loads(data, object_pairs_hook=OrderedDict)
#         except ValueError:
#             print("Attention: pyno-file still uses the old save format, please re-save soon!")
#             paste = eval(data)
#         for node in paste:
#             if node['type'] == 'node':
#                 buff.append([Node(window, 
#                                   node['x'] + x,
#                                   node['y'] + y,
#                                   window.batch,
#                                   tuple(node['color']),
#                                   node['code'],
#                                   node['connects'],
#                                   node['size']),
#                              node['parent']])
#             elif node['type'] == 'field':
#                 buff.append([Field(node['x'] + x,
#                                    node['y'] + y,
#                                    window.batch,
#                                    node['code'],
#                                    node['connects'],
#                                    node['size']),
#                              node['parent']])
#             elif node['type'] == 'sub':
#                 buff.append([Sub(node['x'] + x,
#                                   node['y'] + y,
#                                   window.batch,
#                                   tuple(node['color']),
#                                   node['code'],
#                                   node['connects'],
#                                   node['size']),
#                              node['parent']])
#     except Exception as ex:
#         print('Wrong paste:', ex)
#         return False
#     finally:
#         for node in buff:
#             node[0].reconnect(buff)
#             window.nodes.append(node[0])
#         if data:
#             window.info('Loaded ' + str(len(buff)) + ' nodes!')
#         else:
#             window.info('Pasted ' + str(len(buff)) + ' nodes!')
#         return True


def load(file=None):
    if file:
        path = file
    else:
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename(filetypes=(
                                            ('Pyno files', '*.pn'),
                                            ('All files', '*.*')))
        root.destroy()
    try:
        file = open(path, 'r')
    except Exception as ex:
        print('Can\'t load file:', ex)
        return False
    data = file.read()
    file.close()
    print('File', path, 'saved!')
    return data


def save(data, initialfile='pyno_file.pn'):
    root = Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename(defaultextension='pn',
                                        initialfile=initialfile,
                                        filetypes=(
                                            ('Pyno files', '*.pn'),
                                            ('All files', '*.*')))
    root.destroy()
    try:
        file = open(path, 'w')
    except Exception as ex:
        print('Can\'t save file:', ex)
        return False
    file.write(data)
    file.close()
    print('File', path, 'saved!')
    return True


def autosave(data):
    try:
        file = open('.auto-saved.pn', 'w')
    except:
        return False
    file.write(data)
    file.close()
    return True


class Menu:
    '''
    Save-load controls
    '''

    offset = 10

    def __init__(self, window):
        self.window = window

        save_load_img = pyglet.image.load('imgs/save_load_32.png')
        self.save_load = pyglet.sprite.Sprite(
                save_load_img,
                x=800-save_load_img.width-self.offset, y=self.offset,
                batch=window.batch, group=uiGroup)

        self.save_load.opacity = 100

    def click(self, x, y, button=1):
        if self.update():
            s = self.save_load
            # RUN/PAUSE
            if x < s.x + (s.width / 3):
                if button == 1:
                    if not self.window.running:
                        self.window.running = -1  # -1: run continously
                    else:
                        self.window.running = 0   #  0: pause/stop
                elif (button == 4) and not self.window.running:
                    self.window.running = 1       #  n: do n steps
                    self.window.nodes_update()
                return True
            # SAVE
            if x < s.x + (s.width * 2 / 3):
                save(copy_nodes(self.window, data=True), self.window.filename)
            # LOAD
            else:
                loaded = load()
                if loaded:
                    self.window.new_pyno()
                    paste_nodes(self.window, loaded)
            return True

    def update(self):
        self.save_load.x = self.window.width - self.save_load.width - self.offset
        s = self.save_load
        if s.x < self.window.mouse[0] < s.x + s.width and \
           s.y < self.window.mouse[1] < s.y + s.height:
            s.opacity = 255
            return True
        s.opacity = 100
        return False

