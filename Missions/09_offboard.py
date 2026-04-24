import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw

async def run():
    drone = System()
    await drone.connect(system_address="serial:///dev/serial/by-id/usb-Auterion_PX4_FMU_v6C.x_0-if00:2000000")
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Connected")
            break

    print("-- Arming")
    await drone.action.arm()
    await asyncio.sleep(1)

    await drone.offboard.set_velocity_ned(
        VelocityNedYaw(2.0, 0.0, 185.0, 0.0)
    )
    await drone.offboard.start()
    print("-- Offboard started")

    async def send_setpoint():
        """Continuously send setpoint at 10Hz."""
        while True:
            await drone.offboard.set_velocity_ned(
                VelocityNedYaw(2.0, 0.5, 0.0, 0.0)
            )
            await asyncio.sleep(0.1)

    async def print_speed():
        async for odom in drone.telemetry.odometry():
            print(f"vx: {odom.velocity_body.x_m_s:.3f} m/s, vy: {odom.velocity_body.y_m_s:.3f} m/s")

    # Run both concurrently for 5 seconds
    try:
        await asyncio.wait_for(
            asyncio.gather(send_setpoint(), print_speed()),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        pass

    print("-- Stopping")
    await drone.offboard.set_velocity_ned(
        VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
    )
    await drone.offboard.stop()
    await drone.action.disarm()

if __name__ == "__main__":
    asyncio.run(run())