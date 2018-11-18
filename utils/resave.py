'''
This script will convert old *.pn file to new one.

New versions will have 'call' binding, and return type annotations.
This script will fill this gaps automatically, using 'parser' from old Pyno snapshot.

Usage:
    resave.py < oldFile.pn > newFile.pn
    
'''

import sys
import json

importTyping = 'from typing import *'
imports = importTyping

# You can add additional imports if necessary

# importPyglet = 'import pyglet'
# imports = importPyglet + '\n' + importTyping

def returnAnnotation(names):
    return 'Tuple[' + ', '.join(map(lambda x: '"' + x + '"', names)) + ']'

def main():
    data = sys.stdin.read()

    try:
        nodes = json.loads(data)
    except ValueError:
        nodes = eval(data)

    for node in nodes:
        code = node['code']

        name, outputs = None, None

        # https://github.com/honix/Pyno/blob/4fa27a4335c6841e6c4a6bc29e69d399625e36d5/node.py#L43
        def_pos = code.find('def')
        if def_pos > -1:
            bracket = code[def_pos:].find('(')
            if bracket > -1:
                name = code[def_pos + 3:def_pos + bracket].strip()

            column = code[def_pos:].find(':')

            ret_pos = code.rfind('return')
            if ret_pos > -1:
                outputs = tuple(x.strip()
                                for x in code[ret_pos + 6:].split(','))

        if outputs:
            code = (code[:def_pos + column] + ' -> ' + returnAnnotation(outputs) + ' ' +
                    code[def_pos + column:])

        if name:
            code = (imports + '\n\n' + 
                    code + '\n\n' +
                    'call = ' + name)
        
        node['code'] = code

    print(json.dumps(nodes, indent=4))


if __name__ == '__main__':
    main()