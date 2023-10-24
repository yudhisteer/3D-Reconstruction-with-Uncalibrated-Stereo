#!/usr/bin/env python3

import pathlib
from pathlib import Path
import numpy

_HalconDistortionParameters1 = ['Poly1', 'Poly2', 'Poly3', 'Poly4', 'Poly5']
_HalconDistortionParameters2 = ['Kappa']

def load_halcon_intrinsics(filePath):
    """ Load a halcon camera intrinsics file.
            i.e. the human-readable ASCII ones starting with \"ParGroup\"
        This function just does a 1:1 mapping of the (badly documented)
        file contents into python.
        Input:
            filePath -- The name of the file to read
        Output:
            A dictionary containing the focal length,
            radial distortion polynomial coefficients, etc...
            """
    assert filePath.is_file()
    try:
        lines = filePath.open().readlines()
    except:
        print("File "+str(filePath)+" doesn't seem to be a readable text file! Try using HALCON 12 instead of 13 to generated the intrinsics!")
        raise
    lines = map(lambda line: line.strip(), lines)
    lines = filter(lambda line: line != '', lines)
    lines = filter(lambda line: line[0] != '#', lines)
    lines = map(lambda line: line.strip(), lines)
    lines = list(lines)

    # remove ParGroup header
    assert (lines[0].startswith('ParGroup'))
    currentLine = 2
    otherNames = ['Focus', 'Sx', 'Sy', 'Cx', 'Cy', 'ImageWidth', 'ImageHeight']
    expectedNames = _HalconDistortionParameters1 + _HalconDistortionParameters2 + otherNames
    d = {}
    while currentLine < len(lines):
        line = lines[currentLine]
        key = line.split(':')[0]
        assert key in expectedNames, 'Unhandled key found in intrinsics file!'
        value_string = line.split(':')[2].split(';')[0]
        if key in ('ImageWidth','ImageHeight'):
            float_value = float(value_string)
            from numpy import round, abs
            assert abs(round(float_value) - float_value)< .000001, key+' should be an integer!'
            value = int(round(float_value))
        else:
            value = float(value_string)
        currentLine += 3
        d[key] = value

    # If the camera has no radial distortion, fill in the ~other radial distortion model.
    if 'Kappa' in d and d['Kappa'] == 0.0:
        #print('Detected radial distortion free Polynomial model!')
        d['Poly1'] = 0.0
        d['Poly2'] = 0.0
        d['Poly3'] = 0.0
        d['Poly4'] = 0.0
        d['Poly5'] = 0.0
        return d
    if 'Poly5' in d and all((d['Poly1'] == 0.0, d['Poly2'] == 0.0,
                            d['Poly3'] == 0.0, d['Poly4'] == 0.0,
                            d['Poly5'] == 0.0)):
        #print('Detected radial distortion free Division model!')
        d['Kappa'] = 0.0
        return d

    #if 'Kappa' in d:
        #print('Loading a camera with non-zero kappa... sanity checking distortion model invertiblity...')
        #from camera_models import check_distortion_model_invertability
        #check_distortion_model_invertability(d)

    return d


def load_intrinsics(filePath):
    """ Load and convert the HALCON representation of the camera matrix
        into the representation closer to that used by open source
        programs.
        Input:
            filePath -- The name of the file to read
        Output:
            The 3x3 camera projection matrix K, distortion coefficients, image width, image height, and focal length
            x_pixel_homogeneous = K*x_camera_frame
        """
    d = load_halcon_intrinsics(filePath)
    camera_matrix = numpy.zeros([3, 3])

    fx = d['Focus'] / d['Sx']
    fy = d['Focus'] / d['Sy']
    camera_matrix[0, 0] = fx
    camera_matrix[1, 1] = fy

    cx = d['Cx']
    cy = d['Cy']
    camera_matrix[0, 2] = cx
    camera_matrix[1, 2] = cy
    camera_matrix[2, 2] = 1.0

    if 'Poly5' in d:
        k1 = d['Poly1']
        k2 = d['Poly2']
        k3 = d['Poly3']
        p1 = d['Poly4'] * .001
        p2 = d['Poly5'] * .001
        distCoeffs = {'k1':k1, 'k2':k2, 'p1':p1, 'p2':p2, 'k3':k3}
        distCoeffs['model'] = 'halcon_area_scan_polynomial'
    elif 'Kappa' in d:
        distCoeffs = {'kappa':d['Kappa']}
        distCoeffs['model'] = 'halcon_area_scan_division'
    else:
        distCoeffs = ()
    distCoeffs['cx'] = cx  # Note: these are also in the camera_matrix, but are also used when compensating radial distortion
    distCoeffs['cy'] = cy
    distCoeffs['pixel_w'] = d['Sx']
    distCoeffs['pixel_h'] = d['Sy']
    return camera_matrix, distCoeffs, d['ImageWidth'], d['ImageHeight'], d['Focus']


