import asyncio
import threading
import logging
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.offboard import VelocityNedYaw
from functions import lidar_thread, lidar_loop, get_obstacle_info, avoid_obstacle

logging.basicConfig(level=logging.DEBUG)


async def monitor_mission(drone, mission_complete: asyncio.Event):
    """Watches mission progress and sets the event when finished."""
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")
        if mission_progress.current == mission_progress.total and mission_progress.total > 0:
            print("-- Mission complete!")
            mission_complete.set()
            return


async def obstacle_monitor(drone, lidar_queue: asyncio.Queue, mission_complete: asyncio.Event):
    """Reads lidar data and triggers avoidance until mission is done."""
    while not mission_complete.is_set():
        ranges = await lidar_queue.get()
        obstacle, _ = get_obstacle_info(ranges)
        if obstacle:
            await drone.mission.pause_mission()
            await avoid_obstacle(drone, lidar_queue)
            await drone.mission.start_mission()


async def run():
    # -- Start LIDAR thread --
    thread = threading.Thread(target=lidar_thread, daemon=True)
    thread.start()
    await asyncio.sleep(2)  # Let LIDAR spin up

    lidar_queue = asyncio.Queue()
    lidar_task = asyncio.create_task(lidar_loop(lidar_queue))

    # -- Connect (unchanged from your working file) --
    drone = System()
    await drone.connect(system_address="serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:2000000")
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    # -- Mission items (unchanged from your working file) --
    mission_items = [
        MissionItem(
            66.480329,                       # latitude
            25.720473,                       # longitude
            2,                               # altitude
            .5,                              # speed (m/s)
            True,                            # is_fly_through
            float('nan'),                    # gimbal pitch
            float('nan'),                    # gimbal yaw
            MissionItem.CameraAction.NONE,   # camera action
            float('nan'),                    # loiter time
            float('nan'),                    # camera photo interval
            float('nan'),                    # acceptance radius
            float('nan'),                    # yaw
            float('nan'),                    # photo camera distance
            MissionItem.VehicleAction.NONE,  # vehicle action
        ),
        MissionItem(
            66.480072,                       # latitude
            25.720340,                       # longitude
            2,                               # altitude
            .5,                              # speed (m/s)
            True,                            # is_fly_through
            float('nan'),                    # gimbal pitch
            float('nan'),                    # gimbal yaw
            MissionItem.CameraAction.NONE,   # camera action
            float('nan'),                    # loiter time
            float('nan'),                    # camera photo interval
            float('nan'),                    # acceptance radius
            float('nan'),                    # yaw
            float('nan'),                    # photo camera distance
            MissionItem.VehicleAction.NONE,  # vehicle action
        ),
    ]

    mission_plan = MissionPlan(mission_items)
    await drone.mission.set_return_to_launch_after_mission(True)

    # -- Prime offboard mode before mission starts --
    await drone.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.offboard.start()

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)
    print("-- Arming")
    await drone.action.arm()
    print("-- Starting mission")
    await drone.mission.start_mission()

    # -- Run mission monitor + obstacle avoidance concurrently --
    mission_complete = asyncio.Event()
    await asyncio.gather(
        monitor_mission(drone, mission_complete),
        obstacle_monitor(drone, lidar_queue, mission_complete),
    )

    lidar_task.cancel()
    print("Mission ended, lidar shut down.")


if __name__ == "__main__":
    asyncio.run(run())