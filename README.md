# 3D-Reconstruction with Uncalibrated Stereo

## Problem Statement

## Abstract

## Datasets

1. KITTI Dataset

    - [3D Object Detection Evaluation](https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d)
   
2. Middlebury Datasets:

    - [Temple Dataset](https://www.cvlibs.net/datasets/kitti/)

    - [Rock Dataset](https://www.cvlibs.net/datasets/kitti/)

3. Fountain Dataset

    - [Fountain-P11 Dataset](https://www.cvlibs.net/datasets/kitti/)


## Plan of Action

1. [Uncalibrated Stereo](#us)
2. [Epipolar Geometry](#eg)
3. [Essential Matrix](#em)
4. [Fundamental Matrix](#fm)
5. [Correspondences](#cc)
6. [Estimating Depth](#ed)
7. [Multi-View Stereo](#mvs)
8. [Structure from Motion](#sfm)

------------------------------

<a name="us"></a>
## 1. Uncalibrated Stereo
In the previous project - [Pseudo LiDARS with Stereo Vision](https://github.com/yudhisteer/Pseudo-LiDARs-with-Stereo-Vision) - we have seen how we could use two sets of cameras separated by a distance ```b``` (baseline) and using the intrinsic and extrinsic parameters, we would calculate the disparity, build a depth map, and ultimately get the distances of objects. In that scenario, all the parameters were provided to us from the KITTI dataset. 

But what if we have two images of the same scene taken by two different persons and perhaps two different cameras and we know the internal parameters of the cameras. From these two arbitrary views, can we compute the translation and rotation of one camera w.r.t another camera? If so. can we compute a 3D model of the scene? In this project, we will devise a method to estimate the 3D structure of a static scene from two arbitrary views.

**Assumption**:

1. Intrinsic parameters ![CodeCogsEqn](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/093227d8-b5ea-4ec7-8a9f-163b8c829d9e) are **known** for both cameras. (Obtained from metadata of image)
2. Extrinsic parameters (relative position and orientation of the cameras) are **unknown**.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f72dcf36-1ecf-48e4-9a8a-92ed343b8afe" width="700" height="370"/>
</div>

**Steps**:
1. Find **external parameters**, i.e., the relationship between the 3D coordinate frames of the two cameras.

2. To achieve this, we need to find reliable **correspondences** between the two arbitrary views. For calibration, a minimum of **eight matches** is sufficient.

3. Once correspondences are established, we can determine the **rotation** and **translation** of each camera with respect to the other. This calibrates the stereo system, and then we can find **dense correspondences**.

4. **Dense correspondences** mean finding the corresponding points in the right image for every point in the left image. Knowing the rotation and translation facilitates a **one-dimensional search** to find the dense 
correspondences.

5. With the dense correspondence map, we can **triangulate** and find the 3D location of points in the scene, computing their **depth**.

-------------------

<a name="eg"></a>
## 2. Epipolar Geometry

Our goal is to find the **relative position** and **orientation** between the two cameras (calibrating an uncalibrated stereo system). The relative position and orientation are described by the **epipolar geometry** of the stereo system. It is represented as ```t``` and ```R``` in the image below. 


### 2.1 Epipoles

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/98801dd8-0fdb-4de7-bd3b-332521c6c141" width="700" height="370"/>
</div>


The epipoles (![CodeCogsEqn (18)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/491c74fa-2510-4017-ac2a-0bade6224275) and  ![CodeCogsEqn (19)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/a9995a9c-10e9-4d82-8cdb-df66d5acf57d)) of the stereo system are the ```projections of the center of the left camera onto the right camera image``` and the ```center of the right camera onto the left camera image```. Note that for any stereo system, the epipoles are unique to that system.


### 2.2 Epipolar Plane
The epipolar plane of a scene point ```P``` is defined as the plane formed by the **camera origins** ![CodeCogsEqn (22)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/02f527bb-7a8d-41fd-a6c9-22c82a7c8f1c), **epipoles** ![CodeCogsEqn (21)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/50884222-f111-48d3-b57e-2e409495a1f3)
, and the **scene point P**. Note that each point in the scene has a unique epipolar plane.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/4475786f-a47f-4176-9f56-25e15962e21e" width="700" height="370"/>
</div>

### 2.3 Epipolar Constraint
We first calculate the vector that is normal to the epipolar plane. We compute the cross-product of the unknown translation vector and the vector that corresponds to point P in the left coordinate frame. Moreover, we know that the dot product of the normal vector with ![CodeCogsEqn (24)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2437c9a3-a2da-47da-ba58-a694f542f544) should be zero which then gives us our ```epipolar constraint```:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/4b36ce9a-42b5-48ca-a014-f149d4f88504"/>
</div>

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/123b0a2c-c6bf-4b84-8e46-6b6a4bf23781" width="700" height="370"/>
</div>

We re-write our epipolar constraint as vector then matrix form. Note that the 3x3 matrix is known as the translation matrix.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/5cb67f78-7bfa-41f6-bd28-86fa7e5e3dad"/>
</div>

We have a second constraint such that we can relate the three-dimensional coordinates of a point P in the left camera to the three-dimensional coordinates of the same point in the right camera using ```t``` and ```R```.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/30aea9df-bb1b-4282-932a-f7c77600951e"/>
</div>

Now if we substitute equation 2 into equation 1:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/1665e78e-57c6-4e1e-aa10-e60267b69303"/>
</div>

In the equation above the product of the translation matrix with the translation vector is zero:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e155290f-032d-4aa7-9efb-dd85c8247745"/>
</div>

Hence, we are left with the equation below:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9ea5660d-7c44-4fbf-88c0-366820bf6ee7"/>
</div>

The product is the translation matrix with the rotation matrix gives the ```Essential matrix```:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/a1fff7e8-df6e-43de-8d7e-2a67972d7e67"/>
</div>

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/4b242ccb-7a82-4ae5-afbf-6f7c586e4500"/>
</div>

Hence, plugging in our equation above:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e5d86db9-6238-4bf2-a429-592981be710e"/>
</div>

--------------------------

<a name="em"></a>
## 3. Essential Matrix
Note that it is possible to decompose our Essential Matrix into the translation and rotation matrix. Notice the translation matrix ![CodeCogsEqn (35)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e598cc88-039b-45a0-80a7-292b8a5aa205) is a **skew-symmetric matrix** and ```R``` is an **orthonormal matrix**. It is possible to ```decouple``` the translation matrix and rotation matrix from their product using **Singular Value Decomposition**. Therefore, if we can compute the Essential Matrix, we can calculate the translation ```t``` and rotation ```R```. Once we have these two unknowns, we have calibrated our uncalibrated stereo system.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/14efeccb-beb8-41c2-9264-55524a173130"/>
</div>

One issue with the epipolar constraint is that ![CodeCogsEqn (38)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2a21d317-7afb-4a42-9ddb-b0daf4d994ba) both represents the 3D coordinates of the same scene point and we do not have this information. That is, when we take two pictures, two arbitrary views of the scene, we do not have the locations of points in the scene in 3D. In fact, that's exactly what we hope to recover ultimately. 


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/3a699080-9f2b-464c-b5a6-fb0f640440c0"/>
</div>

However, we do have the image coordinates of the scene points, that is the projection of the scene onto the images - ![CodeCogsEqn (39)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/89d5781a-3137-4e93-af56-1574a04f75fa)

To incorporate the image coordinates, we start with the perspective projection equations of the left camera.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/cc94be73-892d-47ff-bc26-6d9a28ffc4dc"/>
</div>

We multiply the two equations by z:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/55842666-6ba5-4d3a-a2f2-517e0c0db7fe"/>
</div>

Now using Homogeneous Coordinates:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f3ae128e-845e-4536-ab3d-c40d6dd13ee0"/>
</div>


We then have the product of this 3x3 camera matrix and the three-dimensional coordinates of the point scene point in the left camera - X and Y and Z. Note that we know the camera matrix as we assumed we know all the internal parameters of the two cameras.

We then have a left and right camera equation and this is all corresponding to the same point in the scene:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/5da9a97a-2a59-42fb-b1ad-d94c9591b658"/>
</div>

Re-writing the equations above in a more compact form:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c1a91c36-3f5c-4992-ab5b-2af1c7473bd2"/>
</div>

We want to make ![CodeCogsEqn (46)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c49ebfd7-20bc-4c92-9785-1b64f30d31f8) and ![CodeCogsEqn (47)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e0f963c7-121c-49fd-a814-c18e43e5d1f7) the subject of formula:

Left Camera

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/24eac60e-90d8-4db0-9224-ef51ce0bd269"/>
</div>

Right camera:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/72e1403a-6970-4b62-b933-27ec3763ee4e"/>
</div>

Recall our epipolar constraint:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/3a699080-9f2b-464c-b5a6-fb0f640440c0"/>
</div>


We now substitute ![CodeCogsEqn (50)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/44c3d2c6-0c82-433e-8ee5-9986ba2ae963) and ![CodeCogsEqn (51)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/48baee72-9da5-4478-ad87-03213de8facc) in the equation above:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/357e7975-3218-43ea-92e1-135d3bea0f17"/>
</div>

Note that in the equation above, we have our image coordinates and essential matrix, however, we also  have ![CodeCogsEqn (53)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/7a540c37-3a3a-495d-b32b-46c8cd648a65) and ![CodeCogsEqn (54)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2f44b520-6bde-40e2-a5f7-a438ed838157) which are the depth of the same scene point in the two cameras.

In the camera coordinates frame, the center is located at the effective pinhole of the camera). Consequently, the **depth of any point cannot be zero**, except when the point coincides with the center of projection. Considering that the world is situated in front of the camera, it is reasonable to assert that ![CodeCogsEqn (53)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/884ea43e-37e1-42bc-be36-47de1016a1ca) and ![CodeCogsEqn (54)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/dfb50a8f-c491-4500-9308-908ee4369088)
 (depth values) are **not equal to zero**.


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2c5db1b9-2eac-4674-9900-777e294c4638"/>
</div>

Hence, if ![CodeCogsEqn (53)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/884ea43e-37e1-42bc-be36-47de1016a1ca) and ![CodeCogsEqn (54)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/dfb50a8f-c491-4500-9308-908ee4369088) are not equal to zero, then the rest of the equation should be equal to zero because on the right-hand side we have zero. So we can simply eliminate ![CodeCogsEqn (53)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/884ea43e-37e1-42bc-be36-47de1016a1ca) and ![CodeCogsEqn (54)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/dfb50a8f-c491-4500-9308-908ee4369088) from this equation to get an expression:


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/40ac5610-69fa-4421-beef-49e60500f1e6"/>
</div>

Note that ![CodeCogsEqn (57)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/06f9f3fb-e61f-45f2-9ed1-4a52ce946001) and ![CodeCogsEqn (58)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9df927ba-c64d-42d1-b902-5dc8b373f7d1) are 3x3 matrices hence, the product of  ![CodeCogsEqn (57)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f49a45e4-d645-4e46-a3a8-7fa0c9922bf4) with the Essential matrix and ![CodeCogsEqn (58)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9f4b9485-b096-4331-bbfe-5dac3199206d) also gives a 3x3 matrix known as the **Fundamental Matrix**:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/cd04dd61-a140-489a-9b25-8a58cc575e5a"/>
</div>

Re-writing:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/ce761a8e-b133-48c4-bf51-5c3650db9ec7"/>
</div>

One important observation is that finding the **fundamental matrix** using the given constraint enables us to easily derive the **essential matrix**. Since we have prior knowledge of ![CodeCogsEqn (61)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9dcf8bc8-6176-4ea1-8217-84c0e0a69e3d) and ![CodeCogsEqn (62)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/6b890933-8bbc-4b17-8ed8-afab177d6853)  internal parameters, determining the essential matrix becomes straightforward. By applying **singular value decomposition** to the essential matrix, taking into account the **skew-symmetry** of the translation matrix (```T```) and the orthogonality of the rotation matrix (```R```), we can decompose it into its constituent parts to obtain ```T``` and ```R```.


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/b80f3a1d-7f32-4a9e-b724-274dba74aebb"/>
</div>


-------------------
<a name="fm"></a>
## 4. Fundamental Matrix

We now have our epipolar constraint, which essentially tells us that there is a single 3x3 matrix - the fundamental matrix that we need to find to calibrate our uncalibrated stereo system. So our goal here is to estimate the fundamental matrix.

Initially, our task is to identify a limited number(normally ```8```) of corresponding features in the provided pair of images. Although the features might appear different due to the distinct viewpoints, applying techniques like **SIFT** to both images allows us to obtain reliable matches. These matches will serve as a starting point for further analysis.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/76770783-5086-421d-b05f-0d13a64152db" width="680" height="240"/>
</div>

Let's take one of these correspondences of the left and right images  and plug them into our epipolar constraint:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/99c00ff8-af2e-4ad0-b2aa-49cc7b4dd771"/>
</div>

We know the image coordinates in the left and right camera image hence, we only need to find the Fundamental matrix. We expand the matrix to get a linear equation for one scene point:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/7f4a137d-eb02-4088-bb12-c8db41f254ea"/>
</div>

If we now stack all these equations for all corresponding points then we get:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/cf7f99a4-1e24-4d0b-aafd-ad867b6b67a0" width="680" height="140"/>
</div>


Which can also be written as a more compact form as:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/fb29f36c-2161-4f2c-86a8-7dc948b842c2"/>
</div>

Note that we know everything in matrix ```A``` as it only includes the image coordinates in the left and right cameras. We also have the fundamental matrix written as a vector ```f```. The fundamental matrix ```F``` and the fundamental matrix ```K x F``` describe equivalent epipolar geometries. This implies that ```F``` is only defined up to a **scale factor**, allowing for scaling without changing the resulting images. Consequently, the scale of ```F``` can be adjusted accordingly.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e470fd0c-b01b-4728-ba81-548273fa6d23"/>
</div>


Next, we need to find the least squares solution for the fundamental matrix ```F```. We want ```Af```  as close to ```0``` as possible and ![CodeCogsEqn (71)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/80e08e55-9a2d-4704-80e8-3820c58b26df)(same as saying we are fixing the scale of ```F```):


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/ef9c345e-53d0-4db6-bd71-7f135af840e4"/>
</div>

such that:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/72139703-c777-415c-a9b9-e08381a67b6a"/>
</div>

This is referred to as a **constrained linear least squares problem**.

Recall, we saw the same when solving the **Projection Matrix** during **Camera calibration** in the [Pseudo LiDARS with Stereo Vision](https://github.com/yudhisteer/Pseudo-LiDARs-with-Stereo-Vision) project.

Since now we have the **Fundamental Matrix** ```F```, we need to compute the **Essential Matrix** ```E``` from known left and right intrinsic camera matrices. And once we have the Essential Matrix, we can decompose it using **Singular Value Decomposition** into the **translation** and **rotation** matrix.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/392d2cb2-98c9-45c4-9ea7-db3a68084bf7"/>
</div>


    Our uncalibrated stereo system is now fully calibrated!

--------------------

<a name="cc"></a>
## 5. Correspondences

With our stereo system now **fully calibrated**, the next step is to identify correspondences between points in the left and right images. Our goal is to find the corresponding point in the right image for **every point** in the left image. Ultimately, this process will enable us to create a detailed ```depth map``` of the 3-dimensional scene.

Recall in a simple stereo setup, there are two cameras: the left camera and the right camera. Their relationship is straightforward, with the right camera positioned horizontally at a distance called the **baseline** from the left camera. Both cameras have parallel optical axes, so any point in the left image corresponds to a point in the right image lying on the **same horizontal scanline**. This makes stereo matching reduced to a **1-dimensional search**. The same principle applies to uncalibrated stereo systems.

<div align="center">
  <img src="https://github.com/yudhisteer/Pseudo-LiDARs-and-3D-Computer-Vision/assets/59663734/079b502a-8779-46b9-b317-9b34e615393b" width="780" height="480"/>
</div>

In uncalibrated stereo setups, the stereo matching problem still involves a one-dimensional search. After finding the rotation and translation between the two cameras, the question arises about which line in the right image to search for corresponding points.

Recall the epipolar plane is unique for any given point in a scene. It includes the point ```P```, the epipoles, and the center of the two cameras. The epipolar plane intersects with our two image planes to produce the epipolar lines as shown in pink above. Hence, every scene point has two corresponding epipolar lines, one each on the two image planes.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/19955146-8f22-4098-923f-a6a42b04e8a3" width="700" height="370"/>
</div>

When we have a point in the image plane, for example, ![CodeCogsEqn (78)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9d17674c-b871-4180-afda-7cb1d98fc767) in the left image plane, then the corresponding point in the right image must lie on the epipolar line on the right image plane. If we take into consideration u_l, which represents a single outgoing ray, the epipolar line is defined by projecting all the points on this ray onto the right image. Consequently, for any point on this ray, finding its matching point in the right image involves a search along a single line. However, the question remains: which particular line should we search along?

It has been found that, with the **fundamental matrix** and points in the left image, it is possible to derive the **equation of the straight line** in the right image. This equation serves as a guide during the search process to find the corresponding matching points.

    Once more, the process of finding correspondents reduces to a 1-dimensional search.


### 5.1 Epipolar Line

Let's assume we have the Fundamental Matrix ```F``` and a single point in the left image ![CodeCogsEqn (79)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/4bc2d31b-66a2-4202-9f92-8866f131aebe). In the equation below, we want to find an expression for ![CodeCogsEqn (80)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/3e4fa54f-2fae-43df-b245-3c5c136d4d4d):

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/0720b618-c03f-4b85-891b-8d7600a1c88c"/>
</div>

By expanding our matrix equation:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/090970fa-ac69-4bd7-924a-de1914a40169"/>
</div>

Simplifying furthermore we have the equation of a straight line:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e6324936-a533-4185-b53c-55db38f58a8b"/>
</div>


When we have the fundamental matrix, for any point provided in the left image, it becomes possible to determine the specific line in the right image where the corresponding point should be located. Likewise, if we have a point in the right image, I can use the same method to calculate the equation for the epipolar line in the left image. This equation then directs the search to find the corresponding point for the given point in the right image.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/9348fcb1-9679-4d23-9828-07e048a16bde" width="700" height="240"/>
</div>

To establish correspondences between points in the left and right images, we take a small window around a point in the left image and apply **template matching** along the determined red line in the right image. This process helps us find the best-matching point in the right image for the given point in the left image, enabling accurate matching between the two images.


Once we have the corresponding pairs in the left and right images, we can use these pairs for triangulation, enabling the computation of the depths of the three-dimensional coordinates for points in the scene.

--------------------

<a name="ed"></a>
## 6. Estimating Depth

At this stage, we have established correspondences between points in the left and right images. Now, our objective is to utilize the image coordinates of these corresponding pairs to estimate the three-dimensional coordinates of each point in the scene. This process, known as **triangulation**, allows us to compute the **spatial positions** accurately.


Below are the equations for point ```P``` in the 3D coordinate frame of the left and right camera being projected onto the image perspective projection using the internal parameters onto the image plane. Note that the 3x4 matrices are the intrinsic matrices.

Left Camera Imaging Equation:
<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/bc2776b4-b6d0-4829-bb99-c6da815a59b1"/>
</div>

Right Camera Imaging Equation:
<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/22d91758-4dc9-4ea1-a60f-8b912631f47d"/>
</div>

Note that since we have now calibrated our uncalibrated stereo system, we also have the relative position and orientation between the two cameras:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/99d24cd2-64e3-4a3a-a732-043b450ee316"/>
</div>

We thus substitute it in the left camera imaging equation:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/42113b28-08a9-44d2-8041-657090d12479"/>
</div>
    
<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/0b06c587-c462-4809-9cf1-b6a6403f7c06"/>
</div>

Note that the product of the intrinsic matrix and the extrinsic matrix becomes the **Projection Matrix**.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/731928ce-c9cb-4170-8a03-3acfb658881d"/>
</div>


Keeping the Right Camera Imaging Equation the same:
<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/22d91758-4dc9-4ea1-a60f-8b912631f47d"/>
</div>

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2c583df9-d0df-416c-b922-240968db4c38"/>
</div>

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c4ae1f0c-1938-4d51-a2cf-629872af870d"/>
</div>

When we arrange these two equations we get it in the form of:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/6773cb5f-6df7-4b61-81e3-76979530a73a"/>
</div>

This is an overdetermined system of linear equations. We find the least squares using pseudo-inverse:


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/caf2d684-0141-40db-b095-be09e9c05121"/>
</div>

We repeat this for every pair of corresponding points in the left and right images and then that gives us a complete **3D depth map** of the scene. This is how we go from arbitrary views to death maps of the scene through this calibration process.


---------------------

<a name="mvs"></a>
## 7. Multi-View Stereo

Multi-View Stereo ```(MVS)``` is a technique used for dense ```3D reconstruction``` of scenes using ```multiple 2D images``` of the same scene taken from **different viewpoints**. MVS aims to generate a dense 3D representation of the scene, where every pixel in the images is assigned a corresponding 3D point in the ```reconstructed space```.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/659a32a0-6a58-4c70-9e6e-fe24ba096c50" width="580" height="370"/>
</div>

When working with matching images with known camera parameters, the 3D geometry of the scene allows for establishing ```correspondences``` between pixels in different images. When camera parameters are known, matching a pixel in one image with pixels in another image becomes a one-dimensional ```(1D)``` search problem.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/8b8e8aa6-4cf4-4368-8dac-07cb1c3f7c73"/>
</div>

Matching pixels across images is a challenging problem that is not unique to stereo or multi-view stereo. **Optical flow** is another active field that addresses the problem of ```dense correspondence``` across images. However, there are some key differences between MVS and optical flow:

1. Optical flow typically deals with a ```two-image problem```, similar to two-view stereo, whereas MVS involves ```multiple images```.

2. In optical flow, camera calibration is ```not assumed```, while MVS **relies** on known camera parameters.

3. The main application of **optical flow** is ```image interpolation``` and ```motion estimation```, whereas **MVS** is primarily focused on ```3D reconstruction``` and ```depth estimation``` of a scene.

### 7.1 Two-view Stereo Reconstruction
Before we dive into MVS, let's try something simpler: the Two-View Stereo. We pick up where we left off in the [Pseudo LiDARS with Stereo Vision](https://github.com/yudhisteer/Pseudo-LiDARs-with-Stereo-Vision) project. 

We start by taking two pictures from the KITTI Dataset: a left and right image:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/087b23b1-4fe4-4a5c-ab66-17fedcc3151e" width="700" height="200"/>
</div>

We then calculate the disparity using ```Stereo-Global Block Matching (SGBM)``` algorithm between these two images:

```python
    # Compute disparity map
    disparity_map = compute_disparity(left_image, right_image, num_disparities=90, block_size=5, window_size=5, matcher="stereo_sgbm", show_disparity=True)
```

The result:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f225fe14-c38f-4750-b156-7294c51eafb9" width="600" height="250"/>
</div>

#### 7.1.1 Q-Matrix
In order to use the ```reprojectImageTo3D``` function from OpenCV, we first need to calcuate the Q-matrix also known as the ```Disparity-to-depth mapping matrix```.


**Q-matrix**
- 4x4 matrix that takes the disparity value and calculates the depth of the point in 3D space.
- It represents the relationship between disparity values and depth.

**Depth Map**
- 2D image that represents the depth of each pixel in the image.

**Disparity Map**
- 2D image that represents the difference between pixel disparities in left and right images of a stereo pair.
- Used to calculate the depth of a point in 3D space.

In summary, the Q-matrix provides the mathematical mapping between pixel disparities abd 3D coordinates. It allows us to transform the disparity information captured by the stereo camera system into depth information which we can use to perform tasks as 3D reconstruction or scene understanding and so on.

```python
    # Compute Q matrix
    Q = np.zeros((4, 4))

    # Perform stereo rectification
    _, _, _, _, Q, _, _ = cv2.stereoRectify(cameraMatrix1=camera_matrix_left,
                                            cameraMatrix2=camera_matrix_right,
                                            distCoeffs1=None,
                                            distCoeffs2=None,
                                            imageSize=left_image.shape[:2],  # Provide the image size
                                            R=np.identity(3),
                                            T=np.array([baseline[0], 0., 0.]),  # Translation vector
                                            R1=None,
                                            R2=None,
                                            P1=None,
                                            P2=None,
                                            Q=Q)
```

```python
[[   1.            0.            0.         -609.5593338 ]
 [   0.            1.            0.         -172.85400391]
 [   0.            0.            0.          721.53771973]
 [   0.            0.           -1.8771874     0.        ]]
```

We can now use the Q-matrix and disparity map to obtain 3D points:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/0ba12e93-f74c-47b7-a91e-f78883b5f162"/>
</div>

Where:

- b: baseline
- d: disparity value (u,v)
- ![CodeCogsEqn (95)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/262774f2-6e39-45da-a3b5-62147881345a): 3D coordinates of scene point in Homogeneous coordinates.

- ![CodeCogsEqn (94)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c17961d2-ca0c-4ca3-a441-89dbe90a70a4): Q-matrix
- ![CodeCogsEqn (96)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/19965676-fba5-4dc5-8449-44cbeeb45b80): pixel coordinates
- ![CodeCogsEqn (97)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/2cb66b3e-83f8-4d6d-8955-e88587058417) and ![CodeCogsEqn (98)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/39f5cf02-486f-482e-bd1c-d2d039e0795c): optical centers
- ![CodeCogsEqn (99)](https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/73cf58dc-6c1e-4464-9f72-e2fbf4212efa): Is equal to 0 if aligned.


```python
    # Obtain 3D points from the disparity map
    points = cv2.reprojectImageTo3D(disparity_map.copy(), Q)
```

Below is the result of a 3D reconstruction scene:

<video src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/db26dd45-2190-44fe-b537-cac4da3a038e" controls="controls" style="max-width: 730px;">
</video>


### 7.2 Multi-view Stereo Reconstruction
We will now dive into multi-view stereo. We will take two datasets: [Temple of the Dioskouroi in Agrigento, Sicily](https://vision.middlebury.edu/mview/data/) and [The Rock](https://vision.middlebury.edu/mview/data/). We have ```12``` images for each dataset and for each image we have their **extrinsic** and **intrinsic** parameters.

Below is a video for the 12 images for the datasets:

<table>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c3a85dfa-39a4-405f-b11c-588bc3bfaace" alt="GIF 1" style="height: 500px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/a199f156-3964-4fcc-bb00-d0a1227e30ea" alt="GIF 2" style="height: 500px;"></td>
  </tr>
</table>


#### 7.2.1 Topologies
Recall that we had to calculate the disparity between two images. In the Two-view Reconstruction, it was pretty straightforward however, when we have more than 2 images then we have different ways to calculate the disparity between images. Below are ```5``` topologies to calculate disparities. We can choose to have either a dense 3D model at the end with ```360``` or ```overlapping``` topologies,  a medium dense point cloud with ```adjacent``` or a sparse one with  ```skipping_1``` and ```skipping_2```.


<table>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/b9704d53-022c-44e3-a95c-79b84954ff1c" alt="Image 1" style="height: 170px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f21e0f17-fde5-41e2-8b20-11118b06441f" alt="Image 2" style="height: 170px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c00d64e1-5377-49fd-8d99-3a5e58b1da46" alt="Image 3" style="height: 170px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/fa0c79b2-9a8e-431f-8e9b-8cb302502acd" alt="Image 4" style="height: 170px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/48385c9d-2055-4114-b41b-31e6a4708cb3" alt="Image 5" style="height: 170px;"></td>
  </tr>
</table>

Below is the code for the topologies:

```python
topologies['360'] = tuple(zip((0,1,2,3,4,5,6,7,8,9,10,11),
                              (1,2,3,4,5,6,7,8,9,10,11,0)))

topologies['overlapping'] = tuple(zip((0,1,2,3,4,5,6,7,8,9,10),
                                      (1,2,3,4,5,6,7,8,9,10,11)))

topologies['adjacent'] = tuple(zip((0,2,4,6,8,10),
                                   (1,3,5,7,9,11)))

topologies['skipping_1'] = tuple(zip((0,3,6,9),
                                     (1,4,7,10)))

topologies['skipping_2'] = tuple(zip((0,4,8),
                                     (1,5,9)))
```

#### 7.2.2 Camera Calibration
Before rectification, the **intrinsic** and **extrinsic** parameters of the two cameras are estimated through a calibration process. The calibration determines the ```camera matrices```, ```distortion coefficients```, and ```relative pose``` (rotation and translation) between the cameras.

```python
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
        'channels': 1,
        # Number of color channels in the camera images. 1 for grayscale images, 3 for RGB color channels.
        'num_cameras': 12,  # Total number of cameras in the camera array.
        'topology': 'adjacent'
        # Spatial arrangement or topology of the camera array ('adjacent', 'circular', 'linear', 'grid', etc.).
    }

```


#### 7.2.3 Rectification
Stereo rectification is a geometric transformation applied to a pair of stereo images to make them appear as if they were taken from the **same viewpoint**. The goal of stereo rectification is to simplify the **stereo correspondence** problem by ```aligning the epipolar lines``` in the two images.

The rectification process **warps** the two images so that their epipolar lines become **parallel** to the horizontal axis. This ensures that for each point in one image, its corresponding point in the other image lies along the **same horizontal scan line**. Rectification simplifies the stereo-matching process as it reduces the search space for finding corresponding points from ```2D``` search to ```1D```.

```python
    # 1. Rectification
    left_image_rectified, right_image_rectified = rectify_and_show_results(opencv_matcher, image_index=index, show_image=False)

```

```left_maps``` or ```right_maps``` represents the rectification maps for the left or right camera. These rectification maps are used to transform the pixels of the original left or right image to their corresponding positions in the rectified left or right image. The ```cv2.initUndistortRectifyMap``` function generates two maps, ```left_maps[0]``` and ```left_maps[1]```, which are needed for the rectification process. These maps are essentially lookup tables that define the pixel correspondence between the original and rectified images.

1. **left_maps[0]**: Represents the **horizontal (x) displacement map**. It contains the ```x-coordinate``` of the destination pixel in the rectified image for each pixel in the original left image. When applied to the original left image, it remaps the pixels to their new positions in the rectified image along the horizontal direction.

2. **left_maps[1]**: Represents the **vertical (y) displacement map**. It contains the ```y-coordinate``` of the destination pixel in the rectified image for each pixel in the original left image. When applied to the original left image, it remaps the pixels to their new positions in the rectified image along the vertical direction.

Below is the image of the rock, the ```left_maps[1]``` and ```left_image_rectified```.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/dd6d86bb-3cd3-4a09-b0e7-4bdcf2e3b8c7" width="700" height="220"/>
</div>




#### 7.2.4 Disparity Estimation
Once the images are rectified, they can be re-projected into 3D space using **disparity** information. 

```python
 # StereoMatcherOptions
    StereoMatcherOptions = {
        'MinDisparity': -64,  # Minimum disparity value, influences the maximum depth.
        'NumDisparities': 256,  # Number of disparities, influences the minimum depth.
        'BlockSize': 21,  # Size of the window used for matching (odd number).
        'SpeckleWindowSize': 0,  # Speckle window size, must be strictly positive to turn on speckle post-filter.
        'SpeckleRange': 0,  # Speckle range, must be >= 0 to enable speckle post-filter.
        'Disp12MaxDiff': 0  # Maximum allowed difference (in integer pixel units) in the left-right disparity check.
    }

    # StereoBMOptions
    StereoBMOptions = {
        'PreFilterType': (cv2.StereoBM_PREFILTER_NORMALIZED_RESPONSE, cv2.StereoBM_PREFILTER_XSOBEL)[0],
        # Pre-filter type, can be StereoBM_PREFILTER_NORMALIZED_RESPONSE or StereoBM_PREFILTER_XSOBEL.
        'PreFilterSize': 5,  # Size of the pre-filter kernel, must be odd and within the range 5..255.
        'PreFilterCap': 63,  # Pre-filter cap, must be within the range 1..63. Used to truncate pixel values.
        'TextureThreshold': 10,  # Texture threshold, minimum difference to accept the computed disparity.
        'UniquenessRatio': 10
        # Uniqueness ratio, defines the minimum margin between the best and second-best matching cost.
    }

    # StereoSGBMOptions
    StereoSGBMOptions = {
        'PreFilterCap': 0,  # Pre-filter cap.
        'UniquenessRatio': 0,
        # Uniqueness ratio, defines the minimum margin between the best and second-best matching cost.
        'P1': 16 * 21 * 21,  # "Depth Change Cost"
        'P2': 16 * 21 * 21,  # "Depth Step Cost"
        'Mode': (cv2.StereoSGBM_MODE_SGBM, cv2.StereoSGBM_MODE_HH,
                              cv2.StereoSGBM_MODE_SGBM_3WAY)[1]
        # Matching mode, can be StereoSGBM_MODE_SGBM, StereoSGBM_MODE_HH, or StereoSGBM_MODE_SGBM_3WAY.
    }
```


```python
    # 2. Disparity
    disparity_img = compute_and_show_disparity(left_image_rectified, right_image_rectified)
```

Below is the disparity map using ```SGBM```:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/55e5203e-5937-4420-bd8e-9cc32cd65233" width="500" height="370"/>
</div>



#### 7.2.5 Project to 3D
We will now use our Q-matrix and disparity map to project our image into 3D space.


```python
    # 3. Project to 3D
    output_file_path = reproject_and_save_ply(disparity_img, opencv_matcher, index, output_folder)
```

The 3D reconstruction of the rock:

<video src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/c6d8e1ee-2041-4e83-9a85-f70188ebedb8" controls="controls" style="max-width: 730px;">
</video>


The 3D reconstruction of the temple:

<video src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/bd0126a6-5715-488b-a940-6080eaae5d4a" controls="controls" style="max-width: 730px;">
</video>


Note that we got better results for The Rock due to its non-complex structure and a better disparity map. We also have some noise which needs to be filtered. For the Temple's point cloud, we can see the outline of the temple but it is obstructed by noise. For further improvement, **CreSTEREO** can be used to build a better disparity map.

------------------

<a name="sfm"></a>
## 8. Structure from Motion
Structure from Motion aims to recover the three-dimensional (3D) structure of a scene and camera motion from a set of 2D images or video frames. In simpler terms, it's about reconstructing the 3D shape of objects and the camera's trajectory as it moves through a scene, using only the 2D images or video as input.


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/a3267af1-0c78-461d-a894-244e4ff70939" width="380" height="370"/>
</div>

The process of Structure from Motion typically involves the following steps:

1. **Feature Detection and Matching**: Distinctive features, such as ```corners```, ```edges```, or ```keypoints```, are detected in each image. These features are then matched across multiple images to find corresponding points.

2. **Camera Pose Estimation**: Given the correspondences between image points, the next step is to estimate the camera poses (positions and orientations) for each image. This process can be achieved using techniques like the ```RANSAC``` algorithm. This step is most important as we will need to estimate the **Fundamental Matrix** and from it the **Essential Matrix**. Then decompose the Essential Matrix to recover the relative **rotation** and **translation** matrix.

3. **Triangulation**: Triangulation is the process of finding the ```3D coordinates``` of points in the scene by intersecting corresponding rays from multiple camera viewpoints.

4. **Bundle Adjustment**: Bundle adjustment is an ```optimization``` process used to refine the camera poses and 3D points simultaneously. It minimizes the reprojection error, which is the difference between the observed image points and the reprojected 3D points on the image plane.


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/f59f1d9a-c3b9-4e45-ada6-25f129aa8561" width="800" height="150"/>
</div>


The result of the Structure from Motion process is a **sparse** 3D point cloud representation of the scene and the camera poses for each image frame.



### 8.1 Two-View Structure from Motion
Similarly to MVS, let's start simple with two images and reconstruct a 3D model. We will use the [Fountain Dataset](http://certis.enpc.fr/demos/stereo/Data/Fountain11/index.html) which consists of ```11``` images.

<p align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/daa56216-4a19-40e9-90d5-7365dd92463b" alt="GIF" style="height: 300px;">
</p>

#### 8.1.1 Feature Matching
We will now use the **SIFT** algorithm in order to find the matching features on two images. We will also need the x-y coordinates of these matching features.

```python
    ### --------------- FEATURE MATCHING ----------------------- ###

    # Feature Matching using SIFT
    keypoints1, descriptors1, keypoints2, descriptors2, good_matches = match_features_sift(img1_rgb, img2_rgb, show_image=True)

    # Obtain the image coordinates (x, y) of the matched keypoints in both images
    img1pts, img2pts = get_matched_keypoints_coordinates(keypoints1, keypoints2)
```
Note that if the two images are quite different or have a significantly different orientation then it will be hard to find matching features. For example, in the image below we only have ```46``` matching features.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/bb8ed3dc-a620-4092-bbd4-3c8c97ef9094" width="700" height="300"/>
</div>

If we take two pictures with minimal orientation change, then we have the possibility of having more features matching. Here we have ```1577``` features from both images.

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/0a702090-7a98-44ba-bb78-0fa2a46cddba" width="700" height="300"/>
</div>

#### 8.1.2 Fundamental Matrix
We will now use the ```findFundamentalMat``` function from OpenCV to find the Fundamental Matrix, ```F```. The function also returns the mask, which indicates the inliers used to estimate ```F```. We will try different algorithms to calculate F: **FM_LMEDS**, **FM_8POINT**, **FM_RANSAC** and **FM_7POINT**.

```python
    ### --------------- FUNDAMENTAL MATRIX ----------------------- ###

    F, mask = find_fundamental_matrix(img1pts, img2pts)
```

```python
[[-2.32608990e-08 -4.14097505e-07  2.13234106e-04]
 [ 1.10774376e-06 -9.43696790e-08  1.04326766e-02]
 [-1.17953256e-03 -1.15538347e-02  1.00000000e+00]]
```

#### 8.1.3 Epipolar Lines
Using the Fundamental Matrix ```F``` and feature matching coordinates, we will compute the epipolar lines.

```python
    ### --------------- EPIPOLAR LINES ----------------------- ###

    # Compute epipolar lines for both images
    lines_img1 = compute_epipolar_lines(F, img1pts, 1)
    lines_img2 = compute_epipolar_lines(F, img2pts, 2)
```

We will then plot these lines on our images:

```python
    # # Draw epipolar lines on both images
    img1_copy_1, img2_copy_2 = draw_epipolar_lines(img2_rgb, img1_rgb, lines_img2, img2pts, img1pts, draw_only=10)
    img1_copy_3, img2_copy_4 = draw_epipolar_lines(img1_rgb, img2_rgb, lines_img1, img1pts, img2pts, draw_only=10)
```

Below is the result of the epipolar lines when trying different algorithms for the Fundamental Matrix:

<table>
  <tr>
    <th>FM_7POINT</th>
    <th>FM_8POINT</th>
  </tr>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/81c2ec47-878f-4e3c-8e28-defa0a4dca88" alt="Image 1" style="height: 200px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/17921aef-0b3c-4541-9a51-c8f3a7a91048" alt="Image 2" style="height: 200px;"></td>
  </tr>
  <tr>
    <th>FM_LMEDS</th>
    <th>FM_RANSAC</th>
  </tr>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/ec05ce80-ee25-4269-98c0-dd8d482ace04" alt="Image 3" style="height: 200px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/184161bd-8a4a-4d36-b6e6-e75d4bed61a0" alt="Image 4" style="height: 200px;"></td>
  </tr>
</table>


#### 8.1.4 Essential Matrix
Note that we have the intrinsic parameters (given in the dataset) but not the extrinsic ones. Hence, we have our ```K``` matrix - our Camera Matrix  and we will it to estimate the Essential Matrix.

```python
    ### --------------- ESSENTIAL MATRIX ----------------------- ###

    K = np.array([[2759.48, 0, 1520.69],
                  [0, 2764.16, 1006.81],
                  [0, 0, 1]])

    E = K.T.dot(F.dot(K))
```

```python
[[ -0.17712546  -3.15858845  -0.6596703 ]
 [  8.44947533  -0.72103913  33.2312819 ]
 [ -0.27489299 -33.93990701  -0.68567946]]
```

#### 8.1.5 Camera Pose
We derived the Essential Matrix from the Fundamental Matrix. Now, we will decompose the Essential Matrix to recover ```R``` and ```t```.
Recall the formula:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/b80f3a1d-7f32-4a9e-b724-274dba74aebb"/>
</div>

```python
    ### --------------- CAMERA POSE ----------------------- ###

    retval, R, t, mask = cv2.recoverPose(E, img1pts, img2pts, K)
```
Where **R** = 

```python
[[ 0.98756121 -0.02267659 -0.1555912 ]
 [ 0.02552626  0.99954058  0.01634136]
 [ 0.15514915 -0.02010975  0.98768636]]
```
and **t** = 

```python
[[ 0.99550392]
 [ 0.0178422 ]
 [-0.09302477]]
```

#### 8.1.6 Triangulation
We will now use triangulation and get the 3D point cloud using the ```triangulatePoints``` function from OpenCV. The steps are as follows: 

1. Convert 2D points to homogeneous coordinates
2. Normalize 2D points using the camera intrinsic matrix (K)
3. Convert back to inhomogeneous coordinates
4. Triangulate 3D points using OpenCV's triangulatePoints function
5. Convert 4D homogeneous points to inhomogeneous 3D points

```python
    ### --------------- TRIANGULATION ----------------------- ###

    points_3d = triangulate_points(img1pts, img2pts, K, R, t)
```

#### 8.1.7 Project to 3D
Since now we have the 3D points, we can also extract the colors from the image and then save the point cloud in a ```.ply``` format with the respective color.

```python
    ### --------------- IMAGE COLOR EXTRACTION ----------------------- ###

    # Extract color from img1_rgb
    colors_img1 = []
    for pt in img1pts:
        x, y = np.round(pt).astype(int)
        color = img1_rgb[y, x]
        colors_img1.append(color)

    colors_img1 = np.array(colors_img1)

    # Extract color from img2_rgb
    colors_img2 = []
    for pt in img2pts:
        x, y = np.round(pt).astype(int)
        color = img2_rgb[y, x]
        colors_img2.append(color)

    colors_img2 = np.array(colors_img2)

    # Define the file name for the PLY file
    output_file_path = os.path.join(output_folder, f"out_color{index}.ply")

    # Write the points and colors to the PLY file
    write_ply(output_file_path, points_3d, colors_img1)
    print("Point cloud with color saved to:", output_file_path)
```

From this sparse point cloud, we see that we successfully extracted the color and shape of the golden fish in the middle and the golden plate at the top. We have an outline of the fountain. Notice that we have less noise compared to MVS however, we also have a less dense point cloud.

<table>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/daa56216-4a19-40e9-90d5-7365dd92463b" alt="Image 1" style="height: 300px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/3b3082fb-f410-4712-ba41-77d679582472" alt="Image 2" style="height: 300px;"></td>
  </tr>
</table>



### 8.2 Multi-View Structure from Motion
Now we will see how to construct a 3D point cloud with all 11 images. As in MVS, we will make use of the topologies to calculate the fundamental matrix. We will use the ```overlapping``` one
and we will get ```10``` separate point cloud. We will need to ```vstack``` them in order to get a combined 3D reconstructed model. Below is the result of the separate 3D models:

https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/8e4310d8-ad82-4ac3-8520-5e409c1aa5aa

Notice that from the first model, we get a good outline of the fountain and then when we superimpose the other point clouds, they also have a good outline however they are not correctly aligned. It seems that all of them have a different center, hence a different orientation and position.


### 8.3 Bundle Adjustment
In SfM, the camera poses and 3D points are initially estimated from feature correspondences in the images. However, due to noise, inaccuracies, and unmodeled factors during the initial reconstruction, the estimated 3D points may not perfectly align with the observed image points as we saw above.

Bundle Adjustment aims to improve the accuracy of the reconstruction by finding the best possible camera poses and 3D point positions that minimize the discrepancies between the projected 3D points and the actual image observations. It considers all the images simultaneously, taking into account the correlations between camera poses and 3D points, to achieve a globally optimal solution. It simultaneously adjusts the camera positions and orientations, as well as the positions of the 3D points, in order to minimize the ```reprojection error``` between the 2D image observations and their corresponding 3D points.

Some methods for Bundle Adjustment:

1. **Levenberg-Marquardt (LM)**: It is an iterative method that combines the steepest descent method and the Gauss-Newton method to efficiently find the optimal parameters.

2. **Gauss-Newton**: The Gauss-Newton algorithm is an iterative method used to solve non-linear least squares problems.

3. **Conjugate Gradient (CG)**: Conjugate Gradient is an iterative method used to solve large-scale linear systems.

4. **Sparse Bundle Adjustment (SBA)**: SBA is an extension of Bundle Adjustment that takes advantage of the sparsity in the Jacobian matrix, which represents the derivatives of the cost function with respect to the camera poses and 3D points.

5. **Robust Bundle Adjustment**: Robust techniques, such as Huber loss or Tukey loss, can be applied to Bundle Adjustment to handle outliers and improve the robustness of the optimization process against noisy or erroneous measurements.


### 8.4  Iterative Closest Point (ICP)
If we have two 3D reconstructions obtained from different viewpoints and want to align them to create a more complete and accurate 3D model, Iterative Closest Point (ICP) could be used to find the best transformation (translation and rotation) that aligns the two points clouds together.

As Bundle Adjustment is a complex and tedious process, I will instead use ICP to enhance the accuracy and completeness of the 3D reconstructions. Below is the result of before and after using ICP:

<table>
  <tr>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/b4b903ed-3e69-4537-a10f-39b3fac0af89" alt="GIF 1" style="height: 300px;"></td>
    <td><img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/0ebf801d-9df4-4174-b445-73bda3d0e71a" alt="GIF 2" style="height: 300px;"></td>
  </tr>
</table>

We successfully aligned both point clouds!

## Conclusion
In this project, we saw the 3D reconstruction of a Rock, Temple, and Fountain using various photogrammetry techniques. We observed that with Multi-View Stereo (MVS) rpovides a denser and more detailed 3D reconstruction, making it preferable for scenes with textureless or repetitive regions. On the other hand, Structure-from-Motion (SFM) is faster and more computationally efficient, making it suitable for real-time applications and smaller scenes. 

<p align="center">
  <img width="600" height="350" alt="image" src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/890a40a3-e73f-4314-891e-5ba698a38b6e">
</p>

However, further improvements can be achieved by incorporating **Neural Radiance Fields (NeRFs)** into the pipeline. NeRFs is an innovative approach to 3D scene reconstruction that utilizes **neural networks** to model ```volumetric``` scenes. Unlike traditional methods such as ```Multi-View Stereo (MVS)``` and ```Structure-from-Motion (SFM)```, which rely on ```sparse point clouds``` or ```depth maps```, NeRFs learn the ```radiance``` at every 3D point in the scene. 

This enables NeRFs to generate **highly detailed** and **photorealistic reconstructions**, even in regions with limited data or texture. NeRFs offer **continuous** and **consistent** scene representation, filling in missing data, refining surface geometry, and providing a comprehensive 3D representation that preserves intricate details. With its ability to leverage information from multiple views and generate high-fidelity renderings, NeRFs **surpass** MVS and SFM in terms of accuracy and realism, making it a superior choice for tasks requiring rich 3D scene understanding and visualization. 

-------------------
## References
1. https://www.youtube.com/watch?v=GQ3W9ltqqrw&list=PLZgpos4wVnCYhf5jsl2HcsCl_Pql6Kigk&index=13&ab_channel=PRGUMDTeaching
2. https://www.youtube.com/watch?v=RGDNs1kQ7NI&list=PLZgpos4wVnCYhf5jsl2HcsCl_Pql6Kigk&index=16&ab_channel=PRGUMDTeaching
3. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://vgl.ict.usc.edu/Research/XimeaRiver/XimeaRiver_EG_2017.pdf
4. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://cs.nyu.edu/~fergus/teaching/vision_2012/6_Multiview_SfM.pdf
5. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://courses.cs.washington.edu/courses/cse455/10wi/lectures/multiview.pdf
6. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://carlos-hernandez.org/papers/fnt_mvs_2015.pdf
7. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.cs.cmu.edu/~16385/s17/Slides/12.4_8Point_Algorithm.pdf
8. https://www.youtube.com/watch?v=zX5NeY-GTO0&ab_channel=CyrillStachniss
9. https://vision.middlebury.edu/mview/data/
10. chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/http://vision.stanford.edu/teaching/cs231a_autumn1112/lecture/lecture10_multi_view_cs231a.pdf
11. http://ksimek.github.io/2013/08/13/intrinsic/
12. https://github.com/cranberrymuffin/voxel-carving
13. https://www.youtube.com/watch?v=yoQ1zHQsugg&t=2s&ab_channel=PrakrutiCatherineGogia
14. https://medium.com/@AaronLeeIV/3d-reconstruction-from-2d-images-cb21096631ad
15. https://arxiv.org/pdf/2003.08934.pdf
16. https://arxiv.org/pdf/1806.08734.pdf
17. https://creiser.github.io/kilonerf/
18. https://jonbarron.info/mipnerf/
19. https://arxiv.org/pdf/2012.03927.pdf
20. https://arxiv.org/pdf/2012.02190.pdf
21. https://lingjie0206.github.io/papers/NSVF/
22. https://nerfies.github.io/
23. https://arxiv.org/pdf/2008.02268.pdf
