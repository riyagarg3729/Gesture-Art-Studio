
import cv2
import mediapipe as mp
import time
from collections import deque
import math


class HandTracker:
    def __init__(self, max_hands=2, detection_confidence=0.7,
                 tracking_confidence=0.7):

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        self.mp_draw = mp.solutions.drawing_utils

        self.trail = deque(maxlen=25)
        self.smooth_point = None

    def draw_glow(self, frame, x, y):

        overlay = frame.copy()

        # Purple neon glow layers
        cv2.circle(overlay, (x, y), 30, (180, 0, 255), -1)
        cv2.circle(overlay, (x, y), 20, (220, 0, 255), -1)
        cv2.circle(overlay, (x, y), 10, (255, 100, 255), -1)

        cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)

        # Bright center
        cv2.circle(frame, (x, y), 6, (255, 255, 255), -1)

        cv2.circle(
            frame, (x, y), 12,
            (255, 0, 255), 2
        )

    def draw_trail(self, frame):

        points = list(self.trail)

        for i in range(1, len(points)):

            thickness = max(1, int(5 * i / len(points)))

            cv2.line(
                frame,
                points[i - 1],
                points[i],
                (255, 0, 255),
                thickness,
                cv2.LINE_AA
            )

    def detect_hands(self, frame):

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                # Purple hand skeleton
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(
                        color=(255, 0, 255),
                        thickness=2,
                        circle_radius=3
                    ),
                    self.mp_draw.DrawingSpec(
                        color=(180, 0, 255),
                        thickness=3
                    )
                )

                # Index fingertip (Landmark 8)
                index_finger = hand_landmarks.landmark[8]

                h, w, _ = frame.shape

                x = int(index_finger.x * w)
                y = int(index_finger.y * h)

                # Smooth movement
                if self.smooth_point is None:
                    self.smooth_point = (x, y)
                else:
                    sx, sy = self.smooth_point

                    smooth_x = int(sx * 0.65 + x * 0.35)
                    smooth_y = int(sy * 0.65 + y * 0.35)

                    self.smooth_point = (smooth_x, smooth_y)

                px, py = self.smooth_point

                # Update neon trail
                self.trail.append((px, py))

                self.draw_trail(frame)
                self.draw_glow(frame, px, py)

                cv2.putText(
                    frame,
                    "INDEX FINGER TRACKING",
                    (px + 20, py - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 100, 255),
                    2
                )

        else:
            self.trail.clear()
            self.smooth_point = None

        return frame

    def close(self):
        self.hands.close()


def main():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Webcam not detected!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    tracker = HandTracker()

    previous_time = 0

    print("Gesture Art Studio 3D - Neon Tracking Started!")
    print("Move your index finger to see the purple glow.")
    print("Press Q to exit.")

    try:
        while True:

            success, frame = cap.read()

            if not success:
                print("Unable to read webcam frame.")
                break

            frame = cv2.flip(frame, 1)

            frame = tracker.detect_hands(frame)

            current_time = time.time()

            fps = (
                1 / (current_time - previous_time)
                if previous_time else 0
            )

            previous_time = current_time

            cv2.putText(
                frame,
                f"FPS: {int(fps)}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "GESTURE ART STUDIO 3D",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "Gesture Art Studio 3D - Neon Tracking",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        tracker.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
