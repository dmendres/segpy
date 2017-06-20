#!/usr/bin/env python3

"""Print the position coordinates of every trace.

Usage: trace_positions.py [-h] segy-file

Positional arguments:
  segy-file      Path to an existing SEG Y file of 3D seismic data

Optional arguments:
  -h, --help     show this help message and exit

Example:

  trace_positions.py stack_final_int8.sgy
"""

import argparse
import os
import sys
import traceback

from segpy.reader import create_reader


class DimensionalityError(Exception):
    pass


def sample_TracePositions(segyFileName, skipCount = 100):
    """Extract sparse trace positions (every skipCount traces in x and y
       from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.
        skipCount: number of traces to skip between printed samples, also the reduction factor in number of traces printed
    """
    with open(segyFileName, 'rb') as segy_file:
        segy_reader = create_reader(segy_file)
        for trace_index in segy_reader.trace_indexes():
            trace_header = segy_reader.trace_header(trace_index)
            trace_position = (trace_header.cdp_x,
                              trace_header.cdp_y)
            if (trace_index % skipCount == 0) :
                print(trace_index, trace_position, trace_header.num_samples, "samples at ", trace_header.sample_interval/1000.0, "ms per sample")
                

def extract_trace_positions(segy_filename):
    """Extract a timeslice from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.
    """
    with open(segy_filename, 'rb') as segy_file:

        segy_reader = create_reader(segy_file)

        for trace_index in segy_reader.trace_indexes():
            trace_header = segy_reader.trace_header(trace_index)
            trace_position = (trace_header.cdp_x,
                              trace_header.cdp_y)
            print(trace_index, trace_position)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("segy_file", metavar="segy-file",
                        help="Path to an existing SEG Y file of 3D seismic data")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        extract_trace_positions(args.segy_file)
    except (FileNotFoundError, IsADirectoryError) as e:
        print(e, file=sys.stderr)
        return os.EX_NOINPUT
    except PermissionError as e:
        print(e, file=sys.stderr)
        return os.EX_NOPERM
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return os.EX_SOFTWARE
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())


