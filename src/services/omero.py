from omero.gateway import BlitzGateway

from src.ui import theme


class OmeroHandler:
    def __init__(self, ui, state):
        self.ui = ui
        self.state = state

    def connect(username, password, host, port):
        conn = BlitzGateway(username, password, host=host, port=port)
        response = conn.connect()
        if response:
            return conn
        else:
            return False

    def toggle(self, action):
        if action == "OMERO":
            if self.state and self.state.storage == "LOCAL":
                self.ui.topbar.local.config(bg=theme.MUTED)
                self.ui.topbar.omero.config(bg=theme.SUCCESS)
                self.state.storage = "OMERO"
        else:
            if self.state and self.state.storage == "OMERO":
                self.ui.topbar.local.config(bg=theme.DANGER)
                self.ui.topbar.omero.config(bg=theme.MUTED)
                self.state.storage = "LOCAL"
