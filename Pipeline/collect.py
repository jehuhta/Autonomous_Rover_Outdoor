import camera
import numpy as np
import time

# start the camera background thread
camera.start()

frames = []  # grows by 1 every second

print("Collecting frames, press Ctrl+C to stop...")

try:
    while True:
        frame = camera.get_latest_frame()  # numpy (480, 640, 3) uint8 BGR
        if frame is not None:
            frames.append(frame)
            print(f"Collected {len(frames)} frames — latest shape: {frame.shape}")
        time.sleep(1)

except KeyboardInterrupt:
    camera.stop()
    print("Stopped.")

# convert list to single numpy array: shape (N, 480, 640, 3)
frames_array = np.stack(frames)
print(f"Final array shape: {frames_array.shape}")

# your teammate uses this to get the latest frame for TFLite:
latest = frames_array[-1]  # shape (480, 640, 3)
print(f"Latest frame shape: {latest.shape}")
