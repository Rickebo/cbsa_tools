from __future__ import annotations

import gzip
import os
import shutil
import zipfile
from enum import Enum


def get_archive_format(file_path: str) -> str | None:
    formats = [
        '.gz',
        '.zip'
    ]

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    return ext if ext in formats else None


def open_file(archive: str, file_name: str | None = None):
    ext = get_archive_format(archive)

    if ext == '.gz':
        return gzip.open(archive, 'rb')
    if ext == '.zip':
        if file_name is None:
            raise ValueError('No sub file specified')

        archive = zipfile.ZipFile(archive, 'r')
        return archive.open(file_name)
    else:
        raise ValueError('File type is not supported.')


def extract_file(file_path: str):
    ext = get_archive_format(file_path)
    new_file = file_path.rstrip(ext)

    if ext == '.gz':
        with gzip.open(file_path, 'rb') as archive:
            with open(new_file, 'wb') as extracted:
                shutil.copyfileobj(archive, extracted)
                return new_file
    else:
        return None


class DatasetType(Enum):
    NONE = 0
    WORLDCUP98 = 1
    CLARKNET = 2
    NASA = 3

    @staticmethod
    def get_option_names() -> list[str]:
        return [dataset_type.name for dataset_type in DatasetType]

    @staticmethod
    def parse(name: str) -> DatasetType:
        return next(
            filter(lambda dataset_type: dataset_type.name == name, DatasetType),
            None
        )
