#! /usr/bin/env python3   

#python

"""Extract a inline or cross line slice from a 3D seismic volume to a Numpy array.

This utility assumes the time samples, inline and crossline numbers are evenly spaced.
If an inline slice is desired, set the j or cross line slice index to -1,
similarly, if a cross line (j) slice is desired, set the inline index to -1.
Each inline (or cross line, depending on selection) of the source data will be represented as a single row, and
each time samples as a single column in the resulting 2D array.

Usage: ijlice.py [-h] [--dtype DTYPE] [--null NULL]
                    segy-file npy-file slice-iindex slice-jindex

Positional arguments:
  segy-file      Path to an existing SEG Y file of 3D seismic data
  npy-file       Path to the Numpy array file to be created for the timeslice
  slice-iindex   Zero based index of the inline slice to be extracted
  slice-jindex   Zero-based index of the cross line slice to be extracted

Optional arguments:
  -h, --help     show this help message and exit
  --dtype DTYPE  Numpy data type. If not provided a dtype compatible with the
                 SEG Y data will be used.
  --null NULL    Sample value to use for missing or short traces.

Example:

  timeslice.py stack_final_int8.sgy inlineSlice_800.npy 800 -1 --null=42.0 --dtype=f
"""

import argparse
import os
import sys
import traceback
import pdb
import numpy as np

from segpy.reader import create_reader
from segpy_numpy.dtypes import make_dtype


class DimensionalityError(Exception):
    pass



def extractISlice(segy_reader, iIndex, timeslice):
    inline_num = segy_reader.inline_numbers()[iIndex]
    for xline_num in segy_reader.xline_numbers():
            trace_index = segy_reader.trace_index((inline_num, xline_num))
            trace = segy_reader.trace_samples(trace_index)
            xIndex = segy_reader.xline_numbers().index(xline_num)
            
            #this probably should start in lower corner, not upper corner, e.g. reverse the range
            for sIndex in range(0,segy_reader.trace_header(trace_index).num_samples):
                try:
                    sample = trace[sIndex]
                    timeslice[sIndex, xIndex] = sample
                except IndexError:
                    print("bad indices: xline ", xIndex, " time: ", sIndex)
    

def extractXSlice(segy_reader, xIndex, timeslice):
    xline_num = segy_reader.xline_numbers()[xIndex]
    for inline_num in segy_reader.inline_numbers():
            trace_index = segy_reader.trace_index((inline_num, xline_num))
            trace = segy_reader.trace_samples(trace_index)
            iIndex = segy_reader.inline_numbers().index(inline_num)
            
            #this probably should start in lower corner, not upper corner, e.g. reverse the range
            for sIndex in range(0,segy_reader.trace_header(trace_index).num_samples):
                try:
                    sample = trace[sIndex]
                    timeslice[sIndex, iIndex] = sample
                except IndexError:
                    print("bad indices: inline ", iIndex, " time: ", sIndex)

def extract_ixslice(segy_filename, out_filename, iIndex= -1 , xIndex= -1, dtype=None, null=0):
    """Extract an inline or crossline slice from a 3D SEG Y file to a Numpy NPY file.

    Args:
        segy_filename: Filename of a SEG Y file.

        out_filename: Filename of the NPY file.
        
# TODO: SHOULD THESE BE THE ACTUAL I/X LINE VALUE RATHER THAN INDICES?
        
        islice: The zero-based inline index of the slice to be extracted. -1 if xline slice is desired.
        
        xslice: The zero-based cross line index of the slice to be extracted. -1 if inline slice is desired

        dtype: Optional Numpy dtype for the result array. If not provided a dtype compatible with
            the SEG Y data will be used.

        null: Optional sample value to use for missing or short traces. Defaults to zero.
    """
#    pdb.set_trace()
    with open(segy_filename, 'rb') as segy_file:

        segy_reader = create_reader(segy_file)

        if dtype is None:
            dtype = make_dtype(segy_reader.data_sample_format)

        if segy_reader.dimensionality != 3:
            raise DimensionalityError("Cannot slice {n} dimensional seismic.".format(segy_reader.dimensionality))

        if ((iIndex < 0 and xIndex < 0) or (iIndex >= 0 and xIndex >= 0)):
            raise DimensionalityError("Only one of inline or xline slice index must be specified")
            
        i_size = segy_reader.num_inlines()
        x_size = segy_reader.num_xlines()
        t_size = segy_reader.max_num_trace_samples()
        
        if (iIndex >= 0):
            if not (0 <= iIndex < i_size):
                raise ValueError("Inline slice index {0} out of range {0} to {2}".format(iIndex, 0, i_size))
            timeslice = np.full((t_size,x_size), null, dtype)
            extractISlice(segy_reader, iIndex, timeslice)
        else:
            if not (0 <= xIndex < x_size):
                raise ValueError("Crossline slice index {0} out of range {1} to {2}".format(xIndex, 0, x_size))
            timeslice = np.full((t_size, i_size), null, dtype)
            extractXSlice(segy_reader, xIndex, timeslice)

        
        np.save(out_filename, timeslice)

def nullable_dtype(s):
    return None if s == "" else np.dtype(s)


def main(argv=None):
    print("starting ijslicer")
    parser = argparse.ArgumentParser()
    parser.add_argument("segy_file", metavar="segy-file",
                        help="Path to an existing SEG Y file of 3D seismic data")

    parser.add_argument("npy_file", metavar="npy-file",
                        help="Path to the Numpy array file to be created for the timeslice")

    parser.add_argument("slice_iindex", metavar="slice-iindex", type=int,
                        help="Zero based index of the i (inline) slice to be extracted", )
    parser.add_argument("slice_jindex", metavar="slice-jindex", type=int,
                        help="Zero-based index of the j (cross line) slice to be extracted")

    parser.add_argument("--dtype", type=nullable_dtype, default="",
                        help="Numpy data type. If not provided a dtype compatible with the SEG Y data will be used.")

    parser.add_argument("--null",  type=float, default=0.0,
                        help="Sample value to use for missing or short traces.")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        outFile = args.npy_file
        islice = args.slice_iindex
        jslice = args.slice_jindex
        extract_ixslice(args.segy_file,
                          args.npy_file,
                          args.slice_iindex,
                          args.slice_jindex,
                          args.dtype,
                          args.null)
        if (islice >= 0) :
            print("extracted islice {1} to {0}".format(outFile, islice) )
        else :
            print("extracted jslice {1} to {0}".format(outFile, jslice) )

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

