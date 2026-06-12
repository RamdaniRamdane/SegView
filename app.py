import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import torch
from biom3d.pred import pred
from biom3d.preprocess import auto_config_preprocess
from biom3d.train import train

from src.models.app_state import AppState
from src.services.file_manager import FileManager
from src.services.route import Route
from src.ui.helpers.edit_mode import EditMode
from src.ui.helpers.ui_utils import UIutils


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.state = AppState()
        self.ui.set_state(self.state)
        self.file_manager = FileManager(ui, self.state, self)
        self.edit_mode_utils = EditMode(self, self.state)
        self.ui_handel = UIutils(self.ui, self.state, self.file_manager)
        self.route = Route(self.ui, self.file_manager, self.edit_mode_utils, self.state)
        self.worker = None
        self.result = None

    def bind_events(self):

        self.ui.topbar.pred_btn.config(command=lambda: self.route.route("prediction"))
        self.ui.topbar.rev_btn.config(command=lambda: self.route.route("review"))
        self.ui.topbar.fine_btn.config(command=lambda: self.route.route("fineTune"))
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
        self.ui.sidebarright.get_valid_masks.config(
            command=lambda: self.file_manager.open_dir("PATH_VALID")
        )
        self.ui.sidebarright.make_config_file.config(
            command=self.make_config_fine_tuning
        )
        self.ui.sidebarright.start_fine_tuning.config(command=self.run_fine_tuning)
        self.ui.sidebarright.get_model_fine.config(
            command=lambda: self.file_manager.open_dir("PATH_LOG")
        )
        self.ui.sidebarright.tool_size_slider.config(command=self.on_change)

    def on_change(self, value):
        print("size is", int(float(value)))
        self.state.edit_tool_size = int(float(value))

    # load config for fine tuning :

    def make_config_fine_tuning(self):
        if (
            not self.state.path_dir
            or not self.state.path_out_valide
            or not self.state.path_log
        ):
            messagebox.showerror(
                "Error",
                "make sure you have all folders are uploaded : \n 1-Raw\n 2-Model\n 3-Valid masks",
            )
            return
        self.state.config_path = auto_config_preprocess(
            img_path=self.state.path_dir,
            msk_path=self.state.path_out_valide,
            num_classes=1,
            config_dir="configs",
            base_config=None,
            ct_norm=False,
            desc="unet",
            max_dim=128,
            num_epochs=1,
            is_2d=False,
        )
        if self.state.config_path:
            self.ui.sidebarright.start_fine_tuning.grid()
            self.ui.sidebarright.make_config_file.config(
                bg="white", fg="black", text="Remake Config"
            )

    def run_fine_tuning(self):
        # problem with windows a regler et a tester avec mac
        self.worker_fine = threading.Thread(
            target=self._worker, args=("fine",), daemon=True
        )
        self.worker_fine.start()
        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)
        self._check("fine")

    # sidebarleft handle

    def _worker(self, action):
        try:
            if not torch.cuda.is_available() and not torch.backends.mps.is_available():
                if action == "pred":
                    user_response = messagebox.askquestion(
                        title="Warning",
                        message="Warning: No GPU detected , prediciton will slowdown\ncontinue anyway?",
                        type="yesno",
                    )
                    if user_response == "yes":
                        self.result = pred(
                            log=self.state.path_log,
                            path_in=self.state.path_dir,
                            path_out=self.state.path_out,
                            skip_preprocessing=False,
                        )
                    else:
                        return
                elif action == "fine":
                    messagebox.showerror(
                        title="Error",
                        message="NO GPU detected , fine tuning dont work on ur desktop",
                    )

            else:
                if action == "pred":
                    self.result = pred(
                        log=self.state.path_log,
                        path_in=self.state.path_dir,
                        path_out=self.state.path_out,
                        skip_preprocessing=False,
                    )
                elif action == "fine":
                    self.state.new_model_path = train(
                        config=self.state.config_path,
                        path=self.state.path_log,
                    )

        except Exception as e:
            self.result = e

    def _check(self, action):
        if self.worker.is_alive() and action == "pred":
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
                    if len(files_out) >= 1 and not self.state.route == "review":
                        self.route.go_to_review(self.state.path_out)
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
            self.ui.root.after(1000, lambda: self._check(action))
            return

        if isinstance(self.result, Exception) and action == "pred":
            messagebox.showerror("Error", str(self.state.path_out))
            print(Exception)
            print("result", self.result)
        elif not isinstance(self.result, Exception) and action == "pred":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)
            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar, "RESET"
            )
            messagebox.showinfo("Done", f"prediction saved here: {self.result}")
            self.state.predStarted = False

    def get_out_path(self):
        out = filedialog.askdirectory(title="Destination for model predictions")
        if not out:
            return
        else:
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
            if user_response == "yes" and out:
                for item in ls:
                    if os.path.isfile(os.path.join(out, item)):
                        os.remove(os.path.join(out, item))
                    else:
                        shutil.rmtree(os.path.join(out, item))
                self.state.path_out = out
                self.ui.sidebarright.pred.grid()
                self.ui.sidebarright.get_folder_out.config(bg="white", fg="black")
            else:
                out = None
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
        self.worker = threading.Thread(target=self._worker, args=("pred",), daemon=True)
        self.worker.start()
        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)
        self._check("pred")

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
