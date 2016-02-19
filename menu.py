from node import Node
from field import Field
import clipboard


def copy_nodes(window):
    x, y = window.pointer[0], window.pointer[1]
    buff = []
    for node in window.selectedNodes:
        if isinstance(node, Node):
            buff.append({'type': 'node',
                         'x': node.x - x,
                         'y': node.y - y,
                         'size': node.editorSize,
                         'color': node.color,
                         'code': node.code,
                         'connects': node.get_con_id(),
                         'parent': node.id})
        elif isinstance(node, Field):
            buff.append({'type': 'field',
                         'x': node.x - x,
                         'y': node.y - y,
                         'size': (node.w, node.h),
                         'code': node.document.text,
                         'connects': node.get_con_id(),
                         'parent': node.id})
    clipboard.copy(str(buff))
    print('Copy ' + str(len(buff)) + ' nodes')


def paste_nodes(window, description=None):
    x, y = window.pointer[0], window.pointer[1]
    buff = []
    try:
        paste = eval(clipboard.paste())
        for node in paste:
            if node['type'] == 'node':
                buff.append([Node(node['x'] + x,
                                  node['y'] + y,
                                  window.batch,
                                  node['color'],
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
    except:
        print('Wrong paste!')
    finally:
        for node in buff:
            node[0].reconnect(buff)
            window.nodes.append(node[0])
        print('Paste ' + str(len(buff)) + ' nodes')
