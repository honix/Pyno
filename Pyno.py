import pyglet
import window
# import cProfile

# pynoSpace = {}

if __name__ == '__main__':
    print('Loading...')
    
    config = pyglet.gl.Config(double_buffer=False, depth_size=0,
                              stencil_size=0, aux_buffers=0,
                              samples=1)
    try:
        pwindow = window.PynoWindow(config=config)
    except:
        # if config is crashed run more default one
        pwindow = window.PynoWindow(pyglet.gl.Config())

    pyglet.app.run()
    # cProfile.run("pyglet.app.run()")
