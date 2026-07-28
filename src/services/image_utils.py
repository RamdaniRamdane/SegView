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
    "image": None,
    "tk_image": None,
    "item": None,
    "scale": None,
    "offset_x": None,
    "offset_y": None,
    "base_pil": None,
    "overlay_pil": None,
    "base_ref": None,
    "mask_ref": None,
    "alpha": 0.4,
}


def normalize_image(data):

    if data.dtype == np.uint8:
        return data

    data = data.astype(np.float32)

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
        Image.blend(
            DISPLAY_CACHE["base_pil"],
            DISPLAY_CACHE["overlay_pil"],
            alpha,
        )
    )


def display(canvas, data, pred=None, colors=None):

    if colors is None:
        colors = []

    if pred is not None:
        img = overlay(data, pred, colors)

    else:
        gray = normalize_image(data)

        img = np.stack([gray, gray, gray], axis=-1)

    h, w = img.shape[:2]

    canvas.update_idletasks()

    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()

    if c_w < 2 or c_h < 2:
        return

    scale = min(c_w / w, c_h / h)

    new_w = max(1, int(w * scale))

    new_h = max(1, int(h * scale))

    pil = Image.fromarray(img)

    pil = pil.resize((new_w, new_h), Image.NEAREST)

    tk_img = ImageTk.PhotoImage(pil)

    canvas.delete("all")

    item = canvas.create_image(c_w // 2, c_h // 2, image=tk_img)

    canvas.image = tk_img
    DISPLAY_CACHE["image"] = pil
    DISPLAY_CACHE["tk_image"] = tk_img
    DISPLAY_CACHE["item"] = item
    DISPLAY_CACHE["scale"] = scale
    DISPLAY_CACHE["offset_x"] = (c_w - new_w) // 2
    DISPLAY_CACHE["offset_y"] = (c_h - new_h) // 2

    return colors


def update_region(canvas, data, pred, x0, y0, x1, y1, colors):

    if DISPLAY_CACHE["image"] is None:
        return

    region_data = data[y0:y1, x0:x1]

    region_pred = pred[y0:y1, x0:x1]

    region = overlay(region_data, region_pred, colors)

    region_img = Image.fromarray(region)

    scale = DISPLAY_CACHE["scale"]

    region_img = region_img.resize(
        (
            max(1, int(region_img.width * scale)),
            max(1, int(region_img.height * scale)),
        ),
        Image.NEAREST,
    )

    px = int(x0 * scale)
    py = int(y0 * scale)

    DISPLAY_CACHE["image"].paste(region_img, (px, py))

    DISPLAY_CACHE["tk_image"] = ImageTk.PhotoImage(DISPLAY_CACHE["image"])

    canvas.itemconfig(DISPLAY_CACHE["item"], image=DISPLAY_CACHE["tk_image"])

    canvas.image = DISPLAY_CACHE["tk_image"]


def load_icon(img_dir, name, size=None):

    import os

    path = os.path.join(img_dir, name)

    img = Image.open(path)

    if size:
        img = img.resize(size, Image.LANCZOS)

    return ImageTk.PhotoImage(img)


# user in change opacity
def set_overlay_alpha(canvas, alpha):

    DISPLAY_CACHE["alpha"] = alpha

    if DISPLAY_CACHE["base_pil"] is None:
        return

    img = Image.blend(
        DISPLAY_CACHE["base_pil"],
        DISPLAY_CACHE["overlay_pil"],
        alpha,
    )

    scale = DISPLAY_CACHE["scale"]

    w = max(1, int(img.width * scale))
    h = max(1, int(img.height * scale))

    img = img.resize((w, h), Image.NEAREST)

    DISPLAY_CACHE["image"] = img
    DISPLAY_CACHE["tk_image"] = ImageTk.PhotoImage(img)

    canvas.itemconfig(
        DISPLAY_CACHE["item"],
        image=DISPLAY_CACHE["tk_image"],
    )

    canvas.image = DISPLAY_CACHE["tk_image"]
