# Smart Parking System

A computer-vision-based smart parking solution that detects parking slot occupancy from a live camera stream or a static image. The system overlays slot regions on the video feed, marks each slot as free or occupied, and provides a dashboard with real-time occupancy statistics.

## Overview

This project was developed as a computer vision application for smart parking monitoring. It uses OpenCV-based image processing techniques such as grayscale conversion, blur filtering, adaptive thresholding, edge detection, contour analysis, and background subtraction to estimate whether a parking slot is occupied.

## Features

- Live camera-based parking slot detection
- Static image mode for testing and demos
- Interactive slot setup using corner selection
- Visual slot overlays with free/occupied status
- Side-panel dashboard for occupancy summaries
- Adjustable sensitivity for different lighting conditions

## Technologies Used

- Python
- OpenCV
- NumPy
- imutils

## Project Structure

```text
smart_parking/
├── core/
│   └── detector.py
├── data/
├── ui/
│   └── side_panel_ui.py
├── config.py
├── main.py
├── setup_corners.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/baharrajput/smart-parking-system.git
   cd smart-parking-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### 1. Set up parking slots

Run the slot configuration tool:

```bash
python setup_slots.py
```

Click the two corner points of the parking area, then press S to save the generated slot layout.

### 2. Run the smart parking system

```bash
python main.py
```

### Controls

- Q or Esc: Quit
- C: Recalibrate the background when the parking area is empty
- +: Increase sensitivity
- -: Decrease sensitivity

## Notes

- For a mobile camera, you can use an app such as IP Webcam and set the camera URL in the configuration file.
- If no camera is available, you can point the system to a static parking image.

## License

This project is licensed under the MIT License.
