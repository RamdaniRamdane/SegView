import numpy as np
import tifffile


class EditMode:
    def __init__(self, app, state):
        self.app = app
        self.state = state

    def toggle_edit_mode(self):
        self.app.state.edit_mode = not self.app.state.edit_mode
        if self.app.state.edit_mode:
            self.app.ui.sidebarright.edit_frame.grid()
            self.app.ui.sidebarright.ereaser.grid()
            self.app.ui.sidebarright.brush.grid()
        else:
            self.app.ui.sidebarright.edit_frame.grid_remove()

    def toggle_tool(self, tool):
        if tool == "deactivate":
            self.app.state.edit_tool = ""
        else:
            if self.app.state.edit_tool != tool:
                self.app.state.edit_tool = tool
            else:
                self.app.state.edit_tool = ""
        self.change_bg_tool()

    def change_bg_tool(self):
        tool = self.app.state.edit_tool
        if tool == "Brush":
            self.app.ui.sidebarright.brush.config(
                bg="white",
                fg="black",
                activebackground="white",
                activeforeground="black",
            )
            self.app.ui.sidebarright.ereaser.config(
                bg="#3a3a40",
            )
        elif tool == "Ereaser":
            self.app.ui.sidebarright.ereaser.config(
                bg="white",
                fg="black",
                activebackground="white",
                activeforeground="black",
            )
            self.app.ui.sidebarright.brush.config(
                bg="#3a3a40",
            )
        else:
            self.app.ui.sidebarright.brush.config(
                bg="#3a3a40",
            )
            self.app.ui.sidebarright.ereaser.config(
                bg="#3a3a40",
            )

    def on_mouse_down(self, event):
        self.apply_tool(
            event.x,
            event.y,
            self.app.state.edit_tool,
        )

    def on_mouse_drag(self, event):
        self.apply_tool(
            event.x,
            event.y,
            self.app.state.edit_tool,
        )

    def apply_tool(self, x, y, tool):
        if not tool:
            return
        if self.app.state.data is None:
            return
        if self.app.state.prediction is None:
            self.app.state.prediction = np.zeros_like(
                self.app.state.data,
                dtype=np.uint8,
            )
        h, w = self.app.state.data.shape[-2:]
        c_w = self.app.ui.canvas.winfo_width()
        c_h = self.app.ui.canvas.winfo_height()
        scale = min(c_w / w, c_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        offset_x = (c_w - new_w) // 2
        offset_y = (c_h - new_h) // 2
        ix = int((x - offset_x) / scale)
        iy = int((y - offset_y) / scale)
        if ix < 0 or iy < 0 or ix >= w or iy >= h:
            return
        r = self.state.edit_tool_size
        yy, xx = np.ogrid[:h, :w]
        mask = ((yy - iy) ** 2 + (xx - ix) ** 2) <= r * r
        bit = 1 if tool == "Brush" else 0
        if self.app.state.prediction.ndim == 2:
            self.app.state.prediction[mask] = bit
        else:
            z = self.app.state.zoom
            self.app.state.prediction[z][mask] = bit
        self.app.state.edited += 1

        if self.app.state.edited > 0:
            self.app.ui.sidebarright.changes_state_label.grid_remove()
            self.app.ui.sidebarright.save_changes.grid()
        self.app.ui_handel.update_display()

    def save_changes(self):
        if self.app.state.edited <= 0:
            return
        if not self.app.state.prediction_path_file:
            return
        tifffile.imwrite(
            self.app.state.prediction_path_file,
            self.app.state.prediction.astype(np.uint8),
        )
        self.app.state.edited = 0
        self.app.ui.sidebarright.save_changes.grid_remove()
        self.app.ui.sidebarright.changes_state_label.grid()

    def on_change_tool_size(self, value):
        self.state.edit_tool_size = int(float(value))
