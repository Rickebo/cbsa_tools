from __future__ import annotations

import argparse
import datetime
import json
import sys
from enum import Enum

import worldcup98.viewer
from abstract_viewer import Viewer
from generic import DatasetType
from log_viewer import LogViewer

viewer_map = {
    DatasetType.WORLDCUP98: worldcup98.viewer.WorldCup98Viewer,
    DatasetType.CLARKNET: LogViewer,
    DatasetType.NASA: LogViewer
}


class OutputOption(Enum):
    JSON = 1
    PLOT = 2

    @staticmethod
    def get_option_names():
        list(option.name for option in OutputOption)

    @staticmethod
    def parse(name: str) -> OutputOption:
        name = name.upper()
        for option in OutputOption:
            if option.name == name:
                return option

        raise ValueError(f'Name {name} is not a valid OutputOption.')


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--dataset',
        help='The type of dataset to view',
        choices=DatasetType.get_option_names(),
        dest='dataset'
    )

    parser.add_argument(
        '--input',
        help='The input location to read from',
        dest='input'
    )

    parser.add_argument(
        '--part',
        help='Part from within the input to read',
        dest='part',
        default=None
    )

    parser.add_argument(
        '--start',
        help='Start time',
        dest='start_time',
        default=None
    )

    parser.add_argument(
        '--stop',
        help='Stop time',
        dest='stop_time',
        default=None
    )

    parser.add_argument(
        '--duration',
        help='Duration to view data for in hours. Start or stop time is required '
             'when this is specified.',
        dest='duration',
        default=None
    )

    parser.add_argument(
        '--output',
        help='Output file. If not specified, output is written to stdout.',
        dest='output_file',
        default=None
    )

    parser.add_argument(
        '--format',
        help='Output format.',
        choices=OutputOption.get_option_names(),
        default=OutputOption.JSON.name,
        dest='output_format'
    )

    return parser.parse_args(sys.argv[1:])


def main():
    options = parse_options()
    dataset = DatasetType.parse(options.dataset)
    viewer = viewer_map[dataset](
        options.input,
        options.start_time,
        options.stop_time,
        options.duration
    )

    view(viewer, options)


def view(viewer: Viewer, options):
    output_format = OutputOption.parse(options.output_format)
    start_date = viewer.start_time
    end_date = viewer.stop_time
    data = viewer.read(options.part)
    if output_format == OutputOption.JSON:
        output = sys.stdout

        if options.output_file is not None:
            output = open(options.output_file, 'w')

        for line in data:
            output.write(json.dumps(line))
            output.write('\n')

        if output != sys.stdout:
            output.close()
    elif output_format == OutputOption.PLOT:
        bin_count = 256

        first_time = start_date
        last_time = end_date

        items = data
        if start_date is None or end_date is None:
            items = list(data)
            first_time = datetime.datetime.fromisoformat(items[0]['time'])
            last_time = datetime.datetime.fromisoformat(items[-1]['time'])

        step = (last_time - first_time) / bin_count

        bin_times = [first_time + step * i for i in range(bin_count)]
        bin_counts = [0 for _ in bin_times]
        bin = 0
        next_bin = bin_times[1]

        for point in items:
            time = datetime.datetime.fromisoformat(point['time'])

            if next_bin is None:
                break

            while time >= next_bin and bin < bin_count - 2:
                bin += 1
                next_bin = bin_times[bin + 1] if bin + 1 < bin_count else None

                if next_bin is None:
                    break

            if bin < bin_count:
                bin_counts[bin] += 1

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(bin_times[:-2], bin_counts[:-2])
        plt.show()


if __name__ == '__main__':
    main()
