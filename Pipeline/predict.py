import Pipeline.camera as camera
import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
from datetime import datetime
import time

MODEL_PATH  = "../Models/yolo_onnx/best.onnx"
THRESHOLD   = 0.7
CLASS_NAMES = ["bear", "cyclist", "fox", "reindeer", "robot", "santa"]

# STEP 1: Collect frames
# Start the camera and collect frames once per second until Ctrl+C is pressed.
camera.start()
frames = []
timestamps = []
print("Mission started — press Ctrl+C to stop")

try:
    while True:
        frame = camera.get_latest_frame()
        if frame is not None:
            frames.append(frame)
            timestamps.append(datetime.now())
            print(f"Frame {len(frames)} captured at {timestamps[-1]}")
        time.sleep(1)
except KeyboardInterrupt:
    camera.stop()
    print(f"\n{len(frames)} frames collected. Running detection...")

# STEP 2: Run detection on every frame 
# Load the YOLO model and run inference on each collected frame.
# For each frame, track the highest confidence score per class,
# then threshold it to a binary 0/1 detection.
model = YOLO(MODEL_PATH, task="obb")
rows  = []

for i, frame in enumerate(frames):
    result = model.predict(frame, conf=0.001, verbose=False)[0]

    # Initialize scores for each class to zero
    scores = np.zeros(len(CLASS_NAMES), dtype=np.float32)

    if result.obb is not None and len(result.obb) > 0:
        classes = result.obb.cls.cpu().numpy().astype(int)
        confs   = result.obb.conf.cpu().numpy()

        # Keep the highest confidence score seen for each class in this frame
        for cls_id, conf in zip(classes, confs):
            if 0 <= cls_id < len(scores):
                scores[cls_id] = max(scores[cls_id], float(conf))

    # Convert scores to binary: 1 if above threshold, 0 otherwise
    detected = (scores >= THRESHOLD).astype(int)
    rows.append(detected)
    print(f"Frame {i+1}: {dict(zip(CLASS_NAMES, detected.tolist()))}")

# STEP 3: Build dataframe
# Combine detection results and timestamps into a dataframe
# that matches the database schema (timestamp, bear, cyclist, ...)
df = pd.DataFrame(rows, columns=CLASS_NAMES)
df.insert(0, "timestamp", timestamps)


# # STEP 4: Push to database
# # Load credentials from .env and push the full dataframe to Pukki in one shot.
# from sqlalchemy import create_engine
# from dotenv import load_dotenv
# import os

# load_dotenv()
# engine = create_engine(
#     f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
#     f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
# )

# df.to_sql("object_logs", engine, if_exists="append", index=False)
# print("Results saved to database!")