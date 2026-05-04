import os
import tkinter as tk
from tkinter import filedialog

import tifffile

from biom3d_handel import Biom3d
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
        self.files = []
        self.index = 0
        self.path_dir = ""
        self.biom = Biom3d()

    def bind_events(self):
        self.ui.btn.config(command=self.open_dir)
        self.ui.refuse_but.config(state=tk.DISABLED, command=lambda: self.save(False))
        self.ui.validate_but.config(state=tk.DISABLED, command=lambda: self.save(True))
        self.ui.zoom_slider.config(state=tk.DISABLED, command=self.change_z)
        self.ui.next_btn.config(
            state=tk.DISABLED, command=lambda: self.navigate("NEXT")
        )
        self.ui.prev_btn.config(
            state=tk.DISABLED, command=lambda: self.navigate("PREV")
        )
        self.ui.get_model.config(command=self.biom.get_model)

    def open_dir(self):
        path_dir = filedialog.askdirectory()
        if os.path.isdir(path_dir):
            self.path_dir = path_dir
            files = os.listdir(path_dir)
            if any(f.endswith(".tif") for f in files):
                self.files = files
                path_first = path_dir + "/" + files[0]
                self.ui.next_btn.config(state=tk.NORMAL)
                self.ui.prev_btn.config(state=tk.NORMAL)
                self.ui.zoom_slider.config(state=tk.NORMAL)
                self.ui.refuse_but.config(state=tk.NORMAL)
                self.ui.validate_but.config(state=tk.NORMAL)

                self.open_file(path_first)
            else:
                tk.messagebox.showerror(
                    title="Not found", message="no tif file in this dir"
                )

        else:
            tk.messagebox.showerror(title="Not found", message="directory not found")

    def open_file(self, path):
        if os.path.isfile(path):
            self.file_path = path

            display_path = path if len(path) <= 72 else "..." + path[-70:]
            self.ui.path_label.config(text=display_path, fg="white")

            self.data = tifffile.imread(path)
            self.shape = self.data.shape
            # ici j ai mis le zoom au milieu car generalement le model detect dans le milieu (z,x,y)
            self.zoom = int(self.shape[0] / 2)

            self.ui.info_label.config(
                text=f"shape={self.shape} dtype={self.data.dtype}"
            )

            # load prediction
            self.prediction, self.has_prediction = self.file_manager.get_prediction(
                path
            )

            # slider config
            if self.data.ndim > 2:
                self.ui.zoom_slider.config(to=self.shape[0] - 1)
                self.ui.zoom_slider.set(self.zoom)
            else:
                self.ui.zoom_slider.config(to=0)

            self.update_display()
        else:
            tk.messagebox.showerror(title="Not found", message="file not found")

    def navigate(self, direction):
        if direction == "NEXT" and len(self.files):
            self.index = (
                self.index + 1
                if self.index < (len(self.files) - 1)
                else ((self.index + 1) % len(self.files))
            )
            self.open_file(self.path_dir + "/" + self.files[self.index])
        elif direction == "PREV" and len(self.files):
            self.index = (
                self.index - 1
                if self.index > 0
                else ((self.index - 1) % len(self.files))
            )

            self.open_file(self.path_dir + "/" + self.files[self.index])
        else:
            print("no files")

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
