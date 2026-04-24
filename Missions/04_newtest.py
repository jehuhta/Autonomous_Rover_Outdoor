

import asyncio
import logging

from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan

# Enable INFO level logging by default so that INFO messages are shown
logging.basicConfig(level=logging.DEBUG)


async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:2000000")


    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected to drone!")
            break

    mission_items = [
        MissionItem(
            64.987205,                       # latitude
            25.574786,                       # longitude
            2,                               # altitude
            .5,                               # speed (m/s)
            True,                            # is_fly_through
            float('nan'),                    # gimbal pitch
            float('nan'),                    # gimbal yaw
            MissionItem.CameraAction.NONE,   # camera action
            float('nan'),                    # loiter time
            float('nan'),                    # camera photo interval
            float('nan'),                    # acceptance radius
            float('nan'),                    # yaw
            float('nan'),                    # photo camera distrance
            MissionItem.VehicleAction.NONE,  # DELAY, START_MISSION, STOP_MISSION, more.
        ),
        MissionItem(
            64.987519,                       # latitude
            25.573676,                       # longitude
            2,                               # altitude
            .5,                               # speed (m/s)
            True,                            # is_fly_through
            float('nan'),                    # gimbal pitch
            float('nan'),                    # gimbal yaw
            MissionItem.CameraAction.NONE,   # camera action
            float('nan'),                    # loiter time
            float('nan'),                    # camera photo interval
            float('nan'),                    # acceptance radius
            float('nan'),                    # yaw
            float('nan'),                    # photo camera distrance
            MissionItem.VehicleAction.NONE,  # DELAY, START_MISSION, STOP_MISSION, more.
        ),
        MissionItem(
            64.987318,                       # latitude
            25.573308,                       # longitude
            2,                               # altitude
            .5,                               # speed (m/s)
            True,                            # is_fly_through
            float('nan'),                    # gimbal pitch
            float('nan'),                    # gimbal yaw
            MissionItem.CameraAction.NONE,   # camera action
            float('nan'),                    # loiter time
            float('nan'),                    # camera photo interval
            float('nan'),                    # acceptance radius
            float('nan'),                    # yaw
            float('nan'),                    # photo camera distrance
            MissionItem.VehicleAction.NONE,  # DELAY, START_MISSION, STOP_MISSION, more.
        ),
    ]


    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(True)

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()



async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")


if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())
