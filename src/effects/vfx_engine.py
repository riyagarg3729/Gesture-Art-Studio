
import cv2
import random
import math
import colorsys


class VFXEngine:

    def __init__(self):
        self.particles = []
        self.rainbow_hue = 0

        self.rings = []
        self.sparks = []
        self.shockwaves = []

        self.trails = []
        self.energy_orbs = []

    def emit(self, x, y, effect="fire", count=5):

        for _ in range(count):

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)

            if effect == "fire":
                color = random.choice([
                    (0, 80, 255), (0, 140, 255),
                    (0, 200, 255), (0, 255, 255)
                ])
                vx = random.uniform(-2, 2)
                vy = random.uniform(-4, -1)
                size = random.randint(4, 9)
                life = 35

            elif effect == "smoke":
                color = random.choice([
                    (100, 100, 100),
                    (150, 150, 150),
                    (190, 190, 190)
                ])
                vx = random.uniform(-1, 1)
                vy = random.uniform(-2, -0.5)
                size = random.randint(7, 14)
                life = 60

            elif effect == "magic":
                color = random.choice([
                    (255, 0, 255),
                    (255, 100, 0),
                    (255, 255, 0),
                    (255, 255, 255)
                ])
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                size = random.randint(3, 7)
                life = 45

            elif effect == "rainbow":
                self.rainbow_hue = (
                    self.rainbow_hue + 0.025
                ) % 1.0

                rgb = colorsys.hsv_to_rgb(
                    self.rainbow_hue, 1, 1
                )

                color = tuple(
                    int(c * 255) for c in reversed(rgb)
                )

                vx = random.uniform(-1, 1)
                vy = random.uniform(-1, 1)
                size = random.randint(3, 7)
                life = 40

            else:
                continue

            self.particles.append({
                "x": float(x),
                "y": float(y),
                "vx": vx,
                "vy": vy,
                "color": color,
                "size": size,
                "life": life,
                "max_life": life,
                "effect": effect
            })

    def add_trail(self, x, y, color=(255, 0, 255)):

        self.trails.append({
            "x": float(x),
            "y": float(y),
            "color": color,
            "life": 22,
            "max_life": 22,
            "size": random.randint(4, 8)
        })

        if len(self.trails) > 100:
            self.trails.pop(0)

    def burst(self, x, y, count=100):

        self.emit(x, y, "magic", count)

        # 3D-style energy rings
        for i in range(3):

            self.rings.append({
                "x": float(x),
                "y": float(y),
                "radius": 10,
                "max_radius": 180 + i * 60,
                "speed": 5 + i * 1.5,
                "life": 45,
                "max_life": 45,
                "color": random.choice([
                    (255, 0, 255),
                    (255, 100, 0),
                    (255, 255, 255)
                ]),
                "angle": random.uniform(0, 360),
                "rotation": random.choice([-5, 5]),
                "depth": random.uniform(0.35, 0.65)
            })

        # Electric sparks
        for _ in range(35):

            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 8)

            self.sparks.append({
                "x": float(x),
                "y": float(y),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.randint(20, 35),
                "max_life": 35,
                "color": random.choice([
                    (255, 0, 255),
                    (255, 255, 255),
                    (255, 100, 0)
                ])
            })

        # Expanding shockwave
        self.shockwaves.append({
            "x": float(x),
            "y": float(y),
            "radius": 5,
            "speed": 12,
            "max_radius": 280,
            "life": 30,
            "max_life": 30,
            "color": (255, 255, 255)
        })

        # Energy orb
        self.energy_orbs.append({
            "x": float(x),
            "y": float(y),
            "radius": 12,
            "life": 35,
            "max_life": 35,
            "phase": 0
        })

    def update(self):

        # Normal particles
        for p in self.particles:

            p["x"] += p["vx"]
            p["y"] += p["vy"]

            if p["effect"] == "fire":
                p["vy"] -= 0.04

            elif p["effect"] == "smoke":
                p["size"] += 0.08
                p["vx"] *= 0.98

            else:
                p["vx"] *= 0.98
                p["vy"] *= 0.98

            p["life"] -= 1

        self.particles = [
            p for p in self.particles if p["life"] > 0
        ]

        # Energy rings
        for ring in self.rings:
            ring["radius"] += ring["speed"]
            ring["angle"] += ring["rotation"]
            ring["life"] -= 1

        self.rings = [
            r for r in self.rings
            if r["life"] > 0
            and r["radius"] < r["max_radius"]
        ]

        # Electric sparks
        for spark in self.sparks:

            spark["x"] += spark["vx"]
            spark["y"] += spark["vy"]

            spark["vx"] *= 0.94
            spark["vy"] *= 0.94
            spark["life"] -= 1

        self.sparks = [
            s for s in self.sparks if s["life"] > 0
        ]

        # Shockwaves
        for wave in self.shockwaves:
            wave["radius"] += wave["speed"]
            wave["life"] -= 1

        self.shockwaves = [
            w for w in self.shockwaves
            if w["life"] > 0
            and w["radius"] < w["max_radius"]
        ]

        # Light trails
        for trail in self.trails:
            trail["life"] -= 1

        self.trails = [
            t for t in self.trails if t["life"] > 0
        ]

        # Energy orbs
        for orb in self.energy_orbs:
            orb["life"] -= 1
            orb["phase"] += 0.15
            orb["radius"] += 0.5

        self.energy_orbs = [
            o for o in self.energy_orbs if o["life"] > 0
        ]

    def render(self, frame):

        overlay = frame.copy()

        # Normal particles
        for p in self.particles:

            x = int(p["x"])
            y = int(p["y"])

            ratio = p["life"] / p["max_life"]
            size = max(1, int(p["size"] * ratio))
            color = p["color"]

            if p["effect"] == "smoke":
                cv2.circle(
                    overlay, (x, y), size,
                    color, -1, cv2.LINE_AA
                )
            else:
                cv2.circle(
                    overlay, (x, y), size * 2,
                    color, -1, cv2.LINE_AA
                )

                cv2.circle(
                    frame, (x, y), size,
                    (255, 255, 255), -1, cv2.LINE_AA
                )

        # Neon light trails
        for trail in self.trails:

            x = int(trail["x"])
            y = int(trail["y"])

            ratio = trail["life"] / trail["max_life"]
            size = max(1, int(trail["size"] * ratio))

            cv2.circle(
                overlay,
                (x, y),
                size * 3,
                trail["color"],
                -1,
                cv2.LINE_AA
            )

            cv2.circle(
                frame,
                (x, y),
                size,
                (255, 255, 255),
                -1,
                cv2.LINE_AA
            )

        # Energy orbs
        for orb in self.energy_orbs:

            x = int(orb["x"])
            y = int(orb["y"])

            pulse = math.sin(orb["phase"]) * 4
            radius = max(2, int(orb["radius"] + pulse))

            cv2.circle(
                overlay, (x, y), radius * 3,
                (255, 0, 255), -1, cv2.LINE_AA
            )

            cv2.circle(
                frame, (x, y), radius,
                (255, 255, 255), 2, cv2.LINE_AA
            )

        # Shockwaves
        for wave in self.shockwaves:

            x = int(wave["x"])
            y = int(wave["y"])
            radius = int(wave["radius"])

            ratio = wave["life"] / wave["max_life"]
            thickness = max(1, int(8 * ratio))

            cv2.circle(
                overlay, (x, y), radius,
                wave["color"], thickness + 8,
                cv2.LINE_AA
            )

            cv2.circle(
                frame, (x, y), radius,
                wave["color"], thickness,
                cv2.LINE_AA
            )

        # 3D-style rotating energy rings
        for ring in self.rings:

            x = int(ring["x"])
            y = int(ring["y"])
            radius = int(ring["radius"])

            ratio = ring["life"] / ring["max_life"]
            thickness = max(1, int(5 * ratio))
            color = ring["color"]

            axes = (
                radius,
                max(1, int(radius * ring["depth"]))
            )

            cv2.ellipse(
                overlay, (x, y), axes,
                ring["angle"], 0, 360,
                color, thickness + 7,
                cv2.LINE_AA
            )

            cv2.ellipse(
                frame, (x, y), axes,
                ring["angle"], 0, 360,
                color, thickness,
                cv2.LINE_AA
            )

            # Rotating arcs
            cv2.ellipse(
                frame, (x, y), axes,
                ring["angle"], 20, 150,
                (255, 255, 255), 3,
                cv2.LINE_AA
            )

            cv2.ellipse(
                frame, (x, y), axes,
                -ring["angle"], 200, 320,
                (255, 0, 255), 2,
                cv2.LINE_AA
            )

        # Electric sparks
        for spark in self.sparks:

            x = int(spark["x"])
            y = int(spark["y"])

            length = max(
                2,
                int(8 * spark["life"] / spark["max_life"])
            )

            end_x = int(x + spark["vx"] * length)
            end_y = int(y + spark["vy"] * length)

            cv2.line(
                overlay, (x, y), (end_x, end_y),
                spark["color"], 3, cv2.LINE_AA
            )

            cv2.circle(
                frame, (x, y), 2,
                (255, 255, 255), -1
            )

        # Neon glow
        glow = cv2.GaussianBlur(
            overlay, (21, 21), 0
        )

        cv2.addWeighted(
            glow, 0.4,
            frame, 0.6,
            0, frame
        )

        return frame
