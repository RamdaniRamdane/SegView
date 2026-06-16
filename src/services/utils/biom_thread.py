import os
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
                        message="Warning: No GPU detected , prediciton will slowdown\ncontinue anyway?",
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
                        return

                elif action == "fine":
                    messagebox.showerror(
                        title="Error",
                        message="NO GPU detected , fine tuning dont work on ur desktop",
                    )

            else:
                if action == "pred":
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

        except Exception as e:
            self.result = e

    def _check(self, action):
        print("check action=", action)
        print("self.worker_pred=", self.worker_pred)

        if self.worker_pred:
            print("self.worker_pred.is_alive=", self.worker_pred.is_alive())

        if action == "pred" and self.worker_pred and self.worker_pred.is_alive():
            try:
                print("self.state.predStarted:", self.state.predStarted)

                if not self.state.predStarted:
                    if os.path.exists(self.state.path_out):
                        out_list = os.listdir(self.state.path_out)
                    else:
                        out_list = []

                    execp = ["Valide", "NON-valide"]

                    diff = list(set(out_list) - set(self.state.path_out_list))

                    print("out fold:", diff)

                    if diff:
                        candidate = None

                        for el in diff:
                            if el not in execp:
                                candidate = el

                        if candidate:
                            new_path = os.path.join(self.state.path_out, candidate)

                            if os.path.isdir(new_path):
                                self.state.path_out = new_path
                                self.result = new_path
                                self.state.predStarted = True

                else:
                    files_out = os.listdir(self.state.path_out)

                    print("self.state.path_out = ", self.state.path_out)
                    print("files_out = ", files_out)
                    print("route = ", self.state.route)

                    if len(files_out) >= 1 and self.state.route != "review":
                        print("biom thread ligne 80", files_out)
                        self.route.go_to_review(self.state.path_out)

                    if len(files_out) > len(self.state.files_out):
                        test = self.ui.sidebarleft.progressbar["mode"]
                        if str(test) == "indeterminate":
                            self.ui.sidebarleft.toggl_determinate_mode(
                                self.ui.sidebarleft.progressbar
                            )

                        self.ui.sidebarleft.progressbar_handler(
                            self.ui.sidebarleft.progressbar,
                            "GROW",
                            len(self.state.files),
                        )

                        self.ui.sidebarleft.update_color_text_file()

                    self.state.files_out = os.listdir(self.state.path_out)

            except Exception as e:
                print("Erreur lors du listing:", e)

            self.ui.root.after(1000, lambda: self._check(action))
            return

        if self.result is None:
            self.ui.root.after(1000, lambda: self._check(action))
            return

        if isinstance(self.result, Exception) and action == "pred":
            messagebox.showerror("Error", str(self.result))
            return

        elif action == "pred":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)

            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar, "RESET"
            )

            messagebox.showinfo("Done", f"prediction saved here: {self.result}")

            self.state.predStarted = False
