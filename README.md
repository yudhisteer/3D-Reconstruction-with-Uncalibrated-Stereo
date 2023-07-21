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
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/4b242ccb-7a82-4ae5-afbf-6f7c586e4500"/>
</div>

Hence, plugging in our equation above:

<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/a1fff7e8-df6e-43de-8d7e-2a67972d7e67"/>
</div>


<div align="center">
  <img src="https://github.com/yudhisteer/3D-Reconstruction-with-Uncalibrated-Stereo/assets/59663734/e5d86db9-6238-4bf2-a429-592981be710e"/>
</div>

### 2.4 Essential Matrix








-------------------
<a name="fm"></a>
## 3. Fundamental Matrix



--------------------
## References
