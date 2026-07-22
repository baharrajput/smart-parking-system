import os
import json
import sys
import cv2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMART_PARKING_DIR = os.path.join(ROOT, 'smart_parking')

sys.path.insert(0, SMART_PARKING_DIR)

import config
from core.detector import SlotDetector
from ui.side_panel_ui import SidePanelUI

frame_path = os.path.join(SMART_PARKING_DIR, 'data', 'reference_frame.jpg')
slots_path = os.path.join(SMART_PARKING_DIR, 'data', 'slots.json')
out_path = os.path.join(ROOT, 'docs', 'real-screenshot.png')

frame = cv2.imread(frame_path)
if frame is None:
    raise RuntimeError(f'Could not read reference frame: {frame_path}')

with open(slots_path, 'r') as f:
    slots = json.load(f)

frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

detector = SlotDetector()
detector.calibrate(frame, slots)
results = detector.analyze_all(frame, slots)
ui = SidePanelUI()
canvas = ui.draw(frame, results)

os.makedirs(os.path.dirname(out_path), exist_ok=True)
cv2.imwrite(out_path, canvas)
print(f'Saved screenshot to {out_path}')
print(f'Image size: {canvas.shape[1]}x{canvas.shape[0]}')
