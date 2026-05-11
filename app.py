import os
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import filedialog, messagebox

import tifffile
from biom3d.pred import pred

from file_manager import FileManager
from image_utils import display
from ui_helpers import EditMode
from ui_utils import UIutils

BG = "#0e0e0f"
MUTED = "#141416"
TEXT_HI = "#e8e8f0"
MUTED = "#3a3a40"  # inactive elements


@dataclass
class AppState:
    path_log: str = ""
    file_path: str = ""
    prediction_path_file: str = ""

    data: object = None
    prediction: object = None

    shape: tuple | None = None

    zoom: int = 0

    has_prediction: bool = False

    files: list = field(default_factory=list)

    index: int = 0

    path_dir: str = ""
    path_out: str = ""

    edit_mode: bool = False
    edit_tool: str = ""

    edited: int = 0


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.state = AppState()
        self.file_manager = FileManager(ui)
        self.edit_mode_utils = EditMode(self)

    def bind_events(self):

        self.ui.pred_btn.config(command=lambda: self.route("prediction"))
        self.ui.rev_btn.config(command=lambda: self.route("review"))
        self.ui.fine_btn.config(command=lambda: self.route("fineTune"))
        self.ui.btn.config(command=lambda: self.open_dir("PATH_RAW"))

        self.ui.refuse_but.config(
            state=tk.DISABLED,
            command=lambda: self.save(False),
        )
        self.ui.validate_but.config(
            state=tk.DISABLED,
            command=lambda: self.save(True),
        )
        self.ui.zoom_slider.config(
            state=tk.DISABLED,
            command=self.change_z,
        )
        self.ui.next_btn.config(
            state=tk.DISABLED,
            command=lambda: self.navigate("NEXT"),
        )
        self.ui.prev_btn.config(
            state=tk.DISABLED,
            command=lambda: self.navigate("PREV"),
        )
        self.ui.get_model.config(
            state=tk.DISABLED,
            command=lambda: self.open_dir("PATH_LOG"),
        )
        self.ui.get_folder_out.config(command=lambda: self.open_dir("PATH_PRED"))
        self.ui.pred.config(command=self.run_prediction)
        self.ui.get_predictions_path.config(command=lambda: self.open_dir("PATH_PRED"))
        self.ui.correct_but.config(command=self.edit_mode_utils.toggle_edit_mode)
        self.ui.brush.config(command=lambda: self.edit_mode_utils.toggle_tool("Brush"))
        self.ui.ereaser.config(
            command=lambda: self.edit_mode_utils.toggle_tool("Ereaser")
        )
        self.ui.save_changes.config(command=self.edit_mode_utils.save_changes)
        self.ui.canvas.bind(
            "<ButtonPress-1>",
            self.edit_mode_utils.on_mouse_down,
        )
        self.ui.canvas.bind(
            "<B1-Motion>",
            self.edit_mode_utils.on_mouse_drag,
        )

    def run_prediction(self):

        if not self.state.path_log:
            messagebox.showerror("Error", "No model selected")
            return
        if not self.state.path_dir:
            messagebox.showerror("Error", "No input folder selected")
            return
        if not self.state.path_out:
            messagebox.showerror("Error", "No output folder selected")
            return
        pred(
            log=self.state.path_log,
            path_in=self.state.path_dir,
            path_out=self.state.path_out,
            skip_preprocessing=False,
        )
        messagebox.showinfo("Done", "Prediction finished")

    def open_dir(self, action):
        path_dir = filedialog.askdirectory()
        if not path_dir:
            return
        if not os.path.isdir(path_dir):
            messagebox.showerror(
                title="Not found",
                message="directory not found",
            )
            return
        if action in ["PATH_RAW", "PATH_PRED"]:
            files = os.listdir(path_dir)

            tif_files = [f for f in files if f.lower().endswith(".tif")]

            if not tif_files:
                messagebox.showerror(
                    title="Not found",
                    message="no tif file in this dir",
                )
                return
            if action == "PATH_RAW":
                self.state.path_dir = path_dir
                self.state.files = tif_files
                self.ui.use_cases.grid()
                self.ui.navigateFrame.grid()
                self.ui.next_btn.config(state=tk.NORMAL)
                self.ui.prev_btn.config(state=tk.NORMAL)
                self.ui.zoom_slider.config(state=tk.NORMAL)
                self.ui.get_model.config(
                    state=tk.NORMAL,
                    fg="white",
                )
                self.ui.btn.config(bg="white", fg="black")
                first_path = os.path.join(
                    path_dir,
                    tif_files[0],
                )

                self.open_file(first_path)

            elif action == "PATH_PRED":
                self.state.path_out = path_dir
                self.ui.refuse_but.config(state=tk.NORMAL)
                self.ui.validate_but.config(state=tk.NORMAL)
                (
                    self.state.prediction,
                    self.state.prediction_path_file,
                    self.state.has_prediction,
                ) = self.file_manager.get_prediction(
                    self.state.file_path,
                    self.state.path_out,
                )
                if self.ui.st == 2:
                    self.ui.correct_but.grid()
                else:
                    self.ui.correct_but.grid_remove()
                self.state.edit_mode = False
                self.ui.edit_frame.grid_remove()
                self.update_display()
        else:
            self.state.path_log = path_dir
            self.ui.get_model.config(bg="orange")
            self.ui.pred.grid()
            self.ui.get_folder_out.grid()

    def open_file(self, path):
        if not os.path.isfile(path):
            messagebox.showerror(
                title="Not found",
                message="file not found",
            )
            return
        self.state.file_path = path
        display_path = path if len(path) <= 72 else "..." + path[-70:]
        self.ui.path_label.config(
            text=display_path,
            fg="white",
        )
        self.state.data = tifffile.imread(path)
        self.state.shape = self.state.data.shape

        if self.state.data.ndim > 2:
            self.state.zoom = int(self.state.shape[0] / 2)
        else:
            self.state.zoom = 0
        self.ui.info_label.config(
            text=f"shape={self.state.shape} dtype={self.state.data.dtype}"
        )
        if self.state.data.ndim > 2:
            self.ui.zoom_slider.config(to=self.state.shape[0] - 1)
            self.ui.zoom_slider.set(self.state.zoom)
        else:
            self.ui.zoom_slider.config(to=0)
        (
            self.state.prediction,
            self.state.prediction_path_file,
            self.state.has_prediction,
        ) = self.file_manager.get_prediction(
            self.state.file_path,
            self.state.path_out,
        )
        if self.ui.st == 2:
            self.ui.correct_but.grid()
        else:
            self.ui.correct_but.grid_remove()
        if self.state.edited:
            self.ui.changes_state_label.grid_remove()
        else:
            self.ui.changes_state_label.grid()
        self.state.edit_mode = False
        self.ui.edit_frame.grid_remove()
        self.update_display()

    def navigate(self, direction):
        if not self.state.files:
            return
        if direction == "NEXT":
            self.state.index = (self.state.index + 1) % len(self.state.files)
        elif direction == "PREV":
            self.state.index = (self.state.index - 1) % len(self.state.files)
        file_path = os.path.join(
            self.state.path_dir,
            self.state.files[self.state.index],
        )
        self.open_file(file_path)

    def update_display(self):
        if self.state.data is None:
            return
        if self.state.data.ndim == 2:
            img = self.state.data
        else:
            img = self.state.data[self.state.zoom]

        if self.state.has_prediction and self.state.prediction is not None:
            if self.state.prediction.ndim == 2:
                pred_img = self.state.prediction
            else:
                pred_img = self.state.prediction[self.state.zoom]
            display(
                self.ui.canvas,
                img,
                pred_img,
            )
        else:
            display(self.ui.canvas, img)

    def change_z(self, val):
        self.state.zoom = int(float(val))
        self.update_display()

    def save(self, is_valid):
        if not self.state.file_path:
            return
        self.file_manager.save_choice(
            self.state.file_path,
            self.state.path_out,
            is_valid,
        )
        st = 1 if is_valid else 2
        UIutils.set_flag(
            self.ui.flag_sign,
            self.ui.flag_text,
            st,
        )
        if st == 2:
            self.ui.correct_but.grid()
        else:
            self.ui.correct_but.grid_remove()
        if self.state.edited:
            self.ui.changes_state_label.grid_remove()
        else:
            self.ui.changes_state_label.grid()

    def route(self, route):
        if route == "prediction":
            self.ui.pred_btn.config(bg="white", fg="black")
            self.ui.rev_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.fine_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.pred_frame.grid()
            self.ui.rev_Frame.grid_remove()
        elif route == "review":
            self.ui.pred_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.rev_btn.config(bg="white", fg="black")
            self.ui.fine_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.rev_Frame.grid()
            self.ui.pred_frame.grid_remove()
        elif route == "fineTune":
            self.ui.fine_btn.config(bg="white", fg="black")
            self.ui.rev_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.pred_btn.config(bg=MUTED, fg=TEXT_HI)
            self.ui.pred_frame.grid_remove()
            self.ui.rev_Frame.grid_remove()
