import tkinter as tk
from tkinter import ttk

import theme
from src.ui_utils import UIutils


class Sidebarleft:
    def __init__(self, parent, root):
        self.root = root
        self.pourcentage = ""
        self.frame = tk.Frame(root, bg=theme.PANEL, width=200)
        self.frame.grid_propagate(False)
        for i in range(3):
            self.frame.grid_rowconfigure(i, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)

        self.titel = None
        self.title = "prediction info"
        self.progressbartext = UIutils.sidebar_label(self.frame, self.title, 0)

        style = ttk.Style(self.root)

        # Nom et layout corrects pour une Progressbar personnalisée
        style_name = "custom.Horizontal.TProgressbar"

        # Layout minimal (assure l'existence du layout si tu veux customiser plus tard)
        style.layout(
            style_name,
            [
                (
                    "Horizontal.Progressbar.trough",
                    {
                        "children": [
                            (
                                "Horizontal.Progressbar.pbar",
                                {"side": "left", "sticky": "ns"},
                            )
                        ],
                        "sticky": "nswe",
                    },
                )
            ],
        )

        style.configure(
            style_name,
            troughcolor=theme.BG,
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

    # Methods pour handle progressbar status
    def progressbar_handler(self, progressbar, act, max_todo=None):
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
