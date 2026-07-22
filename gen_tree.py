from PIL import Image, ImageDraw, ImageFont
import os

W, PAD = 820, 30
BG       = (250, 251, 253)
FOLDER_C = (30,  100, 200)
FILE_C   = (40,  40,  40)
LINE_C   = (180, 190, 210)
ROOT_C   = (15,  70,  160)
DESC_C   = (110, 115, 130)

ITEMS = [
    # (indent, is_folder, name, description, is_last_at_level)
    (0, True,  "smart_parking/",    "Project root directory",              False),
    (1, False, "main.py",           "Main program — camera loop & detection",True),  # last? no
    (1, False, "config.py",         "All configuration parameters",        False),
    (1, False, "setup_corners.py",  "One-time slot setup tool (2-click)",  False),
    (1, False, "RUN.bat",           "Double-click to run the system",      False),
    (1, False, "SETUP_SLOTS.bat",   "Double-click to run slot setup",      False),
    (1, True,  "core/",             "Detection logic",                     False),
    (2, False, "detector.py",       "SlotDetector — all CV algorithms",    True),
    (1, True,  "ui/",               "User interface",                      False),
    (2, False, "side_panel_ui.py",  "SidePanelUI — live feed + status panel", True),
    (1, True,  "utils/",            "Helper utilities",                    False),
    (2, False, "camera.py",         "Camera connection & reconnect logic", False),
    (2, False, "slot_io.py",        "JSON load/save for slot coordinates", True),
    (1, True,  "data/",             "Persistent data files",               True),
    (2, False, "slots.json",        "Saved 16-slot coordinates (permanent)",False),
    (2, False, "reference_frame.jpg","Reference snapshot from setup",      True),
]

ROW_H   = 36
TOTAL_H = PAD + len(ITEMS) * ROW_H + PAD + 10

try:
    font_reg  = ImageFont.truetype("C:/Windows/Fonts/consola.ttf",  15)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 15)
    font_desc = ImageFont.truetype("C:/Windows/Fonts/consola.ttf",  13)
except:
    font_reg = font_bold = font_desc = ImageFont.load_default()

img  = Image.new("RGB", (W, TOTAL_H), BG)
draw = ImageDraw.Draw(img)

# title bar
draw.rectangle([(0, 0), (W, 42)], fill=(22, 60, 120))
draw.text((PAD, 10), "Project File Structure — Smart Parking Detection System",
          fill=(220, 235, 255), font=font_bold)

INDENT_W = 28
ICON_W   = 20

for i, (indent, is_folder, name, desc, _) in enumerate(ITEMS):
    y = 42 + PAD//2 + i * ROW_H

    x_base = PAD + indent * INDENT_W

    # connector lines
    if indent > 0:
        # vertical line from parent
        lx = PAD + (indent - 1) * INDENT_W + INDENT_W // 2
        draw.line([(lx, y - ROW_H//2), (lx, y + ROW_H//2)], fill=LINE_C, width=1)
        # horizontal branch
        draw.line([(lx, y + 4), (x_base - 4, y + 4)], fill=LINE_C, width=1)

    # icon
    if indent == 0:
        # root folder — filled blue square
        draw.rounded_rectangle([(x_base, y - 3), (x_base + 16, y + 11)],
                                radius=2, fill=ROOT_C)
        draw.text((x_base + 3, y - 2), "P", fill=(255,255,255), font=font_bold)
    elif is_folder:
        draw.rounded_rectangle([(x_base, y - 1), (x_base + 14, y + 10)],
                                radius=2, fill=FOLDER_C)
        draw.rectangle([(x_base + 3, y - 4), (x_base + 9, y - 1)], fill=FOLDER_C)
    else:
        # file icon
        pts = [(x_base, y - 2), (x_base + 10, y - 2),
               (x_base + 14, y + 2), (x_base + 14, y + 11),
               (x_base,      y + 11)]
        draw.polygon(pts, fill=(200, 210, 230), outline=(150, 165, 195))
        draw.line([(x_base + 10, y - 2), (x_base + 14, y + 2)], fill=(150,165,195), width=1)

    text_x = x_base + ICON_W
    color  = ROOT_C if indent == 0 else (FOLDER_C if is_folder else FILE_C)
    draw.text((text_x, y - 3), name, fill=color,
              font=font_bold if (is_folder or indent == 0) else font_reg)

    # description
    name_w = draw.textlength(name, font=font_bold if is_folder else font_reg)
    sep_x  = text_x + int(name_w) + 12
    draw.text((sep_x, y - 2), "—  " + desc, fill=DESC_C, font=font_desc)

# bottom border
draw.rectangle([(0, TOTAL_H - 4), (W, TOTAL_H)], fill=(22, 60, 120))

out = r"d:\Spring 2026\Computer Vision\Final_Project\file_tree.png"
img.save(out, dpi=(150, 150))
print("Saved:", out)
