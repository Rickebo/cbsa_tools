import os.path
import re
import sys

from abstract_scraper import Scraper


class WorldCup98Scraper(Scraper):

    def __init__(self, output_path: str, threads: int):
        super().__init__(output_path, threads)

        self.input_file_path: str = os.path.join(
            os.path.dirname(__file__),
            'input_list.txt'
        )

        self.input_files: list[str] = Scraper.read_input_files(self.input_file_path)
        self.cache_dir: str = os.path.join(os.path.abspath('cache'), 'worldcup98')

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def cache_dataset(self):
        super().cache_files(
            file_list=self.input_files,
            url_format='ftp://ita.ee.lbl.gov/traces/WorldCup/%s',
            output_dir=self.cache_dir
        )

    def scrape(self):
        self.cache_dataset()
