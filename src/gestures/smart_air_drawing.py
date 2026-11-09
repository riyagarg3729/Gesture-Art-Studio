import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

import cv2
import mediapipe as mp
import numpy as np
import time

from effects.particle_engine import ParticleEngine
from effects.vfx_engine import VFXEngine
from effects.shape_engine import ShapeEngine
from effects.background_engine import BackgroundEngine
from effects.segmentation_engine import SegmentationEngine


# =================================
# MEDIAPIPE SETUP
# =================================

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Webcam could not be opened!")


# =================================
# CANVAS SETTINGS
# =================================

canvas = None
previous_point = None
previous_gesture = ""

last_hand_position = None
hand_speed = 0


# =================================
# ENGINES
# =================================

particle_engine = ParticleEngine()
vfx_engine = VFXEngine()
shape_engine = ShapeEngine()
background_engine = BackgroundEngine()
segmentation_engine = SegmentationEngine()

current_effect = "fire"
burst_cooldown = 0


# =================================
# SHAPE SETTINGS
# =================================

shape_mode = False
current_shape = "CIRCLE"
shape_snapshot = None


# =================================
# BRUSH SETTINGS
# =================================

brush_size = 7
MIN_BRUSH = 2
MAX_BRUSH = 40


# =================================
# COLORS
# =================================

colors = {
    "1": (255, 0, 255),
    "2": (255, 100, 0),
    "3": (0, 255, 0),
    "4": (0, 0, 255),
    "5": (0, 255, 255),
    "6": (255, 255, 255)
}

color_keys = list(colors.keys())

current_color_index = 0
current_color = colors[color_keys[0]]


# =================================
# UNDO / REDO
# =================================

undo_stack = []
redo_stack = []

MAX_HISTORY = 20

stroke_active = False
stroke_snapshot = None


def save_undo_state(snapshot):

    if snapshot is None:
        return

    undo_stack.append(snapshot.copy())

    if len(undo_stack) > MAX_HISTORY:
        undo_stack.pop(0)

    redo_stack.clear()


def commit_stroke():

    global stroke_active, stroke_snapshot

    if stroke_active:

        save_undo_state(stroke_snapshot)

        stroke_active = False
        stroke_snapshot = None


def commit_shape():

    global canvas, shape_snapshot

    if not shape_engine.active:
        return

    canvas = shape_engine.finish(
        canvas,
        current_color,
        brush_size
    )

    if shape_snapshot is not None:
        save_undo_state(shape_snapshot)

    shape_snapshot = None

    print("Shape completed!")


def undo_action():

    global canvas

    commit_stroke()
    commit_shape()

    if undo_stack:

        redo_stack.append(canvas.copy())
        canvas = undo_stack.pop()

        print("UNDO SUCCESSFUL!")

    else:

        print("Nothing to undo!")


def redo_action():

    global canvas

    commit_stroke()
    commit_shape()

    if redo_stack:

        undo_stack.append(canvas.copy())

        if len(undo_stack) > MAX_HISTORY:
            undo_stack.pop(0)

        canvas = redo_stack.pop()

        print("REDO SUCCESSFUL!")

    else:

        print("Nothing to redo!")


# =================================
# START MESSAGE
# =================================

print("\n================================")
print("GESTURE ART STUDIO 3D STARTED!")
print("================================")

print("Index = Draw")
print("Peace = Stop")
print("Open Palm = Pause")
print("Three Fingers = Magic")
print("Fist = Clear")
print("Pinch = Eraser")

print("Thumb = Previous Color")
print("Four Fingers = Next Color")

print("\nSHAPE CONTROLS")
print("G = Shape Mode ON/OFF")
print("7 = Circle")
print("8 = Rectangle")
print("9 = Triangle")
print("0 = Star")

print("\nBACKGROUND CONTROLS")
print("T = Next Background")

print("\nOTHER CONTROLS")
print("Z = Undo | Y = Redo")
print("F = Fire | M = Magic | B = Smoke")
print("R = Rainbow | E = VFX Off")
print("1-6 = Colors")
print("+/- = Brush Size")
print("S = Save | Q = Quit")

print("================================")


# =================================
# MAIN APPLICATION
# =================================

