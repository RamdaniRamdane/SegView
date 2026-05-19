import tkinter as tk
from tkinter import ttk

import theme
from src.ui_utils import UIutils


class Sidebarleft:
    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.Frame(root, bg=theme.PANEL, width=200)
        self.frame.grid_propagate(False)
        for i in range(3):
            self.frame.grid_rowconfigure(i, weight=0)
        self.frame.grid_columnconfigure(0, weight=1)

        self.titel = None
        self.title = "prediction info"
        UIutils.sidebar_label(self.frame, self.title, 0)
        self.progressbar = ttk.Progressbar(
            self.frame, orient="horizontal", length=180, mode="indeterminate"
        )

        self.progressbar.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="ew")
        self.progressbar.grid_remove()

    def progressbar_handler(self, progressbar, act, max_todo=None):
        if max_todo:
            grow = progressbar["maximum"] / max_todo
            print(grow)
        print(max_todo)
        print(progressbar["value"])
        print(progressbar["maximum"])
        value = progressbar["value"]
        print("value at start handl : ", value)
        if value == progressbar["maximum"]:
            return False
        elif act == "GROW":
            if (value + grow) <= progressbar["maximum"]:
                progressbar["value"] = value + grow
                print(value)
                print("grow with", value + grow)
                print("progress bar value", progressbar["value"])
            else:
                progressbar["value"] = progressbar["maximum"]
        elif act == "END":
            progressbar["value"] = progressbar["maximum"]
        elif act == "RESET":
            progressbar["value"] = 0
        return True

    def toggl_determinate_mode(self, progressbar):
        print("call determinate")
        progressbar.stop()
        progressbar.config(mode="determinate")
        self.progressbar["maximum"] = 100

    def remove_progressbar(self, progressbar):
        progressbar.grid_remove()

    def show_progressbar(self, progressbar):
        progressbar.config(mode="indeterminate")
        progressbar.start()
        progressbar.grid()
