import os
import shutil

import tifffile

from src.ui_utils import UIutils


class FileManager:
    def __init__(self, ui):
        self.ui = ui

    def get_prediction(self, file_path, out_path):
        if not file_path or not out_path:
            return None, None, False
        filename = os.path.basename(file_path)
        pred_path = os.path.join(out_path, filename)
        if os.path.isfile(pred_path):
            self.ui.sidebarright.refuse_but.grid()
            self.ui.sidebarright.validate_but.grid()
            pred = tifffile.imread(pred_path)
            st = self.status(pred_path)
            self.ui.st = st
            UIutils.set_flag(
                self.ui.status.flag_sign,
                self.ui.status.flag_text,
                st,
            )
            return pred, pred_path, True
        UIutils.set_flag(
            self.ui.status.flag_sign,
            self.ui.status.flag_text,
            0,
        )
        return None, None, False

    def status(self, file_path):
        if not file_path:
            return 0
        parent = os.path.dirname(os.path.dirname(file_path))
        filename = os.path.basename(file_path)
        path_val = os.path.join(
            parent,
            "Valide",
            filename,
        )
        path_ref = os.path.join(
            parent,
            "NON-valide",
            filename,
        )
        path_out = os.path.join(self.ui.state.path_out, filename)
        print("path valide:", path_val)
        print("path refused:", path_ref)
        if os.path.isfile(path_val):
            return 1

        if os.path.isfile(path_ref):
            return 2
        if os.path.isfile(path_out):
            return 3
        return 4

    def save_choice(
        self,
        file_path,
        out_path,
        is_valid,
    ):
        if not file_path or not out_path:
            return
        filename = os.path.basename(file_path)
        parent = os.path.dirname(out_path)
        valid_path = os.path.join(parent, "Valide")
        self.ui.state.path_out_valide = valid_path
        print(
            "changed self.ui.state.path_out_valide line 71 src/file_manager.py : ",
            self.ui.state.path_out_valide,
        )
        invalid_path = os.path.join(parent, "NON-valide")
        os.makedirs(valid_path, exist_ok=True)
        os.makedirs(invalid_path, exist_ok=True)
        src = file_path
        if is_valid:
            dst = os.path.join(valid_path, filename)
            old = os.path.join(
                invalid_path,
                filename,
            )
        else:
            dst = os.path.join(invalid_path, filename)
            old = os.path.join(
                valid_path,
                filename,
            )
        if os.path.isfile(old):
            shutil.move(old, dst)
        else:
            shutil.copy(src, dst)
        self.ui.sidebarleft.update_color_text_file()
