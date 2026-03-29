import cv2
import mediapipe as mp
import pygetwindow as gw
import time

# Global variables to store the previous angles and last detection time
prev_theta1 = 0
prev_theta2 = 0
prev_theta3 = 0
prev_theta4 = 0
hand_center = (0, 0)


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
    global prev_theta1, prev_theta2, prev_theta3, prev_theta4, hand_center, last_detection_time

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hand_side = determine_hand_side(hand_landmarks, screen_width)

            # Check if the hand is in a fist
            if is_fist(hand_landmarks, tolerance=-5):
                print(f"{hand_side} Hand is in a fist.")
                # Update the last detection time
                last_detection_time = time.time()
                continue  # Skip the processing for the fist, move to the next hand

            # Calculate the time since the last detection
            time_since_detection = time.time() - last_detection_time

            # Check if the hand was not detected for 2 seconds
            if time_since_detection >= 2:
                # Save the current hand position as the new reference point
                hand_center = (
                    int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value].x * screen_width),
                    int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value].y * screen_height)
                )
                # Print or use the reference point as needed
                print(f"New reference point: {hand_center}")
                last_detection_time = time.time()

            # Calculate angles relative to the initial hand detection
            x_value = map_value(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value].x,
                                0, 1, -screen_width / 2, screen_width / 2)
            z_value = map_value(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP.value].y,
                                0, 1, screen_height / 2, -screen_height / 2)

            theta1 = map_value(x_value, -screen_width / 2, screen_width / 2, prev_theta1 - 180, prev_theta1 + 180)
            theta2 = map_value(z_value, -screen_height / 2, screen_height / 2, prev_theta2 - 180, prev_theta2 + 180)

            # Print or use the calculated angles as needed
            print(f"{hand_side} Hand - Theta1: {theta1}, Theta2: {theta2}")

            # Additional code for sending angles to the robot as needed

            # Update previous angles
            prev_theta1, prev_theta2, prev_theta3, prev_theta4 = theta1, theta2, prev_theta3, prev_theta4

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
start_time = time.time()
cap = cv2.VideoCapture(0)

print_interval = 0.4  # Interval between prints, in seconds
last_print_time = time.time()  # Initialize the last print time

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    window_width, window_height = get_window_dimensions()
    center_point = hand_center  # Use hand center instead of screen center

    current_time = time.time()
    if current_time - last_print_time >= print_interval:
        control_robot_arm(results, window_width, window_height)
        last_print_time = current_time  # Update the last print time

    fps = 1.0 / (current_time - start_time)
    start_time = current_time

    # Display FPS at the top left corner
    cv2.putText(frame, f"FPS: {round(fps, 2)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
