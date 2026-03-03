import cv2
import time
import math
import logging
import argparse
import numpy as np
import pyautogui
import mediapipe as mp

# LOGGING
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

# ARGUMENT PARSER
parser = argparse.ArgumentParser(description="PAUSE — Pose Aware User State Engine")
parser.add_argument("--camera", type=int, default=0, help="Camera device index (default: 0)")
parser.add_argument("--yaw-right", type=float, default=14.7, help="Yaw threshold for looking right")
parser.add_argument("--yaw-left", type=float, default=15.5, help="Yaw threshold for looking left")
parser.add_argument("--pitch-up", type=float, default=12, help="Pitch threshold for looking up")
parser.add_argument("--pitch-down", type=float, default=20, help="Pitch threshold for looking down")
parser.add_argument("--stability", type=int, default=10, help="Stability frames before action (default: 10)")
parser.add_argument("--cooldown", type=float, default=1.0, help="Cooldown between toggles in seconds (default: 1.0)")
parser.add_argument("--ear", type=float, default=0.18, help="Eye Aspect Ratio threshold for blink detection (default: 0.22)")
parser.add_argument("--blink-frames", type=int, default=120, help="Consecutive closed-eye frames to trigger drowsiness (default: 120 ~4sec)")
args = parser.parse_args()

# EYE ASPECT RATIO (EAR)
# Landmarks: p1(outer) p2(upper-outer) p3(upper-inner) p4(inner) p5(lower-inner) p6(lower-outer)
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def ear(landmarks, eye_ids, w, h):
    pts = [(landmarks[i].x * w, landmarks[i].y * h) for i in eye_ids]
    vertical = math.dist(pts[1], pts[5]) + math.dist(pts[2], pts[4])
    horizontal = math.dist(pts[0], pts[3])
    return vertical / (2.0 * horizontal)

# SETUP MEDIAPIPE
try:
    mp_face_mesh = mp.solutions.face_mesh
except AttributeError:
    logging.error("MediaPipe version incompatibility.")
    exit()

# MAIN EXECUTION
cap = cv2.VideoCapture(args.camera)
if not cap.isOpened():
    logging.error("No webcam detected. Please connect a camera and try again.")
    exit()
cap.set(3, 640)
cap.set(4, 480)

is_paused = False
last_state_change_time = 0
looking_away_counter = 0
blink_counter = 0
is_drowsy = False

logging.info("PAUSE is Active. Open YouTube/VLC and minimize this window.")

with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh:

    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_results = face_mesh.process(image_rgb)

        image.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        h, w, c = image.shape

        # HEAD POSE DETECTION
        currently_looking_away = False
        status_text = "Focused"
        x_angle, y_angle = 0, 0

        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                face_3d, face_2d = [], []

                for idx, lm in enumerate(face_landmarks.landmark):
                    if idx in [33, 263, 1, 61, 291, 199]:
                        x, y = int(lm.x * w), int(lm.y * h)
                        face_2d.append([x, y])
                        face_3d.append([x, y, lm.z])

                face_2d = np.array(face_2d, dtype=np.float64)
                face_3d = np.array(face_3d, dtype=np.float64)

                focal_length = 1 * w
                cam_matrix = np.array([[focal_length, 0, w / 2],
                                       [0, focal_length, h / 2],
                                       [0, 0, 1]])
                dist_matrix = np.zeros((4, 1), dtype=np.float64)

                pnp_success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
                rmat, jac = cv2.Rodrigues(rot_vec)
                angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

                x_angle = angles[0] * 360  # Pitch (Up/Down)
                y_angle = angles[1] * 360  # Yaw (Left/Right)

                if y_angle < -args.yaw_right:
                    status_text = "Looking Right"
                    currently_looking_away = True
                elif y_angle > args.yaw_left:
                    status_text = "Looking Left"
                    currently_looking_away = True
                elif x_angle < -args.pitch_down:
                    status_text = "Looking Down"
                    currently_looking_away = True
                elif x_angle > args.pitch_up:
                    status_text = "Looking Up"
                    currently_looking_away = True

                # DROWSINESS DETECTION
                lm = face_landmarks.landmark
                avg_ear = (ear(lm, LEFT_EYE, w, h) + ear(lm, RIGHT_EYE, w, h)) / 2.0
                if avg_ear < args.ear:
                    blink_counter += 1
                    if blink_counter >= args.blink_frames and not is_drowsy:
                        is_drowsy = True
                        currently_looking_away = True
                        logging.info("Drowsiness Detected!")
                else:
                    blink_counter = 0
                    is_drowsy = False
        else:
            status_text = "Absent"
            currently_looking_away = True

        # STABILITY BUFFER (gradual decay prevents flicker at extreme angles)
        if currently_looking_away:
            looking_away_counter = min(looking_away_counter + 1, args.stability + 15)
        else:
            looking_away_counter = max(looking_away_counter - 3, 0)

        trigger_action = looking_away_counter > args.stability

        # PAUSE/PLAY TRIGGER
        current_time = time.time()
        if (current_time - last_state_change_time) > args.cooldown:
            if trigger_action and not is_paused:
                pyautogui.press('playpause')
                is_paused = True
                last_state_change_time = current_time
                logging.info("Action: PAUSED")
            elif not trigger_action and is_paused:
                pyautogui.press('playpause')
                is_paused = False
                last_state_change_time = current_time
                logging.info("Action: PLAYING")

        # DISPLAY
        cv2.putText(image, f"Yaw: {int(y_angle)} | Pitch: {int(x_angle)}" if face_results.multi_face_landmarks else "No Face", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        if status_text in ["Looking Up", "Looking Down"]:
            cv2.putText(image, status_text, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(image, f"State: {'PAUSED' if is_paused else 'PLAYING'}", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        if is_drowsy:
            cv2.putText(image, "DROWSY!", (w // 2 - 80, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.imshow('PAUSE', image)

        if cv2.waitKey(5) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()