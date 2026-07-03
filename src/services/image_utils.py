import random

import numpy as np
from PIL import Image, ImageTk

BASE_COLORS = [
    (255, 0, 0),  # rouge
    (0, 0, 255),  # bleu
    (255, 255, 0),  # jaune
    (255, 0, 255),  # magenta
    (255, 165, 0),  # orange
    (128, 0, 128),  # violet
]


def normalize_image(data):
    data = data.astype(np.float32)
    d_min = data.min()
    d_max = data.max()
    if d_max - d_min == 0:
        return np.zeros_like(data, dtype=np.uint8)

    data = (data - d_min) / (d_max - d_min)
    return (data * 255).astype(np.uint8)


def color_distance(c1, c2):
    c1 = np.array(c1)
    c2 = np.array(c2)
    return np.linalg.norm(c1 - c2)


def generate_colors(n, min_distance=120):
    colors = BASE_COLORS.copy()

    while len(colors) < n:
        candidate = (
            random.randint(30, 255),
            random.randint(30, 255),
            random.randint(30, 255),
        )

        if sum(candidate) < 100:
            continue

        valid = True
        for existing in colors:
            if color_distance(candidate, existing) < min_distance:
                valid = False
                break

        if valid:
            colors.append(candidate)

    return colors


def overlay(base, mask, colors_st, alpha=0.4):
    base = normalize_image(base)
    base_rgb = np.stack([base] * 3, axis=-1)

    if mask.shape != base.shape:
        mask_img = Image.fromarray(mask.astype(np.uint8))
        mask_img = mask_img.resize(
            (base.shape[1], base.shape[0]),
            resample=Image.NEAREST,
        )
        mask = np.array(mask_img)

    classes = [c for c in np.unique(mask) if c != 0]
    colors = generate_colors(len(classes))
    colors_st.clear()
    colors_st.extend(colors)
    result = base_rgb.astype(np.float32).copy()

    color_map = dict(zip(classes, colors))

    for cls, color in color_map.items():
        class_mask = mask == cls
        color = np.array(color, dtype=np.float32)

        result[class_mask] = (1 - alpha) * result[class_mask] + alpha * color

    return result.astype(np.uint8)


def display(canvas, data, pred=None):
    colors = []
    print("couleurs avant", colors)
    if pred is not None:
        img = overlay(base=data, mask=pred, colors_st=colors)

        print("couleurs apres", colors)
    else:
        gray = normalize_image(data)
        img = np.stack([gray] * 3, axis=-1)
    h, w = img.shape[:2]
    canvas.update_idletasks()
    c_w = canvas.winfo_width()
    c_h = canvas.winfo_height()
    if c_w < 2 or c_h < 2:
        return
    scale = min(c_w / w, c_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    img = Image.fromarray(img)
    img = img.resize(
        (new_w, new_h),
        Image.NEAREST,
    )
    tk_img = ImageTk.PhotoImage(img)
    canvas.delete("all")
    canvas.create_image(
        c_w // 2,
        c_h // 2,
        image=tk_img,
    )
    canvas.image = tk_img
    return colors


def load_icon(img_dir, name, size=None):
    import os

    path = os.path.join(img_dir, name)
    img = Image.open(path)
    if size:
        img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)
