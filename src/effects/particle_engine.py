
import cv2
import numpy as np
import random
import math


class ParticleEngine:

    def __init__(self):
        self.particles = []
        self.trails = []

    # ---------------- PARTICLE EMISSION ----------------

    def emit(self, x, y, color, count=4):

        # Add one point to the neon hand trail
        self.trails.append({
            "x": float(x),
            "y": float(y),
            "color": color,
            "life": 30,
            "max_life": 30,
            "size": 8
        })

        # Limit trail points
        if len(self.trails) > 70:
            self.trails = self.trails[-70:]

        # Create particles
        for _ in range(count):

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)

            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20, 45),
                "max_life": 45,
                "size": random.randint(3, 8),
                "color": color
            })

    # ---------------- PARTICLE BURST ----------------

    def burst(self, x, y, color, count=80):

        self.emit(x, y, color, count)

        for p in self.particles[-count:]:

            p["vx"] *= 2.5
            p["vy"] *= 2.5
            p["size"] += 2

    # ---------------- UPDATE ----------------

    def update(self):

        # Update particles
        for p in self.particles:

            p["x"] += p["vx"]
            p["y"] += p["vy"]

            p["vy"] += 0.04

            p["vx"] *= 0.98
            p["vy"] *= 0.98

            p["life"] -= 1

        self.particles = [
            p for p in self.particles
            if p["life"] > 0
        ]

        # Update neon trail
        for point in self.trails:
            point["life"] -= 1

        self.trails = [
            point for point in self.trails
            if point["life"] > 0
        ]

    # ---------------- NEON TRAIL RENDER ----------------

    def render_trail(self, frame):

        if not self.trails:
            return

        glow = np.zeros_like(frame)

        # Connect consecutive trail points
        for i in range(1, len(self.trails)):

            previous = self.trails[i - 1]
            current = self.trails[i]

            x1 = int(previous["x"])
            y1 = int(previous["y"])

            x2 = int(current["x"])
            y2 = int(current["y"])

            life_ratio = min(
                previous["life"] / previous["max_life"],
                current["life"] / current["max_life"]
            )

            if life_ratio <= 0:
                continue

            color = current["color"]

            thickness = max(
                1,
                int(12 * life_ratio)
            )

            # Outer neon glow
            cv2.line(
                glow,
                (x1, y1),
                (x2, y2),
                color,
                thickness * 3,
                cv2.LINE_AA
            )

            # Inner bright line
            cv2.line(
                glow,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

        # Smooth glow
        glow = cv2.GaussianBlur(
            glow,
            (21, 21),
            0
        )

        cv2.addWeighted(
            glow,
            0.85,
            frame,
            1.0,
            0,
            frame
        )

        return frame

    # ---------------- PARTICLE RENDER ----------------

    def render(self, frame):

        # Render neon hand trail first
        self.render_trail(frame)

        overlay = np.zeros_like(frame)

        for p in self.particles:

            x = int(p["x"])
            y = int(p["y"])

            life_ratio = p["life"] / p["max_life"]

            size = max(
                1,
                int(p["size"] * life_ratio)
            )

            color = p["color"]

            # Particle glow
            cv2.circle(
                overlay,
                (x, y),
                size * 3,
                color,
                -1,
                cv2.LINE_AA
            )

            # Bright particle center
            cv2.circle(
                frame,
                (x, y),
                size,
                (255, 255, 255),
                -1,
                cv2.LINE_AA
            )

        overlay = cv2.GaussianBlur(
            overlay,
            (11, 11),
            0
        )

        cv2.addWeighted(
            overlay,
            0.35,
            frame,
            1.0,
            0,
            frame
        )

        return frame
