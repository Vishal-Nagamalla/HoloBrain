import cv2
import mediapipe as mp
import numpy as np
import socket

# Initialize MediaPipe hands and drawing utilities
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)

# Variables to track gestures
gesture = None
prev_hand_state = None  # To store the previous hand state (palm or fist)
prev_dist = None  # Used for zoom detection
prev_pinch_pos = None  # To store the previous position of the pinch for drag

# Sensitivity thresholds
zoom_threshold = 0.15  # Adjust sensitivity for zoom (palm-to-fist zoom)
pinch_threshold = 0.03  # Adjust pinch detection sensitivity for drag

# Set up socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 65432))  # Localhost and port number for Unity connection
server_socket.listen(1)
print("Waiting for Unity to connect...")
client_socket, _ = server_socket.accept()
print("Unity connected!")

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

# Gesture detection
def detect_gesture(landmarks):
    global gesture, prev_hand_state, prev_pinch_pos, prev_dist
    
    # Extract x and y coordinates of specific landmarks for pinch detection
    index_finger_tip = landmarks[8]
    thumb_tip = landmarks[4]
    
    # Calculate pinch distance and midpoint
    current_dist = np.sqrt((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2)
    pinch_x = (index_finger_tip.x + thumb_tip.x) / 2
    pinch_y = (index_finger_tip.y + thumb_tip.y) / 2
    current_pinch_pos = (pinch_x, pinch_y)
    
    # Check for palm or fist states
    if is_palm(landmarks):
        current_hand_state = "palm"
    elif is_fist(landmarks):
        current_hand_state = "fist"
    else:
        current_hand_state = None  # Neither palm nor fist
        
    # Zoom gesture detection (palm to fist or fist to palm)
    if prev_hand_state == "palm" and current_hand_state == "fist":
        gesture = "zoom_in"  # Palm to fist -> Zoom in
    elif prev_hand_state == "fist" and current_hand_state == "palm":
        gesture = "zoom_out"  # Fist to palm -> Zoom out
    else:
        gesture = None  # No zoom gesture detected
    
    # Pinch detection for drag (if pinch detected, ignore palm/fist gestures)
    if current_dist < pinch_threshold:
        if prev_pinch_pos is not None:
            dx = current_pinch_pos[0] - prev_pinch_pos[0]
            dy = current_pinch_pos[1] - prev_pinch_pos[1]
            
            # Check for drag directions based on x and y movements
            if abs(dx) > abs(dy):  # Horizontal movement
                if dx > 0.05:  # Threshold to prevent minor movement detection
                    gesture = "drag_right"
                elif dx < -0.05:
                    gesture = "drag_left"
            else:  # Vertical movement
                if dy > 0.05:
                    gesture = "drag_down"
                elif dy < -0.05:
                    gesture = "drag_up"
        
        prev_pinch_pos = current_pinch_pos  # Update pinch position
        prev_dist = current_dist  # Update pinch distance for next frame
    else:
        prev_pinch_pos = None  # Reset pinch when not pinched

    # Update previous hand state for the next frame
    prev_hand_state = current_hand_state

    return gesture

# Capture video from webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    # Convert image to RGB for MediaPipe processing
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # Draw landmarks and detect gesture
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = hand_landmarks.landmark
            detected_gesture = detect_gesture(landmarks)

            if detected_gesture:
                cv2.putText(frame, detected_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(detected_gesture)  # To view the output in console
                      # Send gesture to Unity via socket
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