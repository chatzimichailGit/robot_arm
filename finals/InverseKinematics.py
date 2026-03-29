'''
   Inverse Kinematics 
   previous file: testing1_withNewHTM.py

'''
import sympy as sp
import numpy as np
import math

# Symbolic variables for points generation
x, y, z, phi = sp.symbols('x y z phi')

# Define a 1x4 matrix for Cartesian coordinates and roll angle
Pcart = sp.Matrix([x, y, z, phi])

# Define start and end points
PA = Pcart.subs({x: -0.1468314744, y:  -0.572165406573, z: 0.1232062360612, phi: 35})
PB = Pcart.subs({x: -0.1867150770559, y: -0.57321, z: 0.1078, phi: 45})

# Define via points
Pvia = {
    1: Pcart.subs({x: 0.2156, y: 0.5722, z: 0.6553, phi: 90}),
    2: Pcart.subs({x: -0.2074348413120, y: -0.5721654065731, z: 0.1197625614708, phi: 45}),
    3: Pcart.subs({x:  0, y: -0.57321, z: 0.2156, phi: 45}), #starting with new homogeneous
    4: Pcart.subs({x: -0.114250593, y:-0.57321, z:0.18283916, phi: 0}),
    5: Pcart.subs({x:  -0.0940053416, y:-0.57053848755, z:0.15043999410, phi: 0}),
    6: Pcart.subs({x:  -0.1616103863372, y:-0.55825430418, z:0.258630681507, phi: 0}),
    7: Pcart.subs({x:  0.00076533, y:-0.44820886, z:-0.01460342, phi: 0}),
    8: Pcart.subs({x: 0.02837775, y: -0.31306674, z:-0.05119481, phi: 0}),
    # Add more via points as needed
}

# Combine all points
Points = [PA] + [Pvia[i] for i in sorted(Pvia)] + [PB]


#Validation with forward kinematics
def ForwardKinematics(theta1, theta2, theta3):
    d1,  L2, L3 = sp.symbols('d1,  L2, L3')
    theta4, theta5 = sp.symbols('theta4, theta5')
    a1, a2, a3, d3 = sp.symbols('a1, a2, a3, d3')
    
    theta1=math.radians(theta1)
    theta2=math.radians(theta2)
    theta3=math.radians(0)

    scale = 1000
    a1 = 215.6 / scale
    d1 = 298.7 / scale
    a2 = 274.51 / scale
    a3 = 71.3 / scale
    # #end validation for Inverse

    # a | α | d | θ 135 -80 0
    DH4 = sp.Matrix([
        [0,sp.pi/2,d1,theta1],
        [a1,-sp.pi/2,0,theta2],
        [a2,0,0,theta3]
    ])

    DH = DH4

    TG0 = TLink(DH.row(0))
    T01 = TLink(DH.row(1))
    T12 = TLink(DH.row(2))
    TGe = TG0 * T01 * T12 

    TGe = sp.simplify(TGe)

    return TGe


def TLink(DH):
    # DH parameters
    a, alpha, d, theta = DH

    # Initialize a symbolic T matrix
    T = sp.Matrix([
        [sp.cos(theta), -sp.sin(theta), 0, a],
        [sp.sin(theta)*sp.cos(alpha), sp.cos(theta)*sp.cos(alpha), -sp.sin(alpha), -sp.sin(alpha)*d],
        [sp.sin(theta)*sp.sin(alpha), sp.cos(theta)*sp.sin(alpha), sp.cos(alpha), sp.cos(alpha)*d],
        [0, 0, 0, 1]
    ])

    # print("Matrix T:")
    # pprint(T)

    return T



# Inverse Kinematics function
def inverse_kinematicsCOMB(TGe):
    
    scale = 1000
    a1 = 215.6 / scale
    d1 = 298.7 / scale
    a2 = 274.51 / scale
    a3 = 71.3 / scale

    X, Y, Z, phi = TGe[0], TGe[1], TGe[2], TGe[3]

    theta1 = np.arctan2(Z, X)
    
    #This fixes NaN
    arg_arcsin = (Y + d1) / a2
    if arg_arcsin < -1:
        arg_arcsin = -1
    elif arg_arcsin > 1:
        arg_arcsin = 1

    theta2 = np.arcsin(arg_arcsin)

    theta3 = 0

    # Convert angles to degrees and round off
    theta1 = np.degrees(theta1)
    theta1 = round(theta1.item(), 2)  # item() gets the scalar value from a 0-dimensional array

    theta2 = np.degrees(theta2) 
    theta2 = round(theta2.item(), 2)

    
    
    Fk = ForwardKinematics(theta1, theta2, 0)
    Fk = np.array(Fk[:, 3]).astype(np.float64)
    
    X2, Y2, Z2 = Fk[0], Fk[1], Fk[2]
    print(theta1)
    print(theta2)

    tolerance = 1e-1 #desired tolerance of almost equal values
    if (
        np.allclose(X, X2, rtol=tolerance, atol=tolerance) and
        np.allclose(Y, Y2, rtol=tolerance, atol=tolerance) and
        np.allclose(Z, Z2, rtol=tolerance, atol=tolerance)
    ):
        print("\n Values are equal. ")
    else:
        print("\n Values are not equal. Fixing theta2..")
        theta2 = -90 -(theta2+90)
        Fk = ForwardKinematics(theta1, theta2, 0)
        Fk = np.array(Fk[:, 3]).astype(np.float64)
        X2, Y2, Z2 = Fk[0], Fk[1], Fk[2]
        if (
            np.allclose(X, X2, rtol=tolerance, atol=tolerance) and
            np.allclose(Y, Y2, rtol=tolerance, atol=tolerance) and
            np.allclose(Z, Z2, rtol=tolerance, atol=tolerance)
        ):
            print(" >> Values are equal now. ")
        else:
            print("! Error or unreachable !")   

    print("X:", X, "Y:", Y, "Z:", Z)
    print("X2:", X2, "Y2:", Y2, "Z2:", Z2)

    # theta1_angle = np.degrees(np.arctan2(a1,d1))
    theta1_angle = 90
    theta3 = phi - theta2 - theta1_angle
    
    theta3 = round(theta3.item(), 2)
    theta4 = -theta1
    return theta1, theta2, theta3, theta4


# Inverse Kinematics calculations for each point
for i, point in enumerate(Points):
    currentPoint = np.array(point).astype(np.float64)
    theta1i, theta2i, theta3i, theta4i = inverse_kinematicsCOMB(currentPoint)
    
    # Check if the position is valid
    # if any(angle < 0 or angle > 180 for angle in [theta1i, theta2i, theta3i, theta4i]):
    #     print(f"Invalid position for point {i + 1}")
    #     continue

    # Display current joint angles
    print(f"Point {i + 1}: Theta1 = {theta1i}, Theta2 = {theta2i}, Theta3 = {theta3i}, Theta4 = {theta4i}")
