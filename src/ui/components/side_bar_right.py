import os
import tkinter as tk

import src.services.image_utils as image_utils
import src.ui.theme as theme
from src.ui.helpers.ui_utils import UIutils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
IMG_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", "images"))
print(IMG_DIR)


class Sidebarright:
    def __init__(self, parent, root):
        self.root = root
        # side bar containter
        self.container = tk.Frame(root, bg=theme.PANEL, width=200)
        self.container.grid_propagate(False)
        # grid rows reserved to replicate original layout
        for i in range(11):
            self.container.grid_rowconfigure(i, weight=0)
        self.container.grid_columnconfigure(1, weight=1)

        # INPUT label + Import button
        UIutils.sidebar_label(self.container, "INPUT", 0)

        self.btn = UIutils.make_btn(
            self.container,
            "Import Folder RAW",
            1,
            color=theme.MUTED,
            text_color=theme.TEXT_HI,
            pady_top=4,
        )

        # review frame (import predictions + nav + validate/refuse/correct)
        self.review_container = tk.Frame(
            self.container, bg=theme.PANEL, width=200, height=100
        )
        self.get_predictions_path = tk.Button(
            self.review_container,
            text="Import Predictions Folder",
            font=(theme.MONO, 6),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            compound="left",
        )
        # navigation
        self.navigateFrame = tk.Frame(
            self.review_container, bg=theme.PANEL, width=200, height=100
        )
        self.next_btn = tk.Button(
            self.navigateFrame,
            text="Next",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            compound="right",
        )
        self.prev_btn = tk.Button(
            self.navigateFrame,
            text="Prev",
            font=(theme.MONO, 8),
            bg=theme.MUTED,
            fg=theme.TEXT_HI,
            relief="flat",
            cursor="hand2",
            compound="left",
        )
        self.navigateFrame.grid(row=1, column=0)
        self.next_btn.grid(row=0, column=1, sticky="en", padx=2, pady=2)
        self.prev_btn.grid(row=0, column=0, sticky="en", padx=2, pady=2)

        self.validate_but = UIutils.make_btn(
            self.review_container,
            "Validate",
            2,
            color=theme.SUCCESS,
            text_color="white",
            pady_top=4,
        )
        self.refuse_but = UIutils.make_btn(
            self.review_container,
            "Refuse",
            3,
            color=theme.DANGER,
            text_color="white",
            pady_top=4,
        )
        self.unreview_but = UIutils.make_btn(
            self.review_container,
            "unreview",
            4,
            color=theme.WARNING,
            text_color="white",
            pady_top=4,
        )
        self.correct_but = UIutils.make_btn(
            self.review_container,
            "correct imperfections",
            5,
            color=theme.ACCENT,
            text_color="white",
            pady_top=4,
        )

        # edit subframe (brush/eraser/save)
        self.edit_frame = tk.Frame(
            self.review_container, bg=theme.PANEL, width=200, height=100
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
        self.changes_state_label.grid(row=1, column=0, columnspan=2)

        self.get_predictions_path.grid(row=0, column=0)
        self.edit_frame.grid(row=6, column=0)

        # keep frames hidden by default (same behavior as original)
        self.review_container.grid_remove()
        self.validate_but.grid_remove()
        self.unreview_but.grid_remove()
        self.refuse_but.grid_remove()
        self.navigateFrame.grid_remove()
        self.correct_but.grid_remove()
        self.edit_frame.grid_remove()
        self.save_changes.grid_remove()
        self.changes_state_label.grid_remove()

        # predictions frame
        self.pred_container = tk.Frame(
            self.container, bg=theme.PANEL, width=200, height=100
        )
        self.get_model = UIutils.make_btn(
            self.pred_container,
            "Import Biom3d Model",
            0,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )
        self.get_folder_out = UIutils.make_btn(
            self.pred_container,
            "OUT FOlDER",
            1,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )
        self.pred = UIutils.make_btn(
            self.pred_container,
            "Predict",
            2,
            color=theme.SUCCESS,
            text_color=theme.TEXT_HI,
            pady_top=6,
        )
        self.pred.grid_remove()
        self.get_folder_out.grid_remove()

        # fine tuning route
        # ajouter un bouton pour valide path
        self.fine_container = tk.Frame(
            self.container, bg=theme.PANEL, width=200, height=100
        )

        for i in range(2):
            self.edit_frame.grid_columnconfigure(i, weight=0)
        self.edit_frame.grid_rowconfigure(0, weight=0)
        self.get_valid_masks = UIutils.make_btn(
            self.fine_container,
            "Valide Masks",
            0,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )
        self.make_config_file = UIutils.make_btn(
            self.fine_container,
            "Make Config",
            1,
            color=theme.MUTED,
            text_color=theme.TEXT,
            pady_top=6,
        )

        self.fine_container.grid_remove()
        self.get_valid_masks.grid_remove()
        self.make_config_file.grid_remove()
