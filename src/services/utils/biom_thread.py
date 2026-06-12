import os
from tkinter import messagebox

import torch
from biom3d.pred import pred
from biom3d.train import train


class BiomThreading:
    def __init__(self, state, ui, route):
        # init
        self.state = state
        self.ui = ui
        self.route = route

        self.worker_pred = None
        self.worker_fine = None

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
        if self.worker_pred and self.worker_pred.is_alive() and action == "pred":
            try:
                if not self.state.predStarted:
                    out_list = os.listdir(self.state.path_out)
                    execp = ["Valide", "NON-valide"]
                    diff = list(set(out_list) - set(self.state.path_out_list))
                    if diff:
                        candidate = diff[0]
                        for el in diff:
                            if el not in execp:
                                candidate = el
                        new_path = os.path.join(self.state.path_out, candidate)
                        if os.path.isdir(new_path):
                            self.state.path_out = new_path
                            self.result = new_path
                            self.state.predStarted = True
                else:
                    files_out = os.listdir(self.state.path_out)
                    if len(files_out) >= 1 and not self.state.route == "review":
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

        if isinstance(self.result, Exception) and action == "pred":
            messagebox.showerror("Error", str(self.state.path_out))
            print(Exception)
            print("result", self.result)
        elif not isinstance(self.result, Exception) and action == "pred":
            self.ui.sidebarleft.remove_progressbar(self.ui.sidebarleft.progressbar)
            self.ui.sidebarleft.progressbar_handler(
                self.ui.sidebarleft.progressbar, "RESET"
            )
            messagebox.showinfo("Done", f"prediction saved here: {self.result}")
            self.state.predStarted = False
