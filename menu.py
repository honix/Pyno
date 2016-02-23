import pyglet
from tkinter import Tk, filedialog
import clipboard

from node import Node
from field import Field
from draw import uiGroup


def copy_nodes(window, data=False):
    x, y = (0, 0) if data else (window.pointer[0], window.pointer[1])
    nodes = window.nodes if data else window.selectedNodes
    buff = []
    for node in nodes:
        if isinstance(node, Node):
            buff.append({'type': 'node',
                         'x': node.x - x,
                         'y': node.y - y,
                         'size': node.editorSize,
                         'color': node.color,
                         'code': node.code,
                         'connects': node.get_con_id(),
                         'parent': node.id})
        elif isinstance(node, Field):
            buff.append({'type': 'field',
                         'x': node.x - x,
                         'y': node.y - y,
                         'size': (node.w, node.h),
                         'code': node.document.text,
                         'connects': node.get_con_id(),
                         'parent': node.id})
    if data:
        return str(buff)
    clipboard.copy(str(buff))
    print('Copy ' + str(len(buff)) + ' nodes')


def paste_nodes(window, data=None):
    x, y = (0, 0) if data else (window.pointer[0], window.pointer[1])
    buff = []
    try:
        paste = eval(data) if data else eval(clipboard.paste())
        for node in paste:
            if node['type'] == 'node':
                buff.append([Node(node['x'] + x,
                                  node['y'] + y,
                                  window.batch,
                                  node['color'],
                                  node['code'],
                                  node['connects'],
                                  node['size']),
                             node['parent']])
            elif node['type'] == 'field':
                buff.append([Field(node['x'] + x,
                                   node['y'] + y,
                                   window.batch,
                                   node['code'],
                                   node['connects'],
                                   node['size']),
                             node['parent']])
    except:
        print('Wrong paste!')
    finally:
        for node in buff:
            node[0].reconnect(buff)
            window.nodes.append(node[0])
        print('Paste ' + str(len(buff)) + ' nodes')


def load(file=None):
    if file:
        file_path = file
    else:
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=(
                                            ('Pyno files', '*.pn'),
                                            ('All files', '*.*')))
        root.destroy()
    file = open(file_path, 'r')
    data = file.read()
    file.close()
    return data


def save(data):
    root = Tk()
    root.withdraw()
    s = filedialog.asksaveasfilename(defaultextension='pn',
                                     initialfile='pyno_file.pn',
                                     filetypes=(
                                         ('Pyno files', '*.pn'),
                                         ('All files', '*.*')))
    root.destroy()
    file = open(s, 'w')
    file.write(data)
    file.close()


class Menu:
    # Save-load controls

    offset = 10

    def __init__(self, window):
        self.window = window

        save_load_img = pyglet.image.load('imgs/save_load_32.png')
        self.save_load = pyglet.sprite.Sprite(
                save_load_img,
                x=800-save_load_img.width-self.offset, y=self.offset,
                batch=window.batch, group=uiGroup)

        self.save_load.opacity = 100

    def click(self, x, y):
        if self.update():
            s = self.save_load
            if x < s.x + s.width / 2:
                save(copy_nodes(self.window, data=True))
                print('File saved')
            else:
                self.window.new_pyno()
                paste_nodes(self.window, load())
                print('File loaded')
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

