from math import atan2, sin, cos

import pyglet
from pyglet import gl


class UIGroup(pyglet.graphics.OrderedGroup):
    def __init__(self, order):
        super().__init__(order)

    def set_state(self):
        gl.glPushMatrix()
        gl.glLoadIdentity()

    def unset_state(self):
        gl.glPopMatrix()


class LinesGroup(pyglet.graphics.OrderedGroup):
    def __init__(self, order):
        super().__init__(order)

    def set_state(self):
        # Toggle smooth lines
        gl.glEnable(gl.GL_POLYGON_SMOOTH)
        gl.glEnable(gl.GL_BLEND)

    def unset_state(self):
        gl.glDisable(gl.GL_POLYGON_SMOOTH)
        gl.glDisable(gl.GL_BLEND)

uiGroup = UIGroup(-1)
linesGroup = LinesGroup(0)
baseGroup = pyglet.graphics.OrderedGroup(1)
labelsGroup = pyglet.graphics.OrderedGroup(2)


class Line:
    def __init__(self, batch):
        self.id = batch.add_indexed(
                    4, gl.GL_TRIANGLES, linesGroup,
                    [0, 1, 2, 2, 3, 0],
                    ('v2f', (0.0, 0.0,
                             0.0, 0.0,
                             0.0, 0.0,
                             0.0, 0.0)),
                    ('c3B', (100, 100, 100) * 4)
                                   )

    def redraw(self, p1, p2):
        angle = atan2(p2[1] - p1[1], p2[0] - p1[0])
        width = 2.4
        sina = width / 2 * sin(angle)
        cosa = width / 2 * cos(angle)
        self.id.vertices = (p1[0] - sina, p1[1] + cosa,
                            p1[0] + sina, p1[1] - cosa,
                            p2[0] + sina, p2[1] - cosa,
                            p2[0] - sina, p2[1] + cosa)

    def delete(self, fully=False):
        self.id.vertices = (0, 0,
                            0, 0,
                            0, 0,
                            0, 0)
        if fully:
            self.id.delete()
        del self.id


class Quad:
    def __init__(self, batch, backdrop=False, frontdrop=False):
        group = baseGroup
        if backdrop:
            group = linesGroup
        elif frontdrop:
            group = labelsGroup

        self.id = batch.add_indexed(
                                4, gl.GL_TRIANGLES, group,
                                [0, 1, 2, 2, 3, 0],
                                ('v2i', (0, 0,
                                         0, 0,
                                         0, 0,
                                         0, 0)),
                                ('c3B', (0, 0, 0) * 4))

    def redraw(self, x, y, cw, ch, color):
        self.id.vertices = (x - cw, y - ch,
                            x + cw, y - ch,
                            x + cw, y + ch,
                            x - cw, y + ch)
        self.id.colors = color * 4

    def delete(self, fully=False):
        self.id.vertices = (0, 0,
                            0, 0,
                            0, 0,
                            0, 0)
        if fully:
            self.id.delete()
        del self.id


def quad_aligned(x, y, w, h, color):
    quad_data = pyglet.graphics.vertex_list_indexed(
                 4,
                 [0, 1, 2, 2, 3, 0],
                 ('v2i', (x, y,
                          x + w, y,
                          x + w, y + h,
                          x, y + h)),
                 ('c4B', color * 4))

    gl.glEnable(gl.GL_BLEND)
    quad_data.draw(pyglet.gl.GL_TRIANGLES)
    gl.glDisable(gl.GL_BLEND)


def selector(init, corner):
    '''Selection tool representation'''
    quad_data = pyglet.graphics.vertex_list_indexed(
                 4,
                 [0, 1, 2, 2, 3, 0],
                 ('v2i', (init[0],   init[1],
                          corner[0], init[1],
                          corner[0], corner[1],
                          init[0],   corner[1])),
                 ('c4B', (120, 200, 255, 50) * 4))

    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_BLEND)
    quad_data.draw(gl.GL_TRIANGLES)
    gl.glDisable(gl.GL_BLEND)
