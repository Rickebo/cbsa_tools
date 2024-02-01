import json
import struct
from datetime import datetime
from typing import Iterable

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
        self.method: str = self.METHOD_NAMES[int.from_bytes(method, 'big')]
        status_field = int.from_bytes(status, 'big')
        self.status: int = self.STATUS_CODES[status_field & 0b111111]
        self.http_version = status_field >> 6
        self.type: str = self.TYPES[int.from_bytes(type, 'big')]
        server_field = int.from_bytes(server, 'big')
        self.server_id: int = server_field & 0b11111
        self.server_region: int = server_field >> 5

    def to_json(self):
        return json.dumps(self.__dict__)



class WorldCup98Viewer(Viewer):
    def __init__(self, input_path: str, start_time: str, stop_time: str):
        super().__init__(input_path, start_time, stop_time)

    def read(self, part: str | None = None) -> Iterable[str]:
        struct_format = '>IIIIcccc'
        size = struct.calcsize(struct_format)
        with generic.open_file(self.input_path, file_name=part) as file:
            while data := file.read(size):
                values = struct.unpack(struct_format, data)
                time = datetime.fromtimestamp(values[0])

                if self.start_time is not None and time < self.start_time:
                    continue

                if self.stop_time is not None and time > self.stop_time:
                    continue

                data_point = WorldCup98DataPoint(*values)
                yield data_point.to_json()


