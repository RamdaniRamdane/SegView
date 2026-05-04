import os
import tkinter as tk
from tkinter import filedialog


class Biom3d:
    def __init__(self):
        self.path_model = " "

    def get_model(self):
        path = filedialog.askopenfilename()
        if os.path.isfile(path):
            print(path)
        else:
            tk.messagebox.showerror(title="Not found", message="directory not found")
