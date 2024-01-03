import cv2
import mediapipe as mp
import pygetwindow as gw
import time

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

def is_fist(hand_landmarks, tolerance=0.1):
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

def control_robot_arm(results, screen_width, screen_height):
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hand_side = determine_hand_side(hand_landmarks, screen_width)

            # Check if the hand is in a fist
            if is_fist(hand_landmarks, tolerance=-2):
                # print(f"{hand_side} Hand is in a fist.")
                continue  # Skip the processing for the fist, move to the next hand

            if hand_side == "Right":
                middle_finger_base = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value]

                x_value = map_value(middle_finger_base.x, 0, 1, - screen_width / 2, screen_width / 2)
                z_value = map_value(middle_finger_base.y, 0, 1, screen_height / 2, -screen_height / 2)  # Reverse Z direction

                x_percentage = round((x_value / (screen_width / 2)) * 100, 2)
                z_percentage = round((z_value / (screen_height / 2)) * 100, 2)

                x_percentage = round(correct_percentage(x_percentage, -50), 2)

                global x,z 
                z = z_percentage
                x = x_percentage

                # Print values only if the right hand is not in a fist
                # print(f"{hand_side} Hand - X: {x_percentage}%, Z: {z_percentage}")

                # Draw line from hand center to right side center
                hand_center = (int(middle_finger_base.x * screen_width), int(middle_finger_base.y * screen_height))
                screen_center = (screen_width * 3 // 4, screen_height // 2)
                cv2.line(frame, hand_center, screen_center, (11, 190, 255), 4)

                # Display X and Z percentages above the line
                cv2.putText(frame, f"X: {x_percentage}%", (hand_center[0] + 10, hand_center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (110, 0, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, f"Z: {z_percentage}%", (hand_center[0] + 10, hand_center[1] - 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

            elif hand_side == "Left":
                phi_base = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value]

                phi_value = map_value(phi_base.x, 0, 1, - screen_width / 2, screen_width / 2)

                phi_percentage = round((phi_value / (screen_width / 2)) * 100, 2)

                phi_percentage = round(correct_percentage(phi_percentage, 50), 2)

                global phi 
                phi = phi_percentage

                # Print values only if the left hand is not in a fist
                # print(f"{hand_side} Hand - Phi: {phi_percentage}%")

                # Draw line from hand center to left side center
                hand_center = (int(phi_base.x * screen_width), int(phi_base.y * screen_height))
                screen_center = (screen_width // 4, screen_height // 2)
                cv2.line(frame, hand_center, screen_center, (11, 190, 255), 4)

                # Display Phi percentage above the line
                cv2.putText(frame, f"Phi: {phi_percentage}%", (hand_center[0] + 10, hand_center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (110, 0, 255), 1, cv2.LINE_AA)

def draw_axes(frame, center):
    # Draw +-X axis in grey
    cv2.line(frame, center, (frame.shape[1], center[1]), (169, 169, 169), 1)
    cv2.line(frame, center, (0, center[1]), (169, 169, 169), 1)
    # Draw +-Z axis in purple
    cv2.line(frame, center, (center[0], frame.shape[0]), (169, 169, 169), 1)
    cv2.line(frame, center, (center[0], 0), (169, 169, 169), 1)  # Reverse Z direction

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
start_time = time.time()
cap = cv2.VideoCapture(0)

x = 0.0
z = 0.0
phi = 0.0


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    window_width, window_height = get_window_dimensions()
    center_point = (window_width // 2, window_height // 2)

    #draw_axes(frame, center_point)
    control_robot_arm(results, window_width, window_height)
    
    current_time = time.time()
    fps = 1.0 / (current_time - start_time)
    start_time = current_time

    print(f"x: {x}%, z: {z}%, phi: {phi}%, fps: {round(fps,2)}")

    # Display FPS at the top left corner
    cv2.putText(frame, f"FPS: {round(fps, 2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    # if results.multi_hand_landmarks:
    #     for landmarks in results.multi_hand_landmarks:
    #         mp.solutions.drawing_utils.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()