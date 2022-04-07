
__version__ = "1.1.0"

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
from kivy.app import App
from kivy.uix.widget import Widget
from plyer import filechooser
from threading import Thread
from kivy.uix.modalview import ModalView
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Line, Color
from kivy.metrics import dp
from zipfile import ZipFile, ZIP_DEFLATED

from pdf2image import convert_from_path
__POPPLER_PATH__ = Path("poppler-22.01.0/Library/bin").resolve()


class Loading(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start = 0
        self.stop = 180
        self.widget = Widget(size_hint=(None, None), size=(dp(50), dp(50)), pos=self.pos)
        with self.widget.canvas:
            Color(rgba=(1., .65, 0, 1))
            self.loading_obj = Line(width=dp(5))
        self.add_widget(self.widget)
        Clock.schedule_interval(self.size_change, 1/15)
        App.get_running_app().loading_view = self
    
    def size_change(self, dt):
        self.start += 40
        self.stop += 40
        self.loading_obj.ellipse = (
                self.center_x-self.widget.width/2, 
                self.center_y-self.widget.height/2, 
                self.widget.width, self.widget.height, self.start, self.stop)


class MainWidget(Widget):
    paths = []
    b_pressed = False
    clear_once = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dpi = "750"
        self.doc_threads = []

    def process_doc(self, path):
        _path = Path(path)
        self.paths.remove(path)
        pages = convert_from_path(_path, 2, grayscale=True, poppler_path=__POPPLER_PATH__, size=(int(self._dpi), None))
        for i, page in enumerate(pages):
            self.paths.append(_path.parents[0]/f'{_path.stem}{i+1}.png')
            page.save(self.paths[-1], 'PNG')
        _path.unlink()

        
    def convert_pressed(self, button, textinput):
        self.loading = Factory.Loading()
        self.loading.open()
        _text = self.ids.dpi_input.text
        if _text == "" or int(_text) < 200:
            self.ids.dpi_input.text = self._dpi ="200"
        else:
            self._dpi = _text

        if not len(self.paths) == 0 :
            if not self.paths[0] == "":
                for p in self.paths:
                    if p.split(".")[-1] == "pdf":
                        self.doc_threads.append(Thread(name="process_pdf", target=self.process_doc, args=[p], daemon=True))
                for t in self.doc_threads:
                    t.start()
        self._clock = Clock.schedule_interval(lambda x: self.threads_done(button, textinput), 1/10)

    def threads_done(self, button, textinput):
        for t in self.doc_threads:
            if t.is_alive():
                return
        self.doc_threads = []
        self._convert_pressed(button, textinput)
        self._clock.cancel()

    def _convert_pressed(self, button, textinput):
        for p in self.paths:
            try:
                engine.convert(Path(p).as_posix().encode())
            except:
                print("failed: ", Path(p).as_posix().encode())
                
        with ZipFile('Please_rename.zip', 'w', ZIP_DEFLATED) as zipMe:        
            for file in self.paths:
                p = Path(file)
                p = p.parents[0]/(p.stem + ".tms")
                zipMe.write(p.name)
                p.unlink()
    
        textinput.text = ""
        textinput.disabled = False
        button.background_normal = "data/button_done.png"
        self.loading.dismiss()
        
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