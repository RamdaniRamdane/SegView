import os
import tkinter as tk
from tkinter import filedialog

import biom3d


class Biom3d:
    def __init__(self):
        self.path_model = " "

    def get_model(self):
        path = filedialog.askopenfilename()
        if os.path.isfile(path):
            print(path)
            deb = biom3d.__doc__
            print(deb)
            self.preprocess()
        else:
            tk.messagebox.showerror(title="Not found", message="directory not found")

    def preprocess(
        self,
        img_dir="/home/rey/FRSTUDIES/stage/dev/ressources/biom3d/data/btcv/Training/img",
        mask_dir="/home/rey/FRSTUDIES/stage/dev/ressources/biom3d/data/btcv/Training/label",
        num_classes=255,
    ):
        print(img_dir)
        command = f"python -m biom3d.preprocess --img_dir {img_dir} --msk_dir {mask_dir} --num_classes {num_classes} --ct_norm"
        print(command)
        try:
            os.system(command)
        except Exception as e:
            print("problem", e)
