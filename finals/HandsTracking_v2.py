'''
    general Idea is to have a middle point , from where you can do
    +100% -100% means you can divide distance(max+min absolutes)/200 and then find a step that 
    multiplying with real percentages it you find the position XYZ. 
'''
import cv2
import mediapipe as mp
import pygetwindow as gw
import time
import sympy as sp
import serial

serial_port = "COM1"  # Update this with your actual serial port
baud_rate = 9600

# Initialize the serial connection
ser = serial.Serial(serial_port, baud_rate)


def map_value(value, from_min, from_max, to_min, to_max):
    return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

def get_window_dimensions():
    # Get the active window dimensions
    active_window = gw.getActiveWindow()
    return active_window.width, active_window.height

def determine_hand_side(hand_landmarks, screen_width):
    thumb_tip = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP.value]
    pinky_mcp = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP.value]
    
    thumb_tip_x = thumb_tip.x
    pinky_mcp_x = pinky_mcp.x
    
    return "Right" if thumb_tip_x < pinky_mcp_x else "Left"

def correct_percentage(value, correction):
    return (value + correction) * 2

def is_fist(hand_landmarks, tolerance=-0.5):
    thumb_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP.value].y
    index_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP.value].y
    middle_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP.value].y
    ring_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP.value].y
    pinky_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP.value].y

    # Calculate the dynamic threshold based on the range of finger tips' y-coordinates
    dynamic_threshold = max(index_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y) - thumb_tip_y

    # Add tolerance to the dynamic threshold
    threshold = dynamic_threshold * tolerance

    # Check if all finger tips are below the dynamic threshold
    if all(tip > thumb_tip_y + threshold for tip in [index_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y]):
        return True
    else:
        return False
    
def isIndexUp(hand_landmarks, tolerance=-0.5):
    thumb_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP.value].y
    index_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP.value].y
    middle_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP.value].y
    ring_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP.value].y
    pinky_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP.value].y

    # Calculate the dynamic threshold based on the range of finger tips' y-coordinates
    dynamic_threshold = max(index_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y) - thumb_tip_y

    # Add tolerance to the dynamic threshold
    threshold = dynamic_threshold * tolerance

    # Check if the index finger is above the dynamic threshold,
    # the thumb is below its position, and the other fingers are below their corresponding positions
    return (
        index_tip_y < thumb_tip_y - threshold and
        all(tip > index_tip_y for tip in [thumb_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y])
    )

def isIndexAndMiddleUp(hand_landmarks, tolerance=-0.5):
    thumb_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP.value].y
    index_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP.value].y
    middle_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP.value].y
    ring_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP.value].y
    pinky_tip_y = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP.value].y

    # Calculate the dynamic threshold based on the range of finger tips' y-coordinates
    dynamic_threshold = max(index_tip_y, middle_tip_y, ring_tip_y, pinky_tip_y) - thumb_tip_y

    # Add tolerance to the dynamic threshold
    threshold = dynamic_threshold * tolerance

    # Check if both index and middle fingers are above the dynamic threshold,
    # the thumb is below its position, and the other fingers are below their corresponding positions
    return (
        index_tip_y < thumb_tip_y - threshold and
        middle_tip_y < thumb_tip_y - threshold and
        all(tip > index_tip_y and tip > middle_tip_y for tip in [thumb_tip_y, ring_tip_y, pinky_tip_y])
    )




