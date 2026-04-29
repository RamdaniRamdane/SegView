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
    def make_btn(parent, text, row, color=MUTED, text_color=TEXT, cmd=None, pady_top=8):
        f = tk.Frame(parent, bg=PANEL)
        f.grid(row=row, column=0, sticky="ew", padx=12, pady=(pady_top, 0))
        f.grid_columnconfigure(0, weight=1)

        b = tk.Button(
            f,
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
        b.grid(sticky="ew")
        return b

    def sidebar_label(parent, text, row):
        lbl = tk.Label(
            parent,
            text=text,
            font=(MONO, 7),
            bg=PANEL,
            fg=TEXT_DIM,
            anchor="w",
            padx=12,
        )
        lbl.grid(row=row, column=0, sticky="ew", pady=(14, 0))

    def set_flag(flgd, flgtxt, st):
        if st == 1:
            flgd.config(fg=SUCCESS)
            flgtxt.config(text="validated", fg=SUCCESS)
        elif st == 2:
            flgd.config(fg=DANGER)
            flgtxt.config(text="refused", fg=DANGER)
        else:
            flgd.config(fg=WARNING)
            flgtxt.config(text="unreviewed", fg=WARNING)
