import numpy as np
import sympy as sp
import serial
import time

t, x, y, z, roll, pitch, yaw = sp.symbols('t x y z roll pitch yaw')


def inverse_kinematicsCOMB(TGe):
    scale = 1000
    a1 = 215.6 / scale
    d1 = 298.7 / scale
    a3 = 356.6 / scale
    
    theta1 = np.arctan2(-TGe[2, 2], -TGe[0, 2])

    if theta1 != np.pi/2:
        theta2 = np.arctan2((TGe[2, 3] + TGe[0, 2] * a1) / (TGe[0, 2] * a3), 
                    -(TGe[1, 3] + d1) / a3)
    else:
        theta2 = np.arctan2((-TGe[0, 3] + TGe[2, 2] * a1) / (TGe[2, 2] * a3), 
                    -(TGe[1, 3] + d1) / a3)

    theta3 = np.arctan2(TGe[1, 1], -TGe[1, 0]) - theta2

    

    # Convert angles to degrees and round off
    theta1 = round(np.degrees(theta1), 2)
    theta2 = round(np.degrees(theta2), 2)
    theta3 = round(np.degrees(theta3), 2)
    theta4=180-theta1

    return theta1, theta2, theta3, theta4

def is_valid_position(theta1, theta2, theta3, theta4):
    angles = [theta1, theta2, theta3, theta4]
    if any(angle < 0 or angle > 180 for angle in angles):
        print("Invalid position")
        return False
    return True


# Define symbolic variables for points generation
t, x, y, z, theta, zeta = sp.symbols('t x y z theta zeta')


# Define generic form of point in Cartesian space
R_x = sp.Matrix([[1, 0, 0],
                 [0, sp.cos(roll), -sp.sin(roll)],
                 [0, sp.sin(roll), sp.cos(roll)]])  

R_y = sp.Matrix([[sp.cos(pitch), 0, sp.sin(pitch)],
                 [0, 1, 0],
                 [-sp.sin(pitch), 0, sp.cos(pitch)]])

R_z = sp.Matrix([[sp.cos(yaw), -sp.sin(yaw), 0],
                 [sp.sin(yaw), sp.cos(yaw), 0],
                 [0, 0, 1]])

# Combine rotations and translations
R =   R_y * R_z
# R =   R_z * R_y
#sp.pprint(R)
Pcart = sp.Matrix.hstack(R, sp.Matrix([x, y, z]))
Pcart = sp.Matrix.vstack(Pcart, sp.Matrix([[0, 0, 0, 1]]))
sp.pprint(Pcart)
print("\n")

# Define start and end points
PA = Pcart.subs({x:  -0.572, y: -0.295, z: 0, pitch: sp.pi/2, yaw: sp.pi})
PB = Pcart.subs({x: 1, y: 1, z: 1, pitch: sp.pi/2, yaw: sp.pi/2})

# Define via points
Pvia = {}

Pvia[1] = Pcart.subs({x: 0.2156, y: 5.722, z: 0.6553 , pitch: 0, yaw: -sp.pi})
Pvia[2] = Pcart.subs({x: 10.35, y: 0.59, z: 29.86, pitch: 1.83, yaw: 4.92})
Pvia[3] = Pcart.subs({x: 4.85, y: 8.61, z: 16.52, pitch: 1.62, yaw: 0.84})
Pvia[4] = Pcart.subs({x: 14.81, y: 11.99, z: 19.10, pitch: 1.48, yaw: 4.45})
Pvia[5] = Pcart.subs({x: 27.77, y: 17.95, z: 28.78, pitch: 1.61, yaw: 0.77})

# Combine all points
Points = [PA] + [Pvia[i] for i in sorted(Pvia)] + [PB]
Np = len(Points)  # Number of points



# Initialize matrices
PJoints = np.zeros((Np, 3))

# Inverse Kinematics calculations for each point
for i, point in enumerate(Points):
    currentPoint = np.array(point).astype(np.float64)  # Convert to numeric
    theta1i, theta2i, theta3i , theta4i= inverse_kinematicsCOMB(currentPoint)
    PJoints[i, :] = [theta1i, theta2i, theta3i]

    # Debugging: display current joint angles
    print(f"Point {i + 1}: Theta1 = {theta1i}, Theta2 = {theta2i}, Theta3 = {theta3i}, Theta4 = {theta4i}")



# Serial port setup
ser = serial.Serial('COM5', 9600) # Replace 'COM_PORT' with your Arduino's serial port
time.sleep(2) # Wait for the connection to establish

for i, point in enumerate(Points):
    currentPoint = np.array(point).astype(np.float64)
    theta1i, theta2i, theta3i, theta4i = inverse_kinematicsCOMB(currentPoint)
    if not is_valid_position(theta1i, theta2i, theta3i, theta4i):
        continue
    # Debugging: display current joint angles
    print(f"Point {i + 1}: Theta1 = {theta1i}, Theta2 = {theta2i}, Theta3 = {theta3i},Theta4 = {theta4i}")

    # Wait for user input to send the data
    input("Press 'n' and Enter to send the next set of angles: ")

    # Prepare the message to send
    message = f"{theta1i},{theta2i},{theta3i},{theta4i}\n"

    # Send the message
    ser.write(message.encode())

    # Read response from Arduino (optional)
    line = ser.readline().decode('utf-8').rstrip()
    print("Arduino response: ", line)

# Close the serial connection
ser.close()