def control_robot_arm(results, screen_width, screen_height):
    global theta1, theta2, phi 
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hand_side = determine_hand_side(hand_landmarks, screen_width)

            # Check if the hand is in a fist
            if is_fist(hand_landmarks, tolerance=-2):
            # if isIndexUp(hand_landmarks) == False:
                # print(f"{hand_side} Hand is in a fist.")



                # if hand_side == "Right":
                #     theta1 = 0
                #     theta2 = 0
                # elif hand_side == "Left":
                #     phi = 0
                continue  # Skip the processing for the fist, move to the next hand

            if hand_side == "Right":
                middle_finger_base = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value]
                hand_center = (int(middle_finger_base.x * screen_width), int(middle_finger_base.y * screen_height))
                screen_center = (screen_width * 3 // 4, screen_height // 2)
                cv2.line(frame, hand_center, screen_center, (11, 190, 255), 4)

                if isIndexUp(hand_landmarks):
                    theta1_v = map_value(middle_finger_base.x, 0, 1, - screen_width / 2, screen_width / 2)
                    theta1_percentage = round((theta1_v / (screen_width / 2)) * 100, 2)
                    theta1_percentage = round(correct_percentage(theta1_percentage, -50), 2)
                    theta1 = theta1_percentage

                    # theta2 = 0
                    cv2.putText(frame, f"theta1: {theta1_percentage}%", (hand_center[0] + 10, hand_center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (110, 0, 255), 1, cv2.LINE_AA)
                
                elif isIndexAndMiddleUp(hand_landmarks):
                    theta2_v = map_value(middle_finger_base.y, 0, 1, screen_height / 2, -screen_height / 2)  # Reverse Z direction
                    theta2_percentage = round((theta2_v / (screen_height / 2)) * 100, 2)
                    theta2 = theta2_percentage

                    # theta1 = 0
                    cv2.putText(frame, f"theta2: {theta2_percentage}%", (hand_center[0] + 10, hand_center[1] - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                
                else:
                    theta1_v = map_value(middle_finger_base.x, 0, 1, - screen_width / 2, screen_width / 2)
                    theta2_v = map_value(middle_finger_base.y, 0, 1, screen_height / 2, -screen_height / 2)  # Reverse Z direction

                    theta1_percentage = round((theta1_v / (screen_width / 2)) * 100, 2)
                    theta2_percentage = round((theta2_v / (screen_height / 2)) * 100, 2)

                    theta1_percentage = round(correct_percentage(theta1_percentage, -50), 2)

                    theta1 = theta1_percentage
                    theta2 = theta2_percentage

                    # Display X and Z percentages above the line
                    cv2.putText(frame, f"theta1: {theta1_percentage}%", (hand_center[0] + 10, hand_center[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (110, 0, 255), 1, cv2.LINE_AA)
                    cv2.putText(frame, f"theta2: {theta2_percentage}%", (hand_center[0] + 10, hand_center[1] - 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            elif hand_side == "Left":
                phi_base = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value]

                phi_value = map_value(phi_base.x, 0, 1, - screen_width / 2, screen_width / 2)

                phi_percentage = round((phi_value / (screen_width / 2)) * 100, 2)

                phi_percentage = round(correct_percentage(phi_percentage, 50), 2)

                phi = phi_percentage

                hand_center = (int(phi_base.x * screen_width), int(phi_base.y * screen_height))
                screen_center = (screen_width // 4, screen_height // 2)
                cv2.line(frame, hand_center, screen_center, (11, 190, 255), 4)

                # Display Phi percentage above the line
                cv2.putText(frame, f"Phi: {phi_percentage}%", (hand_center[0] + 10, hand_center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (110, 0, 255), 1, cv2.LINE_AA)
            t1_int = int(f_theta1 * 100)  # Multiply by 100 to keep two decimal places
            t2_int = int(f_theta2 * 100)
            t3_int = int((f_theta3+90) * 100)
            t4_int = int(f_theta4 * 100)


            # Construct the message to be sent to the robot
            message = f"{t1_int},{t2_int},{t3_int},{t4_int}\n"

            # Send the message to the robot through the serial port
            ser.write(message.encode())

            # Display the calculated values and the constructed message
            print(f"Calculated Values - theta1: {f_theta1}, theta2: {f_theta2}, theta3: {f_theta3}, theta4: {f_theta4}, phi: {f_phi}")
            print(f"Constructed Message: {message}")    
    # else:
    #     theta1 = 0
    #     theta2 = 0
    #     phi = 0
ser.close()
def draw_axes(frame, center):
    # Draw +-X axis in grey
    cv2.line(frame, center, (frame.shape[1], center[1]), (169, 169, 169), 1)
    cv2.line(frame, center, (0, center[1]), (169, 169, 169), 1)
    # Draw +-Z axis in purple
    cv2.line(frame, center, (center[0], frame.shape[0]), (169, 169, 169), 1)
    cv2.line(frame, center, (center[0], 0), (169, 169, 169), 1)  # Reverse Z direction

def map_theta1(theta1):
    # Map theta1 from [-180, 0, 180] to [0, 90, 180]
    mapped_theta1 = (theta1 + 180) * 0.5
    return mapped_theta1

def map_theta2(theta2):
    # Map theta2 from [-90, 0, 90] to [-180, -90, 0]
    mapped_theta2 = theta2 - 90
    return mapped_theta2

def commander(theta1_v, theta2_v, phi_v, fps):
    #step = (|max|+|min|)/100
    global limit_t1, limit_t2, limit_t3, limit_t4, limit_phi
    
    desired_end_of_screen = 80
    desired_end_of_screen_phi = 90-(desired_end_of_screen-20)+20 #lower limits

    theta1 = round((theta1_v[1] * desired_end_of_screen), 2)
    theta2 = round((theta2_v[1] * desired_end_of_screen), 2)
    phi = round(phi_v[1] * desired_end_of_screen_phi, 2)

    temp_theta1 = round(theta1_v[1]*180,2)

    limit_1_2 = 60 #deg

    # LIMITS 
    if theta1>=limit_1_2 :
        theta1 = limit_1_2
        limit_t1 = False
        limit_t4 = False
    elif theta1<= -limit_1_2 :
        theta1 = -limit_1_2
        limit_t1 = False
        limit_t4 = False
    else :
        limit_t1 = True
        limit_t4 = True
        
    
    if theta2 >= limit_1_2 :
        theta2 = limit_1_2
        limit_t2 = False
    elif theta2 <= -limit_1_2 :
        theta2 = -limit_1_2
        limit_t2 = False
    else:
        limit_t2 = True
    
    # theta3 = servo [-90 eos +90]
    limit_phi = 90 - limit_1_2
    if phi > limit_phi:
        phi = limit_phi
        limit_phi = False
    elif phi < -limit_phi:
        phi = -limit_phi
        limit_phi = False
    else:
        limit_phi = True

    theta3 = round(-theta2+phi, 2)

    if theta3 >= 90 :
        theta3 = 90
        limit_t3 = False
    elif theta3 <= -90 :
        theta3 = -90
        limit_t3 = False
    else :
        limit_t3 = True

    theta4 = round(-theta1, 2)

    print(f"theta1: {theta1} , theta2: {theta2} , theta3: {theta3}, theta4: {theta4},  phi: {phi}, fps: {round(fps,2)}")
    
    return theta1,theta2,theta3,theta4,phi
   

    # av_speed = (movement_x + movement_z + movement_phi)/3*fps
    # av_accel = (movement_x + movement_z + movement_phi)/3*fps**2

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
start_time = time.time()
cap = cv2.VideoCapture(0)

theta1 = 0.0
theta2 = 0.0
phi = 0.0
theta1_values = [0.0, 0.0]  # Initialize with at least two elements
theta2_values = [0.0, 0.0]  # Initialize with at least two elements
phi_values = [0.0, 0.0]  # Initialize with at least two elements

global limit_t1, limit_t2, limit_t3, limit_t4, limit_phi
limit_t1 = False
limit_t2 = False
limit_t3 = False
limit_t4 = False
limit_phi = False

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    window_width, window_height = get_window_dimensions()
    center_point = (window_width // 2, window_height // 2)

    temp_adjust=100 # step = distance/100 => step/2 <=> distance/200
    theta1_values[0]=theta1/temp_adjust
    theta2_values[0]=theta2/temp_adjust
    phi_values[0]=phi/100  
    draw_axes(frame, center_point)
    control_robot_arm(results, window_width, window_height)
    
    current_time = time.time()
    fps = 1.0 / (current_time - start_time)
    start_time = current_time

    theta1_values[1]=theta1/temp_adjust
    theta2_values[1]=theta2/temp_adjust
    phi_values[1]=phi/temp_adjust  
    f_theta1, f_theta2, f_theta3, f_theta4, f_phi = commander(theta1_values, theta2_values, phi_values, fps)
    # print(f"theta1: {theta1}%, theta2: {theta2}%, phi: {phi}%, fps: {round(fps,2)}")

    # Display FPS at the top left corner
    cv2.putText(frame, f"FPS: {round(fps, 2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


    font_size = 0.4
    text_color = (255, 255, 255)
    circle_radius = 6
    circle_color_true = (0, 255, 0)  # Green
    circle_color_false = (0, 0, 255)  # Red

    cv2.putText(frame, f"t1: {round(f_theta1, 2)}", (window_width - 120, 30), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"t2: {round(f_theta2, 2)}", (window_width - 120, 50), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"t3: {round(f_theta3, 2)}", (window_width - 120, 70), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"t4: {round(f_theta4, 2)}", (window_width - 120, 90), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"phi: {round(f_phi, 2)}", (window_width - 120, 110), cv2.FONT_HERSHEY_SIMPLEX, font_size, text_color, 1, cv2.LINE_AA)
    adjust = 5
    cv2.circle(frame, (window_width - 140, 30 - adjust), circle_radius, circle_color_true if limit_t1 else circle_color_false, -1)
    cv2.circle(frame, (window_width - 140, 50 - adjust), circle_radius, circle_color_true if limit_t2 else circle_color_false, -1)
    cv2.circle(frame, (window_width - 140, 70 - adjust), circle_radius, circle_color_true if limit_t3 else circle_color_false, -1)
    cv2.circle(frame, (window_width - 140, 90 - adjust), circle_radius, circle_color_true if limit_t4 else circle_color_false, -1)
    cv2.circle(frame, (window_width - 140, 110 - adjust), circle_radius, circle_color_true if limit_phi else circle_color_false, -1)

    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()