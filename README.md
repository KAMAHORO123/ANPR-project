# Car Number Plate Recognition System

This is my Y3 project for automatic number plate recognition. I followed the book by Gabriel Baziramwabo about extracting car plates in three steps.

## What it does

The program captures video from webcam and reads license plates automatically. It uses OpenCV for detection and Tesseract for reading the text.

### Pipeline

Camera → Detect plate → Fix angle → Read text → Check format → Confirm → Save to CSV

## Setup

You need Python 3.8+ and a webcam.

```bash
# make virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install packages
pip install -r requirements.txt

# install tesseract
sudo apt install tesseract-ocr
```

## How to run

Main program:
```bash
python src/main.py
```

Test individual parts:
```bash
python src/camera.py      # check camera works
python src/detect.py      # test detection
python src/align.py       # test alignment
python src/ocr.py         # test OCR
python src/validate.py    # test validation
```

Press q to quit.

## Files

```
src/
  camera.py       - camera test
  detect.py       - finds plate using contours
  align.py        - fixes perspective
  ocr.py          - extracts text
  validate.py     - checks format
  temporal.py     - confirms across frames
  main.py         - runs everything

data/
  plates.csv      - saved results

screenshots/      - test images
```

## How it works

**Detection** - Uses contour detection to find rectangles that look like plates (aspect ratio 2-8)

**Alignment** - Warps the plate to 450x140 pixels so it's straight

**OCR** - Tesseract reads the characters (only A-Z and 0-9)

**Validation** - Checks if format is correct: 3 letters + 3 numbers + 1 letter (like RAD123A)

**Temporal** - Keeps last 5 readings and uses majority vote to confirm

**Save** - Writes to CSV with timestamp, won't save same plate twice within 10 seconds

## Testing

I tested this on real cars in the school parking. Works best when:
- 2-5 meters away
- good lighting
- plate is clean
- camera pointing straight at plate

## Problems I had

- Sometimes confuses B with 8 or O with 0
- Doesn't work well in bad lighting
- Need to be fairly close to the car
- Extreme angles don't work

## Requirements

- opencv-python
- pytesseract  
- numpy
- pandas

## Reference

Book: "Car Number Plate Extraction in Three Steps" by Gabriel Baziramwabo
# ANPR-project
