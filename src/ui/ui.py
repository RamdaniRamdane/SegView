import tkinter as tk

import src.ui.theme as theme

from .components.extra import CanvasView, SliderRow, StatusStrip, Toolbar
from .components.side_bar_left import Sidebarleft
from .components.side_bar_right import Sidebarright
from .components.top_bar import TopBar


class SegViewUI:
    def __init__(self, root):
        self.st = 3
        self.state = None

        self.root = root
        self.root.title("SegView")
        self.root.geometry("1000x680")
        self.root.configure(background=theme.BG)
        self.root.resizable(True, True)

        # grid weights
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_rowconfigure(3, weight=0)
        self.root.grid_rowconfigure(4, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=0)

        self.topbar = TopBar(self.root)
        self.topbar.frame.grid(row=0, column=0, columnspan=3)
        # instantiate components
        self.toolbar = Toolbar(self.root)
        self.toolbar.frame.grid(row=1, column=1, sticky="ew")

        # thin bottom under toolbar
        tb_sep = tk.Frame(self.root, bg=theme.BORDER, height=0)
        tb_sep.grid(row=1, column=1, sticky="sew")

        # sidebarright
        self.sidebarright = Sidebarright(self.root, self.root)
        self.sidebarright.container.grid(
            row=1, column=2, rowspan=4, sticky="nsew", padx=(0, 0), pady=0
        )

        # canvas view
        self.canvas_view = CanvasView(self.root)
        self.canvas_view.canvas.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        # sidebarleft
        self.sidebarleft = Sidebarleft(self, self.root)
        self.sidebarleft.frame.grid(
            row=1, column=0, rowspan=4, sticky="nsew", padx=(0, 0), pady=0
        )

        # slider row
        self.slider = SliderRow(self.root)
        self.slider.frame.grid(row=3, column=1, sticky="ew", padx=12, pady=(0, 2))

        # status strip
        self.status = StatusStrip(self.root)
        # self.status.status_sep.grid(row=3, column=0, sticky="new")
        self.status.frame.grid(row=4, column=1, sticky="ew")

        # frequently used widgets on top-level
        self.canvas = self.canvas_view.canvas
        self.zoom_slider = self.slider.zoom_slider
        self.path_label = self.toolbar.path_label

    def set_state(self, state):
        self.state = state
