# from test_inverse import inverse_kinematics 
import numpy as np
from movementProgress import ForwardKinematics, TLink
from sympy import *
from sympy.matrices import Matrix
import docx
import math

def point_to_transformation_matrix(point):

    x, y, z, theta,zeta = point
    T = Matrix([
        [cos(theta) * cos(zeta), -sin(zeta) * cos(theta), sin(theta),x ],
        [sin(zeta), cos(zeta), 0,y ],
        [-sin(theta) * cos(zeta), sin(theta) * sin(zeta), cos(theta),z ],
        [0, 0, 0, 1 ]
    ])
    #pprint(T)
    return T



def print_joint_angles_for_points(points):
    scale = 1000
    a3 = 215.6 / scale
    d3 = 298.7 / scale
    a5 = 356.6 / scale

    for i, point in enumerate(points, 1):
        T = point_to_transformation_matrix(point)
        angles = inverse_kinematics(T, a3, a5, d3)  
        print(f"Point {i}: {angles}")

    


def inverse_kinematics(TGe, a1, a3, d1):
    scale=1000
    a1=215.6/scale
    d1=298.7/scale
    a3=356.6/scale
 
    # Extracting elements directly from the matrix using indexing
    x = TGe[0, 3]
    z = TGe[2, 3]
    y = TGe[1, 3]
    theta1 = atan2(-TGe[2,2], -TGe[0,2])
    if (theta1 != 0):
        theta2 = atan2((-x + TGe[2,2]*a1)/TGe[2,2]*a3, -(y+d1)/a3) # theta1 != 0
    else: 
        theta2 = atan2((z + TGe[0,2]*a1)/TGe[0,2]*a3, -(y+d1)/a3)  # theta1 != pi/2
    theta3 = atan2(TGe[1,1], -TGe[1,0])-theta2

    return round(math.degrees(theta1), 2), round(math.degrees(theta2), 2), round(math.degrees(theta3), 2)



via_points = [
   (1, 0, 0.1, -pi/2,pi/2),
   (1.2, 0.2, 0.7, -pi/2,pi/2),
   (1.4, 0.4, 0.9, -pi/2,pi/2),
   (1.6, 0.6, 1.1, -pi/2,pi/2),
   (1.8, 0.8, 1.3, -pi/2,pi/2),
   (2, 1, 1.5, -pi/2,pi/2),
   (2.2, 1.2, 1.7, -pi/2,pi/2),
   (2.4, 1.4, 1.9, -pi/2,pi/2),
   (2.6, 1.6, 2.2, -pi/2,pi/2),
   (0.6553, 0.2156 , 0, 1,pi/2)
   
]



print_joint_angles_for_points(via_points)