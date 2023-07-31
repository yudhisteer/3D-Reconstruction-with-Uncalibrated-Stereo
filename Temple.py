from load_camera_info import load_intrinsics, load_extrinsics
from load_camera_info_temple import load_all_camera_parameters_temple
from load_ply import save_ply
import numpy as np
from pathlib import Path
from IPython.display import display
import inspect
import cv2
import matplotlib.pyplot as plt
import os
from PIL import Image
import collections
from utils import *
import glob
from pyntcloud import PyntCloud
import open3d as o3d
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from ipywidgets import interact, interactive, fixed

def compute_disparity(image, img_pair, num_disparities=6*16, block_size=11, window_size=6, uniqueness_ratio=0, speckleWindowSize=200, matcher="stereo_sgbm", show_disparity=True):
    if matcher == "stereo_bm":
        new_image = cv2.StereoBM_create(numDisparities=num_disparities, blockSize=block_size)
        new_image.setPreFilterType(1)
        new_image.setUniquenessRatio(uniqueness_ratio)
        new_image.setSpeckleRange(2)
        new_image.setSpeckleWindowSize(speckleWindowSize)
    elif matcher == "stereo_sgbm":
        new_image = cv2.StereoSGBM_create(minDisparity=0, numDisparities=num_disparities, blockSize=block_size,
                                         uniquenessRatio=uniqueness_ratio, speckleWindowSize=speckleWindowSize, speckleRange=2, disp12MaxDiff=1,
                                         P1=8 * 1 * window_size **2, P2=32 * 1 * window_size **2)

    new_image = new_image.compute(image, img_pair).astype(numpy.float32) / 16

    if (show_disparity == True):
        plt.figure(figsize=(20, 10))
        plt.imshow(new_image, cmap="plasma")
        plt.show()
    return new_image

def rotate_images_anticlockwise(folder_path):
    # Get a list of all files in the folder
    all_files = os.listdir(folder_path)

    # Filter only the image files
    image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Rotate each image 90 degrees anticlockwise and save it back
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        try:
            image = Image.open(image_path)
            rotated_image = image.transpose(Image.ROTATE_270)
            rotated_image.save(image_path)
        except Exception as e:
            print(f"Error rotating the image {image_file}: {e}")



