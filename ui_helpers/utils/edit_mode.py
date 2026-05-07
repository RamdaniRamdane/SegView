import numpy as np


class Edit_mode:
    def __init__(self, app):
        self.app = app

    def toggle_edit_mode(self):
        self.app.edit_mode = not self.app.edit_mode
        if self.app.edit_mode:
            self.app.ui.edit_frame.grid()
        else:
            self.app.ui.edit_frame.grid_remove()

    def toggle_brush_mode(self):
        self.app.brush_active = not self.app.brush_active
        print("brush:", self.app.brush_active)

    def on_mouse_down(self, event):
        self.apply_brush(event.x, event.y)
        print(event.x, event.y)

    def on_mouse_drag(self, event):
        self.apply_brush(event.x, event.y)

    def apply_brush(self, x, y):
        if not self.app.brush_active:
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
        self.app.prediction[z][mask] = 1
        self.app.update_display()
