import clipboard

from utils import x_y_pan_scale
from draw import *


class CodeEditor(object):
    # Code editor is the window you define nodes function

    def __init__(self, node):
        self.node = node  # node-owner of this codeEditor
        self.document = pyglet.text.document.FormattedDocument(node.code)
        self.document.set_style(0, len(node.code),
                                dict(font_name='Consolas',
                                font_size=12, color=(255,) * 4))
        self.layout = pyglet.text.layout.IncrementalTextLayout(
                                self.document,
                                *node.editorSize,
                                multiline=True, wrap_lines=False)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.color = (255, 255, 255)
        self.caret.visible = False
        self.hover = False
        self.resize = False

        self.pan_scale = [[0.0, 0.0], 1]
        self.screen_size = (800, 600)

    def update_node(self):
        # Push code to node
        self.node.new_code(self.document.text)
        self.node.need_update = True

    def intersect_point(self, point):
        # Intersection with whole codeEditor
        l = self.layout
        return (0 < point[0] - l.x + 20 < l.width + 20 and
                0 < point[1] - l.y < l.height + 10)

    def intersect_corner(self, point):
        # Intersection with bottom right corner to resize
        l = self.layout
        return (0 < point[0] - (l.x + l.width - 10) < 10 and
                0 < point[1] - l.y < 10)

    def render(self):
        l = self.layout
        l.x = self.node.x + self.node.cw + 25
        l.y = self.node.y - l.height + self.node.ch + 25

        if self.hover:
            if self.document.text:
                self.document.set_style(0, len(self.node.code),
                                        dict(color=(255, 255, 255, 255)))
            quad_aligned(l.x - 20, l.y,
                         l.width + 20, l.height + 10,
                         (0, 0, 0, 150))
            quad_aligned(l.x - 20, l.y, 5, l.height + 10,
                         self.node.color + (255,))
            quad_aligned(l.x + l.width - 10, l.y, 10, 10,
                         self.node.color + (255,))
        else:
            if self.document.text:
                self.document.set_style(0, len(self.node.code),
                                        dict(color=(255, 255, 255, 50)))

        self.layout.draw()

    # --- Input events ---

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.screen_size)

        if self.intersect_corner((x, y)):
            self.resize = True
        elif button == 1 and self.hover:
            self.set_focus()
            self.caret.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = x_y_pan_scale(x, y, self.pan_scale, self.screen_size)
        dx, dy = int(dx / self.pan_scale[1]), int(dy / self.pan_scale[1])

        if buttons == 1 and self.resize:
            self.layout.width = max(self.layout.width + dx, 300)
            self.layout.height = max(self.layout.height - dy, 150)
            self.node.editorSize = (self.layout.width, self.layout.height)
        elif buttons == 1 and self.hover:
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        self.resize = False

    def on_text(self, text):
        if self.hover:
            self.caret.on_text(text)
            self.update_node()

    def on_text_motion(self, motion):
        if self.hover:
            self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.hover:
            self.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        key = pyglet.window.key

        if symbol == key.TAB:
            self.document.insert_text(self.caret.position, '    ')
            self.caret.position += 4

        elif modifiers & key.MOD_CTRL:
            if symbol == key.C:
                start = min(self.caret.position, self.caret.mark)
                end = max(self.caret.position, self.caret.mark)
                text = self.document.text[start:end]
                clipboard.copy(text)
            elif symbol == key.V:
                text = clipboard.paste()
                self.document.insert_text(self.caret.position, text)
                self.caret.position += len(text)

    def on_key_release(self, symbol, modifiers):
        k = pyglet.window.key
        if symbol == k.BACKSPACE or symbol == k.DELETE:
            self.update_node()

    def set_focus(self):
        self.caret.visible = True
        self.caret.mark = 0
        self.caret.position = len(self.document.text)

    def __del__(self):
        self.update_node()
