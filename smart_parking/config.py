# ─────────────────────────────────────────────
#  Smart Parking Detection System — Config
# ─────────────────────────────────────────────

# Camera: 0 = laptop webcam
# Mobile : "http://192.168.x.x:4747/video"  (DroidCam app)
CAMERA_SOURCE = "http://10.83.84.113:8080/video"
FRAME_WIDTH   = 1280
FRAME_HEIGHT  = 720

MAX_SLOTS = 16

# ── Static Image Mode ──────────────────────────
# Agar camera nahi hai to apni parking ki photo yahan daalo
# None = camera use karo, path = image use karo
# Example: PARKING_IMAGE = "data/my_parking.jpg"
PARKING_IMAGE = None

# ── Occupancy Detection Sensitivity ───────────
# LOWER = more sensitive (detects small objects)
# HIGHER = less sensitive (ignores small noise)
OCCUPANCY_THRESHOLD = 0.15   # weighted score threshold (0.0-1.0); lower = more sensitive

# ── Preprocessing ──────────────────────────────
BLUR_KERNEL    = (5, 5)
MEDIAN_KERNEL  = 5
GAUSSIAN_SIGMA = 0

# ── Canny (used internally for edge scoring) ───
CANNY_LOW  = 40
CANNY_HIGH = 120

# ── Background Subtraction ─────────────────────
BG_HISTORY        = 300
BG_VAR_THRESHOLD  = 40
BG_DETECT_SHADOWS = True

# ── File Paths ─────────────────────────────────
SLOTS_FILE      = "data/slots.json"
REFERENCE_FRAME = "data/reference_frame.jpg"
