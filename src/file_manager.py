import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

import tifffile

import theme
from src.ui_utils import UIutils


class FileManager:
    def __init__(self, ui=None, state=None, app=None):
        if ui:
            self.ui = ui
        if state:
            self.state = state
        if app:
            self.app = app
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
            self.ui.sidebarright.unreview_but.grid()
            pred = tifffile.imread(pred_path)
            st = self.status(pred_path)
            self.ui.st = st
            UIutils.set_flag(
                self.ui.status.flag_sign,
                self.ui.status.flag_text,
                st,
            )
            return pred, pred_path, True
        else:
            self.ui.sidebarright.refuse_but.grid_remove()
            self.ui.sidebarright.validate_but.grid_remove()
            self.ui.sidebarright.unreview_but.grid_remove()
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
        action,
    ):
        if not file_path or not out_path:
            return
        filename = os.path.basename(file_path)
        parent = os.path.dirname(out_path)
        valid_path = os.path.join(parent, "Valide")
        self.ui.state.path_out_valide = valid_path
        invalid_path = os.path.join(parent, "NON-valide")
        os.makedirs(valid_path, exist_ok=True)
        os.makedirs(invalid_path, exist_ok=True)
        src = file_path
        if action == "validate":
            dst = os.path.join(valid_path, filename)
            old = os.path.join(
                invalid_path,
                filename,
            )
        elif action == "refuse":
            dst = os.path.join(invalid_path, filename)
            old = os.path.join(
                valid_path,
                filename,
            )
        else:
            dst = ""
            old = ""
        if os.path.isfile(old):
            shutil.move(old, dst)
        elif dst:
            shutil.copy(src, dst)
        else:
            valide_file = os.path.join(valid_path, filename)
            invlid_file = os.path.join(invalid_path, filename)
            if os.path.isfile(valide_file):
                os.remove(valide_file)
            elif os.path.isfile(invlid_file):
                os.remove(invlid_file)
        self.ui.sidebarleft.update_color_text_file()
        valid_masks = os.listdir(self.state.path_out_valide)
        valid_len = len(valid_masks)
        if valid_len == len(self.state.files):
            self.app.go_to_fine()

    def open_dir(self, action, path_dir=None):
        if not path_dir:
            path_dir = filedialog.askdirectory(title=action)
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
                self.ui.sidebarleft.show_files_list()
                self.ui.set_state(self.state)
                self.ui.sidebarleft.update_color_text_file()
                for i in range(len(self.ui.sidebarleft.file_buttons)):
                    self.ui.sidebarleft.file_buttons[i].config(
                        command=lambda idx=i: self.sidebarleft_handl_file(idx)
                    )
                self.ui.sidebarleft.file_buttons[0].config(bg="#555")
                for j in range(len(self.state.files)):
                    if not j == 0:
                        self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)
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
            # verrify that the path containe a model special biom3d pour l instant
            list_log = os.listdir(path_dir)
            if "model" in list_log:
                paths = os.path.join(path_dir, "model")
                list_model = os.listdir(paths)
                path_files = [f for f in list_model if f.lower().endswith(".pth")]
                if not path_files:
                    messagebox.showerror(
                        title="No Model Provided",
                        message="check if the folder contain model/*.pth , please import correct model",
                    )
                    return
                self.state.path_log = path_dir
                self.ui.sidebarright.get_model.config(bg="orange")
                self.ui.sidebarright.pred.grid()
            else:
                messagebox.showerror(
                    title="No Model Provided",
                    message="check if the folder contain model/*.pth , please import correct model",
                )
                return

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

    def sidebarleft_handl_file(self, i):
        self.state.index = i
        filename = self.state.files[i]
        path = os.path.join(self.state.path_dir, filename)
        self.open_file(path)
        self.ui.sidebarleft.file_buttons[i].config(bg="#555")
        self.ui.sidebarleft.button_on_view(self.ui.sidebarleft.file_buttons[i])
        for j in range(len(self.state.files)):
            if not j == i:
                self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)
