from sympy import *
from sympy.matrices import Matrix
import docx
# import pandas as pd

from docx.shared import Pt

doc = docx.Document()
# Settings
style = doc.styles['Normal']
font = style.font
font.name = 'Calibri'
font.size = Pt(8)

scale =1
transformation_matrices = []


# INSTALL SYMPY . pip3 install sympy

def ForwardKinematics():
    d2, theta1, theta2, theta3, L2, L3 = symbols('d2, theta1, theta2, theta3, L2, L3')
    theta4, theta5 = symbols('theta4, theta5')
    a5, a3, d3 = symbols('a3, a5, d3')
    # a | α | d | θ
    # DH4 = Matrix([
    #     [0,0,0,pi/2],
    #     [0,pi/2,0,theta2+pi/2],
    #     [215.6/scale,0,298.7/scale,0],
    #     [0,-pi/2,0,theta4-pi/2],
    #     [356.6/scale,0,0,theta5]
    # ])

    DH4 = Matrix([
        [0,0,0,pi/2],
        [0,pi/2,0,theta2+pi/2],
        [a3,0,d3,0],
        [0,-pi/2,0,theta4-pi/2],
        [a5,0,0,theta5]
    ])

    DH = DH4

    TG0 = TLink(DH.row(0))
    T01 = TLink(DH.row(1))
    T12 = TLink(DH.row(2))
    T23 = TLink(DH.row(3))
    T34 = TLink(DH.row(4))

    TGe = TG0 * T01 * T12 * T23 * T34

    TGe = simplify(TGe)
    

    for i in range(5):  # Adjust the range based on the number of matrices
        T_result = TLink(DH.row(i))
        transformation_matrices.append(T_result)
    
    transformation_matrices.append(TGe)

    return TGe


def TLink(DH):
    # DH parameters
    a, alpha, d, theta = DH

    # Initialize a symbolic T matrix
    T = Matrix([
        [cos(theta), -sin(theta), 0, a],
        [sin(theta)*cos(alpha), cos(theta)*cos(alpha), -sin(alpha), -sin(alpha)*d],
        [sin(theta)*sin(alpha), cos(theta)*sin(alpha), cos(alpha), cos(alpha)*d],
        [0, 0, 0, 1]
    ])

    print("Matrix T:")
    pprint(T)

    return T

# def create_table(doc, matrix):
#     table = doc.add_table(rows=len(matrix), cols=len(matrix[0]), style='Table Grid')

#     for i in range(len(matrix)):
#         for j in range(len(matrix[0])):
#             cell = table.cell(i, j)
#             cell.text = str(matrix[i, j])

def create_table(doc, matrix):
    table = doc.add_table(rows=matrix.shape[0], cols=matrix.shape[1], style='Table Grid')

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            cell = table.cell(i, j)
            #cell.text = str(matrix[i, j])
            #cell.text = latex(matrix[i, j])
            cell.text = pretty(matrix[i, j], use_unicode=True)



def save_to_word(result_matrices):
    total_matrices = len(result_matrices)
    
    for i, matrix in enumerate(result_matrices):
        if i == total_matrices - 1:
            doc.add_heading(f'Final Transformation Matrix TGe', level=1)
        else:
            doc.add_heading(f'Transformation Matrix T{i}-{i+1}', level=1)
        create_table(doc, matrix)

    doc.save('forward_kinematics_result.docx')
    print("Word document saved with Forward Kinematics result.")


if __name__ == "__main__":
    TGe_result = ForwardKinematics()
    

    print("Result of Forward Kinematics:")
    pprint(TGe_result)

    # Save the result to a Word document
    save_to_word(transformation_matrices)
