
import cv2
import mediapipe as mp

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Start webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Webcam not detected!")
    exit()

print("GESTURE ART STUDIO 3D STARTED!")
print("Show your hand to the camera.")
print("Press Q to exit.")

while True:
    success, frame = cap.read()

    if not success:
        print("Camera frame unavailable.")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # Convert image to RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect hands
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:

            # Draw hand landmarks
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Get index fingertip
            index_tip = hand_landmarks.landmark[8]

            h, w, _ = frame.shape

            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Glowing fingertip marker
            cv2.circle(frame, (x, y), 20, (255, 0, 255), -1)
            cv2.circle(frame, (x, y), 28, (255, 255, 255), 2)

    cv2.putText(
        frame,
        "GESTURE ART STUDIO 3D",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.imshow("Gesture Art Studio 3D", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
hands.close()
cv2.destroyAllWindows()
