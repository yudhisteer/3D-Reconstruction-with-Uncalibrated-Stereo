#!/usr/bin/env python3

# Simple .ply file loader to avoid adding an unnecessary dependency.

import pathlib
from pathlib import Path
import os
import numpy

def load_ply_using_library(filename):
    """ Load a plyfile using the plyfile library.
        Doing it this way softens the dependency on the external library. """
    from plyfile import PlyData, PlyElement
    plydata = PlyData.read(filename)

    data = plydata['vertex'].data
    properties = plydata.elements[0].properties
    columnnames = [p.name for p in properties]

    # The library represents data in a list of tuples.
    # I use a flat numpy array. plyfile uses structured arrays
    columns = len(data.dtype)
    rows = len(data)
    outdata = numpy.zeros((rows,columns),dtype=numpy.float32)
    i = 0
    for columnname in columnnames:
        outdata[:,i] = data[columnname]
        i += 1

    columntypes = [str(data.dtype[i]) for i in range(len(data.dtype))] # numpy typestrings
    return outdata, columnnames, columntypes


def save_ply(xyz, filename, output_folder):
    """ Dump a point cloud to an ascii ply file.

    Args:
        xyz (numpy.ndarray): The 3D points to be saved as a PLY file.
        filename (str): The file name (without extension) for the PLY file.
        output_folder (str): The folder path where the PLY file should be saved.
    """
    assert len(xyz.shape) == 2
    assert xyz.shape[1] == 3
    header = """ply
format ascii 1.0
element vertex """ + str(xyz.shape[0]) + """
property float x
property float y
property float z
end_header"""
    output_file_path = os.path.join(output_folder, filename + '.ply')
    numpy.savetxt(output_file_path, xyz, header=header, fmt='%.8f', comments='')


def load_ply(filename, enableCaching=True):
    """ Load an ascii based .ply file.
        Inputs:
            filename -- string or path
            enableCaching -- bool, defaults to True
        Outputs:
            data -- row-major AOS numpy array.
            columnnames -- list of string
            columntypes -- list of string 
    """
    # Parse the header
    filename = str(filename)
    file = open(filename,'r')

    header_lines = 0

    try:
        assert file.readline().strip() == 'ply'
    except:
        print("Trouble running readline on the file! Will try loading the file using the plyfile library!")
        return load_ply_using_library(filename)
    header_lines += 1

    nextline = file.readline().strip()
    if 'ascii' not in nextline:
        assert 'binary' in nextline, 'Cannot even detect if ply file is ascii or binary!'
        return load_ply_using_library(filename)
    assert nextline == 'format ascii 1.0'
    header_lines += 1

    nextline = file.readline().strip()
    while(nextline.split(' ')[0] == 'comment'):
        header_lines += 1
        nextline = file.readline().strip()

    assert nextline.split(' ')[0] == 'element'
    assert nextline.split(' ')[1] == 'vertex'
    expected_vertices = int(nextline.split(' ')[2])
    header_lines += 1

    columntypes = []
    columnnames = []

    while(1):
        nextline = file.readline().strip().split(' ')
        if nextline[0] == 'property':
            columntypes.append(nextline[1])
            columnnames.append(nextline[2])
            header_lines += 1
            continue
        else:
            break

    # meshlab annoyingly exports files with zero faces, instead of just ommitting the element.
    if nextline[0] == 'element' and nextline[1] == 'face':
        assert nextline[2] == '0', "Nonzero number of faces in the ply file is not handled yet!"
        header_lines += 1

        nextline = file.readline().strip().split(' ')
        assert nextline[0] == 'property'
        header_lines += 1

        nextline = file.readline().strip().split(' ')

    assert nextline[0] == 'end_header'
    header_lines += 1

    file.close()

    plyPath = Path(filename)
    plyTimestamp = plyPath.stat().st_mtime
    plyCachedPath = plyPath.with_suffix('.npy')
    if enableCaching and plyCachedPath.is_file() and plyCachedPath.stat().st_mtime > plyTimestamp:
        #print("Pickled point cloud is newer than ascii .ply file; loading it!")
        data = numpy.load(file=str(plyCachedPath))
    else:
        data = numpy.loadtxt(fname=filename,skiprows=header_lines)
        #print("Pickle non-existent or older than .ply file; regenerating it!")
        numpy.save(arr=data,file=str(plyCachedPath))

    assert data.shape[0]==expected_vertices, 'Ply file corrupted! Inconsistent number of vertices!'
    assert data.shape[0] > 0, 'Ply file did not contain any points!'
    return data, columnnames, columntypes

def load_ply_just_xyz(plyFilePath, enableCaching=None):
    """ A specialization that just returns the points """
    data, columnnames, columntypes = load_ply(plyFilePath,enableCaching=enableCaching)
    assert columnnames[0:3] == ['x', 'y', 'z']
    xyz = data[:, 0:3].copy() # Just in case some other code needs a dense array.
    return xyz
