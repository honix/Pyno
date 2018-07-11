import pyglet
from inspect import getargspec

from element import Element
from processor import Processor
from draw import labelsGroup
from utils import font


class Node(Element, Processor):
    '''
    Node is a main pyno element, in fact it is a function with in/outputs
    '''

    def __init__(self, x, y, batch, color=(200, 200, 200), code=None,
                 connects=None, size=(300, 150)):
        Element.__init__(self, x, y, color, batch)
        Processor.init_processor(self)  # node has a processor for calculation

        self.editor_size = size

        if connects:
            self.connected_to = connects

        if code:
            self.code = code
        else:
            self.code = '''def newNode(a=0, b=0):
  result = a + b
  return result'''

        self.name = ''
        self.label = pyglet.text.Label(self.name, font_name=font,
                                       bold=True, font_size=11,
                                       anchor_x='center', anchor_y='center',
                                       batch=batch, group=labelsGroup,
                                       color=(255, 255, 255, 230))
        self.new_code(self.code)

    def new_code(self, code):
        # New code, search for in/outputs

        self.code = code

        def_pos = code.find('def')
        if def_pos > -1:
            inputs, outputs = self.inputs, self.outputs

            bracket = code[def_pos:].find('(')
            if bracket > -1:
                self.name = code[def_pos + 3:def_pos + bracket].strip()
                self.label.text = self.name

                S, G = {}, {}  # temporally stores and globals to exec function
                try:
                    exec(code[def_pos:])  # dummy function to eject args names
                except Exception as ex:
                    self.problem = True
                    self.er_label.text = repr(ex)
                else:
                    # got tuple with args names like ('a', 'b')
                    inputs = tuple(getargspec(eval(self.name)).args)

            ret_pos = code.rfind('return')
            if ret_pos > -1:
                outputs = tuple(x.strip()
                                for x in code[ret_pos + 6:].split(','))

            self.w = max(len(self.name) * 10 + 20,
                         len(inputs) * 20, len(outputs) * 20, 64)
            self.cw = self.w // 2

            self.insert_inouts({'inputs': inputs,
                                'outputs': outputs})

    def render_base(self):
        Element.render_base(self)
        self.label.x, self.label.y = self.x, self.y

    def delete(self, fully=False):
        Element.delete(self, fully)
        self.label.delete()