class OpenCVStereoMatcher():
    global FinalOptions, folder_path
    def __init__(self, options=None, calibration_path=None):
            """
            This class initializes an OpenCV stereo matcher for multi-camera stereo vision using provided options and calibration data.

            Parameters:
            - options: A dictionary containing various options for stereo matching and rectification (default is FinalOptions).
            - calibration_path: The path to the calibration data containing camera parameters (optional).

            Initialization Steps:
            1. Load all camera parameters from the calibration data (if provided).
            2. Initialize arrays to store stereo calibration results, rectification maps, and disparity-to-depth mapping matrices (Q) for each camera pair.
            3. Loop through each camera pair based on the specified topology and perform the following steps:
                a. Get camera intrinsic and extrinsic parameters for the left and right cameras.
                b. Perform stereo calibration and rectification to obtain Q, extrinsics_left_rectified_to_global, left_maps, and right_maps.
                c. Get the stereo matcher based on the provided options.
            """
            self.options = options if options is not None else FinalOptions
            self.calibration_path = folder_path
            self.num_cameras = options['CameraArray']['num_cameras']
            self.topology = options['CameraArray']['topology']
            self.all_camera_parameters = load_all_camera_parameters_temple(folder_path)

            self.left_maps_array = []
            self.right_maps_array = []
            self.Q_array = []
            self.extrinsics_left_rectified_to_global_array = []

            for pair_index, (left_index, right_index) in enumerate(topologies[self.topology]):
                # 1 — Get R, T, W, H for each camera
                left_K, left_R, left_T, left_width, left_height = [self.all_camera_parameters[left_index][key] for key
                                                                   in ('camera_matrix', 'R', 'T', 'image_width',
                                                                       'image_height')]
                right_K, right_R, right_T, right_width, right_height = [self.all_camera_parameters[right_index][key] for
                                                                        key in (
                                                                        'camera_matrix', 'R', 'T', 'image_width',
                                                                        'image_height')]
                h, w = left_height, left_width

                # 2 — Stereo Calibrate & Rectify
                Q, extrinsics_left_rectified_to_global, left_maps, right_maps = calibrate_and_rectify(options, left_K,
                                                                                                      right_K,
                                                                                                      left_R, right_R,
                                                                                                      left_T, right_T)
                self.Q_array.append(Q)
                self.extrinsics_left_rectified_to_global_array.append(extrinsics_left_rectified_to_global)
                self.left_maps_array.append(left_maps)
                self.right_maps_array.append(right_maps)

                # 3 — Get Matcher
                self.matcher = get_disparity_temple(options)

    def load_images(self, folder_path):
        """
        Load a set of images from disk. The images are loaded as grayscale, and no further processing is done yet.

        Parameters:
        - imagesPath: The path to the directory containing the undistorted images.

        The method loads the images from the provided directory, converts them to grayscale, and stores them in the 'images' attribute of the class.

        Note:
        - The 'num_cameras' attribute should already be set in the class instance before calling this method, indicating the expected number of images to load.
        - The 'all_camera_parameters' attribute should also be set, containing information about the expected image sizes.

        """
        # Resolve the provided imagesPath to an absolute path
        imagesPath = folder_path.resolve()

        # Load the undistorted images off of disk
        print('Loading the images off of disk...')
        num_cameras = len(list(imagesPath.glob('*.png')))
        assert self.num_cameras == num_cameras, 'Mismatch in the number of available images!'
        images = []
        for i in range(num_cameras):
            # Construct the filename for the current camera
            fileName = 'image_camera%02i.png' % (i + 1)
            filePath = imagesPath / fileName
            print('Loading image', filePath)

            # Read the color image from disk and convert it to grayscale
            colorImage = cv2.imread(str(filePath))
            grayImage = cv2.cvtColor(colorImage, cv2.COLOR_BGR2GRAY)

            # Check if the image size matches the expected size
            expected_parameters = self.all_camera_parameters[i]
            w, h = expected_parameters['image_width'], expected_parameters['image_height']
            assert grayImage.shape == (w, h), 'Mismatch in image sizes!'

            # Append the grayscale image to the 'images' list
            images.append(grayImage)

        # Store the loaded images in the 'images' attribute of the class instance
        self.images = images

    def run(self):
        # Check if camera parameters have been loaded
        assert self.all_camera_parameters is not None, 'Camera parameters not loaded yet; You should run load_all_camera_parameters first!'

        # Create an array to store the 3D points for each pair of images
        xyz_global_array = [None] * len(topologies[self.topology])

        def run_pair(pair_idx, left_idx, right_idx):
            # Load the proper images and rectification maps
            left_img, right_img = self.images[left_idx], self.images[right_idx]
            left_maps = self.left_maps_array[pair_idx]
            right_maps = self.right_maps_array[pair_idx]

            # Rectify the images
            remap_interpolation = self.options['Remap']['interpolation']
            left_image_rectified = cv2.remap(left_img, left_maps[0], left_maps[1], remap_interpolation)
            right_image_rectified = cv2.remap(right_img, right_maps[0], right_maps[1], remap_interpolation)

            # Load & Find Disparity
            disparity_image = self.matcher.compute(left_image_rectified, right_image_rectified)

            # Convert the disparity image to floating-point format
            if disparity_image.dtype == np.int16:
                disparity_image = disparity_image.astype(np.float32)
                disparity_image /= 16

            # Reproject 3D points from the disparity map using the Q-matrix
            Q = self.Q_array[pair_idx]
            threedeeimage = cv2.reprojectImageTo3D(disparity_image, Q, handleMissingValues=True, ddepth=cv2.CV_32F)
            threedeeimage = np.array(threedeeimage)

            # Postprocess the 3D points
            xyz = threedeeimage.reshape((-1, 3))  # x, y, z now in three columns, in left rectified camera coordinates
            z = xyz[:, 2]
            goodz = z < 9999.0
            xyz_filtered = xyz[goodz, :]

            # Transform the 3D points to global coordinates
            R_left_rectified_to_global, T_left_rectified_to_global = self.extrinsics_left_rectified_to_global_array[
                pair_idx]
            xyz_global = np.dot(xyz_filtered, R_left_rectified_to_global.T) + T_left_rectified_to_global.T

            # Save PLY file for the pair of images
            #save_ply(xyz_global, 'pair_' + str(left_index) + '_' + str(right_index) + '.ply', output_folder)
            xyz_global_array[pair_index] = xyz_global

        # Process each pair of images
        for pair_index, (left_index, right_index) in enumerate(topologies[self.topology]):
            run_pair(pair_index, left_index, right_index)

        # Stack all the 3D points from different pairs into one array
        xyz = np.vstack(xyz_global_array)
        return xyz


