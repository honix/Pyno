import pyglet

from .window import PynoWindow

def run():
    print('Loading...')

    create_window()

    pyglet.options['debug_gl'] = False  # performance boost?
    # profile.run('pyglet.app.run()', sort=1)
    pyglet.app.run()


def create_window():
    config = pyglet.gl.Config(double_buffer=True, depth_size=0,
                              stencil_size=0, aux_buffers=0,
                              samples=1)

    try:
        window = PynoWindow(config, filename='.auto-saved.pn')
    except:
        # if config is crashed run more default one
        print('Runnig using default config...')
        window = PynoWindow(pyglet.gl.Config(), filename='.auto-saved.pn')
    
    return window