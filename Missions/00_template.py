import asyncio
import logging
from mavsdk import System
from mavsdk.mission import MissionItem, MissionPlan
from functions import connect_drone, obtain_gps

# Enable INFO level logging by default so that INFO messages are shown
logging.basicConfig(level=logging.INFO)


async def run():

    # Connect the drone
    drone = await connect_drone()

    # -- MISSION ITEMS --
    mission_items = []
    mission_items.append(
        MissionItem(
            47.398039859999997,
            8.5455725400000002,
            25,
            10,
            True,
            float("nan"),
            float("nan"),
            MissionItem.CameraAction.NONE,
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            MissionItem.VehicleAction.NONE,
        )
    )
    mission_items.append(
        MissionItem(
            47.398036222362471,
            8.5450146439425509,
            25,
            10,
            True,
            float("nan"),
            float("nan"),
            MissionItem.CameraAction.NONE,
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            MissionItem.VehicleAction.NONE,
        )
    )
    mission_items.append(
        MissionItem(
            47.397825620791885,
            8.5450092830163271,
            25,
            10,
            True,
            float("nan"),
            float("nan"),
            MissionItem.CameraAction.NONE,
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            MissionItem.VehicleAction.NONE,
        )
    )
    mission_plan = MissionPlan(mission_items)

    # -- RETURN TO HOME WHEN DONE -- 
    await drone.mission.set_return_to_launch_after_mission(True)


    # -- UPLOADING MISSION --
    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    # -- GPS HEALTH CHECK --
    await obtain_gps(drone)

    # -- ARM & START MISSION --
    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()



# -- PRINT MISSION PROGRESS -- 
async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: {mission_progress.current}/{mission_progress.total}")





if __name__ == "__main__":
    # Run the asyncio loop
    asyncio.run(run())