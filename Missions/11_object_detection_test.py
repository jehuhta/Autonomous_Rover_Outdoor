from functions import predict_frames
import camera
from datetime import datetime
import time


# The objects the object_detection_model looks for. 
CLASS_NAMES = ["bear", "cyclist", "fox", "reindeer", "robot", "santa"]

# The level of certainty before considering a predicted object as one of the CLASS_NAMES.
THRESHOLD   = 0.7

def collect_frames():
    """
    Uses the camera to generate a number of frames (20 in this case).
    Returns frames and timestamps.
    """
    
    camera.start()
    frames = []
    timestamps = []

    print("------------------------------")
    print("Starting to collect frames...")    

    try:
        for num in range(20):
            frame = camera.get_latest_frame()
            if frame is not None:
                frames.append(frame)
                timestamps.append(datetime.now())
                print(f"Frame {len(frames)} captured at {timestamps[-1]}")
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\nInterrupted. {len(frames)} frames collected.")
        print("Camera turned off!")
        camera.stop()

    finally:
        print("Turning off camera...")
        camera.stop()
        print("Camera turned off!")

    return frames, timestamps


frames, timestamps = collect_frames()
df = predict_frames(frames, timestamps)
df[CLASS_NAMES] = (df[CLASS_NAMES] > THRESHOLD).astype(int)
print(df.head(19))
