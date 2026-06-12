import threading
from tkinter import messagebox

from biom3d.preprocess import auto_config_preprocess

from src.services.utils.biom_thread import BiomThreading


class B3d:
    def __init__(self, state, ui, route):
        # init
        self.state = state
        self.ui = ui
        self.route = route
        self.b3d_Threading = BiomThreading(self.state, self.ui, self.route)

    def run_prediction(self):
        if not self.state.path_log:
            messagebox.showerror("Error", "No model selected")
            return
        if not self.state.path_dir:
            messagebox.showerror("Error", "No input folder selected")
            return
        # out = filedialog.askdirectory(title="Destination for model predictions")
        if not self.state.path_out:
            messagebox.showerror("Error", "No output folder selected")
            return
        # self.state.path_out = path_out
        self.worker = threading.Thread(
            target=self.b3d_Threading._worker, args=("pred",), daemon=True
        )
        self.worker.start()
        self.ui.sidebarleft.show_progressbar(self.ui.sidebarleft.progressbar)
        self.b3d_Threading._check("pred")

    def run_fine_tuning(self):
        # problem with windows a regler et a tester avec mac
        self.worker_fine = threading.Thread(
            target=self.b3d_Threading._worker, args=("fine",), daemon=True
        )
        self.worker_fine.start()
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
                "make sure you have all folders are uploaded : \n 1-Raw\n 2-Model\n 3-Valid masks",
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
        if self.state.config_path:
            self.ui.sidebarright.start_fine_tuning.grid()
            self.ui.sidebarright.make_config_file.config(
                bg="white", fg="black", text="Remake Config"
            )
