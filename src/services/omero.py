import tkinter as tk
from tkinter import messagebox, ttk

from omero.gateway import BlitzGateway

from src.ui import theme


class OmeroHandler:
    def __init__(self, ui, state):
        self.ui = ui
        self.state = state

    def connect(self, username, password, host, port):
        try:
            conn = BlitzGateway(
                username,
                password,
                host=host,
                port=int(port),
            )

            if conn.connect():
                self.state.conn_omero = conn
                return True

            return False

        except Exception as e:
            messagebox.showerror("OMERO", str(e))
            return False

    def disconnect(self):
        if self.state.conn_omero is not None and self.state.conn_omero.isConnected():
            self.state.conn_omero.close()
            self.state.conn_omero = None

    def check_if_connected(self):
        if self.state.conn_omero is not None and self.state.conn_omero.isConnected():
            return True

        return False

    def popup_connect(self):

        if self.check_if_connected():
            return

        popup = tk.Toplevel(self.ui.root)
        popup.title("Connect to OMERO")
        popup.resizable(False, False)

        popup.configure(bg=theme.BG)

        frame = tk.Frame(
            popup,
            bg=theme.BG,
            padx=20,
            pady=20,
        )
        frame.pack(fill="both", expand=True)

        # Username
        tk.Label(
            frame,
            text="Username",
            bg=theme.BG,
            fg=theme.TEXT,
        ).grid(row=0, column=0, sticky="w", pady=5)

        username = ttk.Entry(frame, width=30)
        username.grid(row=0, column=1)

        # Password
        tk.Label(
            frame,
            text="Password",
            bg=theme.BG,
            fg=theme.TEXT,
        ).grid(row=1, column=0, sticky="w", pady=5)

        password = ttk.Entry(frame, show="*", width=30)
        password.grid(row=1, column=1)

        # Server
        tk.Label(
            frame,
            text="Server",
            bg=theme.BG,
            fg=theme.TEXT,
        ).grid(row=2, column=0, sticky="w", pady=5)

        host = ttk.Entry(frame, width=30)
        host.insert(0, "localhost")
        host.grid(row=2, column=1)

        # Port
        tk.Label(
            frame,
            text="Port",
            bg=theme.BG,
            fg=theme.TEXT,
        ).grid(row=3, column=0, sticky="w", pady=5)

        port = ttk.Entry(frame, width=30)
        port.insert(0, "4064")
        port.grid(row=3, column=1)

        def on_connect():
            ok = self.connect(
                username.get(),
                password.get(),
                host.get(),
                port.get(),
            )

            if ok:
                messagebox.showinfo("OMERO", "Connected successfully.")
                popup.destroy()
                self.toggle("OMERO")
            else:
                messagebox.showerror("OMERO", "Connection failed.")

        ttk.Button(
            frame,
            text="Connect",
            command=on_connect,
        ).grid(row=4, column=0, columnspan=2, pady=15)

    def toggle(self, action):

        if action == "OMERO":
            if self.state.storage == "LOCAL":
                if not self.check_if_connected():
                    self.popup_connect()

                    if not self.check_if_connected():
                        return

                self.ui.topbar.local.config(bg=theme.MUTED)
                self.ui.topbar.omero.config(bg=theme.SUCCESS)

                self.state.storage = "OMERO"

                # TODO:
                # Refresh browser with OMERO datasets
                # instead of local filesystem.

        else:
            if self.state.storage == "OMERO":
                self.ui.topbar.local.config(bg=theme.DANGER)
                self.ui.topbar.omero.config(bg=theme.MUTED)

                self.state.storage = "LOCAL"

                # TODO:
                # Restore local file browser.
