import copy
import numpy as np
import open3d as o3d
import os

# Get the current directory
current_directory = os.getcwd()

# Go back to the parent directory
parent_directory = os.path.dirname(current_directory)

point_cloud_folder = os.path.join(parent_directory, 'Data', 'Point_Cloud_Fountain')

source_path = os.path.join(point_cloud_folder, "out_1_0.ply")
target_path = os.path.join(point_cloud_folder, "out_1_6.ply")

source = o3d.io.read_point_cloud(source_path)
target = o3d.io.read_point_cloud(target_path)


def draw_registration_result(source, target, transformation):
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)
    source_temp.paint_uniform_color([1, 0.706, 0])
    target_temp.paint_uniform_color([0, 0.651, 0.929])
    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp],
                                      zoom=0.4459,
                                      front=[0.9288, -0.2951, -0.2242],
                                      lookat=[1.6784, 2.0612, 1.4451],
                                      up=[-0.3402, -0.9189, -0.1996])

    return source_temp, target_temp


threshold = 100
trans_init = np.asarray([[0.862, 0.011, -0.507, 0.5],
                         [-0.139, 0.967, -0.215, 0.7],
                         [0.487, 0.255, 0.835, -1.4], [0.0, 0.0, 0.0, 1.0]])

draw_registration_result(source, target, trans_init)

print("Initial alignment")
evaluation = o3d.pipelines.registration.evaluate_registration(source, target, threshold, trans_init)
print(evaluation)

print("Apply point-to-point ICP")
reg_p2p = o3d.pipelines.registration.registration_icp(
    source, target, threshold, trans_init,
    o3d.pipelines.registration.TransformationEstimationPointToPoint())
print(reg_p2p)
print("Transformation is:")
print(reg_p2p.transformation)
source_temp, target_temp = draw_registration_result(source, target, reg_p2p.transformation)

source_path = os.path.join(point_cloud_folder, "source_temp_1_0.ply")
target_path = os.path.join(point_cloud_folder, "target_temp_1_6.ply")

# Save the aligned source point cloud to a PLY file
# aligned_output_file_path = source_path
# o3d.io.write_point_cloud(aligned_output_file_path, source_temp)

aligned_output_file_path = target_path
o3d.io.write_point_cloud(aligned_output_file_path, target_temp)
