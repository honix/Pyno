import pyglet
import window
# import profile

if __name__ == '__main__':
    print('Loading...')
    config = pyglet.gl.Config(double_buffer=True, depth_size=0,
                              stencil_size=0, aux_buffers=0,
                              samples=1)
    try:
        pwindow = window.PynoWindow(config=config)
    except:
        # if config is crashed run more default one
        pwindow = window.PynoWindow(pyglet.gl.Config())

    pyglet.options['debug_gl'] = False  # performance boost?

    # profile.run('pyglet.app.run()', sort=1)
    pyglet.app.run()

