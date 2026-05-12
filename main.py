# python version => python 3.10.14
import tkinter as tk

from app import SegViewApp
from src.ui import SegViewUI


def main():
    root = tk.Tk()

    ui = SegViewUI(root)
    app = SegViewApp(ui)
    app.bind_events()

    root.mainloop()


if __name__ == "__main__":
    main()