def rodriguez_vector_to_SO3(a1,a2,a3, implementation='giplib'):
    """ Converts from an axis, angle rotation representation to a 3x3 matrix representation. 
        The angles are assumed to be in radians! """
    assert implementation in ['giplib','scipy']
    if implementation == 'giplib':
        # This implementation was ported over from giplib.
        from numpy import cos,sin,sqrt
        angle = sqrt(a1**2 + a2**2 + a3**2)
        if angle == 0:
            return numpy.eye(3)
        phi = angle
        rx = a1 / angle
        ry = a2 / angle
        rz = a3 / angle
        cosPhi = cos(phi)
        sinPhi = sin(phi)
        l_cosPhi = 1.0 - cosPhi
        rxRyl_cosPhi = rx * ry * l_cosPhi
        rxRzl_cosPhi = rx * rz * l_cosPhi
        return numpy.array([[ cosPhi+(rx**2)*l_cosPhi, rxRyl_cosPhi-rz*sinPhi, ry*sinPhi+rxRzl_cosPhi],
                            [rz*sinPhi+rxRyl_cosPhi, cosPhi+(ry**2)*l_cosPhi, ry*rz*l_cosPhi-rx*sinPhi],
                            [rxRzl_cosPhi-ry*sinPhi, rx*sinPhi+ry*rz*l_cosPhi, cosPhi+(rz**2)*l_cosPhi]])
    elif implementation == 'scipy':
        # A more straightforward way... not sure what is faster or more accurate.
        # Added this mainly to check the correctness of above port.
        import scipy
        a,b,c = a1,a2,a3
        skew = numpy.matrix([[0,-c,b],
                            [c,0,-a],
                            [-b,a,0]])
        return scipy.linalg.expm(skew)


def load_halcon_intrinsics_ascii(filePath):
    """ Load directly from HALCON's ascii format for camera extrinsics.
        HALCON supports 12 different rotation parameterizations.
        As a result, their write_pose function writes ascii files that
        could be any of them.
        This function attempts to load these ascii files and convert
        the results to a homogeneous matrix representation that maps camera
        coordinates to world coordinates.
        For the documentation for HALCON's rotation parameterization codes
        see the table in the documentation for the create_pose operator.
        """
    assert filePath.is_file()
    try:
        lines = filePath.open().readlines()
    except:
        print("File "+str(filePath)+" doesn't seem to be a readable text file containing extrinsics!")
        raise
    lines = map(lambda line: line.strip(), lines)
    lines = filter(lambda line: line != '', lines)
    lines = filter(lambda line: line[0] != '#', lines)
    lines = map(lambda line: line.strip(), lines)
    lines = list(lines)

    rotation_parameterization_code = -1 # Sentinel for "not set"

    d = {}
    expected_keys = set(('f','r','t'))
    for line in lines:
        key = line[0]
        assert key in expected_keys, "Unrecognized character at start of line while parsing extrinsics!"
        expected_keys.remove(key)
        if line[0]=='f':
            rotation_parameterization_code = int(line.split(' ')[1])
            continue
        value = numpy.array(tuple(map(float,list(line.split(' '))[1:])))
        d[key] = value

    anglevector = d['r']*numpy.pi/180 # Supposedly the angles in the ascii files are in degrees... 
    if rotation_parameterization_code == -1:
        assert False, 'Unable to find the rotation parameterization code in the file '+str(filePath)
    elif rotation_parameterization_code == 0:
        # gba euler angles. R = Rx * Ry * Rz
        from numpy import sin,cos,pi
        rx,ry,rz = anglevector[0], anglevector[1], anglevector[2] # Still in radians
        # Check HALCON's definitions for Rx, Ry, Rz here: 
        #http://www.mvtec.com/doc/halcon/13/en/hom_mat3d_rotate.html
        Rx = numpy.matrix([[1,0,0],
                        [0,cos(rx),-sin(rx)],
                        [0,sin(rx),cos(rx)]])
        Ry = numpy.matrix([[cos(ry),0,sin(ry)],
                        [0,1,0],
                        [-sin(ry),0,cos(ry)]])
        Rz = numpy.matrix([[cos(rz),-sin(rz),0],
                        [sin(rz),cos(rz),0],
                        [0,0,1]])

        # Check HALCON's gba rotation order here by "Representation of Orientation":
        # http://www.mvtec.com/doc/halcon/13/en/create_pose.html
        R = numpy.array(Rx*Ry*Rz) # Matrix multiplication
        T = d['t']
        #print('R=',R,'T=',T)
        #R,T = R.T,numpy.dot(-R.T,T) # Invert the transform
    else:
        assert False, "Sorry, rotation parameterization "+str(rotation_parameterization_code)+"not handled yet!"
    # This will be needed for codes 4,5,12, and 13
    #R = rodriguez_vector_to_SO3(anglevector[0], anglevector[1], anglevector[2])
    return R,T


