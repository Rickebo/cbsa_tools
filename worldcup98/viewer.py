import json
import struct
from datetime import datetime
from typing import Iterable, IO, Any

import generic
from abstract_viewer import Viewer


class WorldCup98DataPoint:
    METHOD_NAMES = [
        'GET',
        'HEAD',
        'POST',
        'PUT',
        'DELETE',
        'TRACE',
        'OPTIONS',
        'CONNECT'
    ]

    STATUS_CODES = [
        100,
        101,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        300,
        301,
        302,
        303,
        304,
        305,
        400,
        401,
        402,
        403,
        404,
        405,
        406,
        407,
        408,
        409,
        410,
        411,
        412,
        413,
        414,
        415,
        500,
        501,
        502,
        503,
        504,
        505
    ]

    TYPES = [
        'HTML',
        'IMAGE',
        'AUDIO',
        'VIDEO',
        'JAVA',
        'FORMATTED',
        'DYNAMIC',
        'TEXT',
        'COMPRESSED',
        'PROGRAMS',
        'DIRECTORY',
        'ICL',
        'OTHER_TYPES',
    ]

    def __init__(
            self,
            time: int,
            client_id: int,
            object_id: int,
            size: int,
            method: int,
            status: int,
            type: int,
            server: int
    ):
        self.time: str = datetime.fromtimestamp(time).isoformat()
        self.client_id: int = client_id
        self.object_id: int = object_id
        self.size: int = int(size)
        self.method: str = self.get_safe(
            int.from_bytes(method, 'big'),
            self.METHOD_NAMES,
            'unknown'
        )

        status_field = int.from_bytes(status, 'big')
        self.status: int = self.get_safe(
            status_field & 0b111111,
            self.STATUS_CODES,
            0
        )
        self.http_version = status_field >> 6
        self.type: str = self.get_safe(
            int.from_bytes(type, 'big'),
            self.TYPES,
            'unknown'
        )
        server_field = int.from_bytes(server, 'big')
        self.server_id: int = server_field & 0b11111
        self.server_region: int = server_field >> 5

    @staticmethod
    def get_safe(index: int, from_list: list, default: Any) -> Any:
        if index < 0 or index >= len(from_list):
            return default

        return from_list[index]

    def to_dict(self):
        return self.__dict__


class WorldCup98Viewer(Viewer):
    def __init__(
            self,
            input_path: str,
            start_time: str | None,
            stop_time: str | None,
            duration: str | None = None
    ):
        super().__init__(input_path, start_time, stop_time, duration)

    def read_time(self, file: IO[bytes]):
        time_int = struct.unpack('>I', file.read(4))
        return datetime.fromtimestamp(time_int[0])

    def read_first_time(self, file: IO[bytes]) -> datetime:
        file.seek(0)
        return self.read_time(file)

    def read_last_time(self, file: IO[bytes]) -> datetime:
        file.seek(-5, 2)
        return self.read_time(file)

    def get_parts(self):
        start_file = self.find_file(self.start_time)
        end_file = self.find_file(self.stop_time)

        return self.ordered_files[start_file:end_file + 1]

    def read(self, parts: list[str] | str | None = None) -> Iterable[dict]:
        struct_format = '>IIIIcccc'
        size = struct.calcsize(struct_format)

        if isinstance(parts, str):
            parts = [parts]

        if not parts:
            parts = self.get_parts()

        for part in parts:
            with generic.open_file(*part) as file:
                while data := file.read(size):
                    values = struct.unpack(struct_format, data)
                    time = datetime.fromtimestamp(values[0])

                    if self.start_time is not None and time < self.start_time:
                        break

                    if self.stop_time is not None and time >= self.stop_time:
                        break

                    data_point = WorldCup98DataPoint(*values)
                    yield data_point.to_dict()
