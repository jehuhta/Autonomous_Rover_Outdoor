import asyncio
import threading
import time
from functions import lidar_thread, lidar_loop, get_obstacle_info

async def run():
    # -- Start LIDAR thread --
    thread = threading.Thread(target=lidar_thread, daemon=True)
    thread.start()
    print("Waiting for lidar to spin up...")
    await asyncio.sleep(2)

    lidar_queue = asyncio.Queue()
    lidar_task = asyncio.create_task(lidar_loop(lidar_queue))

    try:
        while True:
            ranges = await lidar_queue.get()
            obstacle, gap_center = get_obstacle_info(ranges)
            print(f"Obstacle: {obstacle}, Gap: {gap_center}, Min range: {min(ranges):.2f}m")
            await asyncio.sleep(0.1)

            if obstacle:
                print(f"⚠  OBSTACLE — best gap at {gap_center:.1f}°")
            else:
                print("✓  Clear")

            

            await asyncio.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        lidar_task.cancel()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(run())