import os
import tkinter as tk
from tkinter import ttk

import theme
from src.file_manager import FileManager
from src.ui_utils import UIutils


class Sidebarleft:
    def __init__(self, parent, root):
        self.root = root
        self.ui = parent
        self.pourcentage = ""
        self.selected_file = None
        self.file_buttons = []

        self.frame = tk.Frame(root, bg=theme.PANEL, width=200, bd=0)

        self.frame.grid_propagate(False)

        for i in range(3):
            self.frame.grid_rowconfigure(i, weight=0)

        self.frame.grid_rowconfigure(
            2,
            weight=1,
        )

        self.frame.grid_columnconfigure(
            0,
            weight=1,
        )

        self.titel = None
        self.title = "prediction info"

        self.progressbartext = UIutils.sidebar_label(
            self.frame,
            self.title,
            0,
        )

        # ==========================
        # PROGRESS BAR Refactor it later
        # ==========================
        style = ttk.Style(self.root)

        style_name = "custom"

        style.layout(
            style_name,
            [
                (
                    "Horizontal.Progressbar.trough",
                    {
                        "children": [
                            (
                                "Horizontal.Progressbar.pbar",
                                {
                                    "side": "left",
                                    "sticky": "ns",
                                },
                            )
                        ],
                        "sticky": "nswe",
                    },
                )
            ],
        )
        style.theme_use("clam")

        style.configure(
            style_name,
            troughcolor=theme.PANEL,
            background=theme.SUCCESS,
        )

        self.progressbar = ttk.Progressbar(
            self.frame,
            orient="horizontal",
            length=180,
            mode="indeterminate",
            style=style_name,
        )

        self.progressbar.grid(
            row=1,
            column=0,
            padx=10,
            pady=(5, 10),
            sticky="ew",
        )

        self.progressbar.grid_remove()

        # ==========================
        # SCROLLABLE FILES FRAME
        # ==========================
        self.files_container = tk.Frame(
            self.frame,
            bg=theme.PANEL,
            width=200,
            bd=0,
        )

        self.files_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(0, 0),
            pady=0,
        )

        self.files_container.grid_rowconfigure(
            0,
            weight=1,
        )

        self.files_container.grid_columnconfigure(
            0,
            weight=1,
        )

        # Canvas
        self.files_canvas = tk.Canvas(
            self.files_container,
            bg=theme.PANEL,
            highlightthickness=0,
            bd=0,
            relief="flat",
        )

        self.files_canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        # Scrollbar

        sbStyle = ttk.Style()
        sbStyle.theme_use("clam")

        sbStyle.configure(
            "Custom.Vertical.TScrollbar",
            gripcount=0,
            background="#555",
            darkcolor="#555",
            lightcolor="#555",
            troughcolor=theme.PANEL,
            bordercolor=theme.PANEL,
            arrowcolor="#999",
            relief="flat",
            borderwidth=0,
        )

        sbStyle.map(
            "Custom.Vertical.TScrollbar",
            background=[
                ("active", "#777"),
            ],
        )
        self.scrollbar = ttk.Scrollbar(
            self.files_container,
            orient="vertical",
            style="Custom.Vertical.TScrollbar",
            command=self.files_canvas.yview,
        )

        self.scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        self.files_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame interne
        self.files_status_frame = tk.Frame(
            self.files_canvas,
            bg=theme.PANEL,
            bd=0,
            highlightthickness=0,
        )

        self.canvas_window = self.files_canvas.create_window(
            (0, 0),
            window=self.files_status_frame,
            anchor="nw",
        )

        # Resize auto scroll region
        self.files_status_frame.bind(
            "<Configure>",
            lambda e: self.files_canvas.configure(
                scrollregion=self.files_canvas.bbox("all")
            ),
        )

        # Resize width auto
        self.files_canvas.bind(
            "<Configure>",
            self._resize_canvas_width,
        )

        # Mouse wheel
        self.files_canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel,
        )

    # ==========================
    # SCROLL METHODS
    # ==========================
    def _resize_canvas_width(self, event):
        self.files_canvas.itemconfig(
            self.canvas_window,
            width=event.width,
        )

    def _on_mousewheel(self, event):
        self.files_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units",
        )

    # ==========================
    # FILES LIST
    # ==========================
    def show_files_list(self):
        if self.ui.state:
            # Clean old widgets
            for widget in self.files_status_frame.winfo_children():
                widget.destroy()

            self.file_buttons = []

            for i in range(len(self.ui.state.files) + 1):
                self.files_status_frame.grid_rowconfigure(
                    i,
                    weight=0,
                )

            self.files_status_frame.grid_columnconfigure(
                0,
                weight=1,
            )

            self.files_status_label = UIutils.sidebar_label(
                self.files_status_frame,
                "files",
                0,
            )

            if len(self.ui.state.files):
                for i in range(len(self.ui.state.files)):
                    btn = tk.Button(
                        self.files_status_frame,
                        text=self.ui.state.files[i],
                        bg=theme.PANEL,
                        fg=theme.TEXT,
                        activebackground="#666",
                        activeforeground="white",
                        relief="flat",
                        bd=0,
                        anchor="w",
                        padx=10,
                        pady=6,
                        cursor="hand2",
                    )

                    btn.grid(
                        row=i + 1,
                        column=0,
                        sticky="ew",
                        padx=5,
                        pady=2,
                    )

                    btn.file_index = i
                    self.file_buttons.append(btn)

        else:
            print("state dont exite")

    # ==========================
    # TOGGLE BUTTON
    # ==========================

    def update_color_text_file(self):
        filemanager = FileManager(self.ui)
        parent = self.ui.state.path_out
        index = 0
        print("update color called")
        if parent:
            for i in self.ui.state.files:
                filepath = os.path.join(
                    parent,
                    i,
                )
                print(filepath)
                print(filemanager.status(filepath))
                if filemanager.status(filepath) == 1:
                    for btn in self.file_buttons:
                        if btn.file_index == index:
                            btn.config(fg=theme.SUCCESS)
                elif filemanager.status(filepath) == 2:
                    for btn in self.file_buttons:
                        if btn.file_index == index:
                            btn.config(fg=theme.DANGER)
                elif filemanager.status(filepath) == 3:
                    for btn in self.file_buttons:
                        if btn.file_index == index:
                            btn.config(fg=theme.WARNING)

                index += 1

    # ==========================
    # PROGRESS BAR METHODS
    # ==========================

    def progressbar_handler(
        self,
        progressbar,
        act,
        max_todo=None,
    ):
        if max_todo:
            grow = progressbar["maximum"] / max_todo

        value = progressbar["value"]

        if value == progressbar["maximum"]:
            return False

        elif act == "GROW":
            if (value + grow) <= progressbar["maximum"]:
                progressbar["value"] = value + grow
                self.update_progress_bar_text()
            else:
                progressbar["value"] = progressbar["maximum"]
                self.update_progress_bar_text()

        elif act == "END":
            progressbar["value"] = progressbar["maximum"]
            self.update_progress_bar_text()

        elif act == "RESET":
            progressbar["value"] = 0
            self.update_progress_bar_text()

        return True

    def toggl_determinate_mode(self, progressbar):
        print("call determinate")

        progressbar.stop()
        progressbar.config(mode="determinate")

        self.progressbar["maximum"] = 100
        self.progressbar["value"] = 0

    def remove_progressbar(self, progressbar):
        progressbar.grid_remove()

    def show_progressbar(self, progressbar):
        progressbar.config(mode="indeterminate")
        progressbar.start()
        progressbar.grid()

    def update_progress_bar_text(self):
        pourcentage = int(self.progressbar["value"])

        pourcentage = pourcentage if pourcentage else "--"

        text = "prediction info  " + str(pourcentage) + "%"

        self.progressbartext.config(text=text)
