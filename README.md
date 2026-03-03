# PAUSE
**P**ose **A**ware **U**ser **S**tate **E**ngine

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

> *You look away, it pauses. You look back, it plays.*

**PAUSE** is a real-time desktop application that uses your webcam to detect where you're looking and automatically controls media playback — no mouse, no keyboard, just your attention.

---

## 🧠 How It Works

PAUSE uses **MediaPipe Face Mesh** to extract 6 facial landmarks, feeds them into OpenCV's **Perspective-n-Point (PnP)** solver to estimate 3D head orientation, and extracts the **Yaw angle** (left/right rotation). When you look away beyond a threshold, it sends a `PlayPause` keystroke to pause your media. When you look back — it resumes.

```
Camera Feed → Face Mesh (468 landmarks) → 6 Key Points → solvePnP → Rotation Matrix → Yaw Angle → Pause/Play
```

### The Math Behind It

1. **6 Landmarks** are extracted: Nose tip, Chin, Left/Right Eye corners, Left/Right Mouth corners
2. **`cv2.solvePnP`** matches these 2D image points to a 3D face model → produces a Rotation Vector
3. **`cv2.RQDecomp3x3`** decomposes the Rotation Matrix into Euler Angles (Pitch, Yaw, Roll)
4. **Decision Logic:**
   - Yaw **> 15°** (Looking Right) → ⏸️ Pause
   - Yaw **< -15°** (Looking Left) → ⏸️ Pause
   - Yaw **within ±15°** (Focused) → ▶️ Play

### Smart Safeguards

| Mechanism | Purpose |
|---|---|
| **Stability Buffer** (10 frames) | Prevents accidental pauses from brief glances |
| **Cooldown Timer** (1 second) | Prevents rapid-fire toggling between pause/play |
| **Absent Detection** | Pauses when no face is detected at all |

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Python** | Core application logic |
| **MediaPipe** | Face Mesh ML model (468 landmarks) |
| **OpenCV** | Image processing, PnP solver, display |
| **PyAutoGUI** | System-level keyboard simulation |
| **NumPy** | Vector & matrix operations |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Webcam

### Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PAUSE.git
cd PAUSE

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Run
```bash
python pause.py
```
Open any media player (YouTube, VLC, Netflix) and let PAUSE handle the rest. Press `Esc` to exit.

---

## 📂 Project Structure

```
PAUSE/
├── pause.py              # Main application script
├── requirements.txt      # Python dependencies
├── README.md             # Documentation
└── .gitignore            # Git ignore rules
```

---

## ⚙️ Configuration

These constants can be adjusted at the top of `pause.py`:

| Parameter | Default | Description |
|---|---|---|
| `CAM_WIDTH` | 640 | Camera resolution width |
| `CAM_HEIGHT` | 480 | Camera resolution height |
| `LOOK_LEFT_THRESHOLD` | -15° | Yaw angle to trigger "Looking Left" |
| `LOOK_RIGHT_THRESHOLD` | 15° | Yaw angle to trigger "Looking Right" |
| `STABILITY_FRAMES` | 10 | Consecutive frames before triggering action |
| `COOLDOWN` | 1.0s | Minimum interval between pause/play toggles |

---

## 🎯 Use Cases

- 📺 **Lecture Watching** — Auto-pauses when you look down to take notes
- 🍳 **Hands-Busy Scenarios** — Controls playback when your hands aren't free
- 🎧 **Focus Sessions** — Only plays content when you're actively watching
