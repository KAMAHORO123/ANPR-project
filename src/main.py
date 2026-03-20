"""
Main entry point for the Car Number Plate Extraction System
This script runs the complete pipeline: detection, alignment, OCR, validation, and logging
"""

import cv2
import numpy as np
import pytesseract
import re
import csv
import os
import time
from collections import Counter

# Configuration constants
MIN_AREA = 600
AR_MIN, AR_MAX = 2.0, 8.0
W_OUT, H_OUT = 450, 140

PLATE_RE = re.compile(r'[A-Z]{3}[0-9]{3}[A-Z]')
BUFFER_SIZE = 5
COOLDOWN = 10  # seconds between saving same plate

# Output file
csv_file = "data/plates.csv"

# Initialize CSV file if it doesn't exist
os.makedirs("data", exist_ok=True)
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Plate Number", "Timestamp"])

def find_plate_candidates(frame):
    """
    Detect potential license plate regions using contour analysis
    Returns list of rotated rectangles that match plate characteristics
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 100, 200)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    candidates = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < MIN_AREA:
            continue
        
        rect = cv2.minAreaRect(cnt)
        (_, _), (w, h), _ = rect
        
        if w <= 0 or h <= 0:
            continue
        
        ar = max(w, h) / max(1.0, min(w, h))
        if AR_MIN <= ar <= AR_MAX:
            candidates.append(rect)
    
    return candidates

def order_points(pts):
    """
    Order points in consistent manner: top-left, top-right, bottom-right, bottom-left
    """
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    top_left = pts[np.argmin(s)]
    bottom_right = pts[np.argmax(s)]
    top_right = pts[np.argmin(diff)]
    bottom_left = pts[np.argmax(diff)]
    
    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)

def warp_plate(frame, rect):
    """
    Apply perspective transformation to rectify the plate region
    """
    box = cv2.boxPoints(rect)
    src = order_points(box)
    
    dst = np.array([
        [0, 0],
        [W_OUT - 1, 0],
        [W_OUT - 1, H_OUT - 1],
        [0, H_OUT - 1]
    ], dtype=np.float32)
    
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(frame, M, (W_OUT, H_OUT))
    
    return warped

def read_plate_text(plate_img):
    """
    Extract text from aligned plate image using Tesseract OCR
    """
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]
    
    text = pytesseract.image_to_string(
        thresh,
        config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )
    
    text = text.upper().replace(" ", "").replace("-", "")
    return text

def extract_valid_plate(text):
    """
    Validate plate text against expected format using regex
    Expected format: 3 letters + 3 digits + 1 letter (e.g., RAD123A)
    """
    m = PLATE_RE.search(text)
    if m:
        return m.group(0)
    return None

def majority_vote(buffer):
    """
    Return most common plate from recent observations
    """
    if not buffer:
        return None
    return Counter(buffer).most_common(1)[0][0]

def main():
    """
    Main pipeline: capture, detect, align, OCR, validate, confirm, and log
    """
    print("Starting ANPR system...")  # Debug print
    print("=" * 60)
    print("Car Number Plate Extraction System")
    print("=" * 60)
    print("Starting camera...")
    
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise RuntimeError("Camera not opened. Please check your camera connection and permissions in System Settings > Privacy & Security > Camera.")
        
        print("Camera initialized successfully")
        print("Press 'q' to quit")
        print("=" * 60)
        
        plate_buffer = []
        last_saved_plate = None
        last_saved_time = 0
        
        frame_count = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Failed to read frame")
                break
            
            frame_count += 1
            if frame_count % 30 == 0:  # Print every 30 frames
                print(f"Processing frame {frame_count}")
            
            vis = frame.copy()
            candidates = find_plate_candidates(frame)
            
            if candidates:
                print(f"Found {len(candidates)} plate candidates")
                # Select largest candidate
                rect = max(candidates, key=lambda r: r[1][0] * r[1][1])
                box = cv2.boxPoints(rect).astype(int)
                
                # Draw detection box
                cv2.polylines(vis, [box], True, (0, 255, 0), 2)
                
                # Align and extract text
                plate_img = warp_plate(frame, rect)
                raw_text = read_plate_text(plate_img)
                valid_plate = extract_valid_plate(raw_text)
                
                if valid_plate:
                    print(f"Detected plate: {valid_plate}")
                    # Add to temporal buffer
                    plate_buffer.append(valid_plate)
                    if len(plate_buffer) > BUFFER_SIZE:
                        plate_buffer.pop(0)
                    
                    # Get confirmed plate via majority vote
                    confirmed_plate = majority_vote(plate_buffer)
                    
                    # Display confirmed plate
                    x = int(np.max(box[:, 0])) - 300
                    y = int(np.max(box[:, 1])) + 25
                    
                    cv2.putText(
                        vis, f"CONFIRMED: {confirmed_plate}", (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                    )
                    
                    # Save to CSV if conditions met
                    now = time.time()
                    
                    if (
                        confirmed_plate and
                        confirmed_plate != last_saved_plate and
                        (now - last_saved_time) > COOLDOWN
                    ):
                        with open(csv_file, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([
                                confirmed_plate,
                                time.strftime("%Y-%m-%d %H:%M:%S")
                            ])
                        
                        print(f"[SAVED] {confirmed_plate} at {time.strftime('%H:%M:%S')}")
                        last_saved_plate = confirmed_plate
                        last_saved_time = now
            
            # Display status
            cv2.putText(
                vis, "Car Number Plate Extraction", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2
            )
            
            cv2.putText(
                vis, "Press 'q' to quit", (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
            
            cv2.imshow("Number Plate Recognition", vis)
            
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break
    
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Please ensure camera permissions are granted and try again.")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        try:
            cap.release()
            cv2.destroyAllWindows()
        except NameError:
            pass  # cap not defined
    
    print("\n" + "=" * 60)
    print("System stopped")
    print(f"Results saved to: {csv_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
