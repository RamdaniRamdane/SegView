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
        for i in range(4):
            self.frame.grid_columnconfigure(i, weight=0)
        self.frame.grid_columnconfigure(2, weight=4)

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
        self.show_info = tk.Label(
            self.frame,
            text="Raw = -- D, Mask = -- D, Classes = -- ",
            font=(theme.MONO, 8),
            bg=theme.BG,
            fg=theme.TEXT_HI,
        )

        self.pred_btn.grid(row=0, column=0, sticky="e")
        self.rev_btn.grid(row=0, column=1, sticky="e")
        self.show_info.grid(row=0, column=3, sticky="e", padx=10)

        # self.frame.grid_propagate(False)
