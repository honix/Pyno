import pyglet
import window
from inspect import getargspec

from element import Element
from processor import Processor
from draw import labelsGroup
from utils import font
from field import Field


class Sub(Element, Processor):
    '''
    Sub is a main pyno element, in fact it is a pyno file with in/outputs
    '''

    def __init__(self, x, y, batch, color=(200, 200, 200), code=None,
                 connects=None, size=(300, 150)):
        Element.__init__(self, x, y, color, batch)
        Processor.init_processor(self)  # node has a processor for calculation

        self.editor_size = size

        if connects:
            self.connected_to = connects

#        if code:
#            self.code = code
#        else:
##            self.code = '''examples/sub_add2.pn'''
#            self.code = '''examples/sub_pass.pn'''  # identical to '''examples/blank.pn'''
##            self.code = 'examples/welcome.pn'
        self.code = None
        if not code:
#            code = '''examples/sub_add2.pn'''
            code = '''examples/sub_pass.pn'''  # identical to '''examples/blank.pn'''
#            code = 'examples/welcome.pn'

        self.name = ''
        self.label = pyglet.text.Label(self.name, font_name=font,
                                       bold=True, font_size=11,
                                       anchor_x='center', anchor_y='center',
                                       batch=batch, group=labelsGroup,
                                       color=(255, 255, 255, 230))
        self.pwindow = None
        self.input_nodes = {}
        self.output_nodes = {}
        self.new_code(code)

    def new_code(self, code):
        # New code, search for in/outputs

        if self.code == code:
            return

        self.code = code

        self.name = code.strip()
        self.label.text = self.name

        try:
            if not window.menu.load(self.code):
                raise FileNotFoundError("File could not be loaded.")
            pwin = window.PynoWindow(pyglet.gl.Config(), filename=self.code)
            if self.pwindow:
                self.pwindow.close()
            del self.pwindow
            self.pwindow = pwin
        except Exception as ex:
            self.problem = True
            self.er_label.text = repr(ex)
            return
        #else:
        #    # got tuple with args names like ('a', 'b')
        #    inputs = tuple(getargspec(eval(self.name)).args)

        # window visibility handeled in window.py

        self.pwindow.nodes_update()

        inputs, outputs = [], []
        self.input_nodes, self.output_nodes = {}, {}
        for nid, node in enumerate(self.pwindow.nodes):
            if not isinstance(node, Field):
                continue
#            print(node.inputs, node.outputs, node.connected_to, node.child, node.name)
#            print(node, node.inputs, node.outputs, node.connected_to, node.child, node.code, node.gen_output)
#            nid = node.id
#            nid = hex(id(node))
            if not node.connected_to:  # fields with free inputs
                for inp in node.inputs:
                    name = "%s_%i" % (inp, nid)
                    inputs.append(name)
                    self.input_nodes[name] = node   # from self.pwindow.nodes
            if not node.child:         # fields with free outputs
                for outp in node.outputs:
                    name = "%s_%i" % (outp, nid)
                    outputs.append(name)
                    self.output_nodes[name] = node  # from self.pwindow.nodes

        self.insert_inouts({'inputs': inputs,
                            'outputs': outputs})

    # processor copying values to and from fields, has error handling
    # works with: sub_pass.pn
    # not yet working with: sub_add2.pn
    def processor(self, space):
        # Called every frame

        if (self.proc_result and not self.need_update) or not self.pwindow:
            return self.proc_result

        self.problem = False

        # check all in-connections, get results and gave names of in-puts
        gen_inputs = {}
        for connection in self.connected_to:
#            print(connection)
            try:
                inputs = connection['output']['node'].processor(space)
                data = inputs[connection['output']['put']['name']]

                # send data to sub part
                node = self.input_nodes[connection['input']['put']['name']]  # from self.pwindow.nodes
                node.gen_output = {'output': data}
                node.document.text = repr(data)
#                node.need_update = True
            except:
                self.er_label.text = 'Cant read input'
                self.problem = True
                continue
            gen_inputs[connection['input']['put']['name']] = data

        # exec process of sub part
        self.pwindow.nodes_update()
#        self.pwindow.update()

        # run-time mode: just get inputs and put in function
        try:
            space['S'] = self.local_space
#            result = self.func(**gen_inputs)
            # get data back and return them
            self.gen_output = {}
            for outp in self.outputs:
                node = self.output_nodes[outp]  # from self.pwindow.nodes
                self.gen_output[outp] = node.gen_output['output']
        except Exception as ex:
            if not self.problem:
                self.er_label.text = str(ex)
            self.problem = True
#        else:
#            # build output
#            for output in self.outputs:
#                if (result and len(self.outputs) > 1
#                    and isinstance(result, tuple)):
#                    r = result[self.outputs.index(output)]
#                    self.gen_output[output] = r  # tuple output
#                else:
#                    self.gen_output[output] = result  # one output
#
#            self.proc_result = self.gen_output
        self.proc_result = self.gen_output
                
#        print(self.gen_output)
        return self.gen_output

    # processor connecting inputs and outputs of fields, does not have error handling
    # works with: sub_pass.pn
    def _processor(self, space):
        # Called every frame

        # directly connect inputs and outputs to fields in sub
        # hackish should not be in processor() since it bypasses and disables it also
        # elegant since it uses processor() mechanics optimal but draws strange wires
        # consider using connect_out_to_in() and connect_in_to_out()

        # connect sub inputs
#        self.pwindow.nodes[0].connected_to[0]['output'] = self.connected_to[0]['output']
        self.pwindow.nodes[0].connected_to = self.connected_to

        # connect sub outputs
#        print(self.child)
#        self.pwindow.nodes[0].add_child(self.child[0])
#        self.pwindow.nodes[0].child = self.child
        if self.child:
#            print(self.child[0].connected_to)
            self.child[0].connected_to[0]['output'] = {'put': {'name': 'output'}, 'node': self.pwindow.nodes[0]}

        return {'output': None}

    def render_base(self):
        Element.render_base(self)
        self.label.x, self.label.y = self.x, self.y

    def delete(self, fully=False):
        if self.pwindow:
            self.pwindow.close()
        del self.pwindow
        Element.delete(self, fully)
        self.label.delete()
