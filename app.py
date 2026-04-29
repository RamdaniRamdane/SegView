import tifffile

from file_manager import FileManager
from image_utils import display


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.file_manager = FileManager(ui)

        self.file_path = ""
        self.data = None
        self.prediction = None
        self.shape = None
        self.zoom = 0
        self.has_prediction = False

    def bind_events(self):
        self.ui.btn.config(command=self.open_file)
        self.ui.refuse_but.config(command=lambda: self.save(False))
        self.ui.validate_but.config(command=lambda: self.save(True))
        self.ui.zoom_slider.config(command=self.change_z)

    def open_file(self):
        from tkinter import filedialog

        path = filedialog.askopenfilename()
        if not path:
            return

        self.file_path = path

        display_path = path if len(path) <= 72 else "..." + path[-70:]
        self.ui.path_label.config(text=display_path, fg="white")

        self.data = tifffile.imread(path)
        self.shape = self.data.shape
        self.zoom = 0

        self.ui.info_label.config(text=f"shape={self.shape} dtype={self.data.dtype}")

        # load prediction
        self.prediction, self.has_prediction = self.file_manager.get_prediction(path)

        # slider config
        if self.data.ndim > 2:
            self.ui.zoom_slider.config(to=self.shape[0] - 1)
            self.ui.zoom_slider.set(0)
        else:
            self.ui.zoom_slider.config(to=0)

        self.update_display()

    def update_display(self):
        if self.data is None:
            return

        img = self.data if self.data.ndim == 2 else self.data[self.zoom]

        if self.has_prediction:
            pred = (
                self.prediction
                if self.prediction.ndim == 2
                else self.prediction[self.zoom]
            )
            display(self.ui.canvas, img, pred)
        else:
            display(self.ui.canvas, img)

    def change_z(self, val):
        self.zoom = int(val)
        self.update_display()

    def save(self, is_valid):
        if not self.file_path:
            return

        self.file_manager.save_choice(self.file_path, is_valid)

        st = 1 if is_valid else 2
        from ui_utils import UIutils

        UIutils.set_flag(self.ui.flag_sign, self.ui.flag_text, st)
