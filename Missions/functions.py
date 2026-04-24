import asyncio
import threading
import subprocess
import time
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw
from ultralytics import YOLO
from rplidar import RPLidar
import camera
import asyncio
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os


# -- LIDAR Constants --
PORT_NAME = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
BAUDRATE = 115200
NUM_BINS = 100

# -- LIDAR Globals --
lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE, timeout=3)
latest_ranges = [float('inf')] * NUM_BINS
lock = threading.Lock()


# -- CAMERA & OBJ_PREDICTION Globals -- 
# The objects the object_detection_model looks for. 
CLASS_NAMES = ["bear", "cyclist", "fox", "reindeer", "robot", "santa"]

# Insert the path of the model used here.
MODEL_PATH  = "/home/robot/robo_proj/Models/yolo_detect/best3.pt"

# The level of certainty before considering a predicted object as one of the CLASS_NAMES.
THRESHOLD   = 0.6

# -- FUNCTIONS --
def lidar_thread():
    """
    Runs in a background thread. Continuously reads scans from the RPLidar,
    bins the distances into NUM_BINS angular slots across -90 to +90 degrees,
    and updates latest_ranges.
    """
    bin_angles = np.linspace(-90, 90, NUM_BINS)

    lidar.stop()
    lidar.stop_motor()
    time.sleep(2)
    lidar.start_motor()
    time.sleep(1)

    try:
        for scan in lidar.iter_scans():
            ranges = np.full(NUM_BINS, np.inf)
            for _, angle, distance in scan:
                if angle > 180:
                    angle -= 360
                if -90 <= angle <= 90:
                    idx = np.argmin(np.abs(bin_angles - angle))
                    dist_meters = distance / 1000.0
                    if dist_meters > 0.15 and dist_meters < ranges[idx]:
                        ranges[idx] = dist_meters
            with lock:
                global latest_ranges
                latest_ranges = ranges.tolist()
    except Exception:
        pass


def read_lidar_ranges():
    """Grab the latest scan - call this whenever you need a reading."""
    with lock:
        return latest_ranges.copy()


async def lidar_loop(lidar_queue):
    """
    Async task that continuously reads latest_ranges and pushes
    them into lidar_queue every 0.1 seconds for the mission to consume.
    """
    while True:
        ranges = read_lidar_ranges()
        await lidar_queue.put(ranges)
        await asyncio.sleep(0.05)


async def connect_drone(system_address: str = "serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:2000000") -> System:
    """
    Helper function which makes connecting to the drone easier and faster.
    system_address(param): serial/udp address for the drone you want to connect to.
    Returns connected `drone`.
    """
    drone = System()
    await drone.connect(system_address=system_address)
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break
    return drone


async def obtain_gps(drone):
    """
    Force the drone to wait until the GPS connection is stable.
    NOTE: The drone MUST be in the home position for this to work.
    drone(param): the connected System() object from connect_drone().
    """
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break


def get_obstacle_info(ranges, threshold=1.5, cone=50):
    """
    Analyses lidar ranges and returns obstacle info. It works by taking a slice
    of the lidar values within the cone angle. Any lidar distances less than the
    threshold value will be detected as an obstacle. When an obstacle is found,
    it counts the number of free angles and finds the largest obstacle-free gap,
    returning its median angle as best_gap_center.

    ranges(param):    Output from read_lidar_ranges().
    threshold(param): Distance in meters before something is considered an obstacle.
    cone(param):      Degrees to search for obstacles. MAX 180.
    Returns (True, best_gap_center) if obstacle detected, (False, None) if clear.
    """
    angles_arr = np.linspace(-90, 90, len(ranges))
    ranges_arr = np.array(ranges)

    # Check for obstacles inside the cone
    cone_mask = np.abs(angles_arr) <= cone
    cone_ranges = ranges_arr[cone_mask]
    # Require at least 2 bins to trigger, not just 1
    if np.sum(cone_ranges < threshold) < 2:
        return (False, None)


    # Find biggest free gap across full 180 degrees
    is_free = ranges_arr > threshold
    best_gap_size = 0
    best_gap_center = 0
    current_gap_size = 0
    current_gap_start_angle = None

    for i, free in enumerate(is_free):
        if free:
            if current_gap_size == 0:
                current_gap_start_angle = angles_arr[i]
            current_gap_size += 1
        else:
            if current_gap_size > best_gap_size:
                best_gap_size = current_gap_size
                best_gap_center = (current_gap_start_angle + angles_arr[i - 1]) / 2
            current_gap_size = 0

    # Check last gap in case it runs to the end
    if current_gap_size > best_gap_size:
        best_gap_center = (current_gap_start_angle + angles_arr[-1]) / 2

    return (True, best_gap_center)


