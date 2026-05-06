import numpy as np
from PIL import Image, ImageTk


def normalize_image(data):
    data = data.astype(float)
    data = (data - data.min()) / (data.max() - data.min() + 1e-8)
    return (data * 255).astype(np.uint8)  # pour avoir une uint8 [0-255]


def overlay(base, mask, alpha=0.4):
    base = normalize_image(base)
    base_rgb = np.stack([base] * 3, axis=-1)

    if mask.shape != base.shape:
        mask_img = Image.fromarray(mask.astype(np.uint8))
        mask_img = mask_img.resize(
            (base.shape[1], base.shape[0]), resample=Image.NEAREST
        )
        mask = np.array(mask_img)

    mask = (mask > 0).astype(np.uint8) * 255
    red_layer = np.zeros_like(base_rgb)
    red_layer[..., 0] = mask

    result = (1 - alpha) * base_rgb + alpha * red_layer
    return result.astype(np.uint8)


def display(can, data, pred=None):
    if pred is not None:
        img = overlay(data, pred)
    else:
        gray = normalize_image(data)
        img = np.stack([gray] * 3, axis=-1)

    h, w = img.shape[:2]
    can.update_idletasks()
    c_w = can.winfo_width()
    c_h = can.winfo_height()
    if c_w < 2 or c_h < 2:
        return

    scale = min(c_w / w, c_h / h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    img = Image.fromarray(img).resize((new_w, new_h), Image.NEAREST)
    tk_img = ImageTk.PhotoImage(img)

    can.delete("all")
    can.create_image(c_w // 2, c_h // 2, image=tk_img)
    can.image = tk_img
