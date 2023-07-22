# 3D-Reconstruction with Uncalibrated Stereo

## Problem Statement

## Abstract

## Plan of Action

1. [Uncalibrated Stereo](#us)
2. [Epipolar Geometry](#eg)
3. [Fundamental Matrix]
4. [Correspondences]
5. [Estimating Depth]

------------------------------

<a name="us"></a>
## 1. Uncalibrated Stereo
In the previous project - [Pseudo LiDARS with Stereo Vison](https://github.com/yudhisteer/Pseudo-LiDARs-with-Stereo-Vision) - we have seen how we could use two sets of cameras separated by a distance ```b``` (baseline) and using the intrinsic and extrinsic parameters, we would calculate the disparity, build a depth map, and ultimately get the distances of objects. In that scenario, all the parameters were provided to us from the KITTI dataset. 

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

### 2.4 Essential Matrix
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



















-------------------
<a name="fm"></a>
## 3. Fundamental Matrix



--------------------
## References
