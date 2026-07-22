"""
Side Panel UI — Camera feed left, status panel right
"""

import cv2
import numpy as np
import time

FONT_LARGE  = cv2.FONT_HERSHEY_DUPLEX
FONT        = cv2.FONT_HERSHEY_SIMPLEX

# Colors (BGR)
C_BG        = (22,  22,  30)
C_FREE      = (50,  205, 80)
C_OCC       = (60,  60,  220)
C_WHITE     = (255, 255, 255)
C_GRAY      = (140, 140, 140)
C_YELLOW    = (0,   210, 255)
C_DARK_CARD = (35,  35,  45)
C_HEADER    = (18,  18,  25)


def _rect(img, x1, y1, x2, y2, color, alpha=1.0):
    if alpha >= 1.0:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)
    else:
        sub = img[y1:y2, x1:x2]
        overlay = np.full(sub.shape, color, dtype=np.uint8)
        cv2.addWeighted(overlay, alpha, sub, 1 - alpha, 0, sub)
        img[y1:y2, x1:x2] = sub


def _text_center(img, text, cx, y, font, scale, color, thick=1):
    (tw, th), _ = cv2.getTextSize(text, font, scale, thick)
    cv2.putText(img, text, (cx - tw // 2, y), font, scale, color, thick)


class SidePanelUI:

    PANEL_W = 320   # right panel width

    def __init__(self):
        self._t0     = time.time()
        self._frames = 0
        self._fps    = 0.0

    def _tick(self):
        self._frames += 1
        now = time.time()
        if now - self._t0 >= 1.0:
            self._fps    = self._frames / (now - self._t0)
            self._frames = 0
            self._t0     = now

    # ─────────────────────────────────────────────────────────────────────────
    def draw(self, frame, results):
        self._tick()
        fh, fw = frame.shape[:2]
        pw      = self.PANEL_W
        canvas  = np.zeros((fh, fw + pw, 3), dtype=np.uint8)

        # ── Left: camera feed with slot overlays ─────────────────────────────
        feed = frame.copy()
        self._draw_slots_on_feed(feed, results)
        canvas[:, :fw] = feed

        # ── Right: dark side panel ────────────────────────────────────────────
        _rect(canvas, fw, 0, fw + pw, fh, C_BG)
        self._draw_side_panel(canvas, results, fw, fh, pw)

        return canvas

    # ── Camera feed overlays ──────────────────────────────────────────────────
    def _draw_slots_on_feed(self, frame, results):
        for r in results:
            x1, y1, x2, y2 = r['coords']
            color  = C_OCC if r['occupied'] else C_FREE
            status = 'OCC' if r['occupied'] else 'FREE'
            alpha  = 0.32 if r['occupied'] else 0.18

            sub = frame[y1:y2, x1:x2]
            overlay = np.full(sub.shape, color, dtype=np.uint8)
            cv2.addWeighted(overlay, alpha, sub, 1 - alpha, 0, sub)
            frame[y1:y2, x1:x2] = sub

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Badge
            badge = f"S{r['id']}"
            (bw, bh), _ = cv2.getTextSize(badge, FONT, 0.55, 2)
            cv2.rectangle(frame, (x1, y1), (x1+bw+8, y1+bh+6), color, -1)
            cv2.putText(frame, badge, (x1+4, y1+bh+2), FONT, 0.55, (0,0,0), 2)

            # Status text inside slot
            sw, sh = x2-x1, y2-y1
            (tw, th), _ = cv2.getTextSize(status, FONT, 0.55, 2)
            cv2.putText(frame, status, (x1+(sw-tw)//2, y1+(sh+th)//2),
                        FONT, 0.55, color, 2)

            # Score bar at bottom of slot
            bx1, bx2 = x1+6, x2-6
            by = y2 - 8
            bw2 = bx2 - bx1
            cv2.rectangle(frame, (bx1, by-3), (bx2, by+3), (50,50,50), -1)
            fill = int(bw2 * min(r['score'] / 0.4, 1.0))
            if fill > 0:
                cv2.rectangle(frame, (bx1, by-3), (bx1+fill, by+3), color, -1)

    # ── Side panel ────────────────────────────────────────────────────────────
    def _draw_side_panel(self, canvas, results, fx, fh, pw):
        cx = fx + pw // 2       # center X of panel
        total = len(results)
        occ   = sum(1 for r in results if r['occupied'])
        free  = total - occ

        y = 0

        # ── Header ────────────────────────────────────────────────────────────
        _rect(canvas, fx, 0, fx+pw, 70, C_HEADER)
        _text_center(canvas, 'SMART', cx, 28, FONT_LARGE, 0.75, C_YELLOW, 2)
        _text_center(canvas, 'PARKING', cx, 58, FONT_LARGE, 0.75, C_YELLOW, 2)
        cv2.line(canvas, (fx+10, 72), (fx+pw-10, 72), (60,60,80), 1)
        y = 80

        # ── FPS ───────────────────────────────────────────────────────────────
        cv2.putText(canvas, f'FPS: {self._fps:.0f}',
                    (fx+10, y+18), FONT, 0.55, C_GRAY, 1)
        y += 30

        # ── Big counters ──────────────────────────────────────────────────────
        # FREE card
        _rect(canvas, fx+10, y, fx+pw//2-5, y+80, C_DARK_CARD)
        cv2.rectangle(canvas, (fx+10, y), (fx+pw//2-5, y+80), C_FREE, 2)
        _text_center(canvas, str(free), fx+pw//4, y+52, FONT_LARGE, 2.0, C_FREE, 3)
        _text_center(canvas, 'FREE', fx+pw//4, y+76, FONT, 0.55, C_FREE, 1)

        # OCCUPIED card
        _rect(canvas, fx+pw//2+5, y, fx+pw-10, y+80, C_DARK_CARD)
        cv2.rectangle(canvas, (fx+pw//2+5, y), (fx+pw-10, y+80), C_OCC, 2)
        _text_center(canvas, str(occ), fx+pw*3//4, y+52, FONT_LARGE, 2.0, C_OCC, 3)
        _text_center(canvas, 'OCCUPIED', fx+pw*3//4, y+76, FONT, 0.45, C_OCC, 1)
        y += 95

        # ── Total bar ─────────────────────────────────────────────────────────
        bar_x1, bar_x2 = fx+10, fx+pw-10
        bar_w = bar_x2 - bar_x1
        _rect(canvas, bar_x1, y, bar_x2, y+14, (50,50,60))
        if total > 0:
            free_w = int(bar_w * free / total)
            _rect(canvas, bar_x1, y, bar_x1+free_w, y+14, C_FREE)
            _rect(canvas, bar_x1+free_w, y, bar_x2, y+14, C_OCC)
        cv2.rectangle(canvas, (bar_x1, y), (bar_x2, y+14), (80,80,100), 1)
        y += 22
        cv2.putText(canvas, f'Total: {total} slots',
                    (fx+10, y+14), FONT, 0.55, C_GRAY, 1)
        y += 28

        cv2.line(canvas, (fx+10, y), (fx+pw-10, y), (60,60,80), 1)
        y += 12

        # ── Row breakdown ─────────────────────────────────────────────────────
        rows = {}
        for r in results:
            rid = r.get('row', 1)
            rows.setdefault(rid, {'free': 0, 'occ': 0, 'slots': []})
            if r['occupied']:
                rows[rid]['occ'] += 1
            else:
                rows[rid]['free'] += 1
            rows[rid]['slots'].append(r)

        cv2.putText(canvas, 'ROW STATUS', (fx+10, y+14),
                    FONT, 0.6, C_YELLOW, 2)
        y += 24

        for rid in sorted(rows.keys()):
            info = rows[rid]
            rf, ro = info['free'], info['occ']
            rt = rf + ro
            row_color = C_FREE if ro == 0 else (C_OCC if rf == 0 else (0, 165, 255))
            status_txt = 'FULL' if rf == 0 else f'{rf} Free'

            _rect(canvas, fx+10, y, fx+pw-10, y+38, C_DARK_CARD)
            cv2.rectangle(canvas, (fx+10, y), (fx+pw-10, y+38), row_color, 1)
            cv2.putText(canvas, f'Row {rid}', (fx+18, y+24),
                        FONT, 0.65, C_WHITE, 2)
            cv2.putText(canvas, status_txt, (fx+pw-10-len(status_txt)*10, y+24),
                        FONT, 0.65, row_color, 2)

            # Mini slot dots
            dot_y = y + 34
            for i, sr in enumerate(info['slots']):
                dot_x = fx + 18 + i * 18
                dot_c = C_OCC if sr['occupied'] else C_FREE
                cv2.circle(canvas, (dot_x, dot_y), 5, dot_c, -1)

            y += 48

        cv2.line(canvas, (fx+10, y), (fx+pw-10, y), (60,60,80), 1)
        y += 12

        # ── Slot list ─────────────────────────────────────────────────────────
        cv2.putText(canvas, 'SLOT DETAILS', (fx+10, y+14),
                    FONT, 0.6, C_YELLOW, 2)
        y += 24

        cols_count = 2
        col_w = (pw - 20) // cols_count
        for i, r in enumerate(results):
            col = i % cols_count
            row_pos = i // cols_count
            sx = fx + 10 + col * col_w
            sy = y + row_pos * 22

            if sy + 20 > fh - 30:
                break

            dot_c = C_OCC if r['occupied'] else C_FREE
            cv2.circle(canvas, (sx + 6, sy + 8), 5, dot_c, -1)
            label = f"S{r['id']:2d} {'OCC' if r['occupied'] else 'free'}"
            cv2.putText(canvas, label, (sx+15, sy+13),
                        FONT, 0.45, dot_c, 1)

        # ── FULL banner ───────────────────────────────────────────────────────
        if free == 0 and total > 0:
            _rect(canvas, fx, fh-50, fx+pw, fh, (0,0,180), 0.85)
            _text_center(canvas, 'PARKING FULL!', cx, fh-18,
                         FONT_LARGE, 0.75, C_WHITE, 2)

        # ── Vertical divider ──────────────────────────────────────────────────
        cv2.line(canvas, (fx, 0), (fx, fh), (80,80,100), 2)
