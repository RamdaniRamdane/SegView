import tkinter as tk

from src.models.app_state import AppState
from src.services.b3d import B3d
from src.services.file_manager import FileManager
from src.services.omero import OmeroHandler
from src.services.route import Route
from src.ui.helpers.edit_mode import EditMode
from src.ui.helpers.ui_utils import UIutils


class SegViewApp:
    def __init__(self, ui):
        self.ui = ui
        self.state = AppState()
        self.ui.set_state(self.state)
        self.edit_mode_utils = EditMode(self, self.state)
        self.file_manager = FileManager(ui, self.state, self, self.edit_mode_utils)
        self.ui_handel = UIutils(
            self.ui, self.state, self.file_manager, self, self.edit_mode_utils
        )
        self.route = Route(self.ui, self.file_manager, self.edit_mode_utils, self.state)
        self.b3d = B3d(self.state, self.ui, self.route)
        self.worker = None
        self.omero_handler = OmeroHandler(self.ui, self.state)

    def bind_events(self):
        # top bar binds
        # ============================================================================
        self.ui.topbar.pred_btn.config(command=lambda: self.route.route("prediction"))
        #        self.ui.topbar.rev_btn.config(command=lambda: self.route.route("review"))
        self.ui.sidebarright.fine_btn.config(command=lambda: self.b3d.run_fine_tuning())
        self.ui.topbar.local.config(command=lambda: self.omero_handler.toggle("LOCAL"))
        self.ui.topbar.omero.config(command=lambda: self.omero_handler.toggle("OMERO"))
        # sidebarright binds
        # =============================================================================
        self.ui.sidebarright.btn.config(
            command=lambda: self.file_manager.open_dir("PATH_RAW")
        )
        # review
        self.ui.sidebarright.refuse_but.config(
            command=lambda: self.file_manager.save("refuse"),
        )
        self.ui.sidebarright.validate_but.config(
            command=lambda: self.file_manager.save("validate"),
        )
        self.ui.sidebarright.unreview_but.config(
            command=lambda: self.file_manager.save("unreview"),
        )
        self.ui.sidebarright.next_btn.config(
            state=tk.DISABLED,
            command=lambda: self.ui_handel.navigate("NEXT"),
        )
        self.ui.sidebarright.prev_btn.config(
            state=tk.DISABLED,
            command=lambda: self.ui_handel.navigate("PREV"),
        )
        # edit mode

        self.ui.sidebarright.correct_but.config(
            command=self.edit_mode_utils.toggle_edit_mode
        )
        self.ui.sidebarright.brush.config(
            command=lambda: self.edit_mode_utils.toggle_tool("Brush")
        )
        self.ui.sidebarright.color.config(command=self.ui_handel.show_palette)
        self.ui.sidebarright.ereaser.config(
            command=lambda: self.edit_mode_utils.toggle_tool("Ereaser")
        )
        self.ui.sidebarright.save_changes.config(
            command=self.edit_mode_utils.save_changes
        )
        self.ui.sidebarright.tool_size_slider.config(
            command=self.edit_mode_utils.on_change_tool_size
        )
        # pred

        self.ui.sidebarright.get_model.config(
            state=tk.DISABLED,
            command=lambda: self.file_manager.open_dir("PATH_LOG"),
        )
        self.ui.sidebarright.get_folder_out.config(
            command=self.file_manager.get_out_path
        )
        self.ui.sidebarright.pred.config(command=self.b3d.run_prediction)

        #        self.ui.sidebarright.get_segview_folder.config(
        #            command=lambda: self.file_manager.open_dir("PATH_SEG")
        #        )
        # fine tuning
        # self.ui.sidebarright.get_valid_masks.config(
        #    command=lambda: self.file_manager.open_dir("PATH_VALID")
        # )
        # self.ui.sidebarright.make_config_file.config(
        #    command=self.b3d.make_config_fine_tuning
        # )
        self.ui.sidebarright.start_fine_tuning.config(command=self.b3d.run_fine_tuning)
        self.ui.sidebarright.get_model_fine.config(
            command=lambda: self.file_manager.open_dir("PATH_LOG")
        )

        # canvas handel
        # ==============================================================================
        self.ui.zoom_slider.config(
            state=tk.DISABLED,
            command=self.ui_handel.change_z,
        )

        self.ui.canvas.bind(
            "<ButtonPress-1>",
            self.edit_mode_utils.on_mouse_down,
        )
        self.ui.canvas.bind(
            "<B1-Motion>",
            self.edit_mode_utils.on_mouse_drag,
        )
        self.ui.canvas.bind("<Configure>", self.ui_handel.on_canvas_resize)