def rectify_and_show_results(opencv_matcher, image_index=0, show_image=True):
    """Rectifies the input stereo images and displays the results.

    Args:
        opencv_matcher (OpenCVStereoMatcher): The OpenCVStereoMatcher instance.
        image_index (int, optional): The index of the stereo image pair to rectify and show results. Defaults to 0.
        show_image (bool, optional): Whether to display the results or not. Defaults to True.

    Returns:
        tuple: A tuple containing the rectified left and right images.
    """

    # Get the Images
    img0 = opencv_matcher.images[image_index]
    img1 = opencv_matcher.images[image_index + 1]

    # Get the Maps
    left_maps = opencv_matcher.left_maps_array[image_index]
    right_maps = opencv_matcher.right_maps_array[image_index]

    # Rectify with the parameters
    remap_int = opencv_matcher.options['Remap']['interpolation']
    left_image_rectified = cv2.remap(img0, left_maps[0], left_maps[1], remap_int)
    right_image_rectified = cv2.remap(img1, right_maps[0], right_maps[1], remap_int)

    if show_image:
        # Show Results
        f, (f0, f1, f2) = plt.subplots(1, 3, figsize=(20, 10))
        f0.imshow(img0)
        f0.set_title('Original Left Image')
        f1.imshow(left_maps[1])
        f1.set_title('Left Disparity Map')
        f2.imshow(left_image_rectified)
        f2.set_title('Rectified Left Image')

        f, (f3, f4, f5) = plt.subplots(1, 3, figsize=(20, 10))
        f3.imshow(img1)
        f3.set_title('Original Right Image')
        f4.imshow(right_maps[1])
        f4.set_title('Right Disparity Map')
        f5.imshow(right_image_rectified)
        f5.set_title('Rectified Right Image')
        plt.show()

    return left_image_rectified, right_image_rectified



def compute_and_show_disparity(opencv_matcher, left_image_rectified, right_image_rectified, show_image=True):
    """Computes the disparity map from rectified left and right images using the stereo matcher and displays it.

    Args:
        left_image_rectified (numpy.ndarray): The rectified left image.
        right_image_rectified (numpy.ndarray): The rectified right image.
        show_image (bool, optional): Whether to display the disparity map or not. Defaults to True.

    Returns:
        numpy.ndarray: The computed disparity map.
    """

    # Compute disparity
    matcher = opencv_matcher.matcher
    disparity_img = matcher.compute(left_image_rectified, right_image_rectified)

    if disparity_img.dtype == np.int16:
        disparity_img = disparity_img.astype(np.float32)
        disparity_img /= 16

    if show_image:
        # Show Results
        plt.imshow(disparity_img)
        plt.title('Disparity Map')
        plt.colorbar()  # Add colorbar to show the disparity values
        plt.show()

    return disparity_img


