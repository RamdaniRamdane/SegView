import os
import sys
import tkinter as tk
from tkinter import Canvas

import image_utils
from ui_utils import UIutils

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "images")

BG = "#0e0e0f"  # near-black base
PANEL = "#141416"  # slightly lighter panel
BORDER = "#222226"  # subtle separator
MUTED = "#3a3a40"  # inactive elements
TEXT_DIM = "#555560"  # secondary labels
TEXT = "#c8c8d0"  # primary text
TEXT_HI = "#e8e8f0"  # highlighted text
ACCENT = "#4a9eff"  # blue accent (validate / active)
DANGER = "#d94f4f"  # red (refuse)
SUCCESS = "#3dab6e"  # green (validated status)
WARNING = "#c09030"  # amber (pending status)
MONO = "Courier"  # monospace for scientific labels
SANS = "Helvetica"  # clean sans


class SegViewUI:
    def __init__(self, root):
        self.st = 3
        # root tkinter tk main config
        self.root = root
        self.root.title("SegView")
        self.root.geometry("1000x680")
        self.root.configure(background=BG)
        self.root.resizable(True, True)

        # Grid weights
        self.root.grid_rowconfigure(0, weight=0)  # toolbar
        self.root.grid_rowconfigure(1, weight=1)  # canvas
        self.root.grid_rowconfigure(2, weight=0)  # slider row
        self.root.grid_rowconfigure(3, weight=0)  # status review
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)  # side bar fixe width

        # sidebar Frame
        self.sidebar = tk.Frame(self.root, bg=PANEL, width=200)
        self.sidebar.grid(
            row=0, column=1, rowspan=4, sticky="nsew", padx=(0, 0), pady=0
        )
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(0, weight=0)
        self.sidebar.grid_rowconfigure(1, weight=0)
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_rowconfigure(3, weight=0)
        self.sidebar.grid_rowconfigure(4, weight=0)
        self.sidebar.grid_rowconfigure(5, weight=0)
        self.sidebar.grid_rowconfigure(6, weight=0)
        self.sidebar.grid_rowconfigure(7, weight=0)
        self.sidebar.grid_rowconfigure(8, weight=0)
        self.sidebar.grid_rowconfigure(9, weight=0)
        self.sidebar.grid_rowconfigure(10, weight=0)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # toolbar
        self.toolbar = tk.Frame(self.root, bg=PANEL, height=36)
        self.toolbar.grid(row=0, column=0, sticky="ew")
        self.toolbar.grid_propagate(False)

        # thin botom under toolbar
        tb_sep = tk.Frame(self.root, bg=BORDER, height=0)
        tb_sep.grid(row=0, column=0, sticky="sew")

        self.path_label = tk.Label(
            self.toolbar,
            text="no file loaded",
            font=(MONO, 9),
            bg=PANEL,
            fg=TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.path_label.pack(side="left", fill="both", expand=True)

        # Canvas image view
        self.canvas = Canvas(root, bg="black", cursor="crosshair")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # slide row
        self.slider_row = tk.Frame(self.root, bg=BG, height=32)
        self.slider_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 2))
        self.slider_row.grid_columnconfigure(1, weight=1)

        self.z_label = tk.Label(
            self.slider_row, text="Z", font=(MONO, 8), bg=BG, fg=TEXT_DIM, width=2
        )
        self.z_label.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)

        self.zoom_slider = tk.Scale(
            self.slider_row,
            from_=0,
            to=0,
            orient="horizontal",
            showvalue=True,
            font=(MONO, 8),
            bg=BG,
            fg=TEXT_DIM,
            troughcolor=BORDER,
            activebackground=ACCENT,
            highlightthickness=0,
            bd=0,
            sliderlength=12,
            sliderrelief="flat",
            width=6,
        )
        self.zoom_slider.grid(row=0, column=1, sticky="ew")

        # status strip
        self.status_strip = tk.Frame(self.root, bg=PANEL, height=22)
        self.status_strip.grid(row=3, column=0, sticky="ew")
        self.status_strip.grid_propagate(False)

        self.status_sep = tk.Frame(self.root, bg=BORDER, height=1)
        self.status_sep.grid(row=3, column=0, sticky="new")

        self.info_label = tk.Label(
            self.status_strip,
            text="",
            font=(MONO, 8),
            bg=PANEL,
            fg=TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.info_label.pack(side="left")

        # flag status
        self.flag_sign = tk.Label(
            self.status_strip,
            text="●",
            font=(MONO, 10),
            bg=PANEL,
            fg=MUTED,
        )
        self.flag_sign.pack(side="right", padx=10)
        self.flag_text = tk.Label(
            self.status_strip,
            text="unreviewed",
            font=(MONO, 8),
            bg=PANEL,
            fg=MUTED,
        )
        self.flag_text.pack(side="right", padx=(0, 2))

        # first try adding icon
        self.import_icon = image_utils.load_icon(IMG_DIR, "import.png", (24, 24))
        UIutils.sidebar_label(self.sidebar, "INPUT", 0)
        self.btn = UIutils.make_btn(
            self.sidebar,
            "Import Folder RAW",
            1,
            color=MUTED,
            text_color=TEXT_HI,
            pady_top=4,
            image=self.import_icon,
        )
        self.btn.image = self.import_icon
        self.use_cases = tk.Frame(self.sidebar, bg=PANEL, width=200, height=100)
        self.predict_icon = image_utils.load_icon(IMG_DIR, "predict.png", (24, 24))
        self.pred_btn = tk.Button(
            self.use_cases,
            text="Predict Mask",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.predict_icon,
            compound="left",
        )
        self.review_icon = image_utils.load_icon(IMG_DIR, "review.png", (24, 24))
        self.rev_btn = tk.Button(
            self.use_cases,
            text="Review Predictions",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.review_icon,
            compound="left",
        )
        self.fine_icon = image_utils.load_icon(IMG_DIR, "fine.png", (24, 24))
        self.fine_btn = tk.Button(
            self.use_cases,
            text="Fine Tuning",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.fine_icon,
            compound="left",
        )

        self.use_cases.grid(row=2, column=0)
        self.pred_btn.pack(fill="both", padx=5, pady=5)
        self.rev_btn.pack(fill="both", padx=5, pady=5)
        self.fine_btn.pack(fill="both", padx=5, pady=5)

        self.use_cases.grid_remove()
        # creating frames

        # reviewing frame
        self.rev_Frame = tk.Frame(self.sidebar, bg=PANEL, width=200, height=100)
        self.get_predictions_path = tk.Button(
            self.rev_Frame,
            text="Import Predictions Folder",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.import_icon,
            compound="left",
        )
        self.rev_Frame.grid(row=3, column=0)
        self.rev_Frame.grid_rowconfigure(0, weight=0)
        self.rev_Frame.grid_rowconfigure(1, weight=0)
        self.rev_Frame.grid_rowconfigure(2, weight=0)
        self.rev_Frame.grid_rowconfigure(3, weight=0)
        self.rev_Frame.grid_rowconfigure(4, weight=0)
        self.rev_Frame.grid_rowconfigure(5, weight=0)
        self.rev_Frame.grid_columnconfigure(0, weight=1)
        # navigate and validate and invalidate results
        self.navigateFrame = tk.Frame(self.rev_Frame, bg=PANEL, width=200, height=100)
        self.navigateFrame.grid(row=1, column=0)
        self.navigateFrame.grid_columnconfigure(0, weight=0)
        self.navigateFrame.grid_columnconfigure(1, weight=0)
        self.navigateFrame.grid_rowconfigure(0, weight=1)
        self.next_icon = image_utils.load_icon(IMG_DIR, "next.png", (24, 24))
        self.next_btn = tk.Button(
            self.navigateFrame,
            text="Next",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.next_icon,
            compound="right",
        )

        self.prev_icon = image_utils.load_icon(IMG_DIR, "prev.png", (24, 24))
        self.next_btn.grid(row=0, column=1, sticky="en", padx=2, pady=2)
        self.prev_btn = tk.Button(
            self.navigateFrame,
            text="Prev",
            font=(MONO, 8),
            bg=MUTED,
            fg=TEXT_HI,
            relief="flat",
            cursor="hand2",
            image=self.prev_icon,
            compound="left",
        )
        self.prev_btn.grid(row=0, column=0, sticky="en", padx=2, pady=2)

        self.validate_icon = image_utils.load_icon(IMG_DIR, "valid.png", (24, 24))
        self.validate_but = UIutils.make_btn(
            self.rev_Frame,
            "Validate",
            2,
            color=SUCCESS,
            text_color="white",
            pady_top=4,
            image=self.validate_icon,
        )
        self.refuse_but = UIutils.make_btn(
            self.rev_Frame, "Refuse", 3, color=DANGER, text_color="white", pady_top=4
        )
        self.correct_but = UIutils.make_btn(
            self.rev_Frame,
            "correct imperfections",
            4,
            color=ACCENT,
            text_color="white",
            pady_top=4,
        )

        self.edit_frame = tk.Frame(self.rev_Frame, bg=PANEL, width=200, height=100)
        self.edit_frame.grid_rowconfigure(0, weight=0)
        self.edit_frame.grid_rowconfigure(1, weight=0)
        self.edit_frame.grid_columnconfigure(0, weight=0)
        self.edit_frame.grid_columnconfigure(1, weight=0)
        self.edit_frame.grid(row=5, column=0)
        self.brush_icon = image_utils.load_icon(IMG_DIR, "brush.png", (24, 24))
        self.brush = UIutils.make_btn(
            self.edit_frame,
            "",
            0,
            color="#555",
            text_color=MUTED,
            pady_top=4,
            col=0,
            image=self.brush_icon,
        )

        self.eraser_icon = image_utils.load_icon(IMG_DIR, "eraser.png", (24, 24))
        self.ereaser = UIutils.make_btn(
            self.edit_frame,
            "",
            0,
            color=MUTED,
            text_color=MUTED,
            pady_top=4,
            col=1,
            image=self.eraser_icon,
        )
        self.save_icon = image_utils.load_icon(IMG_DIR, "save.png", (24, 24))
        self.save_changes = UIutils.make_btn(
            self.edit_frame,
            "",
            1,
            color=SUCCESS,
            text_color="white",
            pady_top=4,
            col=1,
            image=self.save_icon,
        )
        self.changes_state_label = tk.Label(
            self.edit_frame,
            text="no changes",
            font=(MONO, 9),
            bg=PANEL,
            fg=TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.changes_state_label.grid(row=1, column=1)

        self.get_predictions_path.grid(row=0, column=0)
        self.rev_Frame.grid_remove()
        self.validate_but.grid_remove()
        self.refuse_but.grid_remove()
        self.navigateFrame.grid_remove()
        self.correct_but.grid_remove()
        self.edit_frame.grid_remove()
        self.save_changes.grid_remove()
        self.changes_state_label.grid_remove()
        # end reviewing frame

        # predictionss frame
        self.pred_frame = tk.Frame(self.sidebar, bg=PANEL, width=200, height=100)
        self.pred_frame.grid(row=3, column=0)
        self.pred_frame.grid_rowconfigure(0, weight=0)
        self.pred_frame.grid_rowconfigure(1, weight=0)
        self.pred_frame.grid_rowconfigure(2, weight=0)
        self.pred_frame.grid_columnconfigure(0, weight=1)
        self.get_model = UIutils.make_btn(
            self.pred_frame,
            "Import Biom3d Model",
            0,
            color=MUTED,
            text_color=TEXT,
            pady_top=6,
        )
        self.get_folder_out = UIutils.make_btn(
            self.pred_frame,
            "OUT FOlDER",
            1,
            color=MUTED,
            text_color=TEXT,
            pady_top=6,
        )
        self.pred = UIutils.make_btn(
            self.pred_frame, "Predict", 2, color=SUCCESS, text_color=TEXT_HI, pady_top=6
        )
        self.pred_frame.grid_remove()
        self.get_model.grid_remove()
        self.get_folder_out.grid_remove()
        self.pred.grid_remove()
        # end predictionss frame

        # QUIT pinned on the bottom

        self.quit_icon = image_utils.load_icon(IMG_DIR, "quit.png", (24, 24))
        self.quit_btn = tk.Button(
            self.sidebar,
            text="Quit",
            font=(SANS, 8),
            bg=MUTED,
            fg=TEXT_DIM,
            activebackground=DANGER,
            activeforeground=PANEL,
            relief="flat",
            bd=0,
            pady=4,
            cursor="hand2",
            command=self.root.destroy,
            image=self.quit_icon,
            compound="left",
        )

        self.quit_btn.grid(row=10, column=0, sticky="sew", padx=12, pady=(0, 10))
