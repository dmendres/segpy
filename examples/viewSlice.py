#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 15:09:33 2017

@author: DavidMack
"""


import argparse
import os
import sys
import traceback
#import pdb
import numpy as np



import matplotlib.pyplot as plt  # the tidy way

def viewSlice(npfilename):
    print("viewing {0}".format(npfilename))
    image = np.load(npfilename)
    plt.title(npfilename)
    plt.imshow(image, cmap=plt.cm.hot)
    plt.colorbar()
    plt.show()


def main(argv=None):
    print("starting slice viewer")
    parser = argparse.ArgumentParser()
    
    parser.add_argument("npy_file", metavar="npy-file",
                        help="Path to the Numpy array file to be created for the timeslice")

#    parser.add_argument("slice_iindex", metavar="slice-iindex", type=int,
#                        help="Zero based index of the i (inline) slice to be extracted", )
#    parser.add_argument("slice_jindex", metavar="slice-jindex", type=int,
#                        help="Zero-based index of the j (cross line) slice to be extracted")
#
#    parser.add_argument("--dtype", type=nullable_dtype, default="",
#                        help="Numpy data type. If not provided a dtype compatible with the SEG Y data will be used.")
#
#    parser.add_argument("--null",  type=float, default=0.0,
#                        help="Sample value to use for missing or short traces.")

    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)

    try:
        print(args.npy_file)
        viewSlice(args.npy_file)
        print("displayed slice in {0}".format(args.npy_file) )

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