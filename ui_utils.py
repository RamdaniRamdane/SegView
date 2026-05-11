import tkinter as tk

BG = "#0e0e0f"
PANEL = "#141416"
BORDER = "#222226"

MUTED = "#3a3a40"

TEXT_DIM = "#555560"
TEXT = "#c8c8d0"
TEXT_HI = "#e8e8f0"

ACCENT = "#4a9eff"

DANGER = "#d94f4f"
SUCCESS = "#3dab6e"
WARNING = "#c09030"

MONO = "Courier"
SANS = "Helvetica"


class UIutils:
    @staticmethod
    def make_btn(
        parent,
        text,
        row,
        color=MUTED,
        text_color=TEXT,
        cmd=None,
        pady_top=8,
        col=0,
        image=None,
    ):

        frame = tk.Frame(
            parent,
            bg=PANEL,
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
            font=(SANS, 9),
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
            font=(MONO, 7),
            bg=PANEL,
            fg=TEXT_DIM,
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
            flag_dot.config(fg=SUCCESS)

            flag_text.config(
                text="validated",
                fg=SUCCESS,
            )

        elif st == 2:
            flag_dot.config(fg=DANGER)

            flag_text.config(
                text="refused",
                fg=DANGER,
            )

        else:
            flag_dot.config(fg=WARNING)

            flag_text.config(
                text="unreviewed",
                fg=WARNING,
            )
