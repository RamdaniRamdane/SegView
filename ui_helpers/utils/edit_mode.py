import numpy as np


class Edit_mode:
    def __init__(self, app):
        self.app = app
        self.pred_correction = None

    def toggle_edit_mode(self):
        self.app.edit_mode = not self.app.edit_mode
        if self.app.edit_mode:
            self.app.ui.edit_frame.grid()
            self.app.ui.ereaser.grid()
            self.app.ui.brush.grid()
        else:
            self.app.ui.edit_frame.grid_remove()

    def toggle_tool(self, tool):
        if not self.app.edit_tool == tool:
            self.app.edit_tool = tool
            self.change_bg_tool(tool)
        else:
            self.app.edit_tool = 0
            self.change_bg_tool(tool)

    def change_bg_tool(self, tool):
        match tool:
            case "Ereaser":
                self.app.ui.ereaser.config(
                    bg="white",
                    fg="black",
                    activebackground="white",
                    activeforeground="black",
                )
                self.app.ui.brush.config(bg="#141416", fg="#3a3a40")
            case "Brush":
                self.app.ui.brush.config(
                    bg="white",
                    fg="black",
                    activebackground="white",
                    activeforeground="black",
                )
                self.app.ui.ereaser.config(bg="#141416", fg="#3a3a40")
            case _:
                self.app.ui.brush.config(bg="#141416", fg="#3a3a40")
                self.app.ui.ereaser.config(bg="#141416", fg="#3a3a40")

    def on_mouse_down(self, event):
        self.apply_tool(event.x, event.y, self.app.edit_tool)
        print(event.x, event.y)

    def on_mouse_drag(self, event):
        self.apply_tool(event.x, event.y, self.app.edit_tool)

    def apply_tool(self, x, y, tool):
        if not self.app.edit_tool:
            return

        if self.app.data is None:
            return

        if self.app.prediction is None:
            self.app.prediction = np.zeros_like(self.app.data, dtype=np.uint8)

        h, w = self.app.data.shape[-2:]

        # taille canvas
        c_w = self.app.ui.canvas.winfo_width()
        c_h = self.app.ui.canvas.winfo_height()

        # taille affichée image
        scale = min(c_w / w, c_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        offset_x = (c_w - new_w) // 2
        offset_y = (c_h - new_h) // 2
        # conversion coords
        ix = int((x - offset_x) / scale)
        iy = int((y - offset_y) / scale)
        if ix < 0 or iy < 0 or ix >= w or iy >= h:
            return
        r = 2
        yy, xx = np.ogrid[:h, :w]
        mask = (yy - iy) ** 2 + (xx - ix) ** 2 <= r * r
        z = self.app.zoom
        if tool == "Ereaser":
            bit = 0
        elif tool == "Brush":
            bit = 1
        else:
            return
        self.app.prediction[z][mask] = bit
        self.pred_correction = self.app.prediction

        self.app.update_display()

    # a continuer

    def save_changes(self):
        if not np.array_equal():
            print(self.app.prediciton_path_file)
