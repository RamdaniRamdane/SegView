import os
import shutil
import threading
import tkinter as tk
from dataclasses import dataclass, field
from time import sleep
from tkinter import filedialog, messagebox

import torch
from biom3d.pred import pred
from biom3d.preprocess import auto_config_preprocess
from biom3d.train import train

import src.ui.theme as theme
from src.services.file_manager import FileManager
from src.ui.helpers.edit_mode import EditMode
from src.ui.helpers.ui_utils import UIutils


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
    files_out: list = field(default_factory=list)

    index: int = 0

    path_dir: str = ""
    path_out: str = ""
    path_out_valide: str = ""
    path_out_list: list = field(default_factory=list)
    predStarted = False

    edit_mode: bool = False
    edit_tool: str = ""

    edited: int = 0
    config_path = str = ""


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.state = AppState()
        self.ui.set_state(self.state)
        self.file_manager = FileManager(ui, self.state, self)
        self.edit_mode_utils = EditMode(self)
        self.ui_handel = UIutils(self.ui, self.state, self.file_manager)
        self.worker = None
        self.result = None

    def bind_events(self):

        self.ui.topbar.pred_btn.config(command=lambda: self.route("prediction"))
        self.ui.topbar.rev_btn.config(command=lambda: self.route("review"))
        self.ui.topbar.fine_btn.config(command=lambda: self.route("fineTune"))
        self.ui.sidebarright.btn.config(
            command=lambda: self.file_manager.open_dir("PATH_RAW")
        )

        self.ui.sidebarright.refuse_but.config(
            command=lambda: self.save("refuse"),
        )
        self.ui.sidebarright.validate_but.config(
            command=lambda: self.save("validate"),
        )
        self.ui.sidebarright.unreview_but.config(
            command=lambda: self.save("unreview"),
        )
        self.ui.zoom_slider.config(
            state=tk.DISABLED,
            command=self.ui_handel.change_z,
        )
        self.ui.sidebarright.next_btn.config(
            state=tk.DISABLED,
            command=lambda: self.ui_handel.navigate("NEXT"),
        )
        self.ui.sidebarright.prev_btn.config(
            state=tk.DISABLED,
            command=lambda: self.ui_handel.navigate("PREV"),
        )
        self.ui.sidebarright.get_model.config(
            state=tk.DISABLED,
            command=lambda: self.file_manager.open_dir("PATH_LOG"),
        )
        self.ui.sidebarright.get_folder_out.config(command=self.get_out_path)
        self.ui.sidebarright.pred.config(command=self.run_prediction)
        self.ui.sidebarright.get_predictions_path.config(
            command=lambda: self.file_manager.open_dir("PATH_PRED")
        )
        self.ui.sidebarright.correct_but.config(
            command=self.edit_mode_utils.toggle_edit_mode
        )
        self.ui.sidebarright.brush.config(
            command=lambda: self.edit_mode_utils.toggle_tool("Brush")
        )
        self.ui.sidebarright.ereaser.config(
            command=lambda: self.edit_mode_utils.toggle_tool("Ereaser")
        )
        self.ui.sidebarright.save_changes.config(
            command=self.edit_mode_utils.save_changes
        )
        self.ui.canvas.bind(
            "<ButtonPress-1>",
            self.edit_mode_utils.on_mouse_down,
        )
        self.ui.canvas.bind(
            "<B1-Motion>",
            self.edit_mode_utils.on_mouse_drag,
        )

    # load config for fine tuning :

    def make_config_fine_tuning(self):
        self.state.config_path = auto_config_preprocess(
            img_path=self.state.path_dir,
            msk_path=self.state.path_out,
            num_classes=1,
            config_dir="configs",
            base_config=None,
            ct_norm=False,
            desc="unet",
            max_dim=128,
            num_epochs=1,
            is_2d=False,
        )

    def run_fine_tuning(self):
        # problem with windows a regler et a tester avec mac
        if not torch.cuda.is_available() and not torch.backends.mps.is_available():
            messagebox.showerror("Error", "No GPU detected in your machine")
            return
        fine = train(
            config=self.state.config_path,
            path=self.state.path_log,
        )
        print(fine.model_dir)

    # sidebarleft handle

    # for test

    def biopred_simulation(self):
        # a enlever
        path_to_return = "/home/rey/FRSTUDIES/stage/dev/tkinter1/TEST/out3/20260331-170607-Fluo-C3DL-MDA231_02_ST_20epochs_fold0/nuclei_20.tif"
        sleep(10)
        os.mkdir(
            "/home/rey/FRSTUDIES/stage/dev/tkinter1/TEST/testprogress/20260331-170607-Fluo-C3DL-MDA231_02_ST_20epochs_fold0/"
        )
        src = "/home/rey/FRSTUDIES/stage/dev/tkinter1/TEST/fg_out/"
        dist = "/home/rey/FRSTUDIES/stage/dev/tkinter1/TEST/testprogress/20260331-170607-Fluo-C3DL-MDA231_02_ST_20epochs_fold0/"
        files_out = os.listdir(src)

        for file in files_out:
            src_tocopy = os.path.join(src, file)
            shutil.copy(src_tocopy, dist)
            sleep(3)

        return path_to_return

    def _worker(self):
        try:
            if not torch.cuda.is_available() and not torch.backends.mps.is_available():
                print(torch.cuda.is_available())
                messagebox.showerror("Warninig", "No GPU detected in your machine")
                self.result = self.biopred_simulation()
            else:
                self.result = pred(
                    log=self.state.path_log,
                    path_in=self.state.path_dir,
                    path_out=self.state.path_out,
                    skip_preprocessing=False,
                )

        except Exception as e:
            self.result = e

    def _check(self):
        if self.worker.is_alive():
            try:
                if not self.state.predStarted:
                    out_list = os.listdir(self.state.path_out)
                    execp = ["Valide", "NON-valide"]
                    diff = list(set(out_list) - set(self.state.path_out_list))
                    if diff:
                        candidate = diff[0]
                        for el in diff:
                            if el not in execp:
                                candidate = el
                        new_path = os.path.join(self.state.path_out, candidate)
                        if os.path.isdir(new_path):
                            self.state.path_out = new_path
                            self.result = new_path
                            self.state.predStarted = True
                else:
                    files_out = os.listdir(self.state.path_out)
                    if len(files_out) == 1:
                        self.go_to_review(self.state.path_out)
                    if len(files_out) > len(self.state.files_out):
                        test = self.ui.sidebarleft.progressbar["mode"]
                        if str(test) == "indeterminate":
                            self.ui.sidebarleft.toggl_determinate_mode(
                                self.ui.sidebarleft.progressbar
                            )
                        self.ui.sidebarleft.progressbar_handler(
                            self.ui.sidebarleft.progressbar,
                            "GROW",
                            len(self.state.files),
                        )
                        self.ui.sidebarleft.update_color_text_file()
                    self.state.files_out = os.listdir(self.state.path_out)
            except Exception as e:
                print("Erreur lors du listing:", e)
            self.ui.root.after(1000, self._check)
            return

        if isinstance(self.result, Exception):
            messagebox.showerror("Error", str(self.state.path_out))
            print(Exception)
            print("result", self.result)
        else:
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)
            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar, "RESET"
            )
            messagebox.showinfo("Done", f"prediction saved here: {self.result}")
            self.state.predStarted = False

    def get_out_path(self):
        out = filedialog.askdirectory(title="Destination for model predictions")
        if out:
            ls = os.listdir(out)

        if out and not ls:
            self.state.path_out = out
            self.ui.sidebarright.pred.grid()
            self.ui.sidebarright.get_folder_out.config(bg="white", fg="black")
            self.ui.sidebarright.get_predictions_path.config(bg="white", fg="black")
        else:
            user_response = messagebox.askquestion(
                title="Error",
                message="problem occurred , path not found or the folder is not empty \n -> Do you want to empty it before?",
                type="yesno",
            )
            if user_response and out:
                for item in ls:
                    if os.path.isfile(os.path.join(out, item)):
                        os.remove(os.path.join(out, item))
                    else:
                        shutil.rmtree(os.path.join(out, item))
                self.state.path_out = out
                self.ui.sidebarright.pred.grid()
                self.ui.sidebarright.get_folder_out.config(bg="white", fg="black")
        return out

    def run_prediction(self):
        if not self.state.path_log:
            messagebox.showerror("Error", "No model selected")
            return
        if not self.state.path_dir:
            messagebox.showerror("Error", "No input folder selected")
            return
        # out = filedialog.askdirectory(title="Destination for model predictions")
        if not self.state.path_out:
            messagebox.showerror("Error", "No output folder selected")
            return
        # self.state.path_out = path_out
        self.worker = threading.Thread(target=self._worker, daemon=True)
        self.worker.start()
        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)
        self._check()

    def save(self, action):
        if not self.state.file_path:
            return
        self.file_manager.save_choice(
            self.state.file_path,
            self.state.path_out,
            action,
        )
        if action == "validate":
            st = 1
        elif action == "refuse":
            st = 2
        else:
            st = 3
        UIutils.set_flag(
            self.ui.status.flag_sign,
            self.ui.status.flag_text,
            st,
        )

        if st == 2:
            self.ui.sidebarright.correct_but.grid()
        else:
            self.ui.sidebarright.correct_but.grid_remove()
        if self.state.edited:
            self.ui.sidebarright.changes_state_label.grid_remove()
        else:
            self.ui.sidebarright.changes_state_label.grid()

        self.ui.sidebarleft.update_color_text_file()

    def route(self, route):
        if route == "prediction":
            self.go_to_prediction()
        elif route == "review":
            self.go_to_review()
        elif route == "fineTune":
            self.go_to_fine()

    def go_to_prediction(self):
        self.ui.topbar.pred_btn.config(bg="white", fg="black")
        self.ui.topbar.rev_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.topbar.fine_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.sidebarright.pred_frame.grid()
        self.ui.sidebarright.get_folder_out.grid()
        self.ui.sidebarright.rev_Frame.grid_remove()

    def go_to_review(self, path=None):
        if path:
            self.file_manager.open_dir("PATH_PRED", path)
        self.ui.topbar.pred_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.topbar.rev_btn.config(bg="white", fg="black")
        self.ui.topbar.fine_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.sidebarright.rev_Frame.grid()
        self.ui.sidebarright.pred_frame.grid_remove()

    def go_to_fine(self):
        self.ui.topbar.fine_btn.config(bg="white", fg="black")
        self.ui.topbar.rev_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.topbar.pred_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.sidebarright.pred_frame.grid_remove()
        self.ui.sidebarright.rev_Frame.grid_remove()
        # self.make_config_fine_tuning()
        # on change son appel ...
        # self.run_fine_tuning()
