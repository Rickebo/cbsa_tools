import gzip
import os
import queue
import re
import shutil
import sys
import time
from abc import ABC, abstractmethod
from threading import Thread, Event
from typing import Tuple
from urllib.request import urlretrieve


class Scraper(ABC):
    INPUT_FILE_REGEX = re.compile(r'^([\w.]+)')

    def __init__(self, output_path: str, threads: int):
        self.output_path: str = output_path
        self.threads: int = threads

    @abstractmethod
    def scrape(self):
        raise NotImplementedError()

    @staticmethod
    def download_file(url: str, destination: str, extract: bool = True):
        temp_name = destination + ".download"
        urlretrieve(url, temp_name)
        os.rename(temp_name, destination)

    @staticmethod
    def read_input_files(file_path: str, line_regex: re.Pattern = None) -> list[str]:
        line_regex = line_regex or Scraper.INPUT_FILE_REGEX
        result = []
        with open(file_path, 'r') as input_files:
            while line := input_files.readline():
                match = line_regex.match(line)

                if not match:
                    continue

                result.append(match.group(1))

        return result

    def cache_files(self, file_list: str | list[str], output_dir: str,
                    url_format: str):

        if isinstance(file_list, str):
            file_list = [file_list]

        print_format = '\rCaching files: %s (%s)\033[K'
        sys.stdout.write(print_format % ('0%', 'initializing...'))
        sys.stdout.flush()

        task_queue = queue.Queue()
        done_list = []
        ongoing_set = set()

        for file in file_list:
            task_queue.put((url_format, output_dir, file))

        thread_count = min(self.threads, len(file_list))
        threads = [
            Thread(
                target=self._download_threaded,
                args=(task_queue, done_list, ongoing_set)
            )
            for _ in range(thread_count)
        ]

        for thread in threads:
            thread.start()

        last_done = 0

        while any(thread.is_alive() for thread in threads):
            done = len(done_list)

            if done == last_done:
                time.sleep(0.01)
                continue

            last_done = done

            current = ', '.join(ongoing_set)
            progress = len(done_list) / len(file_list)

            sys.stdout.write(print_format % (f'{progress:.0%}', current))
            sys.stdout.flush()

        sys.stdout.write(print_format % ('100%', 'done!'))
        sys.stdout.write('\n')
        sys.stdout.flush()

    def _download_threaded(
            self,
            task_queue: queue.Queue[Tuple[str, str, str]],
            done_list: list[str],
            ongoing_list: set[str]
    ):
        try:
            while task := task_queue.get(block=False):
                url_format, destination, file = task
                file_path = os.path.join(destination, file)

                ongoing_list.add(file)

                if not os.path.exists(file_path):
                    self.download_file(url_format % file, file_path)

                if hasattr(self, 'get_archive_format') and \
                        hasattr(self, 'extract_file') and \
                        self.get_archive_format(file_path) is not None:
                    self.extract_file(file_path)

                ongoing_list.remove(file)
                done_list.append(file)
        except queue.Empty:
            return