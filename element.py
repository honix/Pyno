import pyglet

from draw import *
import utils


class Element(object):
    ''' Element is a base class of pyno objects
    '''

    id_counter = 0  # count of all elements

    def __init__(self, x, y, color):
        Element.id_counter += 1
        self.id = self.id_counter

        self.x, self.y = x, y
        self.w, self.h = 70, 30
        self.cw, self.ch = self.w // 2, self.h // 2
        self.offset = 20
        self.putSize = 5
        self.pinColor = self.select(color)
        self.color = color
        self.draw_color = color
        self.er_color = (230, 20, 20)

        #self.code = '...'
        #self.name = ' '
        self.er_label = pyglet.text.Label('error', font_name='consolas',
                                          bold=True, font_size=12,
                                          color=self.er_color + (255,),
                                          anchor_x='right', anchor_y='center')
        self.inputs = ()
        self.outputs = ()
        self.inlabels = []
        self.connectedTo = []
        self.outlabels = []
        self.selected = False  # 714848
        self.selectedInput = {'name': 'none', 'pos': 0}
        self.selectedOutput = {'name': 'none', 'pos': 0}
        self.hover = False

    def intersect_point(self, point, visual=True):
        ''' Intersection with whole element, also check pins intersection
        '''
        if point[0] < self.x + self.cw and point[0] > self.x - self.cw:
            if (point[1] < self.y + self.ch + self.putSize * 2
            and point[1] > self.y - self.ch - self.putSize * 2):

                self.selectedInput = {'name': 'none', 'pos': 0}
                self.selectedOutput = {'name': 'none', 'pos': 0}

                if visual:
                    self.draw_color = self.select(self.color)
                    self.hover = True

                if point[1] > self.y + self.ch:
                    for put in self.put_pos(self.inputs):
                        if (point[0] < put['pos'] + self.putSize * 2
                        and point[0] > put['pos'] - self.putSize * 2):
                            self.selectedInput = ({'name': put['name']})

                elif point[1] < self.y - self.ch:
                    for put in self.put_pos(self.outputs):
                        if (point[0] < put['pos'] + self.putSize * 2
                        and point[0] > put['pos'] - self.putSize * 2):
                            self.selectedOutput = ({'name': put['name']})

                return True

        self.selectedInput = {'name': 'none', 'pos': 0}
        self.selectedOutput = {'name': 'none', 'pos': 0}
        self.hover = False
        if visual:
            self.draw_color = self.color
        return False

    def insert_inouts(self, data={'inputs': ('a', 'b'),
                                  'outputs': ('result',)}):
        ''' New inputs and output was created.
            We need create labels for each
        '''
        self.inputs = data['inputs']
        self.outputs = data['outputs']
        self.inlabels = []
        for input in self.inputs:
            self.inlabels.append(pyglet.text.Label(input, x=0, y=0,
                                        font_name='consolas',
                                        font_size=12))
        self.outlabels = []
        for output in self.outputs:
            self.outlabels.append(pyglet.text.Label(output, x=0, y=0,
                                        font_name='consolas',
                                        font_size=12, anchor_x='right'))

    def put_pos(self, puts):
        ''' Calclate pos for pins
        '''
        for put in puts:
            yield {'name': put,
                   'pos': int(utils.centered(self.x, self.w * 0.8,
                                             len(puts),
                                             puts.index(put)))}

    def put_pos_by_name(self, name, mode):
        ''' Return pose x of pin by name
        '''
        if mode == 'outputs':
            for put in self.outputs:
                if put == name:
                    return int(utils.centered(self.x, self.w * 0.8,
                                              len(self.outputs),
                                              self.outputs.index(put)))
        elif mode == 'inputs':
            for put in self.inputs:
                if put == name:
                    return int(utils.centered(self.x, self.w * 0.8,
                                              len(self.inputs),
                                              self.inputs.index(put)))

    def select(self, color):
        ''' Color for hover
        '''
        return tuple(map(lambda c: int(c * 0.65), color))

    def inverse(self, color):
        ''' Color for selected
        '''
        return tuple(map(lambda c: int(c * -0.8), color))

    def render_base(self, batch):
        ''' Render for base
        '''
        self.cw, self.ch = self.w // 2, self.h // 2
        if self.problem:
            quad(self.x, self.y, self.cw + self.putSize, self.ch + self.putSize,
                 (190, 20, 20), batch)

        quad(self.x, self.y, self.cw, self.ch, self.draw_color, batch)

        self.pinColor = self.select(self.draw_color)

        for input in self.put_pos(self.inputs):
            put_name = self.selectedInput['name']
            if input['name'] == put_name:
                c = self.inverse(self.pinColor)
            else:
                c = self.pinColor
            quad(input['pos'],
                 self.y + self.ch + self.putSize,
                 self.putSize, self.putSize, c, batch)

        for output in self.put_pos(self.outputs):
            put_name = self.selectedOutput['name']
            if output['name'] == put_name:
                c = self.inverse(self.pinColor)
            else:
                c = self.pinColor
            quad(output['pos'],
                 self.y - self.ch - self.putSize,
                 self.putSize, self.putSize, c, batch)

        for node in self.connectedTo:
            n = node['output']['node']
            try:
                iputx = self.put_pos_by_name(node['input']['put']['name'],
                                         'inputs')
                oputx = n.put_pos_by_name(node['output']['put']['name'],
                                         'outputs')
                line((iputx, self.y + self.ch + self.offset // 2),
                     (iputx, self.y + self.ch + self.offset), batch)
                line((iputx, self.y + self.ch + self.offset),
                     (oputx, n.y - n.ch - n.offset), batch)
                line((oputx, n.y - n.ch - n.offset),
                     (oputx, n.y - n.ch - n.offset // 2), batch)
            except:
                del self.connectedTo[self.connectedTo.index(node)]
                print('Connection is broken while redraw')

    def get_con_id(self):
        new_connectedTo = []
        for connect in self.connectedTo:
            new_connect = {'output': {'node': connect['output']['node'].id,
                                      'put': connect['output']['put']},
                           'input': {'put': connect['input']['put']}}
            new_connectedTo.append(new_connect)
        return new_connectedTo

    def reconnect(self, buff):
        ''' Find parent node when paste
        '''
        for connect in self.connectedTo:
            for o in buff:
                if connect['output']['node'] == o[1]:
                    connect['output']['node'] = o[0]

    def render(self):
        ''' Render for errors and labels of pins
        '''
        if self.problem:
            self.er_label.x = self.x - self.cw - self.offset
            self.er_label.y = self.y
            self.er_label.draw()

        if self.hover:
            for label, put in zip(self.inlabels, self.put_pos(self.inputs)):
                glPushMatrix()
                glTranslatef(put['pos'], self.y + self.ch + 15, 0.0)
                glRotatef(45.0, 0.0, 0.0, 1.0)
                label.draw()
                glPopMatrix()

            for label, put in zip(self.outlabels, self.put_pos(self.outputs)):
                glPushMatrix()
                glTranslatef(put['pos'], self.y - self.ch - 20, 0.0)
                glRotatef(45.0, 0.0, 0.0, 1.0)
                label.draw()
                glPopMatrix()