def load_halcon_extrinsics_homogeneous(filePath):
    """ HALCON has a function for converting camera extrinsics (Pose) to a 
        homogeneous matrix. Often I use this function to write out the
        homogeneous transformation to an ASCII file. This function loads
        that format.
        Input:
        filePath -- The path of the text file containing the homogeous matrix
        Output:
        The Rotation matrix and Translation vector associated with the camera.
        The matrices are for the transformation from the camera frame to
        world coordinate frame, i.e. x_world = R*x_camera + T
        T is in whatever units the camera calibration was done in (usually meters).
        If you need the transformation in the other direction you can do:
        R,T = R.T,numpy.dot(-R.T,T) # Invert the transform
        """
    strings = filePath.open().readlines()[0].strip().split(' ')
    assert len(strings)==12
    H = numpy.array(tuple(map(float,strings))).reshape((3,4))
    R = H[:,0:3]
    T = H[:,3]
    return R, T

def load_extrinsics(filePath):
    # Automatically detect the file format, so that this function
    # works with both types of ascii based HALCON extrinsics formats.
    try:
        lines = filePath.open().readlines()
    except:
        print("File "+str(filePath)+" doesn't seem to be a readable text file!")
        raise
    for line in lines:
        if 'Rotation angles [deg] or Rodriguez vector:' in line:
            #print('Rodriquez type HALCON extrinsics file detected!')
            return load_halcon_intrinsics_ascii(filePath)
    #print('Homogeneous type HALCON extrinsics file detected!')
    return load_halcon_extrinsics_homogeneous(filePath)


def load_all_camera_parameters(calibration_path, throw_error_if_radial_distortion=False):
    ''' Load the camera parameters for every camera in the array '''
    
    # I have a couple filename conventions floating around to support...
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
        
    all_camera_parameters = []
    for i in range(num_cameras):
        # Load the intrinsics
        intrinsicsFilePath = calibration_path / (intrinsics_pattern % (i + 1))
        print('Loading intrinsics for camera',i,'from',intrinsicsFilePath,'...')
        assert intrinsicsFilePath.is_file(), "Couldn't find camera intrinsics in "+str(intrinsicsFilePath)
        camera_matrix, distortion_coefficients, image_width, image_height, f = load_intrinsics(intrinsicsFilePath)
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

        # Load the extrinsics
        extrinsicsFilePath = calibration_path / (extrinsics_pattern % (i + 1))
        print('Loading extrinsics for camera',i,'from',extrinsicsFilePath,'...')
        R, T = load_extrinsics(extrinsicsFilePath)

        # OpenCV and PMVS2 expect the inverse of the transform that HALCON exports!
        R,T = R.T,numpy.dot(-R.T,T) # R,T, now map world coorinates into camera coordinates
        camera_parameters = {'camera_matrix':camera_matrix, 'R':R, 'T':T, 'image_width':image_width, 'image_height':image_height, 'f':f}
        camera_parameters.update(distortion_coefficients)
        all_camera_parameters.append(camera_parameters)
    return all_camera_parameters # List of dictionaries
