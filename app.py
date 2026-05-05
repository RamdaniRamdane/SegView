import os
import tkinter as tk
from tkinter import filedialog

import tifffile
from biom3d.pred import pred

from file_manager import FileManager
from image_utils import display

BG = "#0e0e0f"  # near-black base
PANEL = "#141416"  # slightly lighter panel
BORDER = "#222226"  # subtle separator
MUTED = "#3a3a40"  # inactive elements
TEXT_DIM = "#555560"  # secondary labels
TEXT = "#c8c8d0"  # primary text
TEXT_HI = "#e8e8f0"  # highlighted text
ACCENT = "#4a9eff"  # blue accent (validate / active)
DANGER = "#d94f4f"  # red (refuse)
SUCCESS = "#3dab6e"  # green (validated status)
WARNING = "#c09030"  # amber (pending status)
MONO = "Courier"  # monospace for scientific labels
SANS = "Helvetica"  # clean sans


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.file_manager = FileManager(ui)
        self.path_log = ""
        self.file_path = ""
        self.data = None
        self.prediction = None
        self.shape = None
        self.zoom = 0
        self.has_prediction = False
        self.files = []
        self.index = 0
        self.path_dir = ""
        self.path_out = ""

    def bind_events(self):

        self.ui.pred_btn.config(command=lambda: self.route("prediction"))
        self.ui.rev_btn.config(command=lambda: self.route("review"))
        self.ui.fine_btn.config(command=lambda: self.route("fineTune"))
        self.ui.btn.config(command=lambda: self.open_dir("PATH_RAW"))
        self.ui.refuse_but.config(state=tk.DISABLED, command=lambda: self.save(False))
        self.ui.validate_but.config(state=tk.DISABLED, command=lambda: self.save(True))
        self.ui.zoom_slider.config(state=tk.DISABLED, command=self.change_z)
        self.ui.next_btn.config(
            state=tk.DISABLED, command=lambda: self.navigate("NEXT")
        )
        self.ui.prev_btn.config(
            state=tk.DISABLED, command=lambda: self.navigate("PREV")
        )
        self.ui.get_model.config(
            state=tk.DISABLED, command=lambda: self.open_dir("PATH_LOG")
        )
        self.ui.pred.config(
            command=lambda: pred(
                log=self.path_log,
                path_in=self.path_dir,
                path_out=self.path_out,
                skip_preprocessing=False,
            )
        )

    def open_dir(self, action):
        path_dir = filedialog.askdirectory()
        if os.path.isdir(path_dir):
            if action == "PATH_RAW":
                self.path_dir = path_dir
                path_out = self.path_dir.split("/")
                path_out.pop()
                self.path_out = "/".join(path_out) + "/final_out"
                print(self.path_out)
                files = os.listdir(path_dir)
                if len(files) > 1:
                    self.ui.navigateFrame.grid()

                if any(f.endswith(".tif") for f in files):
                    self.ui.use_cases.grid()
                    self.ui.get_model.grid()
                    self.files = files
                    path_first = path_dir + "/" + files[0]
                    self.ui.next_btn.config(state=tk.NORMAL)
                    self.ui.btn.config(bg="white", fg="black")
                    self.ui.prev_btn.config(state=tk.NORMAL)
                    self.ui.zoom_slider.config(state=tk.NORMAL)
                    self.ui.refuse_but.config(state=tk.NORMAL)
                    self.ui.validate_but.config(state=tk.NORMAL)
                    self.ui.get_model.config(state=tk.NORMAL, fg="white")
                    self.open_file(path_first)
                else:
                    tk.messagebox.showerror(
                        title="Not found", message="no tif file in this dir"
                    )
            else:
                self.path_log = path_dir
                self.ui.get_model.config(bg="orange")
                self.ui.pred.grid()
                self.ui.get_folder_out.grid()

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

    # a reecrire
    def route(self, route):
        if route == "prediction":
            self.ui.pred_btn.config(bg="white", fg="black")
            self.ui.rev_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.fine_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.pred_frame.grid()
            self.ui.rev_Frame.grid_remove()
        elif route == "review":
            self.ui.pred_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.rev_btn.config(bg="white", fg="black")
            self.ui.fine_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.rev_Frame.grid()
            self.ui.pred_frame.grid_remove()
        elif route == "fineTune":
            print(route)
            self.ui.fine_btn.config(bg="white", fg="black")
            self.ui.rev_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.pred_btn.config(bg=PANEL, fg=TEXT_HI)
            self.ui.pred_frame.grid_remove()
            self.ui.rev_Frame.grid_remove()
        else:
            print("nothing")
