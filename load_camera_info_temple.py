import pathlib
from pathlib import Path
import numpy
import numpy as np

def load_extrinsics_temple(filePath):
    file1 = open(filePath, 'r')
    Lines = file1.readlines()  
    count = 0    
    extrinsic_matrix_list = []
    for line in Lines:
        count += 1
        extrinsic_matrix_list.append(line.strip().split())
    extrinsic_matrix_list_1 = extrinsic_matrix_list[0]
    
    extrinsic_matrix_R = [[0 for _ in range(3)] for _ in range(3)]
    extrinsic_matrix_T = [[0 for _ in range(1)] for _ in range(3)]

    extrinsic_matrix_R[0][0] = float(extrinsic_matrix_list_1[0])
    extrinsic_matrix_R[0][1] = float(extrinsic_matrix_list_1[1])
    extrinsic_matrix_R[0][2] = float(extrinsic_matrix_list_1[2])
    extrinsic_matrix_R[1][0] = float(extrinsic_matrix_list_1[3])
    extrinsic_matrix_R[1][1] = float(extrinsic_matrix_list_1[4])
    extrinsic_matrix_R[1][2] = float(extrinsic_matrix_list_1[5])
    extrinsic_matrix_R[2][0] = float(extrinsic_matrix_list_1[6])   
    extrinsic_matrix_R[2][1] = float(extrinsic_matrix_list_1[7])
    extrinsic_matrix_R[2][2] = float(extrinsic_matrix_list_1[8])
    extrinsic_matrix_T[0][0] = float(extrinsic_matrix_list_1[9])
    extrinsic_matrix_T[1][0] = float(extrinsic_matrix_list_1[10])
    extrinsic_matrix_T[2][0] = float(extrinsic_matrix_list_1[11])
    return np.asarray(extrinsic_matrix_R), np.asarray(extrinsic_matrix_T)

def load_intrinsics_temple():
    camera_matrix = numpy.zeros([3, 3])
    camera_matrix[0, 0] = 1520.4
    camera_matrix[1, 1] = 1520.4
    camera_matrix[0, 2] = 302.3
    camera_matrix[1, 2] = 246
    camera_matrix[2, 2] = 1.0
    return camera_matrix


def load_all_camera_parameters_temple(calibration_path, throw_error_if_radial_distortion=False):    
    all_camera_parameters = []
    num_cameras = 0
    if num_cameras == 0:
        num_cameras = len(list(calibration_path.glob("intrinsics_division*.dat")))
        intrinsics_pattern = 'intrinsics_division%02i.dat'
        extrinsics_pattern = 'extrinsics_division%02i.dat'
    if num_cameras == 0:
        num_cameras = len(list(calibration_path.glob("intrinsics_camera*.txt")))
        intrinsics_pattern = 'intrinsics_camera%02i.txt'
        extrinsics_pattern = 'extrinsics_camera%02i.txt'
    if num_cameras == 0:
        assert False, "Couldn't make sense of the filenames for the camera calibrations in "+str(calibration_path.absolute())

    for i in range(num_cameras):

      intrinsicsFilePath = calibration_path / (intrinsics_pattern % (i + 1))
      print('Loading intrinsics for camera',i,'from',intrinsicsFilePath,'...')
      assert intrinsicsFilePath.is_file(), "Couldn't find camera intrinsics in "+str(intrinsicsFilePath)
      #camera_matrix, distortion_coefficients, image_width, image_height, f = load_intrinsics_temple()
      '''
      if throw_error_if_radial_distortion:
          # The images must already be radially undistorted
          if distortion_coefficients['model'] == 'halcon_area_scan_polynomial':
              assert(abs(distortion_coefficients['p1']) < .000000001)
              assert(abs(distortion_coefficients['p2']) < .000000001)
              assert(abs(distortion_coefficients['k1']) < .000000001)
              assert(abs(distortion_coefficients['k2']) < .000000001)
              assert(abs(distortion_coefficients['k3']) < .000000001)
          if distortion_coefficients['model']== 'halcon_divsion':
              assert(abs(distortion_coefficients['kappa']) < .000000001)
      '''
      camera_matrix = load_intrinsics_temple()
      extrinsicsFilePath = calibration_path / (extrinsics_pattern % (i + 1))
      print('Loading extrinsics for camera',i,'from',extrinsicsFilePath,'...')

      R, T = load_extrinsics_temple(extrinsicsFilePath)
      camera_parameters = {'camera_matrix':camera_matrix, 'R':R, 'T':T, 'image_width':640, 'image_height':480, 'f': camera_matrix[0, 0]}   
      #print(camera_parameters)
      #camera_parameters.update(distortion_coefficients)

      all_camera_parameters.append(camera_parameters)
      #print(len(all_camera_parameters))
    return all_camera_parameters # List of dictionaries
