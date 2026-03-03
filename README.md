# PAUSE
**P**ose **A**ware **U**ser **S**tate **E**ngine — Attention-aware media controller using Head Pose Tracking

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-orange)

> *You look away, it pauses. You look back, it plays.*

**PAUSE** is a real-time desktop application that uses your webcam to detect where you're looking and automatically controls media playback — no mouse, no keyboard, just your attention.

---

## 🧠 How It Works

PAUSE uses **MediaPipe Face Mesh** (468 landmarks) for two detection systems:

1. **Head Pose Tracking** — Extracts 6 facial landmarks, feeds them into OpenCV's **PnP solver** to estimate 3D head orientation, and extracts **Yaw** (left/right) and **Pitch** (up/down) angles.
2. **Drowsiness Detection** — Computes the **Eye Aspect Ratio (EAR)** from 6 landmarks per eye. When eyes stay closed beyond a threshold for N consecutive frames, it pauses the video.

```
Camera Feed → Face Mesh (468 landmarks) → Head Pose (PnP) + Eye State (EAR) → Pause/Play
```

### The Math Behind It

1. **6 Landmarks** are extracted: Nose tip, Chin, Left/Right Eye corners, Left/Right Mouth corners
2. **`cv2.solvePnP`** matches these 2D image points to a 3D face model → produces a Rotation Vector
3. **`cv2.RQDecomp3x3`** decomposes the Rotation Matrix into Euler Angles (Pitch, Yaw, Roll)
4. **Decision Logic:**
   - Yaw **> 15°** (Looking Right) → ⏸️ Pause
   - Yaw **< -15°** (Looking Left) → ⏸️ Pause
   - Pitch **> 10°** (Looking Up) → ⏸️ Pause
   - Pitch **< -10°** (Looking Down) → ⏸️ Pause
   - Both **within thresholds** (Focused) → ▶️ Play

### Smart Safeguards

| Mechanism | Purpose |
|---|---|
| **Stability Buffer** (10 frames) | Prevents accidental pauses from brief glances |
| **Cooldown Timer** (1 second) | Prevents rapid-fire toggling between pause/play |
| **Absent Detection** | Pauses when no face is detected at all |
| **Drowsiness Alert** | Pauses and shows `DROWSY!` when eyes are closed too long |

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
git clone https://github.com/thejas-06/PAUSE.git
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

Customize with CLI flags:
```bash
python pause.py --yaw 20 --pitch 15 --camera 0 --stability 12 --cooldown 1.5
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

All parameters are configurable via CLI flags:

| Flag | Default | Description |
|---|---|---|
| `--camera` | `0` | Camera device index |
| `--yaw-right` | `14.7` | Yaw threshold for looking right |
| `--yaw-left` | `15.5` | Yaw threshold for looking left |
| `--pitch-up` | `12` | Pitch threshold for looking up |
| `--pitch-down` | `20` | Pitch threshold for looking down |
| `--stability` | `10` | Consecutive frames before triggering action |
| `--cooldown` | `1.0` | Minimum seconds between pause/play toggles |
| `--ear` | `0.22` | Eye Aspect Ratio threshold for blink detection |
| `--blink-frames` | `15` | Consecutive closed-eye frames for drowsiness |

---

## 🎯 Use Cases

- 📺 **Lecture Watching** — Auto-pauses when you look down to take notes
- 🍳 **Hands-Busy Scenarios** — Controls playback when your hands aren't free
- 🎧 **Focus Sessions** — Only plays content when you're actively watching
- 😴 **Drowsiness Safety** — Pauses content when you start dozing off
