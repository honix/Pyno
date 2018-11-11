import pyglet
import types
import typing
import inspect
from inspect import getargspec

from element import Element
from processor import Processor
from draw import labelsGroup
from utils import font


class Node(Element, Processor):
    '''
    Node is a main pyno element, in fact it is a function with in/outputs
    '''

    def __init__(self, window, x, y, batch, color=(200, 200, 200), code=None,
                 connects=None, size=(300, 150)):
        Element.__init__(self, x, y, color, batch)
        Processor.init_processor(self)  # node has a processor for calculation

        self.window = window
        self.editor_size = size

        if connects:
            self.connected_to = connects

        if code:
            self.code = code
        else:
            self.code = '''def newNode(a=0, b=0):
  result = a + b
  return result

call = newNode'''

        self.env = {}

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
        self.problem = False

        self.func = None
        try:
            self.env = {'S': self.local_space, 'G': self.window.pyno_namespace}
            exec(code, self.env)
            self.func = self.env['call']
            if not isinstance(self.func, types.FunctionType):
                raise Exception('Call value is not callable!')
        except Exception as ex:
            self.problem = True
            self.er_label.text = "Reader error: " + str(ex)
        else:
            inputs, outputs = self.inputs, self.outputs
            self.label.text = self.name = self.func.__name__

            signature = inspect.signature(self.func)
            inputs = tuple(map(lambda x: x.name, signature.parameters.values()))

            if (tuple in signature.return_annotation.mro()):
                out = []
                i = 0
                for arg in list(signature.return_annotation.__args__):
                    is_string = isinstance(arg, typing._ForwardRef) and isinstance(arg.__forward_arg__, str)
                    out.append(arg.__forward_arg__ if is_string else 'result ' + str(i))
                    i += 1
                outputs = tuple(out)
            else:
                outputs = ('result',)

            self.resize_to_name(self.name)
            self.insert_inouts({'inputs': inputs,
                                'outputs': outputs})

    def render_base(self):
        Element.render_base(self)
        self.label.x, self.label.y = self.x, self.y

    def delete(self, fully=False):
        Element.delete(self, fully)
        self.label.delete()