def reproject_and_save_ply(disparity_img, opencv_matcher, index, output_folder):
    """Reprojects the 3D points from disparity image, transforms them into global coordinates, and saves as a PLY file.

    Args:
        disparity_img (numpy.ndarray): The disparity image.
        opencv_matcher (OpenCVStereoMatcher): The OpenCVStereoMatcher instance containing calibration parameters.
        index (int): The index of the stereo pair to process.
        output_folder (str): The folder path where the PLY file should be saved.

    Returns:
        str: The file path of the saved PLY file.
    """

    # Get Q-matrix
    Q = opencv_matcher.Q_array[index]

    # Reproject 3D
    threedeeimage = cv2.reprojectImageTo3D(disparity_img, Q, handleMissingValues=True, ddepth=cv2.CV_32F)
    threedeeimage = np.array(threedeeimage)

    # Postprocess
    xyz = threedeeimage.reshape((-1, 3))  # x,y,z now in three columns, in left rectified camera coordinates
    z = xyz[:, 2]
    goodz = z < 9999.0
    xyz_filtered = xyz[goodz, :]

    # Global Coordinates
    R_left_rectified_to_global, T_left_rectified_to_global = opencv_matcher.extrinsics_left_rectified_to_global_array[index]
    xyz_global = np.dot(xyz_filtered, R_left_rectified_to_global.T) + T_left_rectified_to_global.T

    # Save PLY
    filename = "temple_0"
    output_file_path = os.path.join(output_folder, filename + '.ply')
    save_ply(xyz_global, filename, output_folder)
    print("Saving: ", filename)

    return output_file_path




