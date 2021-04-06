from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import h5py
import argparse

import concurrent.futures
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

def write_coef(fname, coef):
        with open(fname, 'w') as out:
                for c in  coef:
                        out.write('%f ' % c)
                print('%s\n' % fname)
        


if __name__ == "__main__":

        arg_parser = argparse.ArgumentParser(
                formatter_class = argparse.RawTextHelpFormatter,
                description = "split h5py file"
                )
        arg_parser.add_argument(
                "--dataset",
                "-d",
                dest = "dataset",
                required = True,
                help = "h5py file"
                )
        arg_parser.add_argument(
                "--source_dir",
                "-s",
                dest = "source_dir",
                required = True,
                help = "source dir"
                )
        arg_parser.add_argument(
                "--threads",
                dest = "num_threads",
                default = 16
                )
        arg_parser.add_argument(
                "--suffix",
                dest = 'suffix',
                required = True
        )
        args = arg_parser.parse_args()

        args.num_threads = int(args.num_threads)
        dataset = h5py.File(args.dataset, 'r')
        num_file = len(dataset['objpath'])


        for fname, coef in zip(
                [os.path.join(args.source_dir, _fname + args.suffix + '.coef') for _fname in dataset['objpath']],
                [_coef for _coef in dataset['coeffs']]):
                write_coef(fname, coef)
#        with concurrent.futures.ProcessPoolExecutor(
#                max_workers = args.num_threads
#                ) as executor:
#                executor.map(
#                                write_coef,
#                                [os.path.join(args.source_dir, fname + args.suffix + '.coef') for fname in dataset['objpath']],
#                                [coef for coef in dataset['coeffs']]
#                        )
#                executor.shutdown()

