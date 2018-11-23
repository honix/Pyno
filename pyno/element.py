import pyglet
from pyglet import gl

from pyno.draw import Line, Quad
from pyno.utils import font, centered


# some colors functions
def color_select(color):
    '''Color for hover'''
    return tuple(map(lambda c: int(c * 0.65), color))


def color_inverse(color):
    '''Color for selected'''
    return tuple(map(lambda c: int(c * -0.8), color))


class Element():
    '''
    Element is a base class of pyno objects
    '''

    id_counter = 0  # count of all elements

    def __init__(self, x, y, color, batch, id):
        if id:
            self.id_counter = max(self.id_counter, id)
            self.id = self.id_counter
        else:
            Element.id_counter += 1
            self.id = self.id_counter

        self.x, self.y = x, y
        self.w, self.h = 70, 30
        self.cw, self.ch = self.w // 2, self.h // 2
        self.offset = 20
        self.put_size = 5
        self.pin_color = color_select(color)
        self.color = color
        self.draw_color = color
        self.er_color = (230, 20, 20)

        self.active = True
        self.batch = batch
        self.graphics = dict(inputs=dict(), outputs=dict(), connections=list(),
                             error=None, base=Quad(self.batch))

        self.er_label = pyglet.text.Label('...', font_name=font,
                                          bold=True, font_size=12,
                                          color=self.er_color + (255,),
                                          anchor_x='right', anchor_y='center')
        self.inputs = ()
        self.outputs = ()
        self.in_labels = []
        self.connected_to = []
        self.out_labels = []
        self.child = []
        self.selected = False  # 714848
        self.selectedInput = {'name': 'none', 'pos': 0}
        self.selectedOutput = {'name': 'none', 'pos': 0}
        self.hover = False

        self.problem = False

    def intersect_point(self, point, visual=True):
        # Intersection with whole element, also check pins intersection

        if self.x + self.cw > point[0] > self.x - self.cw and \
           self.y + self.ch + self.put_size * 2 > point[1] > \
           self.y - self.ch - self.put_size * 2:
            self.selectedInput = {'name': 'none', 'pos': 0}
            self.selectedOutput = {'name': 'none', 'pos': 0}

            if visual:
                self.draw_color = color_select(self.color)
                self.hover = True

            if point[1] > self.y + self.ch:
                for put in self.put_pos(self.inputs):
                    if put['pos'] + self.put_size * 2 > point[0] > \
                                    put['pos'] - self.put_size * 2:
                        self.selectedInput = ({'name': put['name']})

            elif point[1] < self.y - self.ch:
                for put in self.put_pos(self.outputs):
                    if put['pos'] + self.put_size * 2 > point[0] > \
                                    put['pos'] - self.put_size * 2:
                        self.selectedOutput = ({'name': put['name']})
            self.active = True
            return True

        elif self.hover:
            self.active = True

        self.selectedInput = {'name': 'none', 'pos': 0}
        self.selectedOutput = {'name': 'none', 'pos': 0}
        self.hover = False
        if visual:
            self.draw_color = self.color
        return False

    def render_base(self):
        # Render for base

        if not self.active and not self.hover:
            return False

        gr = self.graphics
        self.cw, self.ch = self.w // 2, self.h // 2

        if self.problem:
            if not gr['error']:
                gr['error'] = Quad(self.batch, True)

            gr['error'].redraw(self.x, self.y, self.cw + self.put_size,
                               self.ch + self.put_size,
                               (190, 20, 20))

        elif gr['error']:
            gr['error'].id.delete()
            gr['error'] = None

        gr['base'].redraw(self.x, self.y, self.cw, self.ch,
                          self.draw_color)

        self.pin_color = color_select(self.draw_color)

        for input in self.put_pos(self.inputs):
            put_name = self.selectedInput['name']
            if input['name'] == put_name:
                c = color_inverse(self.pin_color)
            else:
                c = self.pin_color
            gr['inputs'][input['name']].redraw(
                    input['pos'],
                    self.y + self.ch + self.put_size,
                    self.put_size, self.put_size, c)

        for output in self.put_pos(self.outputs):
            put_name = self.selectedOutput['name']
            if output['name'] == put_name:
                c = color_inverse(self.pin_color)
            else:
                c = self.pin_color
            gr['outputs'][output['name']].redraw(
                    output['pos'],
                    self.y - self.ch - self.put_size,
                    self.put_size, self.put_size, c)

        con = gr['connections']
        while len(con) < len(self.connected_to):
            con.append([Line(self.batch), Line(self.batch), Line(self.batch)])

        i = -1
        for node in self.connected_to:
            i += 1
            n = node['output']['node']

            try:
                iputx = self.put_pos_by_name(node['input']['put']['name'],
                                             'inputs')
                oputx = n.put_pos_by_name(node['output']['put']['name'],
                                          'outputs')
                if not iputx or not oputx:
                    raise Exception()
            except Exception as ex:
                for lines in con[i]:
                    lines.delete()
                con.remove(con[i])
                del self.connected_to[self.connected_to.index(node)]
                print('Connection is broken:', ex)
                break

            from_in = self.y + self.ch + self.offset // 2
            from_out = self.y + self.ch + self.offset
            to_out = n.y - n.ch - n.offset
            to_in = n.y - n.ch - n.offset // 2

            con[i][0].redraw((iputx, from_in), (iputx, from_out))
            con[i][1].redraw((iputx, from_out), (oputx, to_out))
            con[i][2].redraw((oputx, to_out), (oputx, to_in))

        return True

    def render_labels(self):
        # Render for errors and labels of pins

        if not self.active and not self.hover:
            return

        if self.problem:
            self.er_label.x = self.x - self.cw - self.offset
            self.er_label.y = self.y
            self.er_label.draw()

        if self.hover:
            for label, put in zip(self.in_labels, self.put_pos(self.inputs)):
                gl.glPushMatrix()
                gl.glTranslatef(put['pos'], self.y + self.ch + 15, 0.0)
                gl.glRotatef(45.0, 0.0, 0.0, 1.0)
                label.draw()
                gl.glPopMatrix()

            for label, put in zip(self.out_labels, self.put_pos(self.outputs)):
                gl.glPushMatrix()
                gl.glTranslatef(put['pos'], self.y - self.ch - 20, 0.0)
                gl.glRotatef(45.0, 0.0, 0.0, 1.0)
                label.draw()
                gl.glPopMatrix()

    def deactive(self):
        if self.active:
            self.active = False

    def insert_inouts(self, data):
        # New inputs and output was created.
        # We need create labels for each

        gr = self.graphics
        self.inputs = data['inputs']
        self.outputs = data['outputs']
        [put.delete() for put in gr['inputs'].values()]
        [put.delete() for put in gr['outputs'].values()]

        self.in_labels = []
        gr['inputs'] = dict()
        for input in self.inputs:
            gr['inputs'][input] = Quad(self.batch)
            self.in_labels.append(pyglet.text.Label(input, x=0, y=0,
                                                    font_name=font,
                                                    bold=True,
                                                    color=(255,255,255,200),
                                                    font_size=12))
        self.out_labels = []
        gr['outputs'] = dict()
        for output in self.outputs:
            gr['outputs'][output] = Quad(self.batch)
            self.out_labels.append(pyglet.text.Label(output, x=0, y=0,
                                                     font_name=font,
                                                     bold=True,
                                                     color=(255,255,255,200),
                                                     font_size=12,
                                                     anchor_x='right'))

    def put_pos(self, puts):
        # Calculate pos for pins
        for put in puts:
            yield {'name': put,
                   'pos': int(centered(self.x, self.w * 0.8,
                                       len(puts),
                                       puts.index(put)))}

    def put_pos_by_name(self, name, mode):
        # Return pose x of pin by name
        if mode == 'outputs':
            for put in self.outputs:
                if put == name:
                    return int(centered(self.x, self.w * 0.8,
                                        len(self.outputs),
                                        self.outputs.index(put)))
        elif mode == 'inputs':
            for put in self.inputs:
                if put == name:
                    return int(centered(self.x, self.w * 0.8,
                                        len(self.inputs),
                                        self.inputs.index(put)))

    def resize_to_name(self, name):
        self.w = max(len(name) * 10 + 20,
                     len(self.inputs) * 20, len(self.outputs) * 20, 64)
        self.cw = self.w // 2

    def make_active(self):
        self.active = True

    def make_child_active(self):
        self.make_active()
        [c.make_active() for c in self.child]

    def add_child(self, child):
        if child not in self.child:
            self.child.append(child)

    def get_con_id(self):
        new_connectedto = []
        for connect in self.connected_to:
            new_connect = {'output': {'node': connect['output']['node'].id,
                                      'put': connect['output']['put']},
                           'input': {'put': connect['input']['put']}}
            new_connectedto.append(new_connect)
        return new_connectedto

    def reconnect(self, buff):
        # Find parent node when paste
        for connect in self.connected_to:
            for o in buff:
                if connect['output']['node'] == o.id:
                    connect['output']['node'] = o
                    o.add_child(self)

    def delete(self, fully=False):
        for value in self.graphics.values():
            if value:
                if isinstance(value, dict):
                    [v.delete(fully) for v in value.values()]
                elif isinstance(value, list):
                    for l in value:
                        for lines in l:
                            lines.delete(fully)
                else:
                    value.delete(fully)
