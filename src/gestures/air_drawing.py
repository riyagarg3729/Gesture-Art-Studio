
import cv2
import mediapipe as mp
import numpy as np
import colorsys
import time

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

canvas = None
previous_point = None

colors = {
    "1": (255, 0, 255),    # Purple
    "2": (255, 100, 0),    # Blue
    "3": (0, 255, 0),      # Green
    "4": (0, 0, 255),      # Red
    "5": (0, 255, 255),    # Yellow
    "6": (255, 255, 255)   # White
}

color = colors["1"]
brush_size = 5
rainbow_mode = False
eraser_mode = False
hue = 0

print("GESTURE ART STUDIO - ADVANCED AIR CANVAS")
print("Index finger UP = Draw")
print("Index + Middle UP = Stop")
print("1-6 = Change color")
print("+/- = Brush size")
print("R = Rainbow mode")
print("E = Eraser")
print("S = Save artwork")
print("C = Clear canvas")
print("Q = Quit")

try:
    while True:

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = np.zeros_like(frame)

        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if rainbow_mode:
            rgb_color = colorsys.hsv_to_rgb(hue, 1, 1)
            current_color = tuple(
                int(v * 255) for v in reversed(rgb_color)
            )
            hue = (hue + 0.003) % 1

        elif eraser_mode:
            current_color = (0, 0, 0)

        else:
            current_color = color

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            index_tip = hand.landmark[8]
            index_pip = hand.landmark[6]

            middle_tip = hand.landmark[12]
            middle_pip = hand.landmark[10]

            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            index_up = index_tip.y < index_pip.y
            middle_up = middle_tip.y < middle_pip.y

            if index_up and not middle_up:

                if previous_point is not None:
                    cv2.line(
                        canvas,
                        previous_point,
                        (x, y),
                        current_color,
                        brush_size,
                        cv2.LINE_AA
                    )

                previous_point = (x, y)

                cv2.circle(
                    frame,
                    (x, y),
                    max(5, brush_size),
                    current_color,
                    -1
                )

            else:
                previous_point = None

            mp.solutions.drawing_utils.draw_landmarks(
                frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )

        else:
            previous_point = None

        # Neon glow
        glow = cv2.GaussianBlur(canvas, (21, 21), 0)

        frame = cv2.addWeighted(frame, 1, glow, 0.7, 0)
        frame = cv2.addWeighted(frame, 1, canvas, 1, 0)

        # UI
        cv2.putText(
            frame,
            "GESTURE ART STUDIO",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        mode = "ERASER" if eraser_mode else (
            "RAINBOW" if rainbow_mode else "NORMAL"
        )

        cv2.putText(
            frame,
            f"MODE: {mode} | BRUSH: {brush_size}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            current_color,
            2
        )

        cv2.putText(
            frame,
            "1-6 COLORS | +/- SIZE | R RAINBOW | E ERASER",
            (20, h - 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "S SAVE | C CLEAR | Q QUIT",
            (20, h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 255),
            2
        )

        cv2.imshow("Gesture Art Studio - Advanced Canvas", frame)

        key = cv2.waitKey(1) & 0xFF

        if chr(key) in colors if key < 128 else False:
            color = colors[chr(key)]
            rainbow_mode = False
            eraser_mode = False
            previous_point = None

        elif key in (ord('+'), ord('=')):
            brush_size = min(brush_size + 2, 40)

        elif key in (ord('-'), ord('_')):
            brush_size = max(brush_size - 2, 1)

        elif key == ord('r'):
            rainbow_mode = not rainbow_mode
            eraser_mode = False
            previous_point = None

        elif key == ord('e'):
            eraser_mode = not eraser_mode
            rainbow_mode = False
            previous_point = None

        elif key == ord('s'):
            filename = f"artwork_{int(time.time())}.png"
            cv2.imwrite(filename, canvas)
            print(f"Artwork saved: {filename}")

        elif key == ord('c'):
            canvas = np.zeros_like(frame)
            previous_point = None
            print("Canvas cleared!")

        elif key == ord('q'):
            break

finally:
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
