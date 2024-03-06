import copy
import re
from datetime import datetime
from typing import Iterable, IO

from abstract_viewer import Viewer


class LogViewerDataPoint:
    def __init__(
            self,
            host: str,
            time: datetime,
            path: str,
            code: int,
            size: int
    ):
        self.host = host
        self.time = time
        self.path = path
        self.code = code
        self.size = size

    def to_dict(self):
        data = copy.deepcopy(self.__dict__)
        data['time'] = self.time.isoformat()
        return data


class LogViewer(Viewer):
    LOG_LINE_REGEX = re.compile(
        r'([\w\-.]+) - - \[([\w\/:\s-]+)] "(.*)" (\d+) (\w+)')

    def __init__(
            self,
            input_path: str,
            start_time: str | None,
            stop_time: str | None,
            duration: str | None = None
    ):
        super().__init__(input_path, start_time, stop_time, duration)

    def read_last_time(self, file: IO[bytes]) -> datetime | None:
        last_line = None
        with open(self.input_path) as file:
            while line := file.readline():
                last_line = line

        if last_line is None:
            return None

        return self._convert_to_datapoint(last_line)

    def read(self, part: str | None = None) -> Iterable[str]:
        with open(self.input_path) as file:
            while line := file.readline():
                dp = self._convert_to_datapoint(line)
                if dp is None:
                    continue

                time = dp.time
                if self.start_time is not None and time < self.start_time:
                    continue

                if self.stop_time is not None and time > self.stop_time:
                    break

                yield dp.to_dict()

    @staticmethod
    def _convert_to_datapoint(log_line: str) -> LogViewerDataPoint | None:
        match = LogViewer.LOG_LINE_REGEX.match(log_line)
        if not match:
            return None

        host = str(match.group(1))
        time = str(match.group(2))
        path = str(match.group(3))
        code = int(match.group(4))
        size = int(match.group(5))

        time = datetime.strptime(time, '%d/%b/%Y:%H:%M:%S %z')

        return LogViewerDataPoint(
            host=host,
            time=time,
            path=path,
            code=code,
            size=size
        )

    def read_first_time(self, file: IO[bytes]) -> datetime | None:
        line = file.readline()
        if line is None:
            return None

        return self._convert_to_datapoint(line).time
