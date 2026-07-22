"""Camera source abstraction — laptop webcam or mobile IP camera."""

import cv2
from config import CAMERA_SOURCE, FRAME_WIDTH, FRAME_HEIGHT, FPS_TARGET


def get_camera():
    """
    Open camera from config source.
    CAMERA_SOURCE = 0           → laptop webcam
    CAMERA_SOURCE = "http://..." → mobile camera via DroidCam / IP Webcam
    """
    cap = cv2.VideoCapture(CAMERA_SOURCE)

    if not cap.isOpened():
        raise RuntimeError(
            f"Cannot open camera: {CAMERA_SOURCE}\n"
            "Check that the camera is connected or the IP stream URL is correct."
        )

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS,          FPS_TARGET)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"[Camera] {actual_w}x{actual_h} @ {actual_fps:.1f} fps")

    return cap
