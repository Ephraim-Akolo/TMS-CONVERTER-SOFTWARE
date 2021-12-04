
__version__ = "1.0.0"

import ctypes
engine = ctypes.CDLL("./engine.so")
engine.convert.argtypes = [ctypes.c_char_p]
engine.convert.restype = ctypes.c_int 
from pathlib import Path
from kivy.config import Config
Config.set('graphics', 'width', '960')
Config.set('graphics', 'height', '540')
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'KIVY_GL_BACKEND', 'angle_sdl2')
Config.set('kivy', 'window_icon', './data/logo.ico')
# from kivy.core.window import Window
# Window.top = 40
# Window.left = 20
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from plyer import filechooser 

class MainWidget(Widget):
    paths = []
    b_pressed = False
    clear_once = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def convert_pressed(self, button, textinput):
        if not len(self.paths) == 0 :
            if not self.paths[0] == "":
                for p in self.paths:
                    try:
                        engine.convert(Path(p).as_posix().encode())
                    except:
                        print("failed: ", Path(p).as_posix().encode())
                textinput.text = ""
                textinput.disabled = False
                button.background_normal = "data/button_done.png"
        
    def brower_pressed(self, convert_button, textinput):
        self.paths = filechooser.open_file(title="choose file", multiple=True, preview=True)
        convert_button.background_normal = "data/button_normal.png"
        textinput.text = ",".join(self.paths)
        self.opacity = 1
        if len(self.paths) != 0:
            textinput.disabled = True

    def brower_press(self):
        self.opacity = .1
    
    def clear_text(self, textinput, convert_button):
        convert_button.background_normal = "data/button_normal.png"
        if self.clear_once:
            textinput.text = ""
            self.clear_once = False
        if not textinput.focus:
            self.paths = [textinput.text]


class App(App):
    pass

if __name__ == "__main__":
    App().run()