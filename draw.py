import pyglet
from pyglet.gl import *

from math import atan2, sin, cos

# There is some functions for drawing shapes


class UIGroup(pyglet.graphics.OrderedGroup):
    def __init__(self, order):
        super().__init__(order)

    def set_state(self):
        glPushMatrix()
        glLoadIdentity()

    def unset_state(self):
        glPopMatrix()


class LinesGroup(pyglet.graphics.OrderedGroup):
    # Toggle smooth lines
    def __init__(self, order):
        super().__init__(order)

    def set_state(self):
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_BLEND)

    def unset_state(self):
        glDisable(GL_POLYGON_SMOOTH)
        glDisable(GL_BLEND)

uiGroup = UIGroup(-1)
linesGroup = LinesGroup(0)
baseGroup = pyglet.graphics.OrderedGroup(1)
labelsGroup = pyglet.graphics.OrderedGroup(2)


class Line:
    def __init__(self, batch):
        self.id = batch.add_indexed(
                    4, GL_TRIANGLES, linesGroup,
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

    def delete(self):
        self.id.vertices = (0, 0,
                            0, 0,
                            0, 0,
                            0, 0)
        # self.id.delete() # avoid glitch
        del self.id


class Quad:
    def __init__(self, batch, backdrop=False, frontdrop=False):
        group = baseGroup
        if backdrop:
            group = linesGroup
        elif frontdrop:
            group = labelsGroup

        self.id = batch.add_indexed(
                                4, GL_TRIANGLES, group,
                                [0, 1, 2, 2, 3, 0],
                                ('v2i', (0, 0,
                                         0, 0,
                                         0, 0,
                                         0, 0)),
                                ('c3B', (0, 0, 0) * 4)
                                   )

    def redraw(self, x, y, cw, ch, color):
        self.id.vertices = (x - cw, y - ch,
                            x + cw, y - ch,
                            x + cw, y + ch,
                            x - cw, y + ch)
        self.id.colors = color * 4

    def delete(self):
        self.id.vertices = (0, 0,
                            0, 0,
                            0, 0,
                            0, 0)
        # self.id.delete() # avoid glitch
        del self.id


def quad_aligned(x, y, w, h, color):
    quad_data = pyglet.graphics.vertex_list_indexed(
                 4,
                 [0, 1, 2, 2, 3, 0],
                 ('v2i', (x, y,
                          x + w, y,
                          x + w, y + h,
                          x, y + h)),
                 ('c4B', color * 4)
                                                   )

    glEnable(GL_BLEND)
    quad_data.draw(GL_TRIANGLES)
    glDisable(GL_BLEND)


def selector(init, corner):
    # Selection tool representation
    quad_data = pyglet.graphics.vertex_list_indexed(
                 4,
                 [0, 1, 2, 2, 3, 0],
                 ('v2i', (init[0],   init[1],
                          corner[0], init[1],
                          corner[0], corner[1],
                          init[0],   corner[1])),
                 ('c4B', (120, 200, 255, 50) * 4)
                                                   )
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_BLEND)
    quad_data.draw(GL_TRIANGLES)
    glDisable(GL_BLEND)
