import os.path
import struct
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Iterable, Tuple, IO

import generic
from generic import parse_duration, open_file


class Viewer:
    def __init__(
            self,
            input_path: str,
            start_time: str | None,
            stop_time: str | None,
            duration: str | None = None,
            read_flags: str | None = None
    ):
        self.read_flags: str = read_flags
        self.input_path = os.path.abspath(input_path)
        self.is_dir = os.path.isdir(input_path)
        self.start_time: datetime | None = datetime.fromisoformat(start_time) \
            if start_time else None

        self.stop_time: datetime | None = datetime.fromisoformat(stop_time) \
            if stop_time else None

        self.files = generic.get_files(self.input_path)
        start, end = self.get_file_times()
        self.start_times: dict[Tuple[str, str | None], datetime] = start
        self.end_times: dict[Tuple[str, str | None], datetime] = end
        self.ordered_files = list(
            sorted(
                (file for file in self.files if file in self.start_times),
                key=lambda file: self.start_times[file]
            )
        )

        if duration is not None:
            if not (self.start_time is None) ^ (self.stop_time is None):
                raise ValueError('Specify either start or stop time with duration.')

            duration_time = parse_duration(duration)
            if self.stop_time is not None:
                self.start_time = self.stop_time - duration_time

            if self.start_time is not None:
                self.stop_time = self.start_time + duration_time

    @abstractmethod
    def read_first_time(self, file: IO[bytes]) -> datetime:
        raise NotImplementedError()

    @abstractmethod
    def read_last_time(self, file: IO[bytes]) -> datetime:
        raise NotImplementedError()

    def find_file(self, time: datetime) -> int | None:
        index = 0

        for file, part in self.ordered_files:
            start = self.start_times[file, part]

            if start > time:
                continue

            index += 1

        return None if index >= len(self.ordered_files) else index

    def get_file_times(self) -> Tuple[
        dict[Tuple[str, str | None], datetime],
        dict[Tuple[str, str | None], datetime]
    ]:
        files = self.files
        start = dict()
        end = dict()

        for file_path, part in files:
            try:
                with open_file(file_path, part, read_flags=self.read_flags) as file:
                    start[file_path, part] = self.read_first_time(file)
            except struct.error:
                pass

        return start, end

    @abstractmethod
    def read(self, part: str | None = None) -> Iterable[str]:
        raise NotImplementedError()
