import pyglet
import window
# import cProfile

# pynoSpace = {}

if __name__ == '__main__':
    config = pyglet.gl.Config(double_buffer=False, depth_size=0,
                              stencil_size=0, aux_buffers=0)
    pwindow = window.PynoWindow(config=config)

    pyglet.app.run()
    # cProfile.run("pyglet.app.run()")
