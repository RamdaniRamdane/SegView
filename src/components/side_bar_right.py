import os
import tkinter as tk

import src.image_utils as image_utils
import theme
from src.ui_utils import UIutils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "..", "..", "images")


class Sidebarright:
    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.Frame(root, bg=theme.PANEL, width=200)
        self.frame.grid_propagate(False)
        # grid rows reserved to replicate original layout
        for i in range(11):
            self.frame.grid_rowconfigure(i, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)

        # INPUT label + Import button
        UIutils.sidebar_label(self.frame, "INPUT", 0)
        self.import_icon = image_utils.load_icon(IMG_DIR, "import.png", (24, 24))
        self.btn = UIutils.make_btn(
            self.frame,
            "Import Folder RAW",
            1,
            color=theme.MUTED,
            text_color=theme.TEXT_HI,
            pady_top=4,
            image=self.import_icon,
        )
        self.btn.image = self.import_icon

        # use_cases area (Predict / Review / Fine)
        self.use_cases = tk.Frame(self.frame, bg=theme.PANEL, width=200, height=100)
        self.predict_icon = image_utils.load_icon(IMG_DIR, "predict.png", (24, 24))
        self.pred_btn = tk.Button(
            self.use_cases,
            text="Predict Mask",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.predict_icon,
            compound="left",
        )
        self.review_icon = image_utils.load_icon(IMG_DIR, "review.png", (24, 24))
        self.rev_btn = tk.Button(
            self.use_cases,
            text="Review Predictions",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.review_icon,
            compound="left",
        )
        self.fine_icon = image_utils.load_icon(IMG_DIR, "fine.png", (24, 24))
        self.fine_btn = tk.Button(
            self.use_cases,
            text="Fine Tuning",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.fine_icon,
            compound="left",
        )
        self.use_cases.grid(row=2, column=0)
        self.pred_btn.pack(fill="both", padx=5, pady=5)
        self.rev_btn.pack(fill="both", padx=5, pady=5)
        self.fine_btn.pack(fill="both", padx=5, pady=5)

        # review frame (import predictions + nav + validate/refuse/correct)
        self.rev_Frame = tk.Frame(self.frame, bg=theme.PANEL, width=200, height=100)
        self.get_predictions_path = tk.Button(
            self.rev_Frame,
            text="Import Predictions Folder",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.import_icon,
            compound="left",
        )
        # navigation
        self.navigateFrame = tk.Frame(
            self.rev_Frame, bg=theme.PANEL, width=200, height=100
        )
        self.next_icon = image_utils.load_icon(IMG_DIR, "next.png", (24, 24))
        self.next_btn = tk.Button(
            self.navigateFrame,
            text="Next",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.next_icon,
            compound="right",
        )
        self.prev_icon = image_utils.load_icon(IMG_DIR, "prev.png", (24, 24))
        self.prev_btn = tk.Button(
            self.navigateFrame,
            text="Prev",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.prev_icon,
            compound="left",
        )
        self.navigateFrame.grid(row=1, column=0)
        self.next_btn.grid(row=0, column=1, sticky="en", padx=2, pady=2)
        self.prev_btn.grid(row=0, column=0, sticky="en", padx=2, pady=2)

        self.validate_icon = image_utils.load_icon(IMG_DIR, "valid.png", (24, 24))
        self.validate_but = UIutils.make_btn(
            self.rev_Frame,
            "Validate",
            2,
            color=theme.SUCCESS,
            text_color="white",
            pady_top=4,
            image=self.validate_icon,
        )
        self.refuse_but = UIutils.make_btn(
            self.rev_Frame,
            "Refuse",
            3,
            color=theme.DANGER,
            text_color="white",
            pady_top=4,
        )
        self.correct_but = UIutils.make_btn(
            self.rev_Frame,
            "correct imperfections",
            4,
            color=theme.ACCENT,
            text_color="white",
            pady_top=4,
        )

        # edit subframe (brush/eraser/save)
        self.edit_frame = tk.Frame(
            self.rev_Frame, bg=theme.PANEL, width=200, height=100
        )
        for i in range(2):
            self.edit_frame.grid_rowconfigure(i, weight=0)
            self.edit_frame.grid_columnconfigure(i, weight=0)

        self.brush_icon = image_utils.load_icon(IMG_DIR, "brush.png", (24, 24))
        self.brush = UIutils.make_btn(
            self.edit_frame,
            "",
            0,
            color="#555",
            text_color=theme.MUTED,
            pady_top=4,
            col=0,
            image=self.brush_icon,
        )
        self.eraser_icon = image_utils.load_icon(IMG_DIR, "eraser.png", (24, 24))
        self.ereaser = UIutils.make_btn(
            self.edit_frame,
            "",
            0,
            color=theme.MUTED,
            text_color=theme.MUTED,
            pady_top=4,
            col=1,
            image=self.eraser_icon,
        )
        self.save_icon = image_utils.load_icon(IMG_DIR, "save.png", (24, 24))
        self.save_changes = UIutils.make_btn(
            self.edit_frame,
            "",
            1,
            color=theme.SUCCESS,
            text_color="white",
            pady_top=4,
            col=1,
            image=self.save_icon,
        )
        self.changes_state_label = tk.Label(
            self.edit_frame,
            text="no changes",
            font=(theme.MONO, 9),
            bg=theme.PANEL,
            fg=theme.TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.changes_state_label.grid(row=1, column=1)

        self.get_predictions_path.grid(row=0, column=0)
        self.edit_frame.grid(row=5, column=0)

        # keep frames hidden by default (same behavior as original)
        self.use_cases.grid_remove()
        self.rev_Frame.grid_remove()
        self.validate_but.grid_remove()
        self.refuse_but.grid_remove()
        self.navigateFrame.grid_remove()
        self.correct_but.grid_remove()
        self.edit_frame.grid_remove()
        self.save_changes.grid_remove()
        self.changes_state_label.grid_remove()

        # predictions frame
        self.pred_frame = tk.Frame(self.frame, bg=theme.PANEL, width=200, height=100)
        self.get_model = UIutils.make_btn(
            self.pred_frame,
            "Import Biom3d Model",
            0,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )
        self.get_folder_out = UIutils.make_btn(
            self.pred_frame,
            "OUT FOlDER",
            1,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )
        self.pred = UIutils.make_btn(
            self.pred_frame,
            "Predict",
            2,
            color=theme.SUCCESS,
            text_color=theme.TEXT_HI,
            pady_top=6,
        )
        self.pred_frame.grid_remove()
        self.get_model.grid_remove()
        self.get_folder_out.grid_remove()
        self.pred.grid_remove()

        # quit button (pinned bottom)
        self.quit_icon = image_utils.load_icon(IMG_DIR, "quit.png", (24, 24))
        self.quit_btn = tk.Button(
            self.frame,
            text="Quit",
            font=(theme.SANS, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_DIM,
            activebackground=theme.DANGER,
            activeforeground=theme.PANEL,
            relief="flat",
            bd=0,
            pady=4,
            cursor="hand2",
            command=root.destroy,
            image=self.quit_icon,
            compound="left",
        )
        self.quit_btn.grid(row=10, column=0, sticky="sew", padx=12, pady=(0, 10))
