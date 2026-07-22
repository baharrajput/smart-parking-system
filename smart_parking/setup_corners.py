"""
Simple Corner Setup — sirf 4 corners click karo!
Paper ke 4 corners click karo → system khud 16 slots banayega
"""
import cv2
import json
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from config import CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT, SLOTS_FILE, REFERENCE_FRAME

corners = []
FONT = cv2.FONT_HERSHEY_SIMPLEX
ROWS, COLS = 4, 4

corner_labels = [
    "Click 1: Paper ka TOP-LEFT kona (upar baaya) >>",
    "Click 2: Paper ka BOTTOM-RIGHT kona (neeche daaya) >>",
]

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN and len(corners) < 2:
        corners.append((x, y))
        print(f"  Point {len(corners)} saved: ({x}, {y})")

def make_slots_from_corners(pts):
    # Simple 2-point rectangle grid: top-left and bottom-right
    tl, br = pts[0], pts[1]
    x1, y1 = min(tl[0], br[0]), min(tl[1], br[1])
    x2, y2 = max(tl[0], br[0]), max(tl[1], br[1])
    total_w = x2 - x1
    total_h = y2 - y1
    slot_w = total_w // COLS
    slot_h = total_h // ROWS
    pad = 4

    slots = []
    slot_id = 1
    for col in range(COLS):
        for row in range(ROWS):
            sx1 = x1 + col * slot_w + pad
            sy1 = y1 + row * slot_h + pad
            sx2 = x1 + (col+1) * slot_w - pad
            sy2 = y1 + (row+1) * slot_h - pad
            slots.append({
                "id":     slot_id,
                "row":    col + 1,
                "coords": [sx1, sy1, sx2, sy2]
            })
            slot_id += 1
    return slots

def draw_preview(frame, corners, slots=None):
    out = frame.copy()
    h, w = out.shape[:2]

    # Instructions
    cv2.rectangle(out, (0,0), (w, 65), (20,20,20), -1)
    if len(corners) < 2:
        msg = corner_labels[len(corners)]
        cv2.putText(out, msg, (10, 42), FONT, 0.75, (0,230,255), 2)
    else:
        cv2.putText(out, "Done! Green grid dekho -- S=Save  R=Reset", (10,42), FONT, 0.8, (0,255,100), 2)

    cv2.putText(out, f"Clicks: {len(corners)}/2", (w-200, 42), FONT, 0.7, (200,200,200), 2)

    # Draw corners
    c_colors = [(0,255,255),(255,100,0),(0,100,255),(0,255,0)]
    c_names  = ["TOP-LEFT","TOP-RIGHT","BOT-RIGHT","BOT-LEFT"]
    for i, (cx,cy) in enumerate(corners):
        cv2.circle(out, (cx,cy), 12, c_colors[i], -1)
        cv2.putText(out, c_names[i], (cx+14, cy+6), FONT, 0.6, c_colors[i], 2)

    # Draw outline of paper
    if len(corners) == 4:
        pts = np.array(corners, np.int32).reshape((-1,1,2))
        cv2.polylines(out, [pts], True, (0,255,255), 2)

    # Draw grid slots preview
    if slots:
        for s in slots:
            x1,y1,x2,y2 = s["coords"]
            cv2.rectangle(out, (x1,y1), (x2,y2), (0,200,0), 2)
            cv2.putText(out, f"S{s['id']}", (x1+4, y1+20), FONT, 0.5, (0,255,0), 1)

    return out

def main():
    def connect():
        cap = cv2.VideoCapture(CAMERA_SOURCE)
        if not isinstance(CAMERA_SOURCE, str):
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        return cap

    cap = connect()
    if not cap.isOpened():
        print("ERROR: Camera nahi khula!")
        return

    print("\n" + "="*55)
    print("  SIMPLE SETUP — Sirf 4 corners click karo!")
    print("="*55)
    print("  Paper ke 4 corners click karo is order mein:")
    print("  1. TOP-LEFT  2. TOP-RIGHT  3. BOT-RIGHT  4. BOT-LEFT")
    print("  Phir S press karo save karne ke liye\n")

    win = "Parking Corner Setup"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(win, mouse_callback)

    base_frame = None
    no_frame = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            no_frame += 1
            if no_frame > 20:
                cap.release()
                cap = connect()
                no_frame = 0
            cv2.waitKey(100)
            continue
        no_frame = 0
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
        base_frame = frame.copy()

        slots = make_slots_from_corners(corners) if len(corners) == 2 else None
        display = draw_preview(frame, corners, slots)
        cv2.imshow(win, display)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('s') and len(corners) == 2 and base_frame is not None:
            slots = make_slots_from_corners(corners)
            os.makedirs("data", exist_ok=True)
            with open(SLOTS_FILE, "w") as f:
                json.dump(slots, f, indent=2)
            cv2.imwrite(REFERENCE_FRAME, base_frame)
            print(f"\n  Saved {len(slots)} slots!")
            for s in slots:
                print(f"  S{s['id']} row={s['row']} {s['coords']}")
            break

        elif key == ord('r'):
            corners.clear()
            print("  Reset! Dobara corners click karo.")

        elif key in (ord('q'), 27):
            print("  Quit.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
