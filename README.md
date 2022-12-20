# Hard Surface Tools

A collection of hard surface modeling tools designed to aid in creating mesh based fillets on boolean objects.
Tools are implement in Python using the Blender Python and BMesh APIs.

Example fillets created using default tools vs the tools from this repository are shown below.

Default Tools Result       |  Custom Tools Result      |  Fillet Applied To Result
:-------------------------:|:-------------------------:|:-------------------------:
![](./images/two_cylinders/default.png)  |  ![](./images/two_cylinders/fillet.png) | ![](./images/two_cylinders/smoothed.png)
![](./images/profile_test/default.png)  |  ![](./images/profile_test/custom.png) | ![](./images/profile_test/custom_fillet.png)
![](./images/cube_sphere_diff/default.png)  |  ![](./images/cube_sphere_diff/fillet.png) | ![](./images/cube_sphere_diff/smoothed.png)
![](./images/cube_sphere_union/default.png)  |  ![](./images/cube_sphere_union/fillet.png) | ![](./images/cube_sphere_union/smoothed.png)

