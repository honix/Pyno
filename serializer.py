import json
from collections import OrderedDict

from node import Node
from field import Field
from sub import Sub

class Serializer():
    '''
    Serialize nodes to data or deserialize data to nodes.
    Uses json format
    '''

    def __init__(self, window):
        Serializer.version = 0.3
        self.window = window

    def serialize(self, nodes, anchor=(0, 0)):
        buff = []
        buff.append({'version': Serializer.version})
        for node in nodes:
            if isinstance(node, Node):
                buff.append(OrderedDict({'type': 'node',
                            'x': node.x - anchor[0],
                            'y': node.y - anchor[1],
                            'size': node.editor_size,
                            'color': node.color,
                            'code': node.code.split('\n'),
                            'connects': node.get_con_id(),
                            'parent': node.id}))
            elif isinstance(node, Field):
                buff.append(OrderedDict({'type': 'field',
                            'x': node.x - anchor[0],
                            'y': node.y - anchor[1],
                            'size': (node.w, node.h),
                            'code': node.document.text.split('\n'),
                            'connects': node.get_con_id(),
                            'parent': node.id}))
            elif isinstance(node, Sub):
                buff.append(OrderedDict({'type': 'sub',
                            'x': node.x - anchor[0],
                            'y': node.y - anchor[1],
                            'size': node.editor_size,
                            'color': node.color,
                            'code': node.code,
                            'connects': node.get_con_id(),
                            'parent': node.id}))
        return json.dumps(buff, indent=4)

    def deserialize(self, data, anchor=(0, 0)):
        try:
            paste = json.loads(data)
            #paste = json.loads(data, object_pairs_hook=OrderedDict)
        except ValueError:
            print("Attention: pyno-file still uses the old save format, please re-save soon!")
            paste = eval(data)

        try:
            version = paste[0]['version']
        except Exception as ex:
            print('Can\'t fetch format version. Probably format is < 0.3.')
            version = 0.0

        nodes = paste[1:] if version >= 0.3 else paste

        buff = []
        try:
            for node in nodes:
                if node['type'] == 'node':
                    buff.append([Node(self.window, 
                                    node['x'] + anchor[0],
                                    node['y'] + anchor[1],
                                    self.window.batch,
                                    tuple(node['color']),
                                    '\n'.join(node['code']) if version >= 0.3 else node['code'],
                                    node['connects'],
                                    node['size']),
                                node['parent']])
                elif node['type'] == 'field':
                    buff.append([Field(self.window,
                                    node['x'] + anchor[0],
                                    node['y'] + anchor[1],
                                    self.window.batch,
                                    '\n'.join(node['code']) if version >= 0.3 else node['code'],
                                    node['connects'],
                                    node['size']),
                                node['parent']])
                elif node['type'] == 'sub':
                    buff.append([Sub(self.window,
                                    node['x'] + anchor[0],
                                    node['y'] + anchor[1],
                                    self.window.batch,
                                    tuple(node['color']),
                                    node['code'],
                                    node['connects'],
                                    node['size']),
                                node['parent']])
        except Exception as ex:
            print('Wrong data:', ex)
            return None
        finally:
            for node in buff:
                node[0].reconnect(buff)
            return buff
