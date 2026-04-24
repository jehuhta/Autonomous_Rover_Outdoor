import threading
import time
import numpy as np
import cv2
from picamera2 import Picamera2

latest_frame = None
frame_lock   = threading.Lock()
stop_event   = threading.Event()

def _producer():
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(
        main={"format": "RGB888", "size": (1920, 1080)}
    ))
    cam.start()
    global latest_frame
    while not stop_event.is_set():
        frame = cam.capture_array()
        bgr   = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        with frame_lock:
            latest_frame = bgr
    cam.stop()

def start():
    t = threading.Thread(target=_producer, daemon=True)
    t.start()
    time.sleep(0.5)

def get_latest_frame():
    with frame_lock:
        if latest_frame is None:
            return None
        return latest_frame.copy()

def stop():
    stop_event.set()
