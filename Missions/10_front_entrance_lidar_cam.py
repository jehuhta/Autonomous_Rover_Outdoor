import asyncio
import threading
import logging
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import VelocityNedYaw
from functions import lidar_thread, lidar_loop, get_obstacle_info, avoid_obstacle, collect_frames, predict_frames, push_objlogs_db, get_battery, push_battery_db
import datetime
import camera


from mavsdk.offboard import OffboardError

try:


    # post-processing always runs


    # -- CAMERA & OBJ_PREDICTION Globals -- 

    # The objects the object_detection_model looks for. 
    CLASS_NAMES = ["bear", "cyclist", "fox", "reindeer", "robot", "santa"]

    # Insert the path of the model used here.
    MODEL_PATH  = "../Models/yolo_detect/best.pt"

    # The level of certainty before considering a predicted object as one of the CLASS_NAMES.
    THRESHOLD   = 0.6


    # ---------------- MISSION MONITOR ----------------

    async def monitor_mission(drone, mission_complete: asyncio.Event):
        async for mission_progress in drone.mission.mission_progress():
            print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
            if mission_progress.current == mission_progress.total and mission_progress.total > 0:
                print("-- Mission complete!")
                mission_complete.set()
                return


    # ---------------- OBSTACLE MONITOR ----------------

    async def obstacle_monitor(drone, lidar_queue, mission_complete):
        while not mission_complete.is_set():
            ranges = await lidar_queue.get()
            obstacle, _ = get_obstacle_info(ranges)

            if obstacle:
                await avoid_obstacle(drone, lidar_queue)
                await drone.mission.start_mission()


    # ---------------- MAIN RUN ----------------

    async def run():

        # -- Start LIDAR thread --
        thread = threading.Thread(target=lidar_thread, daemon=True)
        thread.start()
        await asyncio.sleep(2)

        lidar_queue = asyncio.Queue()
        lidar_task = asyncio.create_task(lidar_loop(lidar_queue))

        # -- Connect --
        drone = System()
        await drone.connect(system_address="serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:2000000")

        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print("-- Connected to drone!")
                break

        # -- Mission items --
        mission_items = [
            MissionItem(
                66.481580,
                25.722596,
                2,
                0.001,
                True,
                float('nan'),
                float('nan'),
                MissionItem.CameraAction.NONE,
                float('nan'),
                float('nan'),
                float('nan'),
                float('nan'),
                float('nan'),
                MissionItem.VehicleAction.NONE,
            ),
        ]

        mission_plan = MissionPlan(mission_items)
        await drone.mission.set_return_to_launch_after_mission(True)

        # -- Offboard prime --
        await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
        await drone.offboard.start()

        print("-- Uploading mission")
        await drone.mission.upload_mission(mission_plan)

        print("-- Arming")
        await drone.action.arm()

        print("-- Starting mission")
        await drone.mission.start_mission()

        # ---------------- PARALLEL EXECUTION ----------------

        mission_complete = asyncio.Event()

        frame_task = asyncio.create_task(collect_frames(mission_complete))

        await asyncio.gather(
            monitor_mission(drone, mission_complete),
            obstacle_monitor(drone, lidar_queue, mission_complete),
        )

        # mission finished → stop frame collection
        mission_complete.set()

        # wait for camera task to finish cleanly
        frames, timestamps = await frame_task

        lidar_task.cancel()
        print("Mission ended, lidar shut down.")

        # -------------- POST PROCESSING -----------------
        
        print("Predicting Frames")
        df = predict_frames(frames, timestamps)

        print("Writing to .CSV")
        df.to_csv("../Pipeline/object_log.csv", index=False)

        print("Classifying objects based on threshold")
        df[CLASS_NAMES] = (df[CLASS_NAMES] > THRESHOLD).astype(int)
        print(df)

        print("Overwriting previous table and writing to Pukki DBaaS")
        push_objlogs_db(df)

        print("Post Processing complete ")

        print("Retrieving battery level...")
        battery_level = await get_battery(drone)
        battery_level = abs(battery_level)
        print(f"Battery: {battery_level:.1f}%")

        await push_battery_db(drone)


    if __name__ == "__main__":
        asyncio.run(run())

except OffboardError as e:
    print(f"Offboard error: {e}")