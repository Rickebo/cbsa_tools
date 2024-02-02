from __future__ import annotations

import gzip
import os
import shutil
import zipfile
from datetime import timedelta
from enum import Enum
from typing import Tuple


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
        file = archive.open(file_name)

        return gzip.open(file, 'rb') \
            if get_archive_format(file_name) == '.gz' else \
            file
    else:
        raise ValueError('File type is not supported.')


def parse_duration(duration: str) -> timedelta:
    if not duration:
        raise ValueError('Cannot parse empty duration.')

    current = ''
    multipliers = {
        'd': 3600 * 24,
        'h': 3600,
        'm': 60,
        's': 1
    }

    total = 0
    for ch in duration:
        if ch.isspace():
            continue

        if ch.isdigit():
            current += ch
            continue

        multiplier = multipliers.get(ch)
        if not multiplier or not current:
            raise ValueError(f'Cannot parse duration from {duration}.')

        total += int(current) * multiplier
        current = ''

    return timedelta(seconds=total)


def get_files(file_path: str, exclude_empty: bool = True) -> list[Tuple[str, str | None]]:
    if os.path.isdir(file_path):
        dir_files = [os.path.join(file_path, path) for path in os.listdir(file_path)]
        return [
            (path, None) \
            for path in dir_files \
            if not exclude_empty or os.path.getsize(path) > 0
        ]

    _, extension = os.path.splitext(file_path)
    if extension.lower() == '.zip':
        with zipfile.ZipFile(file_path) as file:
            return [
                (file_path, part.filename) \
                for part in  file.filelist \
                if not exclude_empty or part.file_size > 0
            ]

    raise ValueError('The specified file extension is not supported')


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
