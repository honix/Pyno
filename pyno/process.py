from .serializer import Serializer
from .fileOperator import FileOperator
from .field import Field


class Process():
    '''
    Abstract process
    '''
    
    def __init__(self):
        self.running = -1  # -1: run continously, 0: pause/stop, n: do n steps

        self.serializer = Serializer(self)
        self.file_operator = FileOperator()

        self.nodes = []
        self.nodes_to_exec = []

        self.global_scope = {}  # local space for in-pyno programs
        self.global_scope['G'] = self.global_scope  # to get global stuff

    def nodes_update(self):
        if not self.running:
            return
        if self.running > 0:
            self.running -= 1

        for node in self.nodes_to_exec:
            node.reset_proc()
            node.processor()
            self.nodes_to_exec.remove(node)
        
        for node in self.nodes:
            if isinstance(node, Field):
                node.reset_proc()
                node.processor()

    def to_exec(self, node):
        #if node not in self.nodes_to_exec: # TODO: allow self query
        self.nodes_to_exec.append(node)

    def new_pyno(self):
        for node in self.nodes:
            node.delete(fully=True)
            del node
        self.nodes = []
        print('New pyno!')

    def save_pyno(self, filepath=None):
        data = self.serializer.serialize(self.nodes)
        return self.file_operator.save(data, filepath=filepath, initialfile=self.filename)

    def load_pyno(self, filepath=None):
        data, self.filename = self.file_operator.load(filepath)
        if data is None:  # Loading data failed
            return None
        elif data:
            self.new_pyno()
        return self.load_data(data)

    def load_data(self, data, anchor=(0, 0)):
        nodes = self.serializer.deserialize(data, anchor)
        for node in nodes:
            self.nodes.append(node)
        return nodes
