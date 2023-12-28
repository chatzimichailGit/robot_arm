import sympy as sp
import numpy as np
import math
import pandas as pd

df = pd.read_excel('finals/output_positions.xlsx', skiprows=[1])
random_via_points = df.sample(10)

x, y, z, phi = sp.symbols('x y z phi')

Pcart = sp.Matrix([x, y, z, phi])

Pvia = {}
for i, row in random_via_points.iterrows():
    Pvia[i] = Pcart.subs({x: row['X'], y: row['Y'], z: row['Z'], phi: 0})

Points = [Pvia[i] for i in sorted(Pvia)]

def ForwardKinematics(theta1, theta2, theta3):
    a1, a2, d1 = sp.symbols('a1, a2, d1')
    
    theta1=math.radians(theta1)
    theta2=math.radians(theta2)
    theta3=math.radians(0)

    scale = 1000
    a1 = 215.6 / scale
    d1 = 298.7 / scale
    a2 = 274.51 / scale
    a3 = 71.3 / scale
    # #end validation for Inverse

    x=(a1+a2*sp.cos(theta2))*sp.cos(theta1)
    y=a2*sp.sin(theta2)-d1
    z=(a1+a2*sp.cos(theta2))*sp.sin(theta1)

    return sp.Matrix([x, y, z])


def Validation(theta1, theta2, X, Y, Z, trial):
    
    Fk = ForwardKinematics(theta1, theta2, 0)
    X2, Y2, Z2 = np.array(Fk[0]).astype(np.float32), np.array(Fk[1]).astype(np.float32), np.array(Fk[2]).astype(np.float32)

    trial += 1
    tolerance = 1e-5 
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
        X2, Y2, Z2 = np.array(Fk[0]).astype(np.float32), np.array(Fk[1]).astype(np.float32), np.array(Fk[2]).astype(np.float32)

        if (
            np.allclose(X, X2, rtol=tolerance, atol=tolerance) and
            np.allclose(Y, Y2, rtol=tolerance, atol=tolerance) and
            np.allclose(Z, Z2, rtol=tolerance, atol=tolerance)
        ):
            print(" >> Values are equal now. ")
        else:
            if trial == 1:
                theta1 = 180 + theta1

                Fk = ForwardKinematics(theta1, theta2, 0)
                X2, Y2, Z2 = np.array(Fk[0]).astype(np.float32), np.array(Fk[1]).astype(np.float32), np.array(Fk[2]).astype(np.float32)

            else:
                print("! Error or unreachable !")   

    return X2, Y2, Z2, theta1, theta2
    



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

    
    
    X2,Y2,Z2, theta1, theta2 = Validation(theta1,theta2, X, Y, Z, 0)

    print("X:", X, "Y:", Y, "Z:", Z)
    print("X2:", X2, "Y2:", Y2, "Z2:", Z2)


    theta1_angle = 90
    theta3 = phi - theta2 - theta1_angle
    theta3 = round(theta3.item(), 2)
    theta4 = -theta1
    
    return theta1, theta2, theta3, theta4


for i, point in enumerate(Points):
    currentPoint = np.array(point).astype(np.float64)
    theta1i, theta2i, theta3i, theta4i = inverse_kinematicsCOMB(currentPoint)
    
    # Check if the position is valid
    # if any(angle < 0 or angle > 180 for angle in [theta1i, theta2i, theta3i, theta4i]):
    #     print(f"Invalid position for point {i + 1}")
    #     continue

    # Display current joint angles
    print(f"Point {i + 1}: Theta1 = {theta1i}, Theta2 = {theta2i}, Theta3 = {theta3i}, Theta4 = {theta4i}")
