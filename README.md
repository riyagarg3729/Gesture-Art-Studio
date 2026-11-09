# 🎨 Gesture Art Studio 3D

**Draw Anything in the Air with Hand Gestures**

Gesture Art Studio is a real-time computer vision application that allows users to draw in the air using hand gestures through a webcam. It combines hand tracking, interactive drawing, particle effects and customizable backgrounds.

## ✨ Features

- Real-time hand tracking using MediaPipe
- Air drawing with index finger
- Dynamic brush size and multiple colors
- Pinch gesture eraser
- Undo and redo
- Circle, rectangle, triangle and star shapes
- Fire, smoke, magic and rainbow VFX
- Neon trails, energy rings and magic bursts
- Multiple background modes
- Person background segmentation
- Save artwork as PNG

## 🖐️ Gesture Controls

| Gesture | Action |
|---|---|
| Index Finger | Draw |
| Peace Sign | Stop Drawing |
| Open Palm | Pause |
| Three Fingers | Magic Burst |
| Fist | Clear Canvas |
| Pinch | Eraser |
| Thumb | Previous Color |
| Four Fingers | Next Color |

## ⌨️ Keyboard Controls

| Key | Action |
|---|---|
| 1–6 | Change Color |
| + / - | Brush Size |
| G | Shape Mode |
| 7 / 8 / 9 / 0 | Circle / Rectangle / Triangle / Star |
| Z / Y | Undo / Redo |
| F / M / B / R | Fire / Magic / Smoke / Rainbow |
| E | Turn VFX Off |
| T | Change Background |
| S | Save Artwork |
| Q | Quit |

## 🛠️ Tech Stack

- Python 3.12
- OpenCV
- MediaPipe
- NumPy
- Pygame

## 🚀 Installation

```bash
git clone YOUR_REPOSITORY_URL
cd Gesture-Art-Studio

python -m venv .venv312
.venv312\Scripts\activate

pip install -r requirements.txt
```

## ▶️ Run

```bash
python src/gestures/smart_air_drawing.py
```

## 📁 Project Structure

```text
Gesture-Art-Studio/
├── src/
│   ├── core/
│   ├── effects/
│   │   ├── background_engine.py
│   │   ├── particle_engine.py
│   │   ├── segmentation_engine.py
│   │   ├── shape_engine.py
│   │   └── vfx_engine.py
│   ├── gestures/
│   │   ├── air_drawing.py
│   │   ├── gesture_recognition.py
│   │   └── smart_air_drawing.py
│   └── hand_tracker.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 🔮 Future Scope

- Two-hand gesture interaction
- More advanced 3D visual effects
- Improved background segmentation
- Additional drawing tools and animations
- Performance optimization

## 👩‍💻 Developer

Created as a computer vision and interactive drawing project.