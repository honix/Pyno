import pyglet

from element import Element
from processor import Processor
from draw import labelsGroup


class Node(Element, Processor):
    # Field is a main pyno element, in fact it is a function with in/outputs

    def __init__(self, x, y, batch, color=(200, 200, 200), code=None,
                 connects=None, size=None):
        Element.__init__(self, x, y, color, batch)
        Processor.init_processor(self)  # node has a processor for calculation

        if not size is None:
            self.editorSize = size
        else:
            self.editorSize = (300, 150)

        if not connects is None:
            self.connectedTo = connects

        if code is None:
            self.code = """def newNode(a=0, b=0):
    result = a + b
    return result"""
        else:
            self.code = code

        self.name = ''
        self.label = pyglet.text.Label(self.name, font_name='consolas',
                                       bold=True, font_size=12,
                                       anchor_x='center', anchor_y='center',
                                       batch=batch, group=labelsGroup)
        self.new_code(self.code)

        self.render_base(batch, 1)

    def new_code(self, code):
        # New code, search for in/outputs
        self.code = code
        color = code[:12].find('#color')
        if color > -1:
            try:
                value = eval(code[color + 6:code[color + 6:].find(')') + 7])
            except:
                pass
            else:
                if isinstance(value, tuple) and len(value) == 3:
                    check = 0
                    for i in value:
                        if isinstance(i, int):
                            check += 1
                    if check == 3:
                        self.color = value

        def_pos = code.find('def')
        if def_pos > -1:
            inputs = outputs = ()

            b = code[def_pos:].find('(')
            if b > -1:
                self.new_name(code[def_pos + 3:def_pos + b].strip())
                e = code[def_pos:].find(':') - 1
                if e > -1:
                    name = ''
                    trash = False
                    brackets = False
                    for char in code[def_pos + b + 1:def_pos + e]:
                        if char == '(' or char == '[':
                            brackets = True
                            continue
                        elif char == ')' or char == ']':
                            brackets = False
                            continue
                        if not brackets:
                            if char == ',' or char == '=':
                                if not trash:
                                    inputs += (name,)
                                    name = ''
                                trash = True if char == '=' else False
                            elif char != ' ' and not trash:
                                name += char
                    if len(name):
                        inputs += (name,)

            ret_pos = code.rfind('return')
            if ret_pos > -1:
                outputs = tuple(x.strip()
                                for x in code[ret_pos + 6:].split(','))

            self.w = max(len(self.name) * 10 + 20,
                         len(inputs) * 20, len(outputs) * 20, 64)
            self.cw = self.w // 2
            self.insert_inouts({'inputs': inputs,
                                'outputs': outputs})

    def new_name(self, name):
        self.name = name
        self.label.text = self.name

    def render_base(self, batch, dt):
        super().render_base(batch, dt)
        self.label.x, self.label.y = self.x, self.y

    def delete(self):
        super().delete()
        self.label.delete()
