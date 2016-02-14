import pyglet
from pyglet.gl import *

from math import atan2, sin, cos

# There is some functions for drawing shapes


class linesGroup(pyglet.graphics.Group):
    # Toggle smooth lines
    def set_state(self):
        glEnable(GL_POLYGON_SMOOTH)
        glEnable(GL_BLEND)

    def unset_state(self):
        glDisable(GL_POLYGON_SMOOTH)
        glDisable(GL_BLEND)


linesGroup = linesGroup()


def line(p_one, p_two, batch, width=2.4):
    angle = atan2(p_two[1] - p_one[1], p_two[0] - p_one[0])
    sina = width / 2 * sin(angle)
    cosa = width / 2 * cos(angle)

    batch.add_indexed(4, GL_TRIANGLES, linesGroup,
                 [0, 1, 2, 2, 3, 0],
                 ('v2f', (p_one[0] - sina, p_one[1] + cosa,
                          p_one[0] + sina, p_one[1] - cosa,
                          p_two[0] + sina, p_two[1] - cosa,
                          p_two[0] - sina, p_two[1] + cosa)),
                 ('c4B', (255, 255, 255, 80) * 4)
                      )


def quad(x, y, cw, ch, color, batch):
    quad_id = batch.add_indexed(4, GL_TRIANGLES, None,
                 [0, 1, 2, 2, 3, 0],
                 ('v2i', (x - cw, y - ch,
                          x + cw, y - ch,
                          x + cw, y + ch,
                          x - cw, y + ch)),
                 ('c3B', color * 4)
                      )
    return quad_id


class Quad:
    def __init__(self, batch):
        self.id = batch.add_indexed(
                                4, GL_TRIANGLES, None,
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
        self.id.delete()
        del self.id



#def quad_gradient(x, y, cw, ch, col1, col2, batch):
    #batch.add_indexed(6, GL_TRIANGLES, None,
                 #[0, 1, 4, 4, 5, 0,
                  #1, 2, 3, 3, 4, 1],
                 #('v2i', (x - cw, y - ch,
                          #x - cw, y,
                          #x - cw, y + ch,
                          #x + cw, y + ch,
                          #x + cw, y,
                          #x + cw, y - ch,)),
                 #('c3B', col1 + col2 + col1 * 2 + col2 + col1)
                      #)


def quad_aligned(x, y, w, h, color):
    quad_data = pyglet.graphics.vertex_list_indexed(4,
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
    quad_data = pyglet.graphics.vertex_list_indexed(4,
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
