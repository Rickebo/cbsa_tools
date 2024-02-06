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

## Docker

To build the Docker image, either run the ``build_image.sh`` script, or use the 
following command:
```bash
docker build -t datascraper .
```

To, for example, run the view script with a zip file mounted, use the following 
command on POSIX-based systems:
```bash
docker run --volume $PWD/worldcup98.zip:/app/worldcup98.zip datascraper view.py --dataset WORLDCUP98 --part wc_day90_1 --input data/worldcup98.zip --format json
```

and on Windows using Git Bash, use the following command instead:
```bash
docker run --volume $(cygpath -w ${PWD}):$(cygpath -w /c/app/data/) datascraper view.py --dataset WORLDCUP98 --part wc_day90_1 --input data/worldcup98.zip --format json
```
