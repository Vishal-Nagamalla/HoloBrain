import cv2
import mediapipe as mp
import numpy as np
import time
import socket


# Initialize MediaPipe hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)


# Set up socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 65432))  # Bind to localhost on port 65432
server_socket.listen(1)
print("Waiting for Unity to connect...")
client_socket, _ = server_socket.accept()
print("Unity connected!")


# Variables to track gestures
gesture = None
prev_pinch_pos = None  # To store the previous position of the pinch for drag
drag_in_progress = False  # State to track if a drag is in progress
prev_zoom_dist = None  # Store previous distance between two pinch points for zoom
pinch_buffer_frames = 5  # Number of frames to consistently detect pinch before registering it
pinch_buffer_count = 0


# Sensitivity thresholds
pinch_threshold = 0.03  # Adjust pinch detection sensitivity for drag
drag_threshold = 0.04  # Minimum movement required to register a drag (left/right/up/down)
zoom_threshold = 0.02  # Minimum change in distance for zoom in/out
drag_tolerance = 0.4  # Tolerance for diagonal movement, allows more diagonal movement


# Helper function to detect pinch gesture
def is_pinch(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]


    # Calculate the distance between the thumb and index finger
    pinch_dist = np.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
   
    # Return True if the thumb and index finger are close enough to form a pinch
    return pinch_dist < pinch_threshold


# Gesture detection for drag gestures
def detect_drag_gesture(landmarks):
    global gesture, prev_pinch_pos, drag_in_progress, pinch_buffer_count
   
    # Check if a pinch is detected
    if not is_pinch(landmarks):
        gesture = None
        drag_in_progress = False
        pinch_buffer_count = 0
        return None
   
    # Increase the buffer to ensure pinch consistency across multiple frames
    pinch_buffer_count += 1
    if pinch_buffer_count < pinch_buffer_frames:
        return None
   
    # Extract x and y coordinates of specific landmarks for pinch detection
    index_finger_tip = landmarks[8]
    thumb_tip = landmarks[4]
   
    # Calculate pinch midpoint
    pinch_x = (index_finger_tip.x + thumb_tip.x) / 2
    pinch_y = (index_finger_tip.y + thumb_tip.y) / 2
    current_pinch_pos = (pinch_x, pinch_y)


    # Only detect drag gestures if a drag is not already in progress
    if prev_pinch_pos is not None:
        dx = current_pinch_pos[0] - prev_pinch_pos[0]  # Horizontal movement
        dy = current_pinch_pos[1] - prev_pinch_pos[1]  # Vertical movement


        # Allow more tolerance for diagonal movements using drag_tolerance
        if abs(dx) > abs(dy) * (1 - drag_tolerance):  # Horizontal movement
            if dx > drag_threshold:
                gesture = "drag_right"
                drag_in_progress = True  # Set drag in progress
            elif dx < -drag_threshold:
                gesture = "drag_left"
                drag_in_progress = True  # Set drag in progress
        elif abs(dy) > abs(dx) * (1 - drag_tolerance):  # Vertical movement
            if dy > drag_threshold:
                gesture = "drag_down"
                drag_in_progress = True  # Set drag in progress
            elif dy < -drag_threshold:
                gesture = "drag_up"
                drag_in_progress = True  # Set drag in progress
   
    prev_pinch_pos = current_pinch_pos  # Update pinch position for the next frame
    return gesture


# Gesture detection for zoom based on the pinch distance between two hands
def detect_zoom_gesture(landmarks_list):
    global prev_zoom_dist, gesture


    # Ensure two hands are detected
    if len(landmarks_list) < 2:
        prev_zoom_dist = None  # Reset zoom tracking if less than two hands
        return None


    # Check if a pinch is detected on both hands
    if not is_pinch(landmarks_list[0]) or not is_pinch(landmarks_list[1]):
        gesture = None
        return None


    # Get thumb and index finger tips from both hands
    hand_1_thumb_tip = landmarks_list[0][4]
    hand_1_index_tip = landmarks_list[0][8]
    hand_2_thumb_tip = landmarks_list[1][4]
    hand_2_index_tip = landmarks_list[1][8]


    # Calculate pinch points (midpoint between thumb and index finger for each hand)
    hand_1_pinch_x = (hand_1_thumb_tip.x + hand_1_index_tip.x) / 2
    hand_1_pinch_y = (hand_1_thumb_tip.y + hand_1_index_tip.y) / 2
    hand_2_pinch_x = (hand_2_thumb_tip.x + hand_2_index_tip.x) / 2
    hand_2_pinch_y = (hand_2_thumb_tip.y + hand_2_index_tip.y) / 2


    # Calculate the current distance between two pinch points
    current_zoom_dist = np.sqrt(
        (hand_1_pinch_x - hand_2_pinch_x) ** 2 +
        (hand_1_pinch_y - hand_2_pinch_y) ** 2
    )


    if prev_zoom_dist is not None:
        # If the distance between the pinch points increases, zoom in
        if current_zoom_dist - prev_zoom_dist > zoom_threshold:
            gesture = "zoom_in"
        # If the distance between the pinch points decreases, zoom out
        elif prev_zoom_dist - current_zoom_dist > zoom_threshold:
            gesture = "zoom_out"
        else:
            gesture = None


    prev_zoom_dist = current_zoom_dist  # Update previous distance for next frame
    return gesture


# Capture video from webcam and process gestures
cap = cv2.VideoCapture(0)


while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break


    # Convert image to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)


    # Draw landmarks and detect gestures
    if results.multi_hand_landmarks:
        # Draw hand landmarks
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


        # Detect drag gesture for one hand
        if len(results.multi_hand_landmarks) == 1:
            landmarks = results.multi_hand_landmarks[0].landmark
            detected_gesture = detect_drag_gesture(landmarks)


        # Detect zoom gesture if two hands are present
        elif len(results.multi_hand_landmarks) == 2:
            landmarks_list = [hand_landmarks.landmark for hand_landmarks in results.multi_hand_landmarks]
            detected_gesture = detect_zoom_gesture(landmarks_list)


        if detected_gesture:
            cv2.putText(frame, detected_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(detected_gesture)  # Print gesture to console
           
            # Send the detected gesture to Unity via socket
            client_socket.sendall(detected_gesture.encode())
            print(f"Sent gesture: {detected_gesture}")


    cv2.imshow("Hand Gesture Control", frame)
   
    if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
        break


cap.release()
cv2.destroyAllWindows()
hands.close()
client_socket.close()
server_socket.close()