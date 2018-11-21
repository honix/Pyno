import sys
import pyglet
import types
import typing
import inspect
from inspect import getargspec

from .element import Element
from .processor import Processor
from .draw import labelsGroup
from .utils import font


# Fix compatibility in typing module for Python < 3.7
if sys.hexversion < 0x030700F0:
    try:
        typing.ForwardRef = typing._ForwardRef
    except:
        pass


class Node(Element, Processor):
    '''
    Node is a main Pyno element, in fact it is a function with in/outputs
    '''

    def __init__(self, window, x, y, batch, color=(200, 200, 200), code="",
                 connects=None, size=(300, 150), id=None):
        Element.__init__(self, x, y, color, batch, id)
        Processor.init_processor(self, window.global_scope)  # node has a processor for calculation

        self.window = window
        self.editor_size = size
        self.code = code

        if connects:
            self.connected_to = connects

        self.env = {}

        self.name = ''
        self.label = pyglet.text.Label(self.name, font_name=font,
                                       bold=True, font_size=11,
                                       anchor_x='center', anchor_y='center',
                                       batch=batch, group=labelsGroup,
                                       color=(255, 255, 255, 230))
        self.reload()

    def processor(self):
        return Processor.processor(self, self.connected_to, self.outputs)

    def new_code(self, code):
        self.cleanup()
        # New code, search for in/outputs

        self.code = code
        self.problem = False

        self.call_func = None
        self.cleanup_func = None
        try:
            self.env = {'S': self.local_scope, 'G': self.window.global_scope}
            exec(code, self.env)

            self.call_func = self.env['call']
            if not isinstance(self.call_func, types.FunctionType):
                raise Exception('Call value is not callable!')

            if 'cleanup' in self.env:
                self.cleanup_func = self.env['cleanup']
        except Exception as ex:
            self.problem = True
            self.er_label.text = "Reader error: " + str(ex)
        else:
            self.label.text = self.name = self.call_func.__name__

            signature = inspect.signature(self.call_func)
            inputs = tuple(map(lambda x: x.name, signature.parameters.values()))

            if (tuple in signature.return_annotation.mro()):
                out = []
                i = 0
                for arg in list(signature.return_annotation.__args__):
                    is_string = isinstance(arg, typing.ForwardRef) and isinstance(arg.__forward_arg__, str)
                    out.append(arg.__forward_arg__ if is_string else 'result ' + str(i))
                    i += 1
                outputs = tuple(out)
            else:
                outputs = ('result',)

            self.resize_to_name(self.name)
            self.insert_inouts({'inputs': inputs,
                                'outputs': outputs})

    def reload(self):
        self.new_code(self.code)
        self.make_active()

    def render_base(self):
        if Element.render_base(self):
            self.label.x, self.label.y = self.x, self.y

    def delete(self, fully=False):
        self.cleanup()
        Element.delete(self, fully)
        self.label.delete()
