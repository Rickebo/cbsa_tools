import os.path
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Iterable

from generic import parse_duration


class Viewer:
    def __init__(
            self,
            input_path: str,
            start_time: str | None,
            stop_time: str | None,
            duration: str | None = None
    ):
        self.input_path = os.path.abspath(input_path)
        self.is_dir = os.path.isdir(input_path)
        self.start_time: datetime | None = datetime.fromisoformat(start_time) \
            if start_time else None

        self.stop_time: datetime | None = datetime.fromisoformat(stop_time) \
            if stop_time else None

        if duration is not None:
            if not (self.start_time is None) ^ (self.stop_time is None):
                raise ValueError('Specify either start or stop time with duration.')

            duration_time = parse_duration(duration)
            if self.stop_time is not None:
                self.start_time = self.stop_time - duration_time

            if self.start_time is not None:
                self.stop_time = self.start_time + duration_time

    @abstractmethod
    def read(self, part: str | None = None) -> Iterable[str]:
        raise NotImplementedError()
