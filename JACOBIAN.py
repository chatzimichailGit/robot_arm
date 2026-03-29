import sympy as sp
import numpy as np
import math
import pandas as pd

theta1, theta2, theta3, a1, a2, d1 = sp.symbols('theta1 theta2 theta3 a1 a2 d1')

scale = 1000
a1 = 215.6 / scale
d1 = 298.7 / scale
a2 = 274.51 / scale
a3 = 71.3 / scale

# Define the transformation matrices
T01 = sp.Matrix([
    [sp.cos(theta1), -sp.sin(theta1), 0, 0],
    [0, 0, -1, -d1],
    [sp.sin(theta1), sp.cos(theta1), 0, 0],
    [0, 0, 0, 1]
])

T12 = sp.Matrix([
    [sp.cos(theta2), -sp.sin(theta2), 0, a1],
    [0, 0, 1, 0],
    [-sp.sin(theta2), -sp.cos(theta2), 0, 0],
    [0, 0, 0, 1]
])

T23 = sp.Matrix([
    [sp.cos(theta3), -sp.sin(theta3), 0, a2],
    [sp.sin(theta3), sp.cos(theta3), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

# Final transformation matrix TGe
TGe = T01 * T12 * T23
pos_EF = TGe[:3, 3]


# Jacobian matrix
J = sp.zeros(3, 3)
for i, theta in enumerate([theta1, theta2, theta3]):
    J[:, i] = sp.diff(pos_EF, theta)
    


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

# Time to move between points
delta_time = 1  # Adjust as needed

# Assuming you have defined your symbols (theta1, theta2, theta3, etc.)
# and your Jacobian matrix J

# Function to numerically evaluate the Jacobian matrix
def evaluate_jacobian(J, theta1_val, theta2_val, theta3_val):
    # Create a lambda function for numerical evaluation
    J_func = sp.lambdify((theta1, theta2, theta3), J, 'numpy')

    # Use the lambda function to evaluate the Jacobian matrix numerically
    J_numerical = J_func(theta1_val, theta2_val, theta3_val)
    return J_numerical



for i in range(len(Points) - 1):
    # Current and next via points
    currentPoint = np.array(Points[i]).astype(np.float64)
    nextPoint = np.array(Points[i + 1]).astype(np.float64)

    # Inverse kinematics to find joint angles for current and next points
    theta1_current, theta2_current, theta3_current, _ = inverse_kinematicsCOMB(currentPoint)
    theta1_next, theta2_next, theta3_next, _ = inverse_kinematicsCOMB(nextPoint)

    # Compute Jacobian for the current point
    J_current_numerical = evaluate_jacobian(J, theta1_current, theta2_current, theta3_current)

    # Calculate joint velocities
    delta_theta = np.array([theta1_next, theta2_next, theta3_next]) - np.array([theta1_current, theta2_current, theta3_current])
    joint_velocities = J_current_numerical.dot(delta_theta) / delta_time

    print(f"Joint velocities from Point {i} to Point {i + 1}: {joint_velocities}")
sp.pprint(J)
