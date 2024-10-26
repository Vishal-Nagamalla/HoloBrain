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
zoom_threshold = 0.1  # Adjust sensitivity of pinch zoom
prev_dist = None

# Set up socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 65432))  # Localhost and port number for Unity connection
server_socket.listen(1)
print("Waiting for Unity to connect...")
client_socket, _ = server_socket.accept()
print("Unity connected!")

def detect_gesture(landmarks):
    global gesture, prev_dist
    
    # Extract x and y coordinates of specific landmarks for gesture detection
    wrist = landmarks[0]
    index_finger_tip = landmarks[8]
    thumb_tip = landmarks[4]
    
    # Calculate distance between thumb and index finger (pinch gesture)
    current_dist = np.sqrt((index_finger_tip.x - thumb_tip.x) ** 2 + (index_finger_tip.y - thumb_tip.y) ** 2)
    
    # Zoom detection
    if prev_dist is not None:
        if current_dist - prev_dist > zoom_threshold:
            gesture = "zoom_in"
        elif prev_dist - current_dist > zoom_threshold:
            gesture = "zoom_out"
        else:
            gesture = None
    prev_dist = current_dist
    
    # Swipe gestures based on hand position changes
    if index_finger_tip.x < wrist.x - 0.1:
        gesture = "rotate_left"
    elif index_finger_tip.x > wrist.x + 0.1:
        gesture = "rotate_right"
    elif index_finger_tip.y < wrist.y - 0.1:
        gesture = "rotate_up"
    elif index_finger_tip.y > wrist.y + 0.1:
        gesture = "rotate_down"

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
                # Display gesture on the video feed
                cv2.putText(frame, detected_gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                print(detected_gesture)  # To view the output in console

                # Send gesture to Unity via socket
                client_socket.sendall(detected_gesture.encode())
                print(f"Sent gesture: {detected_gesture}")
            
    cv2.imshow("Hand Gesture Control", frame)
    
    if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
hands.close()
client_socket.close()
server_socket.close()