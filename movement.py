import numpy as np
import visual_kinematics
from visual_kinematics.RobotSerial import *
import math


# initialization
pi = math.pi
scale = 1000

#matrix row | d | a | alpha | theta
#joint 1 to 2 has 58.82 deg angle -> 0.3267*π  0.3267*pi
dh_params = np.array([[0, 0., pi/2, 0*pi],
                      [298.7/scale, 215.67/scale, pi/2, pi/2],
                      [0., (274.51+(71.3+10.8))/scale, 0, pi/2.],
                      [0, 0.25, 0, 0.]])

dh_params2 = np.array([[0, 0., pi/2, pi/2],
                      [298.7/scale, 215.67/scale, -pi/2, pi/2],
                      [0., (274.51+(71.3+10.8))/scale, -pi/2, -pi/2.]
                      ])

dh_params = dh_params2

#4th row to see the load orientation
robot = RobotSerial(dh_params)

# peirazeis to n+1 aftou p theleis (n)
theta = np.array([np.deg2rad(0), np.deg2rad(0), np.deg2rad(0)])
# theta = np.array([pi/2, pi/2, pi/2])
f = robot.forward(theta)

print("-------forward-------")
print("end frame t_4_4:")
print(f.t_4_4)
print("end frame xyz:")
print(f.t_3_1.reshape([3, ]))
print("end frame abc:")
print(f.euler_3)
print("end frame rotational matrix:")
print(f.r_3_3)
print("end frame quaternion:")
print(f.q_4)
print("end frame angle-axis:")
print(f.r_3)



robot.show()
