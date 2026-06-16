from dataclasses import dataclass, field


@dataclass
class AppState:
    path_log: str = ""
    file_path: str = ""
    prediction_path_file: str = ""

    data: object = None
    prediction: object = None

    shape: tuple | None = None

    zoom: int = 0

    has_prediction: bool = False

    files: list = field(default_factory=list)
    files_out: list = field(default_factory=list)

    index: int = 0

    path_dir: str = ""
    path_out: str = ""
    path_out_valide: str = ""
    path_out_list: list = field(default_factory=list)
    predStarted = False

    edit_mode: bool = False
    edit_tool: str = ""
    edit_tool_size: int = 2

    edited: int = 0
    config_path: str = ""
    route: str = ""
    new_model_path: str = ""
