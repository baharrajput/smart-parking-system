"""Save and load parking slot ROI definitions."""

import json
import os
from config import SLOTS_FILE


def save_slots(slots, path=SLOTS_FILE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(slots, f, indent=2)
    print(f"[SlotIO] Saved {len(slots)} slots to {path}")


def load_slots(path=SLOTS_FILE):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Slots file not found: {path}\n"
            "Run setup_slots.py first to define parking slots."
        )
    with open(path, "r") as f:
        slots = json.load(f)
    print(f"[SlotIO] Loaded {len(slots)} slots from {path}")
    return slots