if __name__ == '__main__':

    # Get the current directory
    current_directory = os.getcwd()

    # Go back to the parent directory
    parent_directory = os.path.dirname(current_directory)

    # Set input directory
    rock_folder = os.path.join(parent_directory, 'Data', 'rock', 'undistorted')
    temple_folder = os.path.join(parent_directory, 'Data', 'temple', 'undistorted')
    output_folder = os.path.join(parent_directory, 'Data', 'Output')

    # # Call the function to rotate images in the temple_folder
    # rotate_images_anticlockwise(temple_folder)


    # Choose index of image
    index = 0

    # Choose folder
    input_folder = temple_folder

    # Folder path
    folder_path = Path(input_folder)

    # Get a list of all files in the rock_folder directory
    all_files = os.listdir(input_folder)

    # Filter only the image files (e.g., PNG or JPG)
    image_files = [file for file in all_files if file.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # Create a list of image paths by joining the filenames with the rock_folder path
    images = [os.path.join(input_folder, image_file) for image_file in image_files]

    # Call the function to read, rotate, and convert the images
    images_cv = read_and_rotate_images(images)

    # Get parameters of image
    h, w, d = images_cv[index].shape
    print(h, w, d)

    ### -------------------- TOPOLOGIES ---------------------------- ###

    topologies = collections.OrderedDict()
    topologies['360'] = tuple(zip((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11),
                                  (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0)))

    topologies['overlapping'] = tuple(zip((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10),
                                          (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)))

    topologies['adjacent'] = tuple(zip((0, 2, 4, 6, 8, 10),
                                       (1, 3, 5, 7, 9, 11)))
    topologies['skipping_1'] = tuple(zip((0, 3, 6, 9),
                                         (1, 4, 7, 10)))
    topologies['skipping_2'] = tuple(zip((0, 4, 8),
                                         (1, 5, 9)))





    ### -------------------- CAMERA CALIOBRATION AND RECTIFICATION ---------------------------- ###

    # StereoRectifyOptions
    StereoRectifyOptions = {
        'imageSize': (w, h),
        # Specifies the desired size of the rectified stereo images. 'w' and 'h' are width and height, respectively.
        'flags': (0, cv2.CALIB_ZERO_DISPARITY)[0],
        # Flag for stereo rectification. 0: Disparity map is not modified. cv2.CALIB_ZERO_DISPARITY: Zero disparity at all pixels.
        'newImageSize': (w, h),  # Size of the output rectified images after the rectification process.
        'alpha': 0.5
        # Balance between preserving all pixels (alpha = 0.0) and completely rectifying the images (alpha = 1.0).
    }

    # RemapOptions
    RemapOptions = {
        'interpolation': cv2.INTER_LINEAR
        # Interpolation method used during the remapping process. Bilinear interpolation for smoother results.
    }

    # CameraArrayOptions
    CameraArrayOptions = {
        'channels': 3,
        # Number of color channels in the camera images. 1 for grayscale images, 3 for RGB color channels.
        'num_cameras': 12,  # Total number of cameras in the camera array.
        'topology': 'skipping_2'
        # Spatial arrangement or topology of the camera array ('adjacent', 'circular', 'linear', 'grid', etc.).
    }




    ### -------------------- DISPARITY ESTIMATION ---------------------------- ###

    # StereoMatcherOptions
    StereoMatcherOptions = {
        'MinDisparity': 0,
        'NumDisparities': 64,
        'BlockSize': 7,
        'Disp12MaxDiff': 0,
        'PreFilterCap': 0,
        'UniquenessRatio': 15,
        'SpeckleWindowSize': 50,
        'SpeckleRange': 1
    }

    # StereoSGBMOptions
    StereoSGBMOptions = {
        'PreFilterCap': 0,
        'UniquenessRatio': 0,
        'P1': 8,  # "Depth Change Cost
        'P2': 32,  # "Depth Step Cost
    }

    # FinalOptions
    FinalOptions = {
        'StereoRectify': StereoRectifyOptions,  # Options for stereo rectification.
        'StereoMatcher': StereoMatcherOptions,  # Options for the stereo matcher (either StereoBM or StereoSGBM).
        'StereoSGBM': StereoSGBMOptions,  # Options for StereoBM (set to StereoSGBMOptions if needed).
        'CameraArray': CameraArrayOptions,  # Options for the camera array configuration.
        'Remap': RemapOptions  # Options for remapping.
    }

    # Initialize Class
    opencv_matcher = OpenCVStereoMatcher(options=FinalOptions, calibration_path=folder_path)

    # Print Q-matrix to check
    print(opencv_matcher.Q_array[0])

    # Load images
    opencv_matcher.load_images(folder_path)

    # Check images
    plt.imshow(opencv_matcher.images[index])
    plt.show()

    # 1. Rectification
    print("\nRectification")
    left_image_rectified, right_image_rectified = rectify_and_show_results(opencv_matcher, image_index=index, show_image=False)

    # 2. Disparity
    print("\nDisparity")
    disparity_img = compute_and_show_disparity(opencv_matcher, left_image_rectified, right_image_rectified)

    # num_d = (0, 512, 16)
    # b_s = (1, 31, 2)
    # window_s = (1, 13, 2)
    # uniqueness_r = (0, 10, 1)
    # speckle_w = (0, 250, 50)
    #
    # # Replace the display() function with plt.show()
    # disparity_left = interactive(compute_disparity, image=fixed(left_image_rectified),
    #                              img_pair=fixed(right_image_rectified), num_disparities=num_d, block_size=b_s,
    #                              window_size=window_s, matcher=["stereo_sgbm", "stereo_bm"],
    #                              uniqueness_ratio=uniqueness_r, speckleWindowSize=speckle_w)
    # plt.show()  # Instead of display(disparity_left)

    # 3. Project to 3D
    print("\nProject to 3D")
    output_file_path = reproject_and_save_ply(disparity_img, opencv_matcher, index, output_folder)

    # 4. Visualize 3D image
    # print("\nVisualize 3D image")
    # object_3d = PyntCloud.from_file(output_file_path)
    # object_3d.plot()

    # 5. Run in all images
    xyz = opencv_matcher.run()
    save_ply(xyz, "temple_skipping_2", output_folder)
    output_file_path = os.path.join(parent_directory, 'Data', 'Output', 'temple_skipping_2.ply')
    print("Saving: ", output_file_path)
    # # object_3d = PyntCloud.from_file(output_file_path)
    # # object_3d.plot()

    # Load the PLY file
    pcd = o3d.io.read_point_cloud(output_file_path)

    # Visualize the point cloud
    visualization_draw_geometry(pcd)


