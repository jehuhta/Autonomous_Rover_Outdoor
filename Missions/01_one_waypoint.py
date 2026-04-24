'''
This mission serves as a template for the rover rc simulation. The mission moves to 
a single gps marker. 
'''
# Imports 
import asyncio
import threading
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed
from functions import obtain_gps, lidar_reader_thread, lidar_state, get_obstacle_info, avoid_obstacle
from mavsdk.mission import MissionItem, MissionPlan

# This function runs the entire mission.
async def main():
    # Start lidar
    threading.Thread(target=lidar_reader_thread, daemon=True).start()

    # Connect to drone
    drone = System()
    await drone.connect(system_address="udp://:14540")
    # Wait until GPS is OK
    await obtain_gps(drone)
    # Give the mission some instructions (GPS location, speed, etc)
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

    
    
    
    mission_plan = MissionPlan(mission_items)
    # Upload the mission plan
    await drone.mission.upload_mission(mission_plan)
    # Arm the drone
    await drone.action.arm()
    # Start the mission
    await drone.mission.start_mission()

    # Prepare offboard mode (required before we can switch to it later)
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))

    # Monitor for obstacles until mission is complete
    async for progress in drone.mission.mission_progress():
        if progress.current == progress.total:
            print("Mission complete!")
            break

        obstacle, clear_side = get_obstacle_info()
        if obstacle:
            print("Obstacle detected — pausing mission.")
            await drone.mission.pause_mission()
            await asyncio.sleep(0.3)
            await drone.offboard.start()
            await avoid_obstacle(drone, clear_side)
            await drone.offboard.stop()
            print("Resuming mission...")
            await drone.mission.start_mission()

        await asyncio.sleep(0.1)

# Runs the main function.
asyncio.run(main())