async def avoid_obstacle(drone, lidar_queue, threshold=1.5, cone=50):
    SPEED = 2.0
    print("Avoiding obstacle...")

    # Send multiple setpoints before starting to ensure PX4 receives at least one
    for _ in range(5):
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
        await asyncio.sleep(0.1)

    try:
        await drone.offboard.start()
    except Exception as e:
        print(f"Offboard start failed: {e}, retrying...")
        await asyncio.sleep(0.5)
        for _ in range(5):
            await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
            await asyncio.sleep(0.1)
        await drone.offboard.start()

    # Wait until PX4 confirms offboard mode
    async for flight_mode in drone.telemetry.flight_mode():
        if str(flight_mode) == "OFFBOARD":
            break
        await drone.offboard.start()
        await asyncio.sleep(0.1)

    # Flush stale scans, get latest
    while not lidar_queue.empty():
        await lidar_queue.get()
    ranges = await lidar_queue.get()
    obstacle, steer_angle = get_obstacle_info(ranges, threshold, cone)

    if not obstacle:
        print("Obstacle cleared!")
        return

    async for h in drone.telemetry.heading():
        current_heading = h.heading_deg
        break

    target_heading = current_heading + steer_angle
    target_heading_rad = math.radians(target_heading)
    north = SPEED * math.cos(target_heading_rad)
    east  = SPEED * math.sin(target_heading_rad)

    print(f"Committing to gap at {steer_angle:.1f}° for 2 seconds")

    for _ in range(20):
        await drone.offboard.set_velocity_ned(
            VelocityNedYaw(north, east, 0.0, target_heading)
        )
        await asyncio.sleep(0.1)

    print("Obstacle cleared!")


async def collect_frames(mission_complete):
    camera.start()
    frames = []
    timestamps = []

    print("------------------------------")
    print("Starting to collect frames...")    

    try:
        while not mission_complete.is_set():
            frame = camera.get_latest_frame()

            if frame is not None:
                frames.append(frame)
                timestamps.append(datetime.now())
                print(f"Frame {len(frames)} captured at {timestamps[-1]}")

            await asyncio.sleep(1)

    finally:
        print("Turning off camera...")
        camera.stop()
        print("Camera turned off!")

    return frames, timestamps


def build_segments(df, class_names):
    """
    Creates a segmented version of a dataframe suitable for a Gantt Chart.

    df(param): The dataframe, which should have timestamps and the classes.
    class_names(param): The class names which should match the df parameter in column length.
    """
    segments = []

    for cls in class_names:
        active = False
        start = None

        for i in range(len(df)):
            val = df.iloc[i][cls]

            if val == 1 and not active:
                active = True
                start = i

            elif val == 0 and active:
                segments.append({
                    "class": cls,
                    "start": start,
                    "end": i
                })
                active = False

        if active:
            segments.append({
                "class": cls,
                "start": start,
                "end": len(df)
            })

    return segments


def gantt_show(segments, class_names):
    """
    Creates the Gantt plot illustration using matplotlib.pyplot. 
    segments(param):    The segmented dataframe created from the build_segments() function.
    class_names(param): The class names to use for y-axis labels.
    """
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

    # Map each class to a y position
    # FIX 2: was referencing CLASS_NAMES global directly — now uses the class_names parameter
    class_to_y = {cls: i for i, cls in enumerate(class_names)}

    for seg in segments:
        ax.barh(
            y=class_to_y[seg["class"]],
            width=seg["end"] - seg["start"],
            left=seg["start"]
        )

    # Sets the labels, ticks, and titles. 
    ax.set_yticks(list(class_to_y.values()))
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Class")
    ax.set_title("Detection Timeline")

    # Show frame
    plt.tight_layout()
    plt.show()


