"""
Smart Parking Detection System
────────────────────────────────
HOW TO USE:
  Step 1: python setup_slots.py   — run once to mark parking slots
  Step 2: python main.py          — run for live detection

Mobile Camera (Android):
  1. Install 'IP Webcam' app (free, Play Store)
  2. Open app → scroll down → 'Start server'
  3. Note the IP shown (e.g. http://192.168.1.5:8080)
  4. In config.py set:
       CAMERA_SOURCE = "http://192.168.1.5:8080/video"
       PARKING_IMAGE = None

Keyboard Controls:
  Q / ESC  — Quit
  C        — Recalibrate background (press when parking is empty)
  +        — More sensitive detection
  -        — Less sensitive detection
"""

import cv2
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from core.detector      import SlotDetector
from ui.side_panel_ui   import SidePanelUI
from config import (CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT,
                    SLOTS_FILE, PARKING_IMAGE)
import config


def load_slots():
    if not os.path.exists(SLOTS_FILE):
        print("\nERROR: No slots defined yet.")
        print("  Please run:  python setup_slots.py  first.\n")
        sys.exit(1)
    with open(SLOTS_FILE) as f:
        slots = json.load(f)
    print(f"Loaded {len(slots)} parking slots.")
    rows = {}
    for s in slots:
        rows.setdefault(s.get("row", 1), []).append(s["id"])
    for rid, sids in rows.items():
        print(f"  Row {rid}: Slots {sids}")
    return slots


def open_camera():
    src = CAMERA_SOURCE
    # Mobile IP camera string
    if isinstance(src, str) and src.startswith("http"):
        print(f"Connecting to mobile camera: {src}")
        cap = cv2.VideoCapture(src)
    else:
        print(f"Opening camera index: {src}")
        cap = cv2.VideoCapture(src)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"\nERROR: Camera nahi khula (source={src})")
        if isinstance(src, str) and src.startswith("http"):
            print("  → Mobile aur laptop ek hi WiFi pe hone chahiye")
            print("  → IP Webcam app mein 'Start server' press karo")
            print("  → config.py mein sahi IP daalo\n")
        sys.exit(1)
    print(f"Camera ready: {int(cap.get(3))}x{int(cap.get(4))} px")
    return cap


def run_loop(frame_source, slots, detector, ui, is_image=False):
    sensitivity = config.OCCUPANCY_THRESHOLD

    win = "Smart Parking System"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("\nControls: Q=Quit  C=Recalibrate  +=Sensitive  -=LessSensitive\n")

    while True:
        # Get frame
        if is_image:
            frame = frame_source.copy()
            wait  = 30
        else:
            ret, frame = frame_source.read()
            if not ret:
                print("Frame nahi mila, retry...")
                time.sleep(0.3)
                continue
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            wait  = 1

        config.OCCUPANCY_THRESHOLD = sensitivity
        results = detector.analyze_all(frame, slots)
        canvas  = ui.draw(frame, results)

        # Sensitivity hint bottom of panel
        fh, fw = frame.shape[:2]
        pw = ui.PANEL_W
        sens_pct = int((1.0 - sensitivity / 0.5) * 100)
        cv2.putText(canvas,
                    f"Sensitivity: {sens_pct}%  ( +/- )",
                    (fw + 10, fh - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 100, 120), 1)

        cv2.imshow(win, canvas)
        key = cv2.waitKey(wait) & 0xFF

        if key in (ord('q'), 27):
            break
        elif key == ord('c') and not is_image:
            detector.calibrate(frame, slots)
            print("Recalibrated with current frame as empty reference.")
        elif key in (ord('+'), ord('=')):
            sensitivity = max(0.03, sensitivity - 0.01)
            print(f"Sensitivity up -> {sensitivity:.3f}")
        elif key == ord('-'):
            sensitivity = min(0.50, sensitivity + 0.01)
            print(f"Sensitivity down -> {sensitivity:.3f}")

    cv2.destroyAllWindows()
    print("\nSystem stopped.")


def main():
    slots    = load_slots()
    detector = SlotDetector()
    ui       = SidePanelUI()

    # ── IMAGE MODE ─────────────────────────────────────────────────────────
    if PARKING_IMAGE:
        if not os.path.exists(PARKING_IMAGE):
            print(f"ERROR: Image nahi mili: {PARKING_IMAGE}")
            sys.exit(1)
        print(f"\nImage mode: {PARKING_IMAGE}")
        frame = cv2.imread(PARKING_IMAGE)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        run_loop(frame, slots, detector, ui, is_image=True)
        return

    # ── CAMERA MODE ────────────────────────────────────────────────────────
    cap = open_camera()

    # Warm-up + auto-calibrate: read a stable frame and save as reference
    print("Warming up (5 sec) — parking khali rakhein (keep parking empty)...")
    t0 = time.time()
    last_frame = None
    while time.time() - t0 < 5.0:
        ret, f = cap.read()
        if ret:
            detector.bg_subtractor.apply(f)
            last_frame = f
        cv2.waitKey(30)

    if last_frame is not None:
        calib_frame = cv2.resize(last_frame, (FRAME_WIDTH, FRAME_HEIGHT))
        detector.calibrate(calib_frame, slots)
    print("Ready!\n")

    run_loop(cap, slots, detector, ui, is_image=False)
    cap.release()


if __name__ == "__main__":
    main()
