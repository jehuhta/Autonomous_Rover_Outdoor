import threading
import time
import cv2
from picamera2 import Picamera2

latest_frame = None
frame_lock   = threading.Lock()
stop_event   = threading.Event()
_thread      = None

def _producer():
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(
        main={"format": "BGR888", "size": (1920, 1080)}
    ))
    cam.start()
    time.sleep(1)
    cam.set_controls({
    # "ExposureTime":5000,   # 5ms shutter — reduce if still blurry
    "AnalogueGain": 0.3,     # bump gain to compensate for less light
    # "HdrMode": 1,
    "AwbEnable": True,
    "AeEnable": True   
    })
    global latest_frame
    while not stop_event.is_set():
        frame = cam.capture_array()
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # bgr[:, :, 2] = (bgr[:, :,2] * 0.60).astype('uint8')  # dampen red
        with frame_lock:
            latest_frame = bgr
    cam.stop()

def start():
    global _thread, stop_event
    stop_event = threading.Event()  # reset in case start() is called again
    _thread = threading.Thread(target=_producer, daemon=True)
    _thread.start()

def get_latest_frame():
    with frame_lock:
        if latest_frame is None:
            return None
        return latest_frame.copy()

def stop():
    stop_event.set()
    if _thread is not None:
        _thread.join(timeout=3)