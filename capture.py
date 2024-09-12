import cv2
import time
from PIL import Image
import numpy as np
import os
import argparse
from mss import mss

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Capture webcam or screenshot")
parser.add_argument("--mode", choices=["webcam", "screenshot"], default="webcam", help="Capture mode (default: webcam)")
args = parser.parse_args()

# Folder
folder = "frames"

# Create the frames folder if it doesn't exist
frames_dir = os.path.join(os.getcwd(), folder)
os.makedirs(frames_dir, exist_ok=True)

# Initialize the webcam if in webcam mode
cap = None
if args.mode == "webcam":
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError("Cannot open webcam")
    # Wait for the camera to initialize and adjust light levels
    time.sleep(2)

# Initialize mss for screenshot mode
sct = mss()

while True:
    if args.mode == "webcam":
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            continue
        # Convert the frame to a PIL image
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    else:  # screenshot mode
        # Capture screenshot
        screenshot = sct.grab(sct.monitors[0])
        # Convert to PIL Image
        pil_img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    # Resize the image
    max_size = 250
    ratio = max_size / max(pil_img.size)
    new_size = tuple([int(x*ratio) for x in pil_img.size])
    resized_img = pil_img.resize(new_size, Image.LANCZOS)

    # Convert the PIL image back to an OpenCV image
    frame = cv2.cvtColor(np.array(resized_img), cv2.COLOR_RGB2BGR)

    # Save the frame as an image file
    print(f"📸 Capturing {'webcam' if args.mode == 'webcam' else 'screenshot'}!")
    path = f"{folder}/frame.jpg"
    cv2.imwrite(path, frame)

    # Wait for 2 seconds
    time.sleep(2)

# Release the camera if in webcam mode
if args.mode == "webcam" and cap is not None:
    cap.release()
    cv2.destroyAllWindows()
