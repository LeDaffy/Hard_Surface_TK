import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import BSpline


def bspline(control_points: np.ndarray, degree=2):
    ctrl_length = len(control_points.T[0])
    degree = np.clip(degree, 1, ctrl_length - 1)
    t = np.r_[np.zeros(degree+1),
              np.arange(1, ctrl_length-degree, 1),
              np.ones(degree+1)*(ctrl_length-degree)]
    t = t/t[-1]
    return BSpline(t, control_points, degree, extrapolate=True)
    

# k = 2
c = np.array([[0, 0, 0], [1, 2, 0], [2, 3, 1], [3, 0, 2], [4,0, 2], [5,0, 1]])
# print(type(c))
# length = len(c.T[0])
# t = np.r_[np.zeros(k+1), np.arange(1, length-k, 1), np.ones(k+1)*(length-k)]
# t = t/t[-1]
# print(f"{t}")
# spline = BSpline(t, c, k, extrapolate=True)

spline_1= bspline(c, 1)
spline_2= bspline(c, 2)
spline_3= bspline(c, 3)
spline_4= bspline(c, 4)
spline_5= bspline(c, 5)
xx = np.linspace(0, 1, 2000)

fig, ax = plt.subplots()
ax = fig.add_subplot(111, projection='3d')
data_1 = np.array(spline_1(xx)).T
data_2 = np.array(spline_2(xx)).T
data_3 = np.array(spline_3(xx)).T
data_4 = np.array(spline_4(xx)).T
data_5 = np.array(spline_5(xx)).T
ax.plot3D(data_1[0], data_1[1], data_1[2], '-', linewidth=3)
ax.plot3D(data_2[0], data_2[1], data_2[2], '-', linewidth=3)
ax.plot3D(data_3[0], data_3[1], data_3[2], '-', linewidth=3)
ax.plot3D(data_4[0], data_4[1], data_4[2], '-', linewidth=3)
ax.plot3D(data_5[0], data_5[1], data_5[2], '-', linewidth=3)
ax.plot3D(c[:,0], c[:,1], c[:,2], 'ro',c[:,0], c[:,1], 'r-')
plt.show()
