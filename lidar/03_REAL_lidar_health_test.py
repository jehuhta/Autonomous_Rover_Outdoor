from rplidar import RPLidar
import time

PORT_NAME = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'

lidar = RPLidar(PORT_NAME, baudrate=115200, timeout=3)
lidar.stop()
lidar.stop_motor()
time.sleep(2)
lidar.start_motor()
time.sleep(2)

try:
    info = lidar.get_info()
    print("Info:", info)
    health = lidar.get_health()
    print("Health:", health)
finally:
    lidar.stop()
    lidar.disconnect()