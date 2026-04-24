'''
This mission is for the simulator. It's the first mission that uses lidar dodging logic!
The drone simply goes to a single waypoint. If it goes on for long enough, it actually falls off of the map.
The user can place various objects in the path of the rover and it will dodge them accordingly. 
'''

# Imports 
import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityBodyYawspeed, VelocityNedYaw
from functions import obtain_gps, lidar_loop
from mavsdk.mission import MissionItem, MissionPlan


# --  FUNCTIONS -- 

async def monitor_mission(drone, mission_complete):
    """
    Monitors the mission progress until complete. If the mission went to all the waypoints, it's done!
    """

    # Uses an async loop so it allows other code to run in the background.
    async for progress in drone.mission.mission_progress():
        # If the number of completed waypoints == number of waypoints in mission... done!
        if progress.current == progress.total:
            print("Mission complete!")

            # Set the mission to complete.
            mission_complete.set()
            return


async def obstacle_monitor(drone, lidar_queue, mission_complete):
    """
    Handles the object detection and the object dodging. 

    If an object is detected, it will switch to offboard mode (pauses the mission) and runs avoid_obstacle().

    The obstacle monitor works such that if it sees something in X distance (meters), it will consider it an obstacle. 
    You can change this threshold in the `obstacle_info` and `avoid_obstacle` functions as well. The same goes for the
    range of the lidar cone (0-180).

    """
    
# -- MAIN --

async def main():
    """
    This is the mission function where the intialization, mission gps points, and high-level logic is determined.
    """
    # Start lidar. We use a queue system that way it doesn't add more ranges than we typically want to expect 
    # inside of the list it creates.
    lidar_queue = asyncio.Queue()

    # # We create a task which runs lidar loop in the background.
    # lidar_task = asyncio.create_task(lidar_loop(lidar_queue))

    # Connect to the rover
    drone = System()
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    # Mission instructions. These are essentially waypoints for it to go towards. 
    mission_items = [

        MissionItem(
            64.987519,                       # latitude
            25.573676,                       # longitude
            2,                               # altitude
            .2,                               # speed (m/s)
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
            .2,                               # speed (m/s)
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

    # Upload, arm and start. It's important to add the sleep sections here,
    # or it risks failing (start mission requires an armed drone.)
    await drone.mission.upload_mission(mission_plan)
    await drone.action.arm()
    await asyncio.sleep(1.0) 
    await drone.mission.start_mission()
    await asyncio.sleep(1.0) 

    # Prime offboard mode (this is required for offboard mode, I called this already
    # but placing it here again gives safety and redundancy that the mission runs.)
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 0))

    # Set a new event in asyncio, called mission_complete. When mission is complete,
    # multiple functions will know to stop!
    mission_complete = asyncio.Event()

    # Run both tasks concurrently
    await asyncio.gather(
        monitor_mission(drone, mission_complete),
        # obstacle_monitor(drone, lidar_queue, mission_complete)
    )

    # Clean up lidar task when done
    lidar_task.cancel()
    print("Mission ended, lidar shut down.")


# This runs the mission asyncronously. 
asyncio.run(main())