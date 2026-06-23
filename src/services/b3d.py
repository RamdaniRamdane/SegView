import os
import tempfile
import threading
from tkinter import messagebox

from biom3d.preprocess import auto_config_preprocess
from biom3d.utils import shutil

from src.services.utils.biom_thread import BiomThreading
from src.ui.helpers.ui_utils import UIutils


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
        self.ui_uitils = UIutils()

    def run_prediction(self):

        print("pwd", os.getcwd())
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

        self.ui.sidebarleft.show_progressbar(
            self.ui.sidebarleft.progressbar, "Predition info"
        )

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

        self.ui.sidebarleft.show_progressbar(
            self.ui.sidebarleft.progressbar, "Finetuning info"
        )

        self.b3d_Threading._check("fine")

    def make_config_fine_tuning(self):
        needs = []
        msk_pth = ""
        img_pth = ""

        if not self.state.path_dir:
            needs.append("PATH_RAW")
        else:
            img_pth = self.state.path_dir

        if not self.state.path_log:
            needs.append("PATH_LOG")

        if not self.state.path_out_valide:
            test_if_path = os.path.join(os.path.dirname(self.state.path_out), "Valide")
            if os.path.isdir(test_if_path):
                if os.listdir(test_if_path):
                    self.state.path_out_valide = test_if_path
                    msk_pth = test_if_path
                    print("valide:", os.listdir(self.state.path_out_valide))
                    print("raw:", os.listdir(self.state.path_dir))
                    if len(os.listdir(self.state.path_out_valide)) < len(
                        os.listdir(self.state.path_dir)
                    ):
                        print("yas pas asse de valide par raport au raw")
                    else:
                        print("cest same pret pour le Finetuning")
                else:
                    needs.append("PATH_VALID")
            else:
                msk_pth = self.state.path_out_valide
        self.ui_uitils.open_popup(
            self.ui.root, needs, self.route.file_manager, self.state
        )
        if len(os.listdir(msk_pth)) < len(os.listdir(img_pth)):
            # creer un temp dir pour l utuliser
            tempdir = tempfile.TemporaryDirectory()
            for i in os.listdir(msk_pth):
                src = os.path.join(img_pth, i)
                shutil.copy2(os.path.join(img_pth, i), tempdir.name)
            img_pth = tempdir.name
        if not self.state.do_config:
            return

        self.state.config_path = auto_config_preprocess(
            img_path=img_pth,
            msk_path=msk_pth,
            num_classes=self.state.num_classes,
            config_dir="configs",
            base_config=None,
            ct_norm=False,
            desc="unet",
            max_dim=128,
            num_epochs=self.state.num_epochs,
            is_2d=False,
        )

        print(
            "Generated config:",
            self.state.config_path,
        )

        return self.state.config_path
