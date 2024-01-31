from __future__ import annotations

import argparse
import sys
from enum import Enum

import clarknet.scraper
import nasa.scraper
import worldcup98.scraper


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


SCRAPER_MAP = {
    DatasetType.WORLDCUP98: worldcup98.scraper.WorldCup98Scraper,
    DatasetType.CLARKNET: clarknet.scraper.ClarknetScraper,
    DatasetType.NASA: nasa.scraper.NasaScraper
}


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset',
        choices=DatasetType.get_option_names(),
        help='The type of dataset to scrape data from',
        dest='dataset_type'
    )

    parser.add_argument(
        '--output',
        help='File to output data to',
        dest='output'
    )

    parser.add_argument(
        '--threads',
        help='Number of threads to use for scraping/downloading',
        dest='thread_count',
        default=1
    )

    return parser.parse_args(sys.argv[1:])


def scrape(mode: DatasetType, output_path: str, threads: int):
    scraper = SCRAPER_MAP[mode](output_path, threads)
    scraper.scrape()


def main():
    options = parse_options()
    scrape(
        DatasetType.parse(options.dataset_type),
        options.output,
        options.thread_count
    )


if __name__ == '__main__':
    main()
