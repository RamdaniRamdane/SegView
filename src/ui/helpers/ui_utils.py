import os
import tkinter as tk
from tkinter import messagebox

import src.ui.theme as theme
from src.services.image_utils import display


class UIutils:
    def __init__(
        self, ui=None, state=None, file_manager=None, app=None, edit_mode_utils=None
    ):
        if ui:
            self.ui = ui
        if state:
            self.state = state
        if file_manager:
            self.file_manager = file_manager
        if app:
            self.app = app
        if edit_mode_utils:
            self.edit_mode_utils = edit_mode_utils

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
        colspn=None,
    ):

        frame = tk.Frame(
            parent,
            bg=theme.PANEL,
        )

        frame.grid(
            row=row,
            column=col,
            sticky="ew",
            padx=0,
            pady=(pady_top, 0),
            columnspan=colspn if colspn else 1,
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
        import inspect

        caller = inspect.stack()[1]

        print("=== DEBUG CALL set flag===")
        print(f"Appelée par : {caller.function}")
        print(f"Fichier     : {caller.filename}")
        print(f"Ligne       : {caller.lineno}")
        print(f"st        : {st}")
        print("=================")
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

        elif st == 3:
            flag_dot.config(fg=theme.WARNING)

            flag_text.config(
                text="unreviewed",
                fg=theme.WARNING,
            )
        else:
            flag_dot.config(fg=theme.TEXT_HI)
            flag_text.config(text="not yet predicted", fg=theme.TEXT_HI)

    def navigate(self, direction):
        if not self.state.files:
            return
        if self.state.edited > 0:
            user_input = messagebox.askokcancel(message="save changes ?")
            if user_input:
                self.file_manager.edit_mode_utils.save_changes()
            else:
                self.state.edited = 0
        if direction == "NEXT":
            self.state.index = (self.state.index + 1) % len(self.state.files)
            self.ui.sidebarleft.button_on_view(
                self.ui.sidebarleft.file_buttons[self.state.index]
            )

        elif direction == "PREV":
            self.state.index = (self.state.index - 1) % len(self.state.files)
            self.ui.sidebarleft.button_on_view(
                self.ui.sidebarleft.file_buttons[self.state.index]
            )
        self.ui.sidebarleft.file_buttons[self.state.index].config(bg="#555")
        for j in range(len(self.state.files)):
            if not j == self.state.index:
                self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)
                self.ui.sidebarleft.button_on_view(
                    self.ui.sidebarleft.file_buttons[self.state.index]
                )
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

    def open_popup(self, root, needs, file_manager, state):
        modal = tk.Toplevel(root)
        modal.title("Training Configuration")
        modal.configure(bg=theme.PANEL)
        modal.resizable(False, False)
        modal.transient(root)
        modal.grab_set()
        modal.focus_set()

        # ── Outer shell ──────────────────────────────────────────────────────────
        shell = tk.Frame(modal, bg=theme.PANEL, padx=20, pady=20)
        shell.pack(fill="both", expand=True)

        card = tk.Frame(
            shell,
            bg=theme.CARD,
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)
        card.grid_columnconfigure(0, weight=1)

        row = 0

        # ── Header bar ───────────────────────────────────────────────────────────
        header = tk.Frame(card, bg=theme.PANEL, padx=16, pady=12)
        header.grid(row=row, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        tk.Label(
            header,
            text="Training Setup",
            font=(theme.SANS, 13, "bold"),
            bg=theme.PANEL,
            fg=theme.TEXT_HI,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            header,
            text="Configure paths and epochs before running",
            font=(theme.MONO, 8),
            bg=theme.PANEL,
            fg=theme.TEXT_DIM,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        row += 1

        # ── Thin divider ─────────────────────────────────────────────────────────
        tk.Frame(card, bg=theme.BORDER, height=1).grid(row=row, column=0, sticky="ew")
        row += 1

        # ── Body padding frame ────────────────────────────────────────────────────
        body = tk.Frame(card, bg=theme.CARD, padx=16, pady=14)
        body.grid(row=row, column=0, sticky="ew")
        body.grid_columnconfigure(0, weight=1)
        row += 1

        body_row = 0

        # ── Warning banner (if data not reviewed) ────────────────────────────────
        if "Data_Not_Reviewed" in needs:
            warn_frame = tk.Frame(body, bg="#4a1a1a", padx=10, pady=8)
            warn_frame.grid(row=body_row, column=0, sticky="ew", pady=(0, 12))
            warn_frame.grid_columnconfigure(0, weight=1)

            tk.Label(
                warn_frame,
                text="⚠  No validated masks found",
                font=(theme.SANS, 9, "bold"),
                bg="#4a1a1a",
                fg="#ff8080",
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            tk.Label(
                warn_frame,
                text="Review and validate at least one mask before training.",
                font=(theme.MONO, 8),
                bg="#4a1a1a",
                fg="#cc6666",
                anchor="w",
                wraplength=280,
                justify="left",
            ).grid(row=1, column=0, sticky="w", pady=(3, 0))

            needs.remove("Data_Not_Reviewed")
            body_row += 1

        # ── Epochs field ─────────────────────────────────────────────────────────
        tk.Label(
            body,
            text="EPOCHS",
            font=(theme.MONO, 7),
            bg=theme.CARD,
            fg=theme.TEXT_DIM,
            anchor="w",
        ).grid(row=body_row, column=0, sticky="w")
        body_row += 1

        epoch_frame = tk.Frame(
            body, bg=theme.PANEL, highlightbackground=theme.BORDER, highlightthickness=1
        )
        epoch_frame.grid(row=body_row, column=0, sticky="ew", pady=(4, 14))
        epoch_frame.grid_columnconfigure(0, weight=1)

        self.num_epochs_var = tk.IntVar(value=10)
        self.get_num_epoch = tk.Spinbox(
            epoch_frame,
            from_=1,
            to=1000,
            textvariable=self.num_epochs_var,
            font=(theme.MONO, 10),
            bg=theme.PANEL,
            fg=theme.TEXT_HI,
            buttonbackground=theme.MUTED,
            relief="flat",
            bd=0,
            insertbackground=theme.TEXT_HI,
        )
        self.get_num_epoch.grid(row=0, column=0, sticky="ew", padx=8, pady=6)
        body_row += 1

        # ── Path buttons ─────────────────────────────────────────────────────────
        if needs:
            tk.Label(
                body,
                text="MISSING PATHS",
                font=(theme.MONO, 7),
                bg=theme.CARD,
                fg=theme.TEXT_DIM,
                anchor="w",
            ).grid(row=body_row, column=0, sticky="w")
            body_row += 1

        for i, need in enumerate(needs):
            btn_frame = tk.Frame(
                body,
                bg=theme.MUTED,
                highlightbackground=theme.BORDER,
                highlightthickness=1,
            )
            btn_frame.grid(row=body_row, column=0, sticky="ew", pady=(4, 0))
            btn_frame.grid_columnconfigure(1, weight=1)

            tk.Label(
                btn_frame,
                text="○",
                font=(theme.MONO, 9),
                bg=theme.MUTED,
                fg=theme.WARNING,
                padx=10,
            ).grid(row=0, column=0)

            btn = tk.Button(
                btn_frame,
                text=need,
                font=(theme.MONO, 8),
                bg=theme.MUTED,
                fg=theme.TEXT_HI,
                activebackground=theme.PANEL,
                activeforeground=theme.TEXT_HI,
                relief="flat",
                bd=0,
                pady=7,
                cursor="hand2",
                anchor="w",
            )
            btn.config(
                command=lambda b=btn, n=need: file_manager.open_dir(action=n, btn=b)
            )
            btn.grid(row=0, column=1, sticky="ew")
            body_row += 1

        # ── Divider before footer ─────────────────────────────────────────────────
        tk.Frame(card, bg=theme.BORDER, height=1).grid(row=row, column=0, sticky="ew")
        row += 1

        # ── Footer ────────────────────────────────────────────────────────────────
        footer = tk.Frame(card, bg=theme.CARD, padx=16, pady=12)
        footer.grid(row=row, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        def verrify():
            miss = []
            if not state.path_dir:
                miss.append("PATH_RAW")
            if not state.path_log:
                miss.append("PATH_LOG")
            if not state.path_out_valide:
                miss.append("No validated masks")
            if miss:
                messagebox.showerror(
                    title="Missing configuration",
                    message="The following are required:\n\n"
                    + "\n".join(f"  • {m}" for m in miss),
                )
            else:
                state.do_config = True
                state.num_epochs = int(self.get_num_epoch.get())
                modal.destroy()

        run_btn = tk.Button(
            footer,
            text="Start Training →",
            font=(theme.SANS, 10, "bold"),
            bg=theme.SUCCESS,
            fg=theme.TEXT_HI,
            activebackground=theme.SUCCESS,
            activeforeground=theme.TEXT_HI,
            relief="flat",
            bd=0,
            padx=20,
            pady=9,
            cursor="hand2",
            command=verrify,
        )
        run_btn.grid(row=0, column=0, sticky="e")

        # ── Center on parent ──────────────────────────────────────────────────────
        root.update_idletasks()
        rw, rh = root.winfo_width(), root.winfo_height()
        rx, ry = root.winfo_rootx(), root.winfo_rooty()
        modal.update_idletasks()
        pw, ph = modal.winfo_reqwidth(), modal.winfo_reqheight()
        modal.geometry(f"+{rx + max(0, (rw - pw) // 2)}+{ry + max(0, (rh - ph) // 2)}")

        root.wait_window(modal)

    def change_z(self, val):
        self.state.zoom = int(float(val))
        self.update_display()

    def sidebar_right_buttons_show(self, edit_mode_utils):
        if self.ui.st == 2:
            self.ui.sidebarright.correct_but.grid()
            self.ui.sidebarright.refuse_but.grid_remove()
            self.ui.sidebarright.validate_but.grid()
            self.ui.sidebarright.unreview_but.grid()
            self.ui.sidebarright.decision_label.grid()
        elif self.ui.st == 1:
            self.ui.sidebarright.correct_but.grid_remove()
            edit_mode_utils.toggle_tool("deactivate")
            self.ui.sidebarright.refuse_but.grid()
            self.ui.sidebarright.unreview_but.grid()
            self.ui.sidebarright.validate_but.grid_remove()
            self.ui.sidebarright.decision_label.grid()
        elif self.ui.st == 3:
            self.ui.sidebarright.correct_but.grid_remove()
            edit_mode_utils.toggle_tool("deactivate")
            self.ui.sidebarright.refuse_but.grid()
            self.ui.sidebarright.unreview_but.grid_remove()
            self.ui.sidebarright.validate_but.grid()
            self.ui.sidebarright.decision_label.grid()
        else:
            self.ui.sidebarright.correct_but.grid_remove()
            edit_mode_utils.toggle_tool("deactivate")
            self.ui.sidebarright.refuse_but.grid_remove()
            self.ui.sidebarright.unreview_but.grid_remove()
            self.ui.sidebarright.validate_but.grid_remove()
            self.ui.sidebarright.decision_label.grid_remove()
