import os
import tkinter as tk

import theme
from src.image_utils import display


class UIutils:
    def __init__(self, ui=None, state=None, file_manager=None):
        if ui:
            self.ui = ui
        if state:
            self.state = state
        if file_manager:
            self.file_manager = file_manager

    @staticmethod
    def make_btn(
        parent,
        text,
        row,
        color=theme.MUTED,
        text_color=theme.TEXT,
        cmd=None,
        pady_top=8,
        col=0,
        image=None,
    ):

        frame = tk.Frame(
            parent,
            bg=theme.PANEL,
        )

        frame.grid(
            row=row,
            column=col,
            sticky="ew",
            padx=12,
            pady=(pady_top, 0),
        )

        frame.grid_columnconfigure(
            0,
            weight=1,
        )

        button = tk.Button(
            frame,
            text=text,
            font=(theme.SANS, 9),
            bg=color,
            fg=text_color,
            activebackground=color,
            activeforeground=text_color,
            relief="flat",
            bd=0,
            pady=6,
            cursor="hand2",
            command=cmd,
        )
        if image:
            button.config(image=image, compound="left")

        button.grid(sticky="ew")

        return button

    @staticmethod
    def sidebar_label(parent, text, row):

        label = tk.Label(
            parent,
            text=text,
            font=(theme.MONO, 7),
            bg=theme.PANEL,
            fg=theme.TEXT_DIM,
            anchor="w",
            padx=12,
        )

        label.grid(
            row=row,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )

        return label

    @staticmethod
    def set_flag(flag_dot, flag_text, st):

        if st == 1:
            flag_dot.config(fg=theme.SUCCESS)

            flag_text.config(
                text="validated",
                fg=theme.SUCCESS,
            )

        elif st == 2:
            flag_dot.config(fg=theme.DANGER)

            flag_text.config(
                text="refused",
                fg=theme.DANGER,
            )

        else:
            flag_dot.config(fg=theme.WARNING)

            flag_text.config(
                text="unreviewed",
                fg=theme.WARNING,
            )

    def navigate(self, direction):
        if not self.state.files:
            return
        if direction == "NEXT":
            self.state.index = (self.state.index + 1) % len(self.state.files)

        elif direction == "PREV":
            self.state.index = (self.state.index - 1) % len(self.state.files)
        self.ui.sidebarleft.file_buttons[self.state.index].config(bg="#555")
        for j in range(len(self.state.files)):
            if not j == self.state.index:
                self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)
        file_path = os.path.join(
            self.state.path_dir,
            self.state.files[self.state.index],
        )
        self.file_manager.open_file(file_path)

    def update_display(self):
        if self.state.data is None:
            return
        if self.state.data.ndim == 2:
            img = self.state.data
        else:
            img = self.state.data[self.state.zoom]

        if self.state.has_prediction and self.state.prediction is not None:
            if self.state.prediction.ndim == 2:
                pred_img = self.state.prediction
            else:
                pred_img = self.state.prediction[self.state.zoom]
            display(
                self.ui.canvas,
                img,
                pred_img,
            )
        else:
            display(self.ui.canvas, img)

    def change_z(self, val):
        self.state.zoom = int(float(val))
        self.update_display()
