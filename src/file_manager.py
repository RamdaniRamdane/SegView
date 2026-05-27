import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

import tifffile

from src.ui_utils import UIutils


class FileManager:
    def __init__(self, ui=None, state=None):
        if ui:
            self.ui = ui
        if state:
            self.state = state
        if ui and state:
            self.ui_handel = UIutils(ui, state)

    def get_prediction(self, file_path, out_path):
        if not file_path or not out_path:
            return None, None, False
        filename = os.path.basename(file_path)
        pred_path = os.path.join(out_path, filename)
        if os.path.isfile(pred_path):
            self.ui.sidebarright.refuse_but.grid()
            self.ui.sidebarright.validate_but.grid()
            pred = tifffile.imread(pred_path)
            st = self.status(pred_path)
            self.ui.st = st
            UIutils.set_flag(
                self.ui.status.flag_sign,
                self.ui.status.flag_text,
                st,
            )
            return pred, pred_path, True
        UIutils.set_flag(
            self.ui.status.flag_sign,
            self.ui.status.flag_text,
            0,
        )
        return None, None, False

    def status(self, file_path):
        if not file_path:
            return 0
        parent = os.path.dirname(os.path.dirname(file_path))
        filename = os.path.basename(file_path)
        path_val = os.path.join(
            parent,
            "Valide",
            filename,
        )
        path_ref = os.path.join(
            parent,
            "NON-valide",
            filename,
        )
        path_out = os.path.join(self.ui.state.path_out, filename)
        print("path valide:", path_val)
        print("path refused:", path_ref)
        if os.path.isfile(path_val):
            return 1

        if os.path.isfile(path_ref):
            return 2
        if os.path.isfile(path_out):
            return 3
        return 4

    def save_choice(
        self,
        file_path,
        out_path,
        is_valid,
    ):
        if not file_path or not out_path:
            return
        filename = os.path.basename(file_path)
        parent = os.path.dirname(out_path)
        valid_path = os.path.join(parent, "Valide")
        self.ui.state.path_out_valide = valid_path
        print(
            "changed self.ui.state.path_out_valide line 71 src/file_manager.py : ",
            self.ui.state.path_out_valide,
        )
        invalid_path = os.path.join(parent, "NON-valide")
        os.makedirs(valid_path, exist_ok=True)
        os.makedirs(invalid_path, exist_ok=True)
        src = file_path
        if is_valid:
            dst = os.path.join(valid_path, filename)
            old = os.path.join(
                invalid_path,
                filename,
            )
        else:
            dst = os.path.join(invalid_path, filename)
            old = os.path.join(
                valid_path,
                filename,
            )
        if os.path.isfile(old):
            shutil.move(old, dst)
        else:
            shutil.copy(src, dst)
        self.ui.sidebarleft.update_color_text_file()

    def open_dir(self, action, path_dir=None):
        if not path_dir:
            path_dir = filedialog.askdirectory(title=action)
        if not path_dir:
            return
        if not os.path.isdir(path_dir):
            print("dagui : ", path_dir)
            messagebox.showerror(
                title="Not found",
                message="directory not found",
            )
            return
        if action in ["PATH_RAW", "PATH_PRED"]:
            files = os.listdir(path_dir)

            tif_files = [f for f in files if f.lower().endswith(".tif")]

            if not tif_files:
                print("no tif file", path_dir)
                messagebox.showerror(
                    title="Not found",
                    message="no tif file in this dir",
                )
                return
            if action == "PATH_RAW":
                self.state.path_dir = path_dir
                self.state.files = tif_files
                self.ui.sidebarleft.show_files_list()
                self.ui.set_state(self.state)
                self.ui.sidebarleft.update_color_text_file()
                self.ui.sidebarright.navigateFrame.grid()
                self.ui.sidebarright.next_btn.config(state=tk.NORMAL)
                self.ui.sidebarright.prev_btn.config(state=tk.NORMAL)
                self.ui.zoom_slider.config(state=tk.NORMAL)
                self.ui.sidebarright.get_model.config(
                    state=tk.NORMAL,
                    fg="white",
                )
                self.ui.sidebarright.btn.config(bg="white", fg="black")
                first_path = os.path.join(
                    path_dir,
                    tif_files[0],
                )

                self.open_file(first_path)

            elif action == "PATH_PRED":
                self.state.path_out = path_dir
                self.ui.sidebarright.refuse_but.config(state=tk.NORMAL)
                self.ui.sidebarright.validate_but.config(state=tk.NORMAL)
                (
                    self.state.prediction,
                    self.state.prediction_path_file,
                    self.state.has_prediction,
                ) = self.get_prediction(
                    self.state.file_path,
                    self.state.path_out,
                )

                self.ui.sidebarleft.update_color_text_file()
                if self.ui.st == 2:
                    self.ui.sidebarright.correct_but.grid()
                else:
                    self.ui.sidebarright.correct_but.grid_remove()
                self.state.edit_mode = False
                self.ui.sidebarright.edit_frame.grid_remove()
                self.ui_handel.update_display()
        else:
            self.state.path_log = path_dir
            self.ui.sidebarright.get_model.config(bg="orange")
            self.ui.sidebarright.pred.grid()

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
        self.ui.status.info_label.config(
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
        ) = self.get_prediction(
            self.state.file_path,
            self.state.path_out,
        )
        self.ui.sidebarleft.update_color_text_file()
        if self.ui.st == 2:
            self.ui.sidebarright.correct_but.grid()
        else:
            self.ui.sidebarright.correct_but.grid_remove()
        if self.state.edited:
            self.ui.sidebarright.changes_state_label.grid_remove()
        else:
            self.ui.sidebarright.changes_state_label.grid()
        self.state.edit_mode = False
        self.ui.sidebarright.edit_frame.grid_remove()
        self.ui_handel.update_display()
