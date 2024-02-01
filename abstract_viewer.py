import os.path
from abc import abstractmethod
from datetime import datetime
from typing import Iterable


class Viewer:
    def __init__(self, input_path: str, start_time: str, stop_time: str):
        self.input_path = os.path.abspath(input_path)
        self.is_dir = os.path.isdir(input_path)
        self.start_time: datetime | None = datetime.fromisoformat(start_time) \
            if start_time else None

        self.stop_time: datetime | None = datetime.fromisoformat(stop_time) \
            if stop_time else None

    @abstractmethod
    def read(self, part: str | None = None) -> Iterable[str]:
        raise NotImplementedError()

