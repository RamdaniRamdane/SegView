import random

import numpy as np
from PIL import Image, ImageTk

BASE_COLORS = [
    (255, 0, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (255, 165, 0),
    (128, 0, 128),
]


DISPLAY_CACHE = {
    "data": None,
    "mask": None,
    "base_ref": None,
    "mask_ref": None,
    "base_pil": None,
    "overlay_pil": None,
    "tk_image": None,
    "item": None,
    "canvas": None,
    "fit_scale": None,
    "scale": None,
    "zoom_factor": 1.0,
    "offset_x": 0,
    "offset_y": 0,
    "pan_x": 0,
    "pan_y": 0,
    "image_width": 0,
    "image_height": 0,
    "alpha": 0.4,
    "colors": [],
}


def canvas_to_image(canvas, x, y):

    if DISPLAY_CACHE["scale"] is None:
        return None, None

    scale = DISPLAY_CACHE["scale"]

    canvas.update_idletasks()

    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()

    img_w = DISPLAY_CACHE["image_width"]
    img_h = DISPLAY_CACHE["image_height"]

    # Position du coin haut gauche de l'image affichée
    left = c_w / 2 - (img_w * scale) / 2 + DISPLAY_CACHE["pan_x"]

    top = c_h / 2 - (img_h * scale) / 2 + DISPLAY_CACHE["pan_y"]

    ix = int((x - left) / scale)
    iy = int((y - top) / scale)

    if ix < 0 or iy < 0 or ix >= img_w or iy >= img_h:
        return None, None

    return ix, iy


def normalize_image(data):

    if data.dtype == np.uint8:
        return data

    data = data.astype(np.float32, copy=False)

    d_min = data.min()
    d_max = data.max()

    if d_max - d_min == 0:
        return np.zeros(data.shape, dtype=np.uint8)

    data = (data - d_min) / (d_max - d_min)

    return (data * 255).astype(np.uint8)


def color_distance(c1, c2):

    return np.linalg.norm(np.array(c1) - np.array(c2))


def generate_colors(n, min_distance=120):

    colors = BASE_COLORS.copy()

    while len(colors) < n:
        candidate = (
            random.randint(30, 255),
            random.randint(30, 255),
            random.randint(30, 255),
        )

        valid = True

        for existing in colors:
            if color_distance(candidate, existing) < min_distance:
                valid = False
                break

        if valid:
            colors.append(candidate)

    return colors[:n]


def overlay(base, mask, colors_st, alpha=None):

    if alpha is None:
        alpha = DISPLAY_CACHE["alpha"]
    else:
        DISPLAY_CACHE["alpha"] = alpha

    rebuild = (
        DISPLAY_CACHE["base_pil"] is None
        or DISPLAY_CACHE["overlay_pil"] is None
        or DISPLAY_CACHE["base_ref"] is not base
        or DISPLAY_CACHE["mask_ref"] is not mask
    )

    if rebuild:
        gray = normalize_image(base)

        base_rgb = np.stack([gray, gray, gray], axis=-1)

        overlay_rgb = np.zeros_like(base_rgb)

        max_class = int(mask.max())

        if max_class > 0:
            if len(colors_st) < max_class:
                colors_st.clear()

                colors_st.extend(generate_colors(max_class))

            for cls in range(1, max_class + 1):
                overlay_rgb[mask == cls] = colors_st[cls - 1]

        DISPLAY_CACHE["base_pil"] = Image.fromarray(base_rgb)

        DISPLAY_CACHE["overlay_pil"] = Image.fromarray(overlay_rgb)

        DISPLAY_CACHE["base_ref"] = base
        DISPLAY_CACHE["mask_ref"] = mask

    return np.asarray(
        Image.blend(DISPLAY_CACHE["base_pil"], DISPLAY_CACHE["overlay_pil"], alpha)
    )


def _get_current_image():

    base = DISPLAY_CACHE["base_pil"]

    if base is None:
        return None

    overlay_pil = DISPLAY_CACHE["overlay_pil"]

    if overlay_pil is None:
        return base

    return Image.blend(base, overlay_pil, DISPLAY_CACHE["alpha"])


def _render_viewport(canvas):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    canvas.update_idletasks()

    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()

    if canvas_w < 2 or canvas_h < 2:
        return

    image_w = DISPLAY_CACHE["image_width"]

    image_h = DISPLAY_CACHE["image_height"]

    scale = DISPLAY_CACHE["scale"]

    display_w = image_w * scale
    display_h = image_h * scale

    center_x = canvas_w / 2 + DISPLAY_CACHE["pan_x"]

    center_y = canvas_h / 2 + DISPLAY_CACHE["pan_y"]

    left = center_x - (display_w / 2)

    top = center_y - (display_h / 2)

    right = left + display_w
    bottom = top + display_h

    source_x0 = max(0, int(max(0, -left) / scale))

    source_y0 = max(0, int(max(0, -top) / scale))

    source_x1 = min(image_w, int(min(canvas_w - left, display_w) / scale) + 1)

    source_y1 = min(image_h, int(min(canvas_h - top, display_h) / scale) + 1)

    if source_x1 <= source_x0:
        return

    if source_y1 <= source_y0:
        return

    current_image = _get_current_image()

    if current_image is None:
        return

    crop = current_image.crop(
        (
            source_x0,
            source_y0,
            source_x1,
            source_y1,
        )
    )

    new_w = max(1, int(crop.width * scale))

    new_h = max(1, int(crop.height * scale))

    crop = crop.resize((new_w, new_h), Image.NEAREST)

    tk_img = ImageTk.PhotoImage(crop)

    crop_left = left + source_x0 * scale

    crop_top = top + source_y0 * scale

    crop_center_x = crop_left + new_w / 2

    crop_center_y = crop_top + new_h / 2

    if DISPLAY_CACHE["item"] is None:
        DISPLAY_CACHE["item"] = canvas.create_image(
            crop_center_x, crop_center_y, image=tk_img
        )

    else:
        canvas.coords(DISPLAY_CACHE["item"], crop_center_x, crop_center_y)

        canvas.itemconfig(DISPLAY_CACHE["item"], image=tk_img)

    DISPLAY_CACHE["tk_image"] = tk_img

    DISPLAY_CACHE["offset_x"] = int(left)
    DISPLAY_CACHE["offset_y"] = int(top)

    canvas.image = tk_img


def display(canvas, data, pred=None, colors=None):

    if colors is None:
        colors = []

    DISPLAY_CACHE["canvas"] = canvas

    if pred is None:
        gray = normalize_image(data)

        base_rgb = np.stack([gray, gray, gray], axis=-1)

        DISPLAY_CACHE["base_pil"] = Image.fromarray(base_rgb)

        DISPLAY_CACHE["overlay_pil"] = None

        DISPLAY_CACHE["base_ref"] = data
        DISPLAY_CACHE["mask_ref"] = None

    else:
        overlay(data, pred, colors)

    DISPLAY_CACHE["data"] = data
    DISPLAY_CACHE["mask"] = pred
    DISPLAY_CACHE["colors"] = colors

    DISPLAY_CACHE["image_height"] = data.shape[0]

    DISPLAY_CACHE["image_width"] = data.shape[1]

    canvas.update_idletasks()

    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()

    if c_w < 2 or c_h < 2:
        return colors

    scale = min(c_w / DISPLAY_CACHE["image_width"], c_h / DISPLAY_CACHE["image_height"])

    DISPLAY_CACHE["fit_scale"] = scale
    DISPLAY_CACHE["scale"] = scale
    DISPLAY_CACHE["zoom_factor"] = 1.0

    DISPLAY_CACHE["pan_x"] = 0
    DISPLAY_CACHE["pan_y"] = 0

    canvas.delete("all")

    DISPLAY_CACHE["item"] = None

    _render_viewport(canvas)

    return colors


def zoom_in(canvas, factor=1.25):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    old_scale = DISPLAY_CACHE["scale"]

    new_zoom = DISPLAY_CACHE["zoom_factor"] * factor

    new_zoom = min(new_zoom, 20.0)

    DISPLAY_CACHE["zoom_factor"] = new_zoom

    DISPLAY_CACHE["scale"] = DISPLAY_CACHE["fit_scale"] * new_zoom

    _keep_center(canvas, old_scale)

    _render_viewport(canvas)


def zoom_out(canvas, factor=1.25):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    old_scale = DISPLAY_CACHE["scale"]

    new_zoom = DISPLAY_CACHE["zoom_factor"] / factor

    new_zoom = max(new_zoom, 0.2)

    DISPLAY_CACHE["zoom_factor"] = new_zoom

    DISPLAY_CACHE["scale"] = DISPLAY_CACHE["fit_scale"] * new_zoom

    _keep_center(canvas, old_scale)

    _render_viewport(canvas)


def _keep_center(canvas, old_scale):

    if old_scale is None:
        return

    canvas.update_idletasks()

    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()

    if canvas_w < 2 or canvas_h < 2:
        return

    center_x = canvas_w / 2 + DISPLAY_CACHE["pan_x"]

    center_y = canvas_h / 2 + DISPLAY_CACHE["pan_y"]

    DISPLAY_CACHE["pan_x"] = center_x - canvas_w / 2

    DISPLAY_CACHE["pan_y"] = center_y - canvas_h / 2

    _clamp_pan(canvas)


def go_right(canvas, amount=80):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    DISPLAY_CACHE["pan_x"] -= amount

    _clamp_pan(canvas)

    _render_viewport(canvas)


def go_left(canvas, amount=80):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    DISPLAY_CACHE["pan_x"] += amount

    _clamp_pan(canvas)

    _render_viewport(canvas)


def go_down(canvas, amount=80):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    DISPLAY_CACHE["pan_y"] -= amount

    _clamp_pan(canvas)

    _render_viewport(canvas)


def go_up(canvas, amount=80):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    DISPLAY_CACHE["pan_y"] += amount

    _clamp_pan(canvas)

    _render_viewport(canvas)


def _clamp_pan(canvas):

    canvas.update_idletasks()

    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()

    image_w = DISPLAY_CACHE["image_width"] * DISPLAY_CACHE["scale"]

    image_h = DISPLAY_CACHE["image_height"] * DISPLAY_CACHE["scale"]

    if image_w <= c_w:
        DISPLAY_CACHE["pan_x"] = 0

    else:
        max_pan_x = (image_w - c_w) / 2

        DISPLAY_CACHE["pan_x"] = max(-max_pan_x, min(DISPLAY_CACHE["pan_x"], max_pan_x))

    if image_h <= c_h:
        DISPLAY_CACHE["pan_y"] = 0

    else:
        max_pan_y = (image_h - c_h) / 2

        DISPLAY_CACHE["pan_y"] = max(-max_pan_y, min(DISPLAY_CACHE["pan_y"], max_pan_y))


def update_region(canvas, data, pred, x0, y0, x1, y1, colors):

    if DISPLAY_CACHE["base_pil"] is None:
        return

    gray = normalize_image(data)

    base_rgb = np.stack([gray, gray, gray], axis=-1)

    DISPLAY_CACHE["base_pil"] = Image.fromarray(base_rgb)

    if pred is not None:
        max_class = int(pred.max())

        overlay_rgb = np.zeros_like(base_rgb)

        if max_class > 0:
            if len(colors) < max_class:
                colors.clear()

                colors.extend(generate_colors(max_class))

            for cls in range(1, max_class + 1):
                overlay_rgb[pred == cls] = colors[cls - 1]

        DISPLAY_CACHE["overlay_pil"] = Image.fromarray(overlay_rgb)

    else:
        DISPLAY_CACHE["overlay_pil"] = None

    DISPLAY_CACHE["data"] = data
    DISPLAY_CACHE["mask"] = pred
    DISPLAY_CACHE["base_ref"] = data
    DISPLAY_CACHE["mask_ref"] = pred
    DISPLAY_CACHE["colors"] = colors

    _render_viewport(canvas)


def set_overlay_alpha(canvas, alpha):

    DISPLAY_CACHE["alpha"] = alpha

    if DISPLAY_CACHE["base_pil"] is None:
        return

    _render_viewport(canvas)


def load_icon(img_dir, name, size=None):

    import os

    path = os.path.join(img_dir, name)

    img = Image.open(path)

    if size:
        img = img.resize(size, Image.LANCZOS)

    return ImageTk.PhotoImage(img)


def start_pan(event):

    event.widget._pan_x = event.x
    event.widget._pan_y = event.y


def pan_move(event):

    canvas = event.widget

    old_x = getattr(canvas, "_pan_x", event.x)

    old_y = getattr(canvas, "_pan_y", event.y)

    dx = event.x - old_x
    dy = event.y - old_y

    DISPLAY_CACHE["pan_x"] += dx
    DISPLAY_CACHE["pan_y"] += dy

    _clamp_pan(canvas)

    canvas._pan_x = event.x
    canvas._pan_y = event.y

    _render_viewport(canvas)


def stop_pan(event):

    event.widget._pan_x = None
    event.widget._pan_y = None
