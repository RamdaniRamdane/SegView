import os
import shutil
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

import tifffile
from omero.plugins.download import DownloadControl

import src.ui.theme as theme
from src.ui.helpers.ui_utils import UIutils


class FileManager:
    def __init__(self, ui=None, state=None, app=None, edit_mode_utils=None):
        if ui:
            self.ui = ui
        if state:
            self.state = state
        if app:
            self.app = app
        if ui and state:
            self.ui_handel = UIutils(ui, state)
        if edit_mode_utils:
            self.edit_mode_utils = edit_mode_utils

    def get_prediction(self, file_path, out_path):
        if not file_path or not out_path:
            return None, None, False
        filename = os.path.basename(file_path)
        pred_path = os.path.join(out_path, filename)
        if os.path.isfile(pred_path):
            self.ui.sidebarright.refuse_but.grid()
            self.ui.sidebarright.validate_but.grid()
            self.ui.sidebarright.unreview_but.grid()
            pred = tifffile.imread(pred_path)
            self.state.mask_dim = pred.ndim
            self.ui.topbar.show_info.config(
                text=f"Raw = {self.state.raw_dim if self.state.raw_dim else '--'}D, Mask = {self.state.mask_dim if self.state.mask_dim else '--'}D, Classes = {self.state.num_classes - 1 if self.state.num_classes else '--'} "
            )
            # show it
            self.status(pred_path)
            UIutils.set_flag(
                self.ui.status.flag_sign,
                self.ui.status.flag_text,
                self.ui.st,
            )

            self.ui_handel.sidebar_right_buttons_show(self.edit_mode_utils)

            return pred, pred_path, True
        else:
            self.ui.sidebarright.refuse_but.grid_remove()
            self.ui.sidebarright.validate_but.grid_remove()
            self.ui.sidebarright.unreview_but.grid_remove()
            self.ui.sidebarright.correct_but.grid_remove()
            self.ui.sidebarright.edit_frame.grid_remove()
        UIutils.set_flag(
            self.ui.status.flag_sign,
            self.ui.status.flag_text,
            0,
        )
        return None, None, False

    def status(self, file_path):
        if not file_path:
            self.ui.st = 0
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
        path_out = ""
        path_out = os.path.join(self.ui.state.path_out, filename)

        if os.path.isfile(path_val):
            self.ui.st = 1
            return 1

        elif os.path.isfile(path_ref):
            self.ui.st = 2
            return 2
        elif path_out and os.path.isfile(path_out):
            self.ui.st = 3
            return 3
        self.ui.st = 4
        return 4

    def save_choice(
        self,
        file_path,
        out_path,
        action,
    ):
        if not file_path or not out_path:
            return
        filename = os.path.basename(file_path)
        parent = os.path.dirname(out_path)
        valid_path = os.path.join(parent, "Valide")
        self.ui.state.path_out_valide = valid_path
        invalid_path = os.path.join(parent, "NON-valide")
        os.makedirs(valid_path, exist_ok=True)
        os.makedirs(invalid_path, exist_ok=True)
        src = os.path.join(out_path, filename)
        if self.state.edited > 0:
            user_input = messagebox.askokcancel(message="save changes ?")
            if user_input:
                self.edit_mode_utils.save_changes()
            else:
                self.state.edited = 0

        if action == "validate":
            dst = os.path.join(valid_path, filename)
            old = os.path.join(
                invalid_path,
                filename,
            )
        elif action == "refuse":
            dst = os.path.join(invalid_path, filename)
            old = os.path.join(
                valid_path,
                filename,
            )
        else:
            dst = ""
            old = ""
        if os.path.isfile(old):
            shutil.move(old, dst)
        elif dst:
            shutil.copy(src, dst)
        else:
            valide_file = os.path.join(valid_path, filename)
            invlid_file = os.path.join(invalid_path, filename)
            if os.path.isfile(valide_file):
                os.remove(valide_file)
            elif os.path.isfile(invlid_file):
                os.remove(invlid_file)
        self.ui.sidebarleft.update_color_text_file()
        valid_masks = os.listdir(self.state.path_out_valide)
        valid_len = len(valid_masks)
        if valid_len >= 2 and self.state.path_out and self.state.path_dir:
            self.ui.sidebarright.fine_btn.grid()
        else:
            self.ui.sidebarright.fine_btn.grid_remove()

    # TODO : refactor

    def handle_raw(self, path_dir, tif_files):
        self.state.path_dir = path_dir
        self.state.files = tif_files
        self.ui.sidebarleft.show_files_list()
        self.ui.set_state(self.state)
        for i in range(len(self.ui.sidebarleft.file_buttons)):
            self.ui.sidebarleft.file_buttons[i].config(
                command=lambda idx=i: self.sidebarleft_handl_file(idx)
            )
        self.ui.sidebarleft.update_color_text_file()
        self.ui.sidebarleft.file_buttons[0].config(bg="#555")
        for j in range(len(self.state.files)):
            if not j == 0:
                self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)
        self.ui.sidebarright.navigateFrame.grid()
        self.ui.sidebarright.next_btn.config(state=tk.NORMAL)
        self.ui.sidebarright.prev_btn.config(state=tk.NORMAL)
        self.ui.zoom_slider.config(state=tk.NORMAL)
        self.ui.sidebarright.get_model.config(
            state=tk.NORMAL,
            fg="white",
        )
        self.ui.sidebarright.btn.config(bg="white", fg="black")
        first_path = os.path.join(
            path_dir,
            tif_files[0],
        )
        if self.state.path_log and self.state.path_out:
            self.ui.sidebarright.pred.grid()

        self.open_file(first_path)

    def handle_pred(self, path_dir, btn=None):
        self.state.path_out = path_dir
        if os.listdir(self.state.path_out):
            self.ui.sidebarright.refuse_but.config(state=tk.NORMAL)
            self.ui.sidebarright.validate_but.config(state=tk.NORMAL)
        (
            self.state.prediction,
            self.state.prediction_path_file,
            self.state.has_prediction,
        ) = self.get_prediction(
            self.state.file_path,
            self.state.path_out,
        )

        self.ui.sidebarleft.update_color_text_file()
        self.ui.sidebarright.get_folder_out.config(bg=theme.PANEL, fg=theme.TEXT_HI)
        if btn:
            btn.config(bg="white", fg="white")
        if (
            self.state.path_out
            and os.path.isdir(self.state.path_out)
            and os.listdir(self.state.path_out)
        ):
            self.ui_handel.sidebar_right_buttons_show(self.edit_mode_utils)
        self.state.edit_mode = False
        self.ui.sidebarright.edit_frame.grid_remove()
        self.ui_handel.update_display()

    def handle_model(self, path_dir, btn=None):
        # handle PATH_LOG
        list_log = os.listdir(path_dir)
        if "model" in list_log:
            paths = os.path.join(path_dir, "model")
            list_model = os.listdir(paths)
            path_files = [f for f in list_model if f.lower().endswith(".pth")]
            if not path_files:
                messagebox.showerror(
                    title="No Model Provided",
                    message="check if the folder contain model/*.pth , please import correct model",
                )
                return
            self.state.path_log = path_dir
            self.ui.sidebarright.get_model.config(
                bg="white", fg="black", text="Change Model"
            )
            if btn:
                btn.config(bg="white", fg="black")
            if (
                self.state.path_out
                and self.state.path_log
                and not os.listdir(self.state.path_out)
            ):
                self.ui.sidebarright.pred.grid()
        else:
            messagebox.showerror(
                title="No Model Provided",
                message="check if the folder contain model/*.pth , please import correct model",
            )
            return

    def handle_segview_folder(self, path_dir, btn=None):
        self.state.path_seg = path_dir
        list_seg = os.listdir(path_dir)
        if "config.json" in list_seg:
            self.state.path_seg = path_dir
            # traitement selon config.json

            cfg = self.load_config(os.path.join(self.state.path_seg, "config.json"))

            pred_name_fold = cfg["pred"] if cfg else ""
            self.state.out_name_folder = pred_name_fold
            if os.path.isdir(os.path.join(self.state.path_seg, pred_name_fold)):
                list = os.listdir(os.path.join(self.state.path_seg, pred_name_fold))
                list_tif = [f for f in list if f.lower().endswith(".tif")]

                if not list_tif:
                    messagebox.showerror(
                        title="No Segview folder Provided",
                        message="check if the folder contain fold where there is masks please import correct fodler",
                    )
                    return
            else:
                messagebox.showerror(
                    title="No Segview folder Provided",
                    message="check if the folder contain fold where there is masks please import correct fodler",
                )
                return

            self.state.path_out = os.path.join(self.state.path_seg, pred_name_fold)
            self.ui.sidebarright.get_segview_folder.config(bg="white", fg="black")
            if os.listdir(self.state.path_out):
                self.ui.sidebarright.refuse_but.config(state=tk.NORMAL)
                self.ui.sidebarright.validate_but.config(state=tk.NORMAL)
            (
                self.state.prediction,
                self.state.prediction_path_file,
                self.state.has_prediction,
            ) = self.get_prediction(
                self.state.file_path,
                self.state.path_out,
            )

            self.ui.sidebarleft.update_color_text_file()
            self.ui.sidebarright.get_folder_out.config(bg=theme.PANEL, fg=theme.TEXT_HI)
            if btn:
                btn.config(bg="white", fg="white")
            if (
                self.state.path_out
                and os.path.isdir(self.state.path_out)
                and os.listdir(self.state.path_out)
            ):
                self.ui_handel.sidebar_right_buttons_show(self.edit_mode_utils)
            self.state.edit_mode = False
            self.ui.sidebarright.edit_frame.grid_remove()
            self.ui_handel.update_display()
        else:
            messagebox.showerror(
                title="No Segview folder Provided",
                message="check if the folder contain config.json , predictions  , please import correct fodler",
            )
            return

    def ask_omero_id(self):
        dialog = tk.Toplevel(self.ui.root)
        dialog.title("Open from OMERO")
        dialog.geometry("320x170")
        dialog.resizable(False, False)

        dialog.transient(self.ui.root)
        dialog.grab_set()

        result = None

        ttk.Label(dialog, text="Object type").pack(padx=15, pady=(15, 5), anchor="w")

        object_type = tk.StringVar(value="Dataset")

        selector = ttk.Combobox(
            dialog,
            textvariable=object_type,
            values=["Dataset", "File"],
            state="readonly",
        )
        selector.pack(fill="x", padx=15)

        ttk.Label(dialog, text="Object ID").pack(padx=15, pady=(10, 5), anchor="w")

        entry = ttk.Entry(dialog)
        entry.pack(fill="x", padx=15)
        entry.focus()

        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill="x", padx=15, pady=15)

        def ok():
            nonlocal result

            try:
                print("in try")
                obj_id = int(entry.get())
                result = (object_type.get(), obj_id)
                dialog.destroy()
            except ValueError:
                entry.selection_range(0, tk.END)
                entry.focus()

        def cancel():
            dialog.destroy()

        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side="right")
        ttk.Button(button_frame, text="OK", command=ok).pack(side="right", padx=5)

        dialog.bind("<Return>", lambda e: ok())
        dialog.bind("<Escape>", lambda e: cancel())

        self.ui.root.wait_window(dialog)

        return result

    def ls_omero(self, obj):
        contents = []

        if obj.OMERO_CLASS == "Project":
            contents = [ds.getName() for ds in obj.listChildren()]

        elif obj.OMERO_CLASS == "Dataset":
            contents = [img.getName() for img in obj.listChildren()]

        elif obj.OMERO_CLASS == "Image":
            contents = [
                ann.getFile().getName()
                for ann in obj.listAnnotations()
                if ann.OMERO_CLASS == "FileAnnotation"
            ]

        elif obj.OMERO_CLASS == "OriginalFile":
            contents = [obj.getName()]

        print(contents)
        return contents

    def get_working_directory(self):
        """
        Return the current working directory.
        Ask the user if none is configured.
        """

        if self.state.omero_dir and os.path.isdir(self.state.omero_dir):
            return self.state.omero_dir

        workdir = filedialog.askdirectory(title="Choose a working directory")

        if not workdir:
            return None

        self.state.omero_dir = workdir
        return workdir

    def get_download_control(self):
        """
        Return OMERO DownloadControl.
        """

        return DownloadControl()

    def download_dataset(self, dataset, destination):
        """
        Download an OMERO Dataset using its original files.
        """

        os.makedirs(destination, exist_ok=True)

        dc = self.get_download_control()

        dataset_dir = os.path.join(destination, dataset.getName())

        os.makedirs(dataset_dir, exist_ok=True)

        print("Downloading Dataset:", dataset.getName())

        for image in dataset.listChildren():
            fileset = image.getFileset()

            if fileset is None:
                print("No fileset for:", image.getName())
                continue

            print("Downloading image:", image.getName())

            dc.download_fileset(self.state.conn_omero, fileset, dataset_dir)

        return dataset_dir

    def download_file(self, file_obj, destination):

        os.makedirs(destination, exist_ok=True)

        filename = file_obj.getName()

        output = os.path.join(destination, filename)

        print("Downloading:", filename)

        store = self.state.conn_omero.c.sf.createRawFileStore()

        try:
            store.setFileId(file_obj.getId())

            size = file_obj.getSize()

            with open(output, "wb") as f:
                offset = 0

                while offset < size:
                    block = store.read(offset, 1024 * 1024)

                    f.write(block)

                    offset += len(block)

        finally:
            store.close()

        print("Saved:", output)

        return output

    def download_omero_object(self, obj):

        destination = self.get_working_directory()

        if destination is None:
            return None

        try:
            if obj.OMERO_CLASS == "Dataset":
                return self.download_dataset(obj, destination)

            elif obj.OMERO_CLASS == "OriginalFile":
                return self.download_file(obj, destination)

            else:
                messagebox.showerror("OMERO", f"Unsupported: {obj.OMERO_CLASS}")

                return None

        except Exception as e:
            messagebox.showerror("Download failed", str(e))

            return None

    def get_dir(self, action):
        dest = ""
        if (
            self.state.storage == "OMERO"
            and self.state.conn_omero is not None
            and self.state.conn_omero.isConnected()
        ):
            result = self.ask_omero_id()
            print(result)
            if result is None:
                return None

            obj_type, obj_id = result

            # Conversion du nom du sélecteur vers le type OMERO
            type_map = {
                "Project": "Project",
                "Dataset": "Dataset",
                "File": "OriginalFile",  # ou "FileAnnotation" selon ce que tu veux ouvrir
            }

            omero_type = type_map[obj_type]

            obj = self.state.conn_omero.getObject(omero_type, obj_id)

            if obj is None:
                print(f"{omero_type} {obj_id} not found.")
                return None

            print(f"Found {omero_type}")
            print("ID:", obj.getId())
            if hasattr(obj, "getName"):
                print("Name:", obj.getName())
            content = self.ls_omero(obj)
            if action == "PATH_RAW" or action == "PATH_PRED":
                for i in content:
                    if not i.endswith("tif"):
                        return None
                print("Telechargement ..")
                dest = self.download_omero_object(obj)

            return dest if dest else ""

        else:
            p = filedialog.askdirectory()
            return p

    def open_dir(self, action, path_dir=None, btn=None):
        if not path_dir:
            path_dir = self.get_dir(action)
        if not path_dir:
            return
        if not os.path.isdir(path_dir):
            messagebox.showerror(
                title="Not found",
                message="directory not found",
            )
            return
        if action in ["PATH_RAW", "PATH_PRED", "PATH_VALID"]:
            files = os.listdir(path_dir)

            tif_files = [f for f in files if f.lower().endswith(".tif")]

            if not tif_files:
                messagebox.showerror(
                    title="Not found",
                    message="no tif file in this dir",
                )
                return
            if action == "PATH_RAW":
                self.handle_raw(path_dir=path_dir, tif_files=tif_files)

            elif action == "PATH_PRED":
                self.handle_pred(path_dir=path_dir, btn=btn)

        else:
            if action == "PATH_LOG":
                self.handle_model(path_dir=path_dir, btn=btn)

            elif action == "PATH_SEG":
                self.handle_segview_folder(path_dir=path_dir, btn=btn)

    def open_file(self, path):
        if not os.path.isfile(path):
            messagebox.showerror(
                title="Not found",
                message="file not found",
            )
            return
        self.state.file_path = path
        display_path = path if len(path) <= 72 else "..." + path[-70:]
        self.ui.path_label.config(
            text=display_path,
            fg="white",
        )
        self.state.data = tifffile.imread(path)
        self.state.shape = self.state.data.shape
        self.state.raw_dim = self.state.data.ndim

        self.ui.topbar.show_info.config(
            text=f"Raw = {self.state.raw_dim if self.state.raw_dim else '--'}D, Mask = {self.state.mask_dim if self.state.mask_dim else '--'}D, Classes = {self.state.num_classes - 1 if self.state.num_classes else '--'} "
        )
        # show it
        if self.state.data.ndim > 2:
            self.state.zoom = int(self.state.shape[0] / 2)
        else:
            self.state.zoom = 0
        self.ui.status.info_label.config(
            text=f"shape={self.state.shape} dtype={self.state.data.dtype}"
        )
        if self.state.data.ndim > 2:
            self.ui.zoom_slider.config(to=self.state.shape[0] - 1)
            self.ui.zoom_slider.set(self.state.zoom)
        else:
            self.ui.zoom_slider.config(to=0)

        (
            self.state.prediction,
            self.state.prediction_path_file,
            self.state.has_prediction,
        ) = self.get_prediction(
            self.state.file_path,
            self.state.path_out,
        )

        self.ui_handel.sidebar_right_buttons_show(self.edit_mode_utils)
        if self.state.edited:
            self.ui.sidebarright.changes_state_label.grid_remove()
        else:
            self.ui.sidebarright.changes_state_label.grid()

        self.ui.sidebarleft.update_color_text_file()
        self.state.edit_mode = False
        self.ui.sidebarright.edit_frame.grid_remove()
        self.ui_handel.update_display()

    def sidebarleft_handl_file(self, i):
        if self.state.edited > 0:
            user_input = messagebox.askokcancel(message="save changes ?")
            if user_input:
                self.edit_mode_utils.save_changes()
            else:
                self.state.edited = 0
        self.state.index = i
        filename = self.state.files[i]
        path = os.path.join(self.state.path_dir, filename)
        self.open_file(path)
        self.ui.sidebarleft.file_buttons[i].config(bg="#555")
        self.ui.sidebarleft.button_on_view(self.ui.sidebarleft.file_buttons[i])
        for j in range(len(self.state.files)):
            if not j == i:
                self.ui.sidebarleft.file_buttons[j].config(bg=theme.PANEL)

    def create_segview_out_folder(self, base_dir):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_%f")
        folder_name = f"SegView_out_{timestamp}"
        path = os.path.join(base_dir, folder_name)
        os.makedirs(path, exist_ok=False)
        return path

    def get_out_path(self):
        out = filedialog.askdirectory(title="Destination for model predictions")
        if not out:
            return
        self.state.path_out = out
        self.ui.st = 4
        if self.state.path_log and self.state.path_dir:
            self.ui.sidebarright.pred.grid()
        self.ui.sidebarright.get_folder_out.config(bg="white", fg="black")
        self.ui_handel.update_display()
        return out

    def save(self, action):
        if not self.state.file_path:
            return
        self.save_choice(
            self.state.file_path,
            self.state.path_out,
            action,
        )
        if action == "validate":
            self.ui.st = 1
        elif action == "refuse":
            self.ui.st = 2
            self.state.edit_mode = False
        else:
            self.ui.st = 3
            self.state.edit_mode = False

        UIutils.set_flag(
            self.ui.status.flag_sign,
            self.ui.status.flag_text,
            self.ui.st,
        )
        self.ui_handel.sidebar_right_buttons_show(self.edit_mode_utils)
        if self.state.edited:
            self.ui.sidebarright.changes_state_label.grid_remove()
        else:
            self.ui.sidebarright.changes_state_label.grid()

        self.ui.sidebarleft.update_color_text_file()

    def write_config(self, folder_path, extra=None):
        import json

        path = os.path.split(folder_path)
        filename = path[-1]

        config = {
            "app": "SegView",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "folder": filename,
            "version": "1.0",
        }

        if extra:
            config.update(extra)

        config_path = os.path.join(folder_path, "config.json")

        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        return config_path

    def load_config(self, config_path):
        import json

        if not os.path.isfile(config_path):
            return None

        with open(config_path, "r") as f:
            return json.load(f)
