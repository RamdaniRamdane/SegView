import os
import threading
from tkinter import messagebox

from biom3d.preprocess import auto_config_preprocess

from src.services.utils.biom_thread import BiomThreading


class B3d:
    def __init__(self, state, ui, route):
        self.state = state
        self.ui = ui
        self.route = route
        self.b3d_Threading = BiomThreading(
            self.state,
            self.ui,
            self.route,
        )

    def run_prediction(self):
        if self.b3d_Threading.worker_fine and self.b3d_Threading.worker_fine.is_alive():
            messagebox.showwarning(
                "Busy",
                "Fine tuning is currently running.\nPlease wait until it finishes.",
            )
            return

        if self.b3d_Threading.worker_fine and self.b3d_Threading.worker_fine.is_alive():
            messagebox.showwarning(
                "Warning",
                "Fine tuning is currently running.",
            )
            return

        if not self.state.path_log:
            messagebox.showerror(
                "Error",
                "No model selected",
            )
            return

        if not self.state.path_dir:
            messagebox.showerror(
                "Error",
                "No input folder selected",
            )
            return

        if not self.state.path_out:
            messagebox.showerror(
                "Error",
                "No output folder selected",
            )
            return

        self.b3d_Threading.result = None

        self.state.predStarted = False
        self.state.files_out = []

        if os.path.exists(self.state.path_out):
            self.state.path_out_list = os.listdir(self.state.path_out)
        else:
            self.state.path_out_list = []

        self.b3d_Threading.worker_pred = threading.Thread(
            target=self.b3d_Threading._worker,
            args=("pred",),
            daemon=True,
        )

        self.b3d_Threading.worker_pred.start()

        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)

        self.b3d_Threading._check("pred")

    def run_fine_tuning(self):
        if self.b3d_Threading.worker_pred and self.b3d_Threading.worker_pred.is_alive():
            messagebox.showwarning(
                "Busy",
                "Prediction is currently running.\nPlease wait until it finishes.",
            )
            return
        if self.b3d_Threading.worker_fine and self.b3d_Threading.worker_fine.is_alive():
            messagebox.showwarning(
                "Warning",
                "Fine tuning already running.",
            )
            return

        self.make_config_fine_tuning()

        if not getattr(self.state, "config_path", None):
            return

        self.b3d_Threading.result = None

        self.b3d_Threading.worker_fine = threading.Thread(
            target=self.b3d_Threading._worker,
            args=("fine",),
            daemon=True,
        )

        self.b3d_Threading.worker_fine.start()

        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)

        self.b3d_Threading._check("fine")

    def make_config_fine_tuning(self):
        if (
            not self.state.path_dir
            or not self.state.path_out_valide
            or not self.state.path_log
        ):
            messagebox.showerror(
                "Error",
                "Make sure all folders are provided:\n\n"
                "1 - Raw images\n"
                "2 - Model\n"
                "3 - Valid masks (review step required)",
            )
            return

        self.state.config_path = auto_config_preprocess(
            img_path=self.state.path_dir,
            msk_path=self.state.path_out_valide,
            num_classes=1,
            config_dir="configs",
            base_config=None,
            ct_norm=False,
            desc="unet",
            max_dim=128,
            num_epochs=1,
            is_2d=False,
        )

        print(
            "Generated config:",
            self.state.config_path,
        )

        return self.state.config_path
