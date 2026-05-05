import os
import shutil

import tifffile

from ui_utils import UIutils


class FileManager:
    def __init__(self, ui):
        self.ui = ui

    def get_prediction(self, file_path):
        parts = file_path.split("/")
        parts[-2] = "fg_out"
        pred_path = "/".join(parts)

        if os.path.isfile(pred_path):
            self.ui.refuse_but.grid()
            self.ui.validate_but.grid()
            pred = tifffile.imread(pred_path)
            st = self.status(pred_path)
            UIutils.set_flag(self.ui.flag_sign, self.ui.flag_text, st)
            return pred, True
        else:
            UIutils.set_flag(self.ui.flag_sign, self.ui.flag_text, 0)
            return None, False

    def status(self, file_path):
        if file_path:
            path = file_path.split("/")
            path_val = path.copy()
            path_ref = path.copy()

            path_val[-2] = "Valide"
            path_ref[-2] = "NON-valide"

            path_val = "/".join(path_val)
            path_ref = "/".join(path_ref)

            if os.path.isfile(path_val):
                return 1
            elif os.path.isfile(path_ref):
                return 2
            else:
                return 3
        return 0

    def save_choice(self, file_path, is_valid):
        if not file_path:
            return

        path = file_path.split("/")
        filename = path[-1]
        path.pop()

        valid_path = path.copy()
        invalid_path = path.copy()

        valid_path[-1] = "Valide"
        invalid_path[-1] = "NON-valide"

        valid_path = "/".join(valid_path)
        invalid_path = "/".join(invalid_path)

        os.makedirs(valid_path, exist_ok=True)
        os.makedirs(invalid_path, exist_ok=True)

        if is_valid:
            if os.path.isfile(invalid_path + "/" + filename):
                shutil.move(invalid_path + "/" + filename, valid_path)
            else:
                shutil.copy(file_path, os.path.join(valid_path, filename))
        else:
            if os.path.isfile(valid_path + "/" + filename):
                shutil.move(valid_path + "/" + filename, invalid_path)
            else:
                shutil.copy(file_path, os.path.join(invalid_path, filename))
