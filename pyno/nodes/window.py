import pyglet

class Window():

    def __init__(self, globalScope):
        self._globalScope = globalScope
        self._window = pyglet.window.Window(450, 450)

    def call(self):
        return self._window
    
    def cleanup(self):
        self._window.close()