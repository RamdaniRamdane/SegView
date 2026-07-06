from dataclasses import dataclass, field

import numpy as np


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
    path_seg: str = ""
    path_out: str = ""
    path_out_valide: str = ""
    path_out_list: list = field(default_factory=list)
    predStarted = False

    edit_mode: bool = False
    edit_tool: str = ""
    edit_tool_size: int = 2
    brush_bit: int = 1

    edited: int = 0
    config_path: str = ""
    route: str = ""
    new_model_path: str = ""
    do_config: bool = False
    num_epochs: int = 1
    num_classes: int = 0
    out_name_folder: str = ""

    colors = []

    def __setattr__(self, name, value):
        debug = True
        old = getattr(self, name, "<UNSET>")

        changed = True

        if isinstance(old, np.ndarray) or isinstance(value, np.ndarray):
            changed = False
        else:
            changed = old != value

        if changed and debug:
            print(f"[STATE] {name}: {type(old)} -> {type(value)} -> {value}")

        super().__setattr__(name, value)
