import os
import tkinter as tk
from tkinter import messagebox

import src.ui.theme as theme
from src.services.image_utils import display


class UIutils:
    def __init__(self, ui=None, state=None, file_manager=None, app=None):
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
            padx=0,
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
        if self.state.edited > 0:
            user_input = messagebox.askokcancel(message="save changes ?")
            if user_input:
                self.file_manager.edit_mode_utils.save_changes()
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
        modal.title("Modal Pop-up")
        modal.configure(bg=theme.PANEL)
        modal.resizable(False, False)
        modal.transient(root)
        modal.grab_set()
        modal.focus_set()

        frame = tk.Frame(
            modal,
            bg=theme.CARD,
            bd=1,
            relief="solid",
            highlightbackground=theme.BORDER,
            highlightthickness=1,
        )
        frame.pack(padx=12, pady=12, fill="both", expand=True)

        for i in range(len(needs) + 2):
            frame.grid_rowconfigure(i, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        label = tk.Label(
            frame,
            text="number of opochs ?",
            bg=theme.CARD,
            fg=theme.TEXT_HI,
            font=(theme.MONO, 11),
        )
        label.grid(row=0, column=0)

        self.num_epochs_var = tk.IntVar(value=1)
        self.get_num_epoch = tk.Spinbox(
            frame, from_=1, to=1000, textvariable=self.num_epochs_var
        )
        self.get_num_epoch.grid(row=1, column=0)

        widgets = []
        k = 0
        print(needs)
        if "PATH_VALID" in needs:
            print(needs)
            warning_label = tk.Label(
                frame,
                text="you have to review before , you must have at least one valide mask",
                bg=theme.DANGER,
                fg="white",
                font=(theme.MONO, 13),
            )
            warning_label.grid(row=len(needs) + 3, column=0)
            needs.remove("PATH_VALID")
            print("after remove", needs)
        for i in needs:
            widgets.append(
                tk.Button(
                    frame,
                    text=i,
                    bg=theme.PANEL,
                    fg=theme.TEXT_HI,
                    relief="flat",
                    padx=12,
                    pady=6,
                )
            )
            widgets[k].config(
                command=lambda b=widgets[k]: file_manager.open_dir(action=i, btn=b),
            )
            widgets[k].grid(row=k + 2, column=0)
            k += 1

        def verrify():
            miss = []
            if not state.path_dir:
                miss.append("PATH_RAW")
            if not state.path_log:
                miss.append("PATH_LOG")
            if not state.path_out_valide:
                miss.append("PATH_VALID")
            if miss:
                mes = "\n".join(miss)
                text = f"missing elements: {mes}"
                messagebox.showerror(title="missing", message=text)
            else:
                state.do_config = True
                state.num_epochs = int(self.get_num_epoch.get())
                modal.destroy()

        confirm = tk.Button(
            frame,
            text="GO",
            bg=theme.SUCCESS,
            fg=theme.TEXT_HI,
            relief="flat",
            padx=12,
            pady=6,
            command=verrify,
        )
        confirm.grid(row=len(needs) + 7, column=0)

        root.update_idletasks()
        rw, rh = root.winfo_width(), root.winfo_height()
        rx, ry = root.winfo_rootx(), root.winfo_rooty()
        modal.update_idletasks()
        pw, ph = modal.winfo_reqwidth(), modal.winfo_reqheight()
        x = rx + max(0, (rw - pw) // 2)
        y = ry + max(0, (rh - ph) // 2)
        modal.geometry(f"+{x}+{y}")

        root.wait_window(modal)
        print("Modal dialog closed.")

    def change_z(self, val):
        self.state.zoom = int(float(val))
        self.update_display()
