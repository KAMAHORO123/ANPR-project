import cv2

try:
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise RuntimeError("Camera not opened - please check permissions in System Settings > Privacy & Security > Camera")
    
    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame")
            break
        
        cv2.imshow("Camera Test", frame)
        
        if (cv2.waitKey(1) & 0xFF) == ord("q"):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Camera test completed successfully")

except RuntimeError as e:
    print(f"Error: {e}")
    print("Make sure to grant camera permissions to Terminal application")
