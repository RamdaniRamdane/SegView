import numpy as np
import tifffile

from src.services.image_utils import canvas_to_image, update_region


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
            self.app.ui.sidebarright.color.config(bg="red")
            self.state.brush_bit = 1
        else:
            self.toggle_tool("deactivate")
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
            self.app.ui.sidebarright.color.grid()
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

            self.app.ui.sidebarright.color.grid_remove()
        else:
            self.app.ui.sidebarright.brush.config(
                bg="#3a3a40",
            )
            self.app.ui.sidebarright.ereaser.config(
                bg="#3a3a40",
            )

            self.app.ui.sidebarright.color.grid_remove()

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

        # Image courante
        if self.app.state.data.ndim == 2:
            img_h, img_w = self.app.state.data.shape

        else:
            img_h, img_w = self.app.state.data.shape[-2:]

        # Conversion canvas -> image

        ix, iy = canvas_to_image(
            self.app.ui.canvas,
            x,
            y,
        )

        if ix is None:
            return

        r = self.state.edit_tool_size

        x0 = max(0, ix - r)

        x1 = min(img_w, ix + r + 1)

        y0 = max(0, iy - r)

        y1 = min(img_h, iy + r + 1)

        yy, xx = np.ogrid[y0:y1, x0:x1]

        mask = ((yy - iy) ** 2 + (xx - ix) ** 2) <= r * r

        value = self.state.brush_bit if tool == "Brush" else 0

        if self.app.state.prediction.ndim == 2:
            region = self.app.state.prediction[y0:y1, x0:x1]

            region[mask] = value

            update_region(
                self.app.ui.canvas,
                self.app.state.data,
                self.app.state.prediction,
                x0,
                y0,
                x1,
                y1,
                self.app.state.colors,
            )

        else:
            z = self.app.state.zoom

            region = self.app.state.prediction[z, y0:y1, x0:x1]

            region[mask] = value

            update_region(
                self.app.ui.canvas,
                self.app.state.data[z],
                self.app.state.prediction[z],
                x0,
                y0,
                x1,
                y1,
                self.app.state.colors,
            )

        self.app.state.edited += 1

        if self.app.state.edited > 0:
            self.app.ui.sidebarright.changes_state_label.grid_remove()

            self.app.ui.sidebarright.save_changes.grid()

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
