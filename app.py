import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

from src.models.app_state import AppState
from src.services.b3d import B3d
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
        self.b3d = B3d(self.state, self.ui, self.route)
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
        self.ui.sidebarright.pred.config(command=self.b3d.run_prediction)
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
            command=self.b3d.make_config_fine_tuning
        )
        self.ui.sidebarright.start_fine_tuning.config(command=self.b3d.run_fine_tuning)
        self.ui.sidebarright.get_model_fine.config(
            command=lambda: self.file_manager.open_dir("PATH_LOG")
        )
        self.ui.sidebarright.tool_size_slider.config(command=self.on_change)

    def on_change(self, value):
        print("size is", int(float(value)))
        self.state.edit_tool_size = int(float(value))

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
