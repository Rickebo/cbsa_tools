from __future__ import annotations

import argparse
import sys
from enum import Enum

import clarknet.scraper
import nasa.scraper
import worldcup98.scraper
from generic import DatasetType

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
