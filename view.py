import argparse
import sys

import worldcup98.viewer
from generic import DatasetType

viewer_map = {
    DatasetType.WORLDCUP98: worldcup98.viewer.WorldCup98Viewer
}


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

    output = sys.stdout

    if options.output_file is not None:
        output = open(options.output_file, 'w')

    for line in viewer.read(options.part):
        output.write(line)
        output.write('\n')

    if output != sys.stdout:
        output.close()


if __name__ == '__main__':
    main()
