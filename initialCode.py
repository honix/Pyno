node = '''def newNode(a=0, b=0):
  result = a + b
  return result

call = newNode'''

open_node = '''path = 'nodes/identity.py'

with open(path) as file:
  exec(file.read())'''