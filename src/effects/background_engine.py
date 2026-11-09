
import cv2
import numpy as np
import random


class BackgroundEngine:

    def __init__(self):

        self.modes = [
            "CAMERA",
            "BLACK",
            "WHITE",
            "PURPLE",
            "BLUE",
            "GRADIENT",
            "GRID",
            "SPACE"
        ]

        self.current_index = 0

        random.seed(42)

        self.stars = [
            (
                random.randint(0, 1280),
                random.randint(0, 720),
                random.randint(1, 3)
            )
            for _ in range(120)
        ]

    def get_mode(self):

        return self.modes[self.current_index]

    def next_background(self):

        self.current_index = (
            self.current_index + 1
        ) % len(self.modes)

        return self.get_mode()

    def render(self, width, height, camera_frame=None):

        mode = self.get_mode()

        # CAMERA BACKGROUND
        if mode == "CAMERA" and camera_frame is not None:
            return camera_frame.copy()

        # BLACK BACKGROUND
        if mode == "BLACK":

            return np.zeros(
                (height, width, 3),
                dtype=np.uint8
            )

        # WHITE BACKGROUND
        if mode == "WHITE":

            return np.full(
                (height, width, 3),
                (245, 245, 245),
                dtype=np.uint8
            )

        # PURPLE BACKGROUND
        if mode == "PURPLE":

            return np.full(
                (height, width, 3),
                (45, 15, 65),
                dtype=np.uint8
            )

        # BLUE BACKGROUND
        if mode == "BLUE":

            return np.full(
                (height, width, 3),
                (65, 25, 10),
                dtype=np.uint8
            )

        # GRADIENT BACKGROUND
        if mode == "GRADIENT":

            background = np.zeros(
                (height, width, 3),
                dtype=np.uint8
            )

            top = np.array([65, 15, 25])
            bottom = np.array([10, 5, 35])

            for y in range(height):

                ratio = y / max(height - 1, 1)

                color = (
                    top * (1 - ratio) +
                    bottom * ratio
                )

                background[y, :] = color

            return background

        # NEON GRID BACKGROUND
        if mode == "GRID":

            background = np.full(
                (height, width, 3),
                (18, 8, 30),
                dtype=np.uint8
            )

            for x in range(0, width, 40):

                cv2.line(
                    background,
                    (x, 0),
                    (x, height),
                    (65, 35, 90),
                    1
                )

            for y in range(0, height, 40):

                cv2.line(
                    background,
                    (0, y),
                    (width, y),
                    (65, 35, 90),
                    1
                )

            return background

        # SPACE BACKGROUND
        if mode == "SPACE":

            background = np.full(
                (height, width, 3),
                (8, 5, 15),
                dtype=np.uint8
            )

            for x, y, radius in self.stars:

                sx = int(x * width / 1280)
                sy = int(y * height / 720)

                if sx < width and sy < height:

                    cv2.circle(
                        background,
                        (sx, sy),
                        radius,
                        (220, 220, 255),
                        -1,
                        cv2.LINE_AA
                    )

            return background

        return np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )
