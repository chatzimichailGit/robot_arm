from movementProgress import ForwardKinematics, TLink
from sympy import *
from sympy.matrices import Matrix
import docx



def inverse_kinematics(TGe, a3, a6, d3):
    """
    Calculate the inverse kinematics using elements from the transformation matrix TGe.
    
    TGe is a 4x4 SymPy Matrix representing the transformation matrix from Forward Kinematics.
    a3, a6, d3 are parameters of the robotic arm.
    
    Returns the calculated joint angles theta2, theta4, theta5.
    """
    scale=1000
    a3=215.6/scale
    d3=298.7/scale
    a6=356.6/scale
    # Extracting elements directly from the matrix using indexing
    x = TGe[0, 3]
    z = TGe[2, 3]

    # Inverse Kinematics equations using direct indexing
    theta2 = atan2(-TGe[2, 2], -TGe[1, 2])
    theta4 = atan2((z + TGe[1, 2] * a6) / a3, (x - d3) / a3)
    theta5 = atan2(-TGe[0, 1], TGe[0, 0]) - theta4

    return theta2, theta4, theta5

# Example usage
if __name__ == "__main__":
    TGe_result = ForwardKinematics()

    # Define parameters a3, a6, d3 for your robotic arm
    a3, a6, d3 = symbols('a3 a6 d3')

    # Calculate inverse kinematics
    theta2, theta4, theta5 = inverse_kinematics(TGe_result, a3, a6, d3)

    print("Calculated joint angles:")
    pprint(theta2)
    pprint(theta4)
    pprint(theta5)




