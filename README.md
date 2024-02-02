# cbsa_tools

Collection of utilities to scrape and view load datasets.

## datascraper.py

Utility to scrape/download various types of load data.

Use ``py datascraper.py --help`` for instructions on how the utility is used.

### Examples

To scrape all data from the world cup 98 dataset, use:
````bash
py datascraper.py --dataset WORLDCUP98 --output output_dir
````
NOTE: In the current version, after running the command, the world cup dataset will 
be downloaded to the cache/worldcup98 directory, not the specified output directory.

## view.py

Utility to view load data from binary formats.

Use ``py view.py --help`` for instructions on how the utility is used.

### Examples

To dump a whole day from the world cup 98 dataset to a file in JSON format, use:
````bash
py view.py --dataset WORLDCUP98 --input cache/workdcup98 --start 1998-07-23T00:00:00 --duration 1m --output test.json
````