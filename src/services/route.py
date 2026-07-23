import src.ui.theme as theme


class Route:
    def __init__(self, ui, file_manager, edit_mode_utils, state):
        self.file_manager = file_manager
        self.edit_mode_utils = edit_mode_utils
        self.ui = ui
        self.state = state

    def route(self, route):
        if route == "prediction":
            self.go_to_prediction()
        elif route == "review":
            self.go_to_review()
        elif route == "fineTune":
            self.go_to_fine()

    def go_to_prediction(self):
        self.edit_mode_utils.toggle_tool("deactivate")
        self.state.route = "prediction"
        self.ui.topbar.pred_btn.config(bg="white", fg="black")
        self.ui.topbar.rev_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        self.ui.sidebarright.pred_container.grid()
        self.ui.sidebarright.get_folder_out.grid()
        self.ui.sidebarright.review_container.grid_remove()
        self.ui.sidebarright.fine_container.grid_remove()

    def go_to_review(self, path=None):
        self.state.route = "review"
        if path:
            self.file_manager.open_dir("PATH_PRED", path)
        #        self.ui.topbar.pred_btn.config(bg=theme.MUTED, fg=theme.TEXT_HI)
        #        self.ui.topbar.rev_btn.config(bg="white", fg="black")
        self.ui.sidebarright.review_container.grid()
        self.ui.sidebarright.pred_container.grid_remove()
        self.ui.sidebarright.fine_container.grid_remove()
        if not self.state.path_out:
            self.ui.sidebarright.correct_but.grid_remove()
