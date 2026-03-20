# Testing Guide for Car Number Plate Extraction System

## Overview
This guide provides instructions for testing the ANPR system components individually and as a whole.

## Prerequisites
- Run commands from the project root: `cd /Users/mac/Desktop/ANPR-Project`
- Use the project venv python (recommended, avoids `cv2`/`pytesseract` import issues):
  - `.venv/bin/python --version`
- Webcam available for live testing
- Tesseract OCR installed

## Testing Individual Components

### 1. Camera Test
```bash
.venv/bin/python src/camera.py
```
- Should open a window showing live camera feed
- Press 'q' to quit
- Expected: Clear video feed without errors

### 2. Detection Test
```bash
.venv/bin/python src/detect.py
```
- Shows camera feed with plate detection overlays
- Green rectangles indicate detected plate candidates
- Press 'q' to quit

### 3. Alignment Test
```bash
.venv/bin/python src/align.py
```
- Detects and warps plates to 450x140 pixels
- Shows original and aligned plate images
- Press 'q' to quit

### 4. OCR Test
```bash
.venv/bin/python src/ocr.py
```
- Extracts text from detected plates
- Shows plate image with recognized text overlay
- Press 'q' to quit

### 5. Validation Test
```bash
.venv/bin/python src/validate.py
```
- Validates extracted text against plate format
- Shows valid/invalid status
- Press 'q' to quit

### 6. Temporal Test
```bash
.venv/bin/python src/temporal.py
```
- Full pipeline with temporal confirmation
- Saves results to plates_log.csv
- Press 'q' to quit

## Full System Test
```bash
.venv/bin/python src/main.py
```
- Runs complete ANPR pipeline
- Saves confirmed plates to data/plates.csv
- Press 'q' to quit

## Test Scenarios

### Best Case
- Well-lit environment
- Plate 2-5 meters away
- Camera perpendicular to plate
- Clean, standard plate

### Edge Cases
- Poor lighting
- Extreme angles
- Dirty plates
- Motion blur
- Multiple plates in frame

## Troubleshooting

### Camera Issues
- Check camera permissions
- Try different camera index in code
- Ensure no other apps using camera

### Python/Import Issues
- If you see `ModuleNotFoundError: No module named 'cv2'`, you almost certainly ran outside the venv.
- Always run the scripts using `.venv/bin/python ...` (from the project root).

### Detection Issues
- Adjust MIN_AREA constant
- Check lighting conditions
- Verify plate is in focus

### OCR Issues
- Install Tesseract correctly
- Check Tesseract path in code
- Try different PSM modes

### Performance Issues
- Close other applications
- Reduce frame processing if needed
- Check system resources

## Expected Outputs
- Detection: Green bounding boxes around plates
- OCR: Recognized text displayed on image
- Validation: "VALID" or "INVALID" status
- Temporal: Confirmed plates saved to CSV

## Sample Test Data
See data/plates.csv for sample outputs.