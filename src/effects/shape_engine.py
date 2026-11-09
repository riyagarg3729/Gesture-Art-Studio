
import cv2
import numpy as np
import math


class ShapeEngine:

    def __init__(self):
        self.shape = "CIRCLE"
        self.start_point = None
        self.end_point = None
        self.active = False

    def start(self, x, y, shape="CIRCLE"):

        self.start_point = (x, y)
        self.end_point = (x, y)

        self.shape = shape
        self.active = True

    def update(self, x, y):

        if self.active:
            self.end_point = (x, y)

    def draw_shape(self, image, color, thickness=3):

        if not self.active:
            return image

        if self.start_point is None:
            return image

        x1, y1 = self.start_point
        x2, y2 = self.end_point

        preview = image.copy()

        if self.shape == "CIRCLE":

            radius = int(
                math.hypot(x2 - x1, y2 - y1)
            )

            cv2.circle(
                preview,
                (x1, y1),
                radius,
                color,
                thickness,
                cv2.LINE_AA
            )

        elif self.shape == "RECTANGLE":

            cv2.rectangle(
                preview,
                (x1, y1),
                (x2, y2),
                color,
                thickness,
                cv2.LINE_AA
            )

        elif self.shape == "TRIANGLE":

            points = np.array([
                [x1, y2],
                [x2, y2],
                [(x1 + x2) // 2, y1]
            ], np.int32)

            cv2.polylines(
                preview,
                [points],
                True,
                color,
                thickness,
                cv2.LINE_AA
            )

        elif self.shape == "STAR":

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            outer_radius = int(
                math.hypot(x2 - x1, y2 - y1) / 2
            )

            inner_radius = outer_radius * 0.4

            points = []

            for i in range(10):

                angle = (
                    -math.pi / 2
                    + i * math.pi / 5
                )

                radius = (
                    outer_radius
                    if i % 2 == 0
                    else inner_radius
                )

                px = int(cx + radius * math.cos(angle))
                py = int(cy + radius * math.sin(angle))

                points.append([px, py])

            points = np.array(points, np.int32)

            cv2.polylines(
                preview,
                [points],
                True,
                color,
                thickness,
                cv2.LINE_AA
            )

        return preview

    def finish(self, canvas, color, thickness=3):

        if not self.active:
            return canvas

        result = self.draw_shape(
            canvas,
            color,
            thickness
        )

        self.active = False
        self.start_point = None
        self.end_point = None

        return result

    def cancel(self):

        self.active = False
        self.start_point = None
        self.end_point = None
