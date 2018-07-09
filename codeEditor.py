import pyglet
import pyperclip

from utils import x_y_pan_scale, font
from draw import quad_aligned


class CodeEditor(object):
    '''
    Code editor is the window you define nodes function
    '''

    def __init__(self, node):
        self.node = node  # node-owner of this codeEditor
        self.document = pyglet.text.document.FormattedDocument(node.code)

        self.document.set_style(0, len(node.code),
                                dict(font_name=font,
                                font_size=11, color=(255, 255, 255, 230)))

        self.layout = pyglet.text.layout.IncrementalTextLayout(
                                self.document,
                                *node.editor_size,
                                multiline=True, wrap_lines=False)

        self.update_label = pyglet.text.Label('CTRL+ENTER to save and execute',
                                              font_name=font,
                                              font_size=9)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.color = (255, 255, 255)
        self.caret.visible = False
        self.hover = False
        self.hovered = True
        self.resize = False

        self.change = False

        self.pan_scale = [[0.0, 0.0], 1]
        self.screen_size = (800, 600)

    def update_node(self):
        # Push code to node
        self.node.new_code(self.document.text)
        self.node.need_update = True
        self.change = False

    def intersect_point(self, point):
        # Intersection with whole codeEditor
        l = self.layout
        if 0 < point[0] - l.x + 20 < l.width + 20 and \
           0 < point[1] - l.y < l.height + 10:
            self.node.hover = True
            return True
        return False

    def intersect_corner(self, point):
        # Intersection with bottom right corner to resize
        l = self.layout
        return (0 < point[0] - (l.x + l.width - 10) < 10 and
                0 < point[1] - l.y < 10)

    def render(self):
        self.node.make_child_active()

        l = self.layout
        l.x = self.node.x + self.node.cw + 25
        l.y = self.node.y - l.height + self.node.ch + 25

        if self.change:
            self.update_label.x = l.x
            self.update_label.y = l.y - 20
            self.update_label.draw()

        if self.hover:
            if self.document.text and not self.hovered:
                self.hovered = True
                self.document.set_style(0, len(self.node.code),
                                        dict(color=(255, 255, 255, 255)))

            color = self.node.color if not self.change else (255, 100, 10)
            #  codeEditor background
            quad_aligned(l.x - 20, l.y,
                         l.width + 20, l.height + 10,
                         ((0, 0, 0) if not self.change
                                    else (20, 10, 5)) + (230,))

            if self.resize:
                quad_aligned(self.node.x + self.node.cw + 5,
                             self.node.y + self.node.ch + 35,
                             self.node.editor_size[0] + 20,
                             -self.node.editor_size[1] - 10,
                             color + (100,))
            #  codeEditor left line
            quad_aligned(l.x - 20, l.y, 5, l.height + 10, color + (255,))
            #  codeEditor resize corner
            quad_aligned(l.x + l.width - 10, l.y, 10, 10, color + (255,))
        else:
            if self.document.text and self.hovered:
                self.hovered = False
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
            width = max(self.node.editor_size[0] + dx, 300)
            height = max(self.node.editor_size[1] - dy, 150)
            self.node.editor_size = width, height
        elif buttons == 1 and self.hover:
            self.caret.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.resize:
            self.layout.width, self.layout.height = self.node.editor_size
            self.resize = False

    def on_text(self, text):
        if self.hover:
            self.change = True
            self.caret.on_text(text)

    def on_text_motion(self, motion):
        if self.hover:
            self.caret.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        if self.hover:
            self.caret.on_text_motion_select(motion)

    def on_key_press(self, symbol, modifiers):
        key = pyglet.window.key

        if symbol == key.TAB:
            self.change = True
            self.document.insert_text(self.caret.position, '  ')
            self.caret.position += 2

        elif modifiers & key.MOD_CTRL and symbol == key.ENTER:
            print('Reload code')
            self.update_node()

        elif modifiers & key.MOD_CTRL:
            if symbol == key.C and self.caret.mark:
                start = min(self.caret.position, self.caret.mark)
                end = max(self.caret.position, self.caret.mark)
                text = self.document.text[start:end]
                pyperclip.copy(text)
            elif symbol == key.V:
                text = pyperclip.paste()
                self.document.insert_text(self.caret.position, text)
                self.caret.position += len(text)

        elif symbol == key.BACKSPACE or symbol == key.DELETE:
            self.change = True

    def set_focus(self):
        self.caret.visible = True
        self.caret.mark = 0
        self.caret.position = len(self.document.text)

    def __del__(self):
      self.layout.delete()
      self.update_label.delete()
      self.caret.delete()
