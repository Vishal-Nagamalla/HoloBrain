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
server_socket.bind(('localhost', 65432))  # Host and port for the connection
server_socket.listen(1)
print("Waiting for Unity to connect...")
client_socket, _ = server_socket.accept()
print("Unity connected!")

# Variables to track gestures
gesture = None
prev_hand_state = None  # To store the previous hand state (palm or fist)
prev_dist = None  # Used for zoom detection
prev_pinch_pos = None  # To store the previous position of the pinch for drag
drag_in_progress = False  # State to track if a drag is in progress
prev_zoom_dist = None  # Store previous distance between two index fingers for zoom

# Sensitivity thresholds
pinch_threshold = 0.03  # Adjust pinch detection sensitivity for drag
drag_threshold = 0.05  # Minimum movement required to register a drag (left/right/up/down)
zoom_threshold = 0.02  # Minimum change in distance for zoom in/out
<<<<<<< HEAD

# Set up socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 65432))  # Localhost and port number for Unity connection
server_socket.listen(1)
print("Waiting for Unity to connect...")
client_socket, _ = server_socket.accept()
print("Unity connected!")
=======
>>>>>>> eac4cafec81f893680267e280f9a033cb771968a

# Palm detection
def is_palm(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    index_knuckle = landmarks[5]
    middle_knuckle = landmarks[9]
    ring_knuckle = landmarks[13]
    pinky_knuckle = landmarks[17]

    return (
        index_tip.y < index_knuckle.y and
        middle_tip.y < middle_knuckle.y and
        ring_tip.y < ring_knuckle.y and
        pinky_tip.y < pinky_knuckle.y
    )

# Fist detection
def is_fist(landmarks):
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]

    wrist = landmarks[0]

    return (
        index_tip.y > wrist.y and
        middle_tip.y > wrist.y and
        ring_tip.y > wrist.y and
        pinky_tip.y > wrist.y
    )

# Gesture detection for drag gestures
def detect_drag_gesture(landmarks):
    global gesture, prev_pinch_pos, prev_dist, drag_in_progress
    
    # Extract x and y coordinates of specific landmarks for pinch detection
    index_finger_tip = landmarks[8]
    thumb_tip = landmarks[4]
    
    # Calculate pinch distance and midpoint
    current_dist = np.sqrt((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2)
    pinch_x = (index_finger_tip.x + thumb_tip.x) / 2
    pinch_y = (index_finger_tip.y + thumb_tip.y) / 2
    current_pinch_pos = (pinch_x, pinch_y)
    
    # Pinch detection for drag (left/right/up/down)
    if current_dist < pinch_threshold:
        if prev_pinch_pos is not None:
            dx = current_pinch_pos[0] - prev_pinch_pos[0]  # Horizontal movement
            dy = current_pinch_pos[1] - prev_pinch_pos[1]  # Vertical movement

            # Only detect drag gestures if a drag is not already in progress
            if not drag_in_progress:
                # Horizontal drag detection
                if abs(dx) > abs(dy):  # Detect if horizontal movement is larger than vertical
                    if dx > drag_threshold:
                        gesture = "drag_right"
                        drag_in_progress = True  # Set drag in progress
                    elif dx < -drag_threshold:
                        gesture = "drag_left"
                        drag_in_progress = True  # Set drag in progress
                # Vertical drag detection
                else:  # Detect vertical movement
                    if dy > drag_threshold:
                        gesture = "drag_down"
                        drag_in_progress = True  # Set drag in progress
                    elif dy < -drag_threshold:
                        gesture = "drag_up"
                        drag_in_progress = True  # Set drag in progress
        
        prev_pinch_pos = current_pinch_pos  # Update pinch position
        prev_dist = current_dist  # Update pinch distance for next frame
    else:
        # Reset the gesture and stop dragging when the pinch is released
        gesture = None  # Stop returning any gesture when the pinch is released
        prev_pinch_pos = None  # Reset pinch when not pinched
        drag_in_progress = False  # Reset drag state when pinch is no longer detected

    return gesture

# Gesture detection for zoom based on the distance between two hands
def detect_zoom_gesture(landmarks_list):
    global prev_zoom_dist, gesture

    # Ensure two hands are detected
    if len(landmarks_list) < 2:
        prev_zoom_dist = None  # Reset zoom tracking if less than two hands
        return None

    # Get index finger tips from both hands
    hand_1_index_finger = landmarks_list[0][8]
    hand_2_index_finger = landmarks_list[1][8]

    # Calculate the current distance between two index fingers
    current_zoom_dist = np.sqrt(
        (hand_1_index_finger.x - hand_2_index_finger.x) ** 2 +
        (hand_1_index_finger.y - hand_2_index_finger.y) ** 2
    )

    if prev_zoom_dist is not None:
        # If the distance between the index fingers increases, zoom in
        if current_zoom_dist - prev_zoom_dist > zoom_threshold:
            gesture = "zoom_in"
        # If the distance between the index fingers decreases, zoom out
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

<<<<<<< HEAD
       
            if detected_gesture:
                cv2.putText(frame, detected_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(detected_gesture)  # To view the output in console
                    # Send gesture to Unity via socket
                client_socket.sendall(detected_gesture.encode())
                print(f"Sent gesture: {detected_gesture}")
           
=======
        if detected_gesture:
            # Display the detected gesture on the frame
            cv2.putText(frame, detected_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(detected_gesture)  # Print gesture to console
            
            # Send the detected gesture via socket to Unity
            client_socket.sendall(detected_gesture.encode())
            print(f"Sent gesture: {detected_gesture}")

>>>>>>> eac4cafec81f893680267e280f9a033cb771968a
    cv2.imshow("Hand Gesture Control", frame)
    
    if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
client_socket.close()
server_socket.close()
