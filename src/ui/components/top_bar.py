import os
import tkinter as tk

import src.services.image_utils as image_utils
import src.ui.theme as theme

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "..", "..", "..", "images")


class TopBar:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(
            self.root, bg=theme.BG, height=30, width=self.root.winfo_screenmmwidth()
        )
        self.frame.grid_rowconfigure(0, weight=0)
        for i in range(3):
            self.frame.grid_columnconfigure(i, weight=0)

        self.predict_icon = image_utils.load_icon(IMG_DIR, "predict.png", (10, 10))
        self.pred_btn = tk.Button(
            self.frame,
            text="Predict Mask",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.predict_icon,
            compound="left",
        )

        self.review_icon = image_utils.load_icon(IMG_DIR, "review.png", (10, 10))
        self.rev_btn = tk.Button(
            self.frame,
            text="Review Predictions",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.review_icon,
            compound="left",
        )
        self.fine_icon = image_utils.load_icon(IMG_DIR, "fine.png", (10, 10))
        self.fine_btn = tk.Button(
            self.frame,
            text="Fine Tuning",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.fine_icon,
            compound="left",
        )
        self.pred_btn.grid(row=0, column=0)
        self.rev_btn.grid(row=0, column=1)
        self.fine_btn.grid(row=0, column=2)

        self.frame.grid_propagate(False)
