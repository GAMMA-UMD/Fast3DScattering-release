import os
os.environ["MKL_NUM_THREADS"] = "2"
import sys
sys.path.append('..')
import numpy as np
import h5py
import argparse
from time import time
from multiprocessing import Pool
import pyshtools

import utils.fileio as fileio
from utils.sphmath import cart2sph


def convert_SH(field, outfile, lmax):
    pressure = fileio.read_field_pressure(outfile)
    az, el, r = cart2sph(field[:, 0], field[:, 1], field[:, 2])
    lon = np.rad2deg(az)
    lat = np.rad2deg(el)
    try:
        coeffs, residual = pyshtools.expand.SHExpandLSQ(pressure, lat, lon, lmax)
        shvec = pyshtools.shio.SHCilmToVector(coeffs)
    except:
        print("failed to fit pressure field {}".format(outfile))
        return [], 1000
    return shvec, residual


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='1_data_extraction',
                                     description="""Script to extract input data and label and save as an h5py file""")
    parser.add_argument("--input", "-i", required=True, help="Directory of simulated data", type=str)
    parser.add_argument("--shorder", "-s", default=3, help="Maximum spherical harmonics order", type=int)
    parser.add_argument("--freq", "-f", required=True, help="Simulation frequency to extract", type=str)
    parser.add_argument("--suffix", "-e", default="034.obj", help="Suffix of objects", type=str)
    parser.add_argument("--nthreads", "-n", type=int, default=1, help="Number of threads to use")

    args = parser.parse_args()

    folder_path = args.input
    shorder = args.shorder
    freq = args.freq
    suffix = args.suffix
    nthreads = args.nthreads

    assert os.path.exists(folder_path)

    output_name = 'output_result.{}.dat'.format(freq)
    root = os.path.join(folder_path, '')

    task_list = []
    infile = None
    for dirName, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(suffix):
                # extract field points from any input mesh since all field points are the same
                if not infile and os.path.exists(os.path.join(dirName, 'input.dat')):
                    infile = os.path.join(dirName, 'input.dat')
                outfile = os.path.join(dirName, output_name)
                if not os.path.exists(outfile):
                    continue
                else:
                    objfile = os.path.join(dirName, file)
                    task_list.append([outfile, objfile])
    field = fileio.read_field_points(infile)

    N = len(task_list)
    print("Total tasks: {}".format(N))
    res = []
    ts = time()
    try:
        # # Create a pool to communicate with the worker threads
        pool = Pool(processes=nthreads)
        for task in task_list:
            res.append(pool.apply_async(convert_SH, args=(field, task[0], shorder)))
    except Exception as e:
        print(str(e))
        pool.close()
    pool.close()
    pool.join()
    print('Took {}'.format(time() - ts))

    num_examples = N
    veclen = (shorder + 1) * (shorder + 1)

    h5_file_output = os.path.join(folder_path, 'data_{}Hz.h5'.format(freq))
    h5_dataset = h5py.File(h5_file_output, 'w')

    h5_dataset.require_dataset('coeffs', shape=(num_examples, veclen), maxshape=(None, None), compression=None,
                               dtype='f4')
    h5_dataset.require_dataset('residual', shape=(num_examples,), maxshape=(None,), compression=None, dtype='f4')
    dt = h5py.special_dtype(vlen=str)
    h5_dataset.require_dataset('objpath', shape=(num_examples,), maxshape=(None,), compression=None, dtype=dt)

    try:
        for i in range(N):
            shvec, residual = res[i].get(timeout=1)
            objpath = task_list[i][1]
            rel_path = objpath.replace(root, '')
            h5_dataset['coeffs'][i] = shvec
            h5_dataset['residual'][i] = residual
            h5_dataset['objpath'][i] = rel_path
    except TimeoutError:
        print("We lacked patience and got a multiprocessing.TimeoutError")
    except:
        print("File {} caused numerical error.".format(task_list[i][0]))
    h5_dataset.close()
