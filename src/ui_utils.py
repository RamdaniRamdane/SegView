import tkinter as tk

import theme


class UIutils:
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