def predict_frames(frames, timestamps):
    """
    Runs YOLO detection on frames and returns a binary dataframe
    aligned with CLASS_NAMES and timestamps.
    """

    model = YOLO(MODEL_PATH) 
    rows = []

    for i, frame in enumerate(frames):
        result = model.predict(frame, verbose=False)[0]
              
        scores = np.zeros(len(CLASS_NAMES), dtype=np.float32)

        if result.boxes is not None and len(result.boxes) > 0:
            classes = result.boxes.cls.cpu().numpy().astype(int)
            confs = result.boxes.conf.cpu().numpy()

            for cls_id, conf in zip(classes, confs):
                if 0 <= cls_id < len(scores):
                    scores[cls_id] = max(scores[cls_id], float(conf))

        print(scores.tolist())

        print(f"Predicting frame number: {i+1}")
        rows.append(scores)


    df = pd.DataFrame(rows, columns=CLASS_NAMES)
    df.insert(0, "timestamp", timestamps)

    print(df)
    
    return df


async def get_battery(drone) -> float:
    async for battery in drone.telemetry.battery():
        return battery.remaining_percent * 100


def push_objlogs_db(df):
    """
    Pushes the dataframe into the Pukki DBaaS and overwrites the previous table.

    df(param): The dataframe expected to be pushed into the database table. 
    """
    load_dotenv()

    # FIX 4: was re-reading from CSV and discarding the df parameter entirely.
    # Now uses the df passed in directly, as intended.

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        with conn.cursor() as cursor:
            # 1. Clear table
            cursor.execute("TRUNCATE TABLE object_logs RESTART IDENTITY;")

            # 2. Prepare insert
            cols = list(df.columns)
            values = [tuple(row) for row in df.to_numpy()]

            insert_query = f"""
                INSERT INTO object_logs ({", ".join(cols)})
                VALUES %s
            """

            execute_values(cursor, insert_query, values)

        conn.commit()

    finally:
        conn.close()


async def push_battery_db(drone):
    """
    Creates a battery_log table if it doesn't exist, clears it,
    and inserts the current battery level as a single row.
    """
    load_dotenv()

    battery_level = await get_battery(drone)

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        with conn.cursor() as cursor:
            # 1. Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS battery_log (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    battery_percent FLOAT
                );
            """)

            # 2. Clear previous data
            cursor.execute("TRUNCATE TABLE battery_log RESTART IDENTITY;")

            # 3. Insert current battery level
            cursor.execute(
                "INSERT INTO battery_log (timestamp, battery_percent) VALUES (%s, %s)",
                (datetime.now(), battery_level)
            )

        conn.commit()
        print(f"Battery level pushed to DB: {battery_level:.1f}%")

    finally:
        conn.close()


async def create_gps_table(conn):
    """Creates the gps_log table if it doesn't exist."""
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gps_log (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                latitude FLOAT,
                longitude FLOAT,
                altitude FLOAT
            );
        """)
    conn.commit()


async def push_gps_db(drone, mission_complete):
    """
    Streams GPS position to the database once per second
    until mission_complete is set.
    """
    load_dotenv()

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        await create_gps_table(conn)

        print("Starting GPS logging...")
        while not mission_complete.is_set():
            async for position in drone.telemetry.position():
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO gps_log (timestamp, latitude, longitude, altitude)
                           VALUES (%s, %s, %s, %s)""",
                        (
                            datetime.now(),
                            position.latitude_deg,
                            position.longitude_deg,
                            position.absolute_altitude_m
                        )
                    )
                conn.commit()
                print(f"GPS: {position.latitude_deg:.6f}, {position.longitude_deg:.6f}")
                break  # get one reading then sleep

            await asyncio.sleep(1)

    finally:
        conn.close()
        print("GPS logging stopped.")