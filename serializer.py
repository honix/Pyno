class Serializer():

    def __init__(self, widnow):
        self.window = window

    def serialize(self, anchor=(0, 0), nodes=window.nodes):
        #x, y = (0, 0) if data else (self.window.pointer[0], self.window.pointer[1])
        #nodes = window.nodes if data else window.selected_nodes
        buff = []
        for node in nodes:
            if isinstance(node, Node):
                buff.append(OrderedDict({'type': 'node',
                            'x': node.x - anchor[0],
                            'y': node.y - anchor[1],
                            'size': node.editor_size,
                            'color': node.color,
                            'code': node.code,
                            'connects': node.get_con_id(),
                            'parent': node.id}))
            elif isinstance(node, Field):
                buff.append(OrderedDict({'type': 'field',
                            'x': node.x - anchor[0],
                            'y': node.y - anchor[1],
                            'size': (node.w, node.h),
                            'code': node.document.text,
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
        #pyperclip.copy(json.dumps(buff, indent=4))
        #window.info('Copied ' + str(len(buff)) + ' nodes')

    def deserialize(self, data):
        x, y = (0, 0) if data else (window.pointer[0], window.pointer[1])
        buff = []
        try:
            data = data if data else pyperclip.paste()
            try:
                paste = json.loads(data)
                #paste = json.loads(data, object_pairs_hook=OrderedDict)
            except ValueError:
                print("Attention: pyno-file still uses the old save format, please re-save soon!")
                paste = eval(data)
            for node in paste:
                if node['type'] == 'node':
                    buff.append([Node(window, 
                                    node['x'] + x,
                                    node['y'] + y,
                                    window.batch,
                                    tuple(node['color']),
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
                elif node['type'] == 'sub':
                    buff.append([Sub(node['x'] + x,
                                    node['y'] + y,
                                    window.batch,
                                    tuple(node['color']),
                                    node['code'],
                                    node['connects'],
                                    node['size']),
                                node['parent']])
        except Exception as ex:
            print('Wrong paste:', ex)
            return False
        finally:
            for node in buff:
                node[0].reconnect(buff)
                window.nodes.append(node[0])
            if data:
                window.info('Loaded ' + str(len(buff)) + ' nodes!')
            else:
                window.info('Pasted ' + str(len(buff)) + ' nodes!')
            return True