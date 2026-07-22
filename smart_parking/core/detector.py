"""
Core Occupancy Detector
────────────────────────
Uses these CV techniques on each slot ROI:
  1. Grayscale conversion
  2. Gaussian blur        (noise removal)
  3. Median filter        (salt-and-pepper noise)
  4. Adaptive threshold   (segmentation — handles uneven lighting)
  5. Morphological ops    (erosion + dilation to clean binary mask)
  6. Canny edge detection (edge density as secondary signal)
  7. Contour detection    (object shape evidence)
  8. Background subtraction mask overlay (motion-based signal)

Final decision: weighted score from all signals.
"""

import cv2
import numpy as np
from config import BLUR_KERNEL, MEDIAN_KERNEL, CANNY_LOW, CANNY_HIGH, OCCUPANCY_THRESHOLD


class SlotDetector:

    def __init__(self):
        self.morph_kernel  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=40, detectShadows=True
        )
        self.ref_frame  = None   # reference "empty" frame
        self.ref_grays  = {}     # per-slot grayscale reference ROIs

    # ── Preprocessing ──────────────────────────────────────────────────────

    def _preprocess(self, roi):
        """Grayscale → Median filter → Gaussian blur → Adaptive threshold."""
        gray    = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        denoised = cv2.medianBlur(gray, MEDIAN_KERNEL)        # salt-and-pepper removal
        blurred  = cv2.GaussianBlur(denoised, BLUR_KERNEL, 0) # Gaussian smoothing
        thresh   = cv2.adaptiveThreshold(                      # segmentation
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            blockSize=21, C=12
        )
        return gray, blurred, thresh

    # ── Morphological Cleaning ─────────────────────────────────────────────

    def _clean_mask(self, mask):
        """Opening (removes noise) then Closing (fills gaps)."""
        opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  self.morph_kernel, iterations=1)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, self.morph_kernel, iterations=2)
        return closed

    # ── Signal 1: Pixel Density ────────────────────────────────────────────

    def _pixel_score(self, thresh):
        total  = thresh.size
        filled = cv2.countNonZero(thresh)
        return filled / total if total > 0 else 0.0

    # ── Signal 2: Edge Density (Canny) ────────────────────────────────────

    def _edge_score(self, blurred):
        edges = cv2.Canny(blurred, CANNY_LOW, CANNY_HIGH)
        return cv2.countNonZero(edges) / edges.size if edges.size > 0 else 0.0

    # ── Signal 3: Contour Area ────────────────────────────────────────────

    def _contour_score(self, thresh):
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0
        largest = max(contours, key=cv2.contourArea)
        return cv2.contourArea(largest) / thresh.size if thresh.size > 0 else 0.0

    # ── Signal 4: Background Subtraction ──────────────────────────────────

    def _bg_score(self, roi):
        fg = self.bg_subtractor.apply(roi)
        _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)  # remove shadows
        return cv2.countNonZero(fg) / fg.size if fg.size > 0 else 0.0

    # ── Reference Frame ────────────────────────────────────────────────────

    def calibrate(self, frame, slots):
        """Save current frame as 'empty parking' reference."""
        self.ref_frame = frame.copy()
        self.ref_grays = {}
        for slot in slots:
            x1, y1, x2, y2 = slot["coords"]
            roi = frame[y1:y2, x1:x2]
            if roi.size > 0:
                self.ref_grays[slot["id"]] = cv2.cvtColor(
                    cv2.GaussianBlur(roi, BLUR_KERNEL, 0), cv2.COLOR_BGR2GRAY
                ).astype(np.float32)
        print("Calibrated! Reference frame saved.")

    # ── Reference-based diff score ─────────────────────────────────────────

    def _diff_score(self, roi, slot_id):
        """Compare ROI with reference — high score = something changed (occupied)."""
        if slot_id not in self.ref_grays:
            return 0.0
        ref = self.ref_grays[slot_id]
        cur = cv2.cvtColor(
            cv2.GaussianBlur(roi, BLUR_KERNEL, 0), cv2.COLOR_BGR2GRAY
        ).astype(np.float32)
        if cur.shape != ref.shape:
            cur = cv2.resize(cur, (ref.shape[1], ref.shape[0]))
        diff = cv2.absdiff(cur, ref)
        return float(np.mean(diff)) / 255.0

    # ── Main Analysis ──────────────────────────────────────────────────────

    def analyze(self, frame, slot):
        x1, y1, x2, y2 = slot["coords"]
        roi = frame[y1:y2, x1:x2]

        if roi.size == 0 or roi.shape[0] < 5 or roi.shape[1] < 5:
            return False, 0.0, {}

        gray, blurred, thresh = self._preprocess(roi)
        thresh_clean = self._clean_mask(thresh)

        p_score = self._pixel_score(thresh_clean)
        e_score = self._edge_score(blurred)
        c_score = self._contour_score(thresh_clean)
        b_score = self._bg_score(roi)
        d_score = self._diff_score(roi, slot["id"])

        if self.ref_grays:
            # Reference available — diff score is most reliable
            final = (0.50 * d_score +
                     0.20 * p_score +
                     0.15 * e_score +
                     0.10 * c_score +
                     0.05 * b_score)
        else:
            # No reference yet — use pixel/edge/contour
            final = (0.40 * p_score +
                     0.30 * e_score +
                     0.20 * c_score +
                     0.10 * b_score)

        occupied = final > OCCUPANCY_THRESHOLD

        return occupied, round(final, 3), {
            "pixel":   round(p_score, 3),
            "edge":    round(e_score, 3),
            "contour": round(c_score, 3),
            "diff":    round(d_score, 3),
        }

    def analyze_all(self, frame, slots):
        results = []
        for slot in slots:
            occupied, score, debug = self.analyze(frame, slot)
            results.append({
                "id":       slot["id"],
                "row":      slot.get("row", 1),
                "coords":   slot["coords"],
                "occupied": occupied,
                "score":    score,
                "debug":    debug,
            })
        return results
