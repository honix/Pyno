import pyglet

from draw import uiGroup


class Menu:
    '''
    Patch controls (time control, save-load)
    '''

    offset = 10

    def __init__(self, window):
        self.window = window

        save_load_img = pyglet.image.load('imgs/save_load_32.png')
        self.save_load = pyglet.sprite.Sprite(
                save_load_img,
                x=800-save_load_img.width-self.offset, y=self.offset,
                batch=window.batch, group=uiGroup)

        self.save_load.opacity = 100

    def click(self, x, y, button=1):
        if self.update():
            s = self.save_load
            # RUN/PAUSE
            if x < s.x + (s.width / 3):
                if button == 1:
                    if not self.window.running:
                        self.window.running = -1  # -1: run continously
                    else:
                        self.window.running = 0   #  0: pause/stop
                elif (button == 4) and not self.window.running:
                    self.window.running = 1       #  n: do n steps
                    self.window.nodes_update()
                return True
            # SAVE
            if x < s.x + (s.width * 2 / 3):
                self.window.save_pyno()
            # LOAD
            else:
                self.window.load_pyno()
            return True

    def update(self):
        self.save_load.x = self.window.width - self.save_load.width - self.offset
        s = self.save_load
        if s.x < self.window.mouse[0] < s.x + s.width and \
           s.y < self.window.mouse[1] < s.y + s.height:
            s.opacity = 255
            return True
        s.opacity = 100
        return False
