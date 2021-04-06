import trimesh
import os
from time import time
import argparse
import numpy as np
import xml.etree.ElementTree as ET
from multiprocessing import Pool


def parsePath(pathfile):
    # create element tree object
    tree = ET.parse(pathfile)

    # get root element
    root = tree.getroot()

    # create empty list for paths
    paths = []

    # iterate news items
    for point in root.findall('Point'):
        trans = point.find('Transform')
        x = float(trans.attrib['x'])
        y = float(trans.attrib['y'])
        z = float(trans.attrib['z'])

        xx = float(trans.attrib["xx"])
        xy = float(trans.attrib["xy"])
        xz = float(trans.attrib["xz"])

        yx = float(trans.attrib["yx"])
        yy = float(trans.attrib["yy"])
        yz = float(trans.attrib["yz"])

        zx = float(trans.attrib["zx"])
        zy = float(trans.attrib["zy"])
        zz = float(trans.attrib["zz"])

        mat = np.array([[xx, xy, xz, x],
                        [yx, yy, yz, y],
                        [zx, zy, zz, z],
                        [0, 0, 0, 1]])
        paths.append(mat)

    return paths


def merge_mesh(mesh1, mesh2, save_path):
    merged = mesh1.union(mesh2)
    merged.apply_translation(-merged.centroid)
    merged.export(save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='keyframe_obj_export',
                                     description="""Script to export objects at keyframes from paths""")
    # parser.add_argument("--input", "-i", required=True, help="Directory of simulated data", type=str)
    parser.add_argument("--start", "-s", type=int, default=1, help="Start index")
    parser.add_argument("--thresh", "-t", default=float("inf"), help="Threshold distance for exporting objects", type=float)
    parser.add_argument("--output", "-o", required=True, help="Directory to write merged objects", type=str)
    parser.add_argument("--inc", "-i", type=int, default=1, help="Increment for frames")
    parser.add_argument("--nthreads", "-n", type=int, default=1, help="Number of threads to use")


    args = parser.parse_args()

    output = args.output
    start = args.start
    thresh = args.thresh
    inc = args.inc
    nthreads = args.nthreads

    if not os.path.exists(output):
        os.makedirs(output)

    path1 = parsePath("C:/Users/Zhenyu Tang/Codes/GSound-diffraction/GSound/Test/Recordings/Sibenik/obj1.xml")
    path2 = parsePath("C:/Users/Zhenyu Tang/Codes/GSound-diffraction/GSound/Test/Recordings/Sibenik/obj2.xml")
    m1 = trimesh.load("C:/Users/Zhenyu Tang/Codes/GSound-diffraction/GSound/Test/Data/Models/Sibenik/00055697_f360de213ceb403d91c54c0d_trimesh_001.simple.034.obj")
    m2 = trimesh.load("C:/Users/Zhenyu Tang/Codes/GSound-diffraction/GSound/Test/Data/Models/Sibenik/00330008_582ad1d69c61dd11019b43b2_trimesh_001.simple.034.obj")

    N = min(len(path1), len(path2))
    ts = time()
    try:
        # # Create a pool to communicate with the worker threads
        pool = Pool(processes=nthreads)
        i = start
        while i < N:
            mesh1 = m1.copy()
            mesh2 = m2.copy()
            mesh1.apply_transform(path1[i])
            mesh2.apply_transform(path2[i])
            dist = trimesh.util.euclidean(mesh1.centroid, mesh2.centroid)
            if thresh > dist:
                pool.apply_async(merge_mesh, args=(mesh1, mesh2, os.path.join(output, '{}.obj'.format(i))))
            else:
                print('skipping frame {}, dist: {}'.format(i, dist))
            i += inc

    except Exception as e:
        print(str(e))
        pool.close()
    pool.close()
    pool.join()
    print('Took {}'.format(time() - ts))