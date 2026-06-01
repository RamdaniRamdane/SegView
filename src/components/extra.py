import tkinter as tk
from tkinter import Canvas

import theme


class Toolbar:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=theme.PANEL, height=36)
        self.frame.grid_propagate(False)
        self.path_label = tk.Label(
            self.frame,
            text="no file loaded",
            font=(theme.MONO, 9),
            bg=theme.PANEL,
            fg=theme.TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.path_label.pack(side="left", fill="both", expand=True)


class CanvasView:
    def __init__(self, parent):
        self.canvas = Canvas(parent, bg="black", cursor="crosshair")


class SliderRow:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=theme.BG, height=32)
        self.frame.grid_columnconfigure(1, weight=1)

        self.z_label = tk.Label(
            self.frame,
            text="Z",
            font=(theme.MONO, 8),
            bg=theme.BG,
            fg=theme.TEXT_DIM,
            width=2,
        )
        self.z_label.grid(row=0, column=0, sticky="w", padx=(0, 6), pady=4)

        self.zoom_slider = tk.Scale(
            self.frame,
            from_=0,
            to=0,
            orient="horizontal",
            showvalue=True,
            font=(theme.MONO, 8),
            bg=theme.BG,
            fg=theme.TEXT_DIM,
            troughcolor=theme.BORDER,
            activebackground=theme.ACCENT,
            highlightthickness=0,
            bd=0,
            sliderlength=12,
            sliderrelief="flat",
            width=6,
        )
        self.zoom_slider.grid(row=0, column=1, sticky="ew")


class StatusStrip:
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=theme.PANEL, height=22)
        self.frame.grid_propagate(False)

        # self.status_sep = tk.Frame(parent, bg=theme.DANGER, height=1)

        self.info_label = tk.Label(
            self.frame,
            text="",
            font=(theme.MONO, 8),
            bg=theme.PANEL,
            fg=theme.TEXT_DIM,
            anchor="w",
            padx=10,
            pady=10,
        )
        self.info_label.pack(side="left")

        self.flag_sign = tk.Label(
            self.frame,
            text="●",
            font=(theme.MONO, 10),
            bg=theme.PANEL,
            fg=theme.MUTED,
        )
        self.flag_sign.pack(side="right", padx=10)
        self.flag_text = tk.Label(
            self.frame,
            text="unreviewed",
            font=(theme.MONO, 8),
            bg=theme.PANEL,
            fg=theme.MUTED,
        )
        self.flag_text.pack(side="right", padx=(0, 2))
