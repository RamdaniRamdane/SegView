import os
import shutil
from tkinter import messagebox

import torch
from biom3d.pred import pred
from biom3d.train import train


class BiomThreading:
    def __init__(self, state, ui, route):
        self.state = state
        self.ui = ui
        self.route = route

        self.worker_pred = None
        self.worker_fine = None
        self.result = None

    def _worker(self, action):
        try:
            if not torch.cuda.is_available() and not torch.backends.mps.is_available():
                if action == "pred":
                    user_response = messagebox.askquestion(
                        title="Warning",
                        message="Warning: No GPU detected, prediction will be slow.\nContinue anyway?",
                        type="yesno",
                    )

                    if user_response == "yes":
                        self.result = pred(
                            log=self.state.path_log,
                            path_in=self.state.path_dir,
                            path_out=self.state.path_out,
                            skip_preprocessing=False,
                        )
                    else:
                        self.result = "CANCELLED"
                        return

                elif action == "fine":
                    self.result = "NO_GPU"

                    messagebox.showerror(
                        title="Error",
                        message="No GPU detected, fine tuning is disabled.",
                    )
                    return

            else:
                if action == "pred":
                    print("pwd", os.getcwd())
                    self.result = pred(
                        log=self.state.path_log,
                        path_in=self.state.path_dir,
                        path_out=self.state.path_out,
                        skip_preprocessing=False,
                    )

                elif action == "fine":
                    self.state.new_model_path = train(
                        config=self.state.config_path,
                        path=self.state.path_log,
                    )

                    self.result = self.state.new_model_path.model_dir
                    out_fine_path = os.path.join(
                        self.state.path_out, "..", "fine_tuned_models_out"
                    )
                    if not os.path.isdir(out_fine_path):
                        os.mkdir(out_fine_path)
                    if self.result:
                        print("result", self.result)
                        self.result = os.path.join(os.getcwd(), self.result)
                        shutil.copytree(self.result, out_fine_path)
                    # ou mettre nouveau model ? si on le met dans out on a peur que le user fait une prediction et le supprime , donc je pense a faire un nouveau dossier

        except Exception as e:
            self.result = e

    def _check(self, action):
        if action == "pred" and self.worker_pred and self.worker_pred.is_alive():
            try:
                if not self.state.predStarted:
                    if os.path.exists(self.state.path_out):
                        out_list = os.listdir(self.state.path_out)
                    else:
                        out_list = []

                    execp = ["Valide", "NON-valide"]

                    diff = list(set(out_list) - set(self.state.path_out_list))

                    if diff:
                        candidate = None

                        for el in diff:
                            if el not in execp:
                                candidate = el

                        if candidate:
                            new_path = os.path.join(
                                self.state.path_out,
                                candidate,
                            )

                            if os.path.isdir(new_path):
                                self.state.path_out = new_path
                                self.result = new_path
                                self.state.predStarted = True

                else:
                    files_out = os.listdir(self.state.path_out)

                    if len(files_out) >= 1 and self.state.route != "review":
                        self.route.go_to_review(self.state.path_out)

                    if len(files_out) > len(self.state.files_out):
                        mode = self.ui.sidebarleft.progressbar["mode"]

                        if str(mode) == "indeterminate":
                            self.ui.sidebarleft.toggl_determinate_mode(
                                self.ui.sidebarleft.progressbar
                            )

                        self.ui.sidebarleft.progressbar_handler(
                            self.ui.sidebarleft.progressbar,
                            "GROW",
                            len(self.state.files),
                        )

                        self.ui.sidebarleft.update_color_text_file()

                    self.state.files_out = files_out

            except Exception as e:
                print("Listing error:", e)

            self.ui.root.after(
                1000,
                lambda: self._check(action),
            )
            return

        if self.result is None:
            self.ui.root.after(
                1000,
                lambda: self._check(action),
            )
            return

        if self.result == "CANCELLED":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar,
                "RESET",
            )

            self.state.predStarted = False
            self.worker_pred = None

            return
        if self.result == "NO_GPU":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar,
                "RESET",
            )

            self.worker_fine = None
            return

        if isinstance(self.result, Exception):
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar,
                "RESET",
            )

            messagebox.showerror(
                "Error",
                str(self.result),
            )

            self.worker_pred = None
            self.worker_fine = None

            return

        if action == "pred":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar,
                "RESET",
            )

            self.ui.sidebarleft.update_color_text_file()

            messagebox.showinfo(
                "Done",
                f"Prediction saved here:\n{self.result}",
            )

            self.state.predStarted = False
            self.worker_pred = None

        elif action == "fine":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar,
                "RESET",
            )

            self.worker_fine = None

            messagebox.showinfo(
                "Done",
                "Fine tuning completed.",
            )
