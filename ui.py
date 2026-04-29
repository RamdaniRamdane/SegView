import tkinter as tk
from tkinter import Canvas

from ui_utils import UIutils

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
        self.sidebar.grid_rowconfigure(4, weight=1)  # space
        self.sidebar.grid_rowconfigure(5, weight=0)
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

        UIutils.sidebar_label(self.sidebar, "INPUT", 0)
        self.btn = UIutils.make_btn(
            self.sidebar, "Import Image", 1, color=MUTED, text_color=TEXT_HI, pady_top=4
        )
        self.get_model = UIutils.make_btn(
            self.sidebar, "Import Model", 2, color=MUTED, text_color=TEXT, pady_top=6
        )

        UIutils.sidebar_label(self.sidebar, "REVIEW", 3)
        self.validate_but = UIutils.make_btn(
            self.sidebar, "Validate", 4, color=SUCCESS, text_color="white", pady_top=4
        )
        self.refuse_but = UIutils.make_btn(
            self.sidebar, "Refuse", 5, color=DANGER, text_color="white", pady_top=4
        )

        # QUIT pinned on the bottom
        self.quit_btn = tk.Button(
            self.sidebar,
            text="Quit",
            font=(SANS, 8),
            bg=PANEL,
            fg=TEXT_DIM,
            activebackground=PANEL,
            activeforeground=DANGER,
            relief="flat",
            bd=0,
            pady=4,
            cursor="hand2",
            command=self.root.destroy,
        )
        self.quit_btn.grid(row=6, column=0, sticky="ew", padx=12, pady=(0, 10))
