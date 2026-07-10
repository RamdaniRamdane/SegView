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


def overlay(base, mask, colors_st, alpha=0.4):

    base = normalize_image(base)

    result = np.stack([base, base, base], axis=-1).astype(np.float32)

    classes = np.unique(mask)

    classes = classes[classes != 0]

    if len(colors_st) < len(classes):
        colors_st.clear()

        colors_st.extend(generate_colors(len(classes)))

    for i, cls in enumerate(classes):
        class_mask = mask == cls

        color = np.array(colors_st[i], dtype=np.float32)

        result[class_mask] = (1 - alpha) * result[class_mask] + alpha * color

    return result.astype(np.uint8)


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

    # taille affichage
    region_img = region_img.resize(
        (max(1, int(region_img.width * scale)), max(1, int(region_img.height * scale))),
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