try:

    while True:

        success, camera_frame = cap.read()

        if not success:
            print("Webcam not working!")
            break

        camera_frame = cv2.flip(camera_frame, 1)

        h, w, _ = camera_frame.shape

        if canvas is None:
            canvas = np.zeros_like(camera_frame)

        # Keep camera image for hand tracking
        rgb = cv2.cvtColor(
            camera_frame,
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(rgb)

        # Render selected background
        selected_background = background_engine.render(
            w,
            h,
            camera_frame
        )

        # Keep the person from the camera and replace the surrounding background
        display_frame = segmentation_engine.remove_background(
            camera_frame,
            selected_background
        )

        gesture = "NO HAND"
        previous_action = previous_gesture


        # =================================
        # HAND DETECTION
        # =================================

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            thumb_up = lm[4].x < lm[3].x

            index_up = lm[8].y < lm[6].y
            middle_up = lm[12].y < lm[10].y
            ring_up = lm[16].y < lm[14].y
            pinky_up = lm[20].y < lm[18].y

            x = int(lm[8].x * w)
            y = int(lm[8].y * h)

            distance = np.hypot(
                lm[4].x - lm[8].x,
                lm[4].y - lm[8].y
            )

            brush_distance = np.hypot(
                lm[4].x - lm[12].x,
                lm[4].y - lm[12].y
            )


            # =================================
            # GESTURE RECOGNITION
            # =================================

            if distance < 0.045:

                gesture = "ERASER"

            elif (
                thumb_up
                and index_up
                and middle_up
                and ring_up
                and pinky_up
            ):

                gesture = "PAUSED"

            elif (
                thumb_up
                and not index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            ):

                gesture = "PREVIOUS COLOR"

            elif (
                not thumb_up
                and index_up
                and middle_up
                and ring_up
                and pinky_up
            ):

                gesture = "NEXT COLOR"

            elif not any([
                index_up,
                middle_up,
                ring_up,
                pinky_up
            ]):

                gesture = "CLEAR"

            elif (
                index_up
                and middle_up
                and ring_up
                and not pinky_up
            ):

                gesture = "MAGIC"

            elif (
                index_up
                and middle_up
                and not ring_up
                and not pinky_up
            ):

                gesture = "STOP"

            elif (
                index_up
                and not middle_up
                and not ring_up
                and not pinky_up
            ):

                gesture = "DRAW"

            else:

                gesture = "UNKNOWN"


            # =================================
            # BRUSH SIZE CONTROL
            # =================================

            if gesture not in ["DRAW", "ERASER"]:

                brush_size = int(
                    np.interp(
                        brush_distance,
                        [0.05, 0.35],
                        [MIN_BRUSH, MAX_BRUSH]
                    )
                )

                brush_size = max(
                    MIN_BRUSH,
                    min(MAX_BRUSH, brush_size)
                )


            # =================================
            # SHAPE DRAWING
            # =================================

            is_shape_drawing = (
                shape_mode and gesture == "DRAW"
            )

            if is_shape_drawing:

                if not shape_engine.active:

                    commit_stroke()

                    shape_snapshot = canvas.copy()

                    shape_engine.start(
                        x,
                        y,
                        current_shape
                    )

                    print("Started:", current_shape)

                else:

                    shape_engine.update(x, y)

            else:

                if shape_engine.active:
                    commit_shape()


            # =================================
            # STROKE HISTORY
            # =================================

            if (
                gesture in ["DRAW", "ERASER"]
                and not is_shape_drawing
            ):

                if not stroke_active:

                    stroke_snapshot = canvas.copy()
                    stroke_active = True

            else:

                commit_stroke()


            # =================================
            # COLOR SWITCHING
            # =================================

            if (
                gesture == "PREVIOUS COLOR"
                and previous_action != "PREVIOUS COLOR"
            ):

                current_color_index = (
                    current_color_index - 1
                ) % len(color_keys)

                current_color = colors[
                    color_keys[current_color_index]
                ]

                previous_point = None
                last_hand_position = None

                print("Previous Color Selected!")

            elif (
                gesture == "NEXT COLOR"
                and previous_action != "NEXT COLOR"
            ):

                current_color_index = (
                    current_color_index + 1
                ) % len(color_keys)

                current_color = colors[
                    color_keys[current_color_index]
                ]

                previous_point = None
                last_hand_position = None

                print("Next Color Selected!")


            # =================================
            # MAGIC BURST
            # =================================

            if (
                gesture == "MAGIC"
                and previous_action != "MAGIC"
                and burst_cooldown == 0
            ):

                magic_x = int(lm[9].x * w)
                magic_y = int(lm[9].y * h)

                vfx_engine.burst(
                    magic_x,
                    magic_y,
                    count=100
                )

                burst_cooldown = 30

                print("MAGIC BURST ACTIVATED!")


            # =================================
            # CLEAR CANVAS
            # =================================

            if (
                gesture == "CLEAR"
                and previous_action != "CLEAR"
            ):

                commit_stroke()
                commit_shape()

                if np.any(canvas):

                    save_undo_state(canvas)

                    canvas = np.zeros_like(camera_frame)

                    print("Canvas cleared!")

                previous_point = None


            # =================================
            # FREEHAND DRAWING / ERASER
            # =================================

            if (
                gesture in ["DRAW", "ERASER"]
                and not is_shape_drawing
            ):

                thickness = (
                    35 if gesture == "ERASER"
                    else brush_size
                )

                draw_color = (
                    (0, 0, 0)
                    if gesture == "ERASER"
                    else current_color
                )

                if previous_point is not None:

                    cv2.line(
                        canvas,
                        previous_point,
                        (x, y),
                        draw_color,
                        thickness,
                        cv2.LINE_AA
                    )

                previous_point = (x, y)

                if gesture == "DRAW":

                    if last_hand_position is not None:

                        hand_speed = np.hypot(
                            x - last_hand_position[0],
                            y - last_hand_position[1]
                        )

                    else:

                        hand_speed = 0

                    last_hand_position = (x, y)

                    particle_count = min(
                        3 + int(hand_speed / 15),
                        15
                    )

                    particle_engine.emit(
                        x,
                        y,
                        current_color,
                        count=particle_count
                    )

                    if current_effect is not None:

                        vfx_count = min(
                            3 + int(hand_speed / 12),
                            20
                        )

                        vfx_engine.emit(
                            x,
                            y,
                            effect=current_effect,
                            count=vfx_count
                        )

                        vfx_engine.add_trail(
                            x,
                            y,
                            current_color
                        )

                else:

                    last_hand_position = None

                cv2.circle(
                    display_frame,
                    (x, y),
                    10,
                    current_color,
                    -1
                )


            # =================================
            # SHAPE CURSOR
            # =================================

            elif is_shape_drawing:

                previous_point = None
                last_hand_position = None

                cv2.circle(
                    display_frame,
                    (x, y),
                    10,
                    current_color,
                    -1
                )

            else:

                previous_point = None
                last_hand_position = None


            # =================================
            # HAND LANDMARKS
            # =================================

            mp_draw.draw_landmarks(
                display_frame,
                hand,
                mp_hands.HAND_CONNECTIONS
            )


        # =================================
        # HAND DISAPPEARED
        # =================================

        else:

            if shape_engine.active:
                commit_shape()

            commit_stroke()

            previous_point = None
            last_hand_position = None


        # =================================
        # MAGIC COOLDOWN
        # =================================

        if burst_cooldown > 0:
            burst_cooldown -= 1

        previous_gesture = gesture


        # =================================
        # SHAPE PREVIEW
        # =================================

        display_canvas = canvas.copy()

        if shape_engine.active:

            display_canvas = shape_engine.draw_shape(
                canvas,
                current_color,
                brush_size
            )


        # =================================
        # BACKGROUND + CANVAS COMPOSITION
        # =================================

        glow = cv2.GaussianBlur(
            display_canvas,
            (21, 21),
            0
        )

        artwork_frame = cv2.addWeighted(
            display_frame,
            1,
            glow,
            0.7,
            0
        )

        artwork_frame = cv2.addWeighted(
            artwork_frame,
            1,
            display_canvas,
            1,
            0
        )


        # =================================
        # PARTICLES
        # =================================

        particle_engine.update()

        artwork_frame = particle_engine.render(
            artwork_frame
        )


        # =================================
        # VFX
        # =================================

        vfx_engine.update()

        artwork_frame = vfx_engine.render(
            artwork_frame
        )


        # =================================
        # INTERFACE
        # =================================

        frame = artwork_frame.copy()

        cv2.putText(
            frame,
            "GESTURE ART STUDIO 3D",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"GESTURE: {gesture}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 0, 255),
            2
        )

        cv2.putText(
            frame,
            f"BRUSH SIZE: {brush_size}",
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"SHAPE MODE: {'ON' if shape_mode else 'OFF'}",
            (20, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 0) if shape_mode else (200, 200, 200),
            2
        )

        cv2.putText(
            frame,
            f"SHAPE: {current_shape}",
            (20, 185),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 200, 0),
            2
        )

        cv2.putText(
            frame,
            f"BACKGROUND: {background_engine.get_mode()}",
            (20, 220),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            f"VFX: {current_effect.upper() if current_effect else 'OFF'}",
            (20, 255),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            f"COLOR: {color_keys[current_color_index]}",
            (20, 290),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            current_color,
            2
        )

        cv2.putText(
            frame,
            f"UNDO: {len(undo_stack)}  REDO: {len(redo_stack)}",
            (20, 325),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "G MODE | 7 CIRCLE | 8 RECT | 9 TRIANGLE | 0 STAR",
            (20, h - 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "T BACKGROUND | Z UNDO | Y REDO | F FIRE | M MAGIC",
            (20, h - 42),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            "1-6 COLORS | +/- BRUSH | S SAVE | Q QUIT",
            (20, h - 19),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (255, 255, 255),
            1
        )


        # =================================
        # DISPLAY
        # =================================

        cv2.imshow(
            "Smart Gesture Art Studio",
            frame
        )


        # =================================
        # KEYBOARD CONTROLS
        # =================================

        key = cv2.waitKey(1) & 0xFF


        # UNDO

        if key == ord("z"):

            undo_action()

            previous_point = None
            last_hand_position = None


        # REDO

        elif key == ord("y"):

            redo_action()

            previous_point = None
            last_hand_position = None


        # SHAPE MODE

        elif key == ord("g"):

            commit_shape()
            commit_stroke()

            shape_mode = not shape_mode

            previous_point = None

            print(
                "SHAPE MODE:",
                "ON" if shape_mode else "OFF"
            )


        # CIRCLE

        elif key == ord("7"):

            commit_shape()

            current_shape = "CIRCLE"

            print("Circle Selected!")


        # RECTANGLE

        elif key == ord("8"):

            commit_shape()

            current_shape = "RECTANGLE"

            print("Rectangle Selected!")


        # TRIANGLE

        elif key == ord("9"):

            commit_shape()

            current_shape = "TRIANGLE"

            print("Triangle Selected!")


        # STAR

        elif key == ord("0"):

            commit_shape()

            current_shape = "STAR"

            print("Star Selected!")


        # =================================
        # BACKGROUND SWITCHING
        # =================================

        elif key == ord("t"):

            commit_shape()
            commit_stroke()

            selected_background = (
                background_engine.next_background()
            )

            previous_point = None

            print(
                "Background Selected:",
                selected_background
            )


        # =================================
        # VFX
        # =================================

        elif key == ord("f"):

            current_effect = "fire"
            print("Fire Effect Selected!")


        elif key == ord("m"):

            current_effect = "magic"
            print("Magic Effect Selected!")


        elif key == ord("b"):

            current_effect = "smoke"
            print("Smoke Effect Selected!")


        elif key == ord("r"):

            current_effect = "rainbow"
            print("Rainbow Effect Selected!")


        elif key == ord("e"):

            current_effect = None
            print("VFX Disabled!")


        # =================================
        # COLORS
        # =================================

        elif key < 128 and chr(key) in colors:

            current_color_index = color_keys.index(
                chr(key)
            )

            current_color = colors[
                chr(key)
            ]

            previous_point = None

            print("Color selected!")


        # =================================
        # BRUSH SIZE
        # =================================

        elif key in [ord("+"), ord("=")]:

            brush_size = min(
                brush_size + 2,
                MAX_BRUSH
            )


        elif key in [ord("-"), ord("_")]:

            brush_size = max(
                brush_size - 2,
                MIN_BRUSH
            )


        # =================================
        # SAVE ARTWORK
        # =================================

        elif key == ord("s"):

            commit_shape()
            commit_stroke()

            filename = (
                f"artwork_{int(time.time())}.png"
            )

            cv2.imwrite(
                filename,
                artwork_frame
            )

            print(
                "Artwork with background saved:",
                filename
            )


        # =================================
        # QUIT
        # =================================

        elif key == ord("q"):

            break


finally:

    hands.close()
    segmentation_engine.close()
    cap.release()
    cv2.destroyAllWindows()

    print("Gesture Art Studio Closed!")