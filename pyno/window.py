import pkg_resources
import pyglet
import pyperclip
from pyglet.window import Window
from pyglet import gl

from . import draw, initialCode, menu
from .process import Process
from .node import Node
from .field import Field
from .sub import Sub
from .codeEditor import CodeEditor
from .element import color_inverse
from .utils import font, x_y_pan_scale, point_intersect_quad, random_node_color


class PynoWindow(Window, Process):
    '''
    Visual interface for Process
    '''

    def __init__(self, config, filename=None, caption='Pyno', style=Window.WINDOW_STYLE_DEFAULT):
        Window.__init__(self, resizable=True, caption=caption, config=config, style=style)
        Process.__init__(self)
        self.set_minimum_size(320, 200)
        self.set_size(800, 600)

        # set window position to center
        screen = self.display.get_default_screen()
        self.set_location(screen.width // 2 - 400, screen.height // 2 - 300)

        pyglet.clock.schedule_interval(self.update, 0.016) # ~60fps
        pyglet.clock.schedule_interval(lambda x: self.info(), 1) # drop time arg
        pyglet.clock.schedule_interval(lambda x: self.autosave(), 30)

        self.active_nodes = []
        self.selected_nodes = []

        self.code_editor = None
        self.field = None
        self.node_drag = False
        self.select = False
        self.connection = False
        self.connecting_node = None
        self.nodes_check = 0

        self.w, self.c = (0, 0), (0, 0)
        self.mouse = (0, 0)
        self.pointer = (0, 0)
        self.line = ()
        self.pan_scale = [[0.0, 0.0], 1]

        self.batch = None
        self.info_label, self.pyno_logo, self.menu = None, None, None

        self.new_batch()

        if filename:
            # open auto-save or welcome-file
            welcome = pkg_resources.resource_filename('pyno', 'examples/welcome.pn')
            (self.load_pyno(filename) or self.load_pyno(welcome))

    def new_batch(self):
        self.batch = pyglet.graphics.Batch()
        self.info_label = pyglet.text.Label('BOOM!!', font_name=font,
                                            font_size=9, batch=self.batch,
                                            color=(200, 200, 255, 100),
                                            x=160, y=10, group=draw.uiGroup)
        # load pyno-logo in left bottom
        corner = pkg_resources.resource_stream('pyno', 'imgs/corner.png')
        pyno_logo_img = pyglet.image.load('dummyname', file=corner)
        self.pyno_logo = pyglet.sprite.Sprite(pyno_logo_img,
                                              batch=self.batch,
                                              group=draw.uiGroup)
        self.menu = menu.Menu(self)
        # line place-holder
        self.line = (draw.Line(self.batch), draw.Line(self.batch))

    def info(self, message=None):
        self.info_label.text = message or \
                                'fps:' + str(int(pyglet.clock.get_fps())) + \
                                ' active:' + str(len(self.active_nodes)) + \
                                ' run:' + str(self.running)

    def update(self, dt):
        self.global_scope['dt'] = dt

        # ---- Calculations ----

        self.nodes_update()

        if self.selected_nodes:
            for node in self.selected_nodes:
                node.make_active()
        else:
            # pointer over nodes
            nc = self.nodes_check
            self.nodes_check = nc + 1 if nc < len(self.nodes)-25 else 0
            for node in self.nodes[self.nodes_check:self.nodes_check+25]:
                node.intersect_point(self.pointer)

        if self.code_editor:
            if self.code_editor.intersect_point(self.pointer):
                self.code_editor.node.hover = True

        self.menu.update()

        # a bit strange to do drawing here, but it does better results here
        self.active_nodes = list(filter(lambda x: x.active, self.nodes))
        for node in self.active_nodes:
            node.render_base()

    def on_draw(self):
        # ---- BG ----

        pyglet.gl.glClearColor(0.14, 0.14, 0.14, 0)
        self.clear()

        # ---- PYNORAMA ----

        ps = self.pan_scale
        gl.glTranslatef(self.width / 2, self.height / 2, 0)
        gl.glScalef(ps[1], ps[1], ps[1])
        gl.glTranslatef(self.width / -2 + ps[0][0],
                        self.height / -2 + ps[0][1], 0.0)

        # ---- CURRENT LINK DRAW ----

        if self.connection:
            p = self.pointer
            cn = self.connecting_node
            n = self.connecting_node['node']

            if self.connecting_node['mode'] == 'input':
                start = n.put_pos_by_name(cn['put']['name'], 'inputs')
                self.line[0].redraw((start, n.y + n.ch + n.offset // 2),
                                    (start, n.y + n.ch + n.offset))
                self.line[1].redraw((start, n.y + n.ch + n.offset), p)

            elif self.connecting_node['mode'] == 'output':
                start = n.put_pos_by_name(cn['put']['name'], 'outputs')
                self.line[0].redraw((start, n.y - n.ch - n.offset // 2),
                                    (start, n.y - n.ch - n.offset))
                self.line[1].redraw((start, n.y - n.ch - n.offset), p)

        else:
            # line place-holder
            self.line[0].redraw((-9000, 9000), (-9000, 9010))
            self.line[1].redraw((-9000, 9010), (-9010, 9000))

        # ---- NODES ----

        self.batch.draw()

        for node in self.active_nodes:
            node.render_labels()

        if self.code_editor:
            self.code_editor.render()

        if self.select:
            draw.selector(self.w, self.c)

        # ---- GUI ----

        # reset camera position
        gl.glLoadIdentity()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse = (x, y)

        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())
        self.pointer = (x, y)

        if not self.selected_nodes:
            if self.code_editor:
                if self.code_editor.intersect_point(self.pointer):
                    if not self.code_editor.hover and not self.field:
                        self.push_handlers(self.code_editor)
                    self.code_editor.pan_scale = self.pan_scale
                    self.code_editor.screen_size = self.get_size()
                    self.code_editor.hover = True
                    self.code_editor.node.hover = True
                    return
            elif self.field:
                if self.field.intersect_point((x, y)):
                    self.field.pan_scale = self.pan_scale
                    self.field.screen_size = self.get_size()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.menu.click(x, y, button):
            return

        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())

        if button == 1:
            if self.field:
                self.pop_handlers()
                self.push_handlers()
                self.field = None
            if self.code_editor:
                if self.code_editor.intersect_point((x, y)):
                    return
                else:
                    if self.code_editor.hover:
                        self.pop_handlers()
                        self.push_handlers()
                    self.code_editor = None
            for node in self.nodes:
                if node.intersect_point((x, y)):
                    if (node in self.selected_nodes and
                            len(self.selected_nodes) > 1):
                        self.node_drag = True
                        return
                    else:
                        si = node.selectedInput['name'] != 'none'
                        so = node.selectedOutput['name'] != 'none'
                        if si or so:
                            self.pointer = (x, y)
                            self.connection = True
                            if si:
                                self.disconnect_node(node)
                            elif so:
                                self.connecting_node = \
                                    {'node': node,
                                     'put': node.selectedOutput,
                                     'mode': 'output'}
                            return
                        if isinstance(node, Node):
                            self.code_editor = CodeEditor(node)
                        elif isinstance(node, Field) and not self.field:
                            self.push_handlers(node)
                            self.field = node
                        elif isinstance(node, Sub):
                            self.code_editor = CodeEditor(node, highlighting=2)
                            if node.pwindow:
                                node.pwindow.set_visible(not node.pwindow.visible)
                        self.selected_nodes = [node]
                        self.node_drag = True
                        return
            self.select = True
            self.selectPoint = (x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())
        dx, dy = int(dx / self.pan_scale[1]), int(dy / self.pan_scale[1])

        if self.node_drag and buttons != 5:
            for node in self.selected_nodes:
                node.x += dx
                node.y += dy
                node.make_child_active()
        elif self.select:
            self.w = self.selectPoint
            self.c = (x, y)
        elif self.connection:
            self.pointer = (x, y)
            for node in self.nodes:
                node.intersect_point((x, y))

        if buttons == 4 or buttons == 5:
            self.pan_scale[0][0] += dx
            self.pan_scale[0][1] += dy

    def on_mouse_release(self, x, y, button, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.get_size())

        if button == 1:
            self.node_drag = False
            self.connection = False

            if self.select:
                select = []
                for node in self.nodes:
                    if point_intersect_quad((node.x, node.y),
                                            (self.c + self.w)):
                        select.append(node)
                        node.draw_color = color_inverse(node.color)
                self.selected_nodes = select
                self.w, self.c = (0, 0), (0, 0)
                self.select = False
            else:
                self.selected_nodes = []

            cn = self.connecting_node
            if cn:
                for node in self.nodes:
                    if node.intersect_point((x, y)):
                        if node != cn['node']:
                            if (node.selectedInput['name'] != 'none' and
                                    cn['mode'] == 'output'):
                                self.connect_out_to_in(node)
                            elif (node.selectedOutput['name'] != 'none' and
                                    cn['mode'] == 'input'):
                                self.connect_in_to_out(node)
                cn = self.connecting_node

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        di = 10
        max_zoom = 1

        ps = self.pan_scale
        zoom = scroll_y / di * ps[1]

        if ps[1] + zoom < max_zoom:
            ps[1] += zoom
            ps[0][0] -= ((self.width / -2 + x) / ps[1] * scroll_y) // di
            ps[0][1] -= ((self.height / -2 + y) / ps[1] * scroll_y) // di
        elif ps[1] < max_zoom:
            ps[1] = max_zoom
            ps[0][0] -= ((self.width / -2 + x) / 2 * scroll_y) // di
            ps[0][1] -= ((self.height / -2 + y) / 2 * scroll_y) // di
        else:
            ps[1] = max_zoom

    def on_key_press(self, symbol, modifiers):
        key = pyglet.window.key

        if modifiers == 2 and symbol == key.EQUAL:
            # double zoom
            self.pan_scale[1] = 2

        if not (self.code_editor or self.field):
            if symbol == key.N:
                self.nodes.append(Node(self, self.pointer[0], self.pointer[1], self.batch,
                                       random_node_color(), code=initialCode.node))

            elif symbol == key.O:
                self.nodes.append(Node(self, self.pointer[0], self.pointer[1], self.batch,
                                       random_node_color(), code=initialCode.open_node))

            elif symbol == key.F:
                self.nodes.append(Field(self, self.pointer[0], self.pointer[1], self.batch))

            elif symbol == key.S:
                self.nodes.append(Sub(self, self.pointer[0], self.pointer[1], self.batch,
                                      random_node_color()))

            elif symbol == key.R:
                for node in self.nodes:
                    if isinstance(node, Node):
                        node.reload()

            if modifiers & key.MOD_CTRL:
                if symbol == key.C:
                    self.copy_nodes()

                elif symbol == key.V:
                    self.paste_nodes()

            if symbol == key.DELETE:
                for node in self.selected_nodes:
                    node.make_child_active()
                    node.delete()
                    node.outputs = ()
                    del self.nodes[self.nodes.index(node)]
                    del node
                    print('Delete node')
                self.selected_nodes = []

            elif symbol == key.HOME:
                self.pan_scale = [[0.0, 0.0], 1]

            elif symbol == key.END:
                print(len(self.nodes))
                for node in self.selected_nodes:
                    print(str(node))

    def on_close(self, force=False):
        if (not self.caption == "Pyno") and (not force):  # is this the root/main window?
            return True
        for node in self.nodes:
            if isinstance(node, Sub) and node.pwindow:
                node.pwindow.on_close(force=True)
        self.autosave()
        self.close()

    def disconnect_node(self, node):
        n = node.connected_to
        for c in n:
            a = c['output']
            # if user clicked on input connection destroyed
            if c['input']['put']['name'] == node.selectedInput['name']:
                self.connecting_node = {'node': a['node'],
                                        'put': {'name': a['put']['name']},
                                        'mode': 'output'}
                del n[n.index(c)]
                for line in node.graphics['connections']:
                    for segment in line:
                        segment.delete()
                node.graphics['connections'] = list()
                return
        # if user clicked on output connecting wire created
        self.connecting_node = {'node': node,
                                'put': node.selectedInput,
                                'mode': 'input'}

    def connect_out_to_in(self, node):
        del self.connecting_node['mode']
        another = {'node': node,
                   'put': node.selectedInput}
        insert = {'output': self.connecting_node,
                  'input': another}

        # check if something already connected to put
        i, n = node.selectedInput, node.connected_to
        for inp in n:
            if inp['input']['put']['name'] == i['name']:
                del n[n.index(inp)]
                break

        if insert not in node.connected_to:
            node.connected_to.append(insert)
            self.connecting_node['node'].add_child(node)
            # print('Connect output to input')

    def connect_in_to_out(self, node):
        del self.connecting_node['mode']
        another = {'node': node,
                   'put': node.selectedOutput}
        insert = {'output': another,
                  'input': self.connecting_node}

        n = self.connecting_node['node']
        if insert not in n.connected_to:
            n.connected_to.append(insert)
            node.add_child(n)
            n.make_active()
            # print('Connect input to output')

    def new_pyno(self):
        Process.new_pyno(self)
        self.switch_to()
        self.code_editor = None
        self.new_batch()
        self.pan_scale = [[0.0, 0.0], 1]
        print('New window!')

    def autosave(self):
        if self.save_pyno(filepath='.auto-saved.pn'):
            self.info('auto-saved')

    def copy_nodes(self):
        data = self.serializer.serialize(self.selected_nodes, anchor=self.pointer)
        pyperclip.copy(data)

    def paste_nodes(self):
        data = pyperclip.paste()
        self.load_data(data, anchor=self.pointer)
