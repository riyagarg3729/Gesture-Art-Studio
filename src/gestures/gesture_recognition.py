
import cv2
import mediapipe as mp
import time


class GestureRecognition:

    def __init__(self):
        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.drawer = mp.solutions.drawing_utils

    def recognize(self, hand):

        lm = hand.landmark

        fingers = []

        # Thumb
        fingers.append(lm[4].x < lm[3].x)

        # Index, Middle, Ring, Pinky
        for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            fingers.append(lm[tip].y < lm[pip].y)

        thumb, index, middle, ring, pinky = fingers

        # Pinch detection
        pinch_distance = (
            (lm[4].x - lm[8].x) ** 2 +
            (lm[4].y - lm[8].y) ** 2
        ) ** 0.5

        if pinch_distance < 0.045:
            return "PINCH / ERASER"

        # Open palm
        if all(fingers):
            return "OPEN PALM / PAUSE"

        # Thumb only: Previous color
        if thumb and not index and not middle and not ring and not pinky:
            return "THUMB / PREVIOUS COLOR"

        # Four fingers: Next color
        if not thumb and index and middle and ring and pinky:
            return "FOUR FINGERS / NEXT COLOR"

        # Fist
        if not any(fingers):
            return "FIST / CLEAR"

        # Three fingers: Magic Burst
        if index and middle and ring and not pinky:
            return "THREE FINGERS / MAGIC"

        # Peace
        if index and middle and not ring and not pinky:
            return "PEACE / STOP DRAWING"

        # Index
        if index and not middle and not ring and not pinky:
            return "INDEX / DRAW"

        return "UNKNOWN"

    def close(self):
        self.hands.close()


def main():

    detector = GestureRecognition()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Webcam not detected!")
        detector.close()
        return

    print("GESTURE RECOGNITION STARTED")
    print("Press Q to exit")

    last_gesture = ""
    last_time = 0

    try:
        while True:

            success, frame = cap.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.hands.process(rgb)

            gesture = "NO HAND DETECTED"

            if results.multi_hand_landmarks:

                hand = results.multi_hand_landmarks[0]

                gesture = detector.recognize(hand)

                detector.drawer.draw_landmarks(
                    frame,
                    hand,
                    detector.mp_hands.HAND_CONNECTIONS
                )

            if gesture != last_gesture:
                last_gesture = gesture
                last_time = time.time()
                print("Gesture:", gesture)

            cv2.putText(
                frame,
                "GESTURE ART STUDIO",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                gesture,
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 255),
                2
            )

            cv2.imshow("Gesture Recognition", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
