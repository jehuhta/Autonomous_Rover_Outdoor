import threading
import numpy as np
from rplidar import RPLidar
import time

# -- LIDAR --

# Constants
PORT_NAME = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
BAUDRATE = 115200
NUM_BINS = 60

lidar = RPLidar(PORT_NAME, baudrate=BAUDRATE, timeout=3)

# Creates 60 infinite values.
latest_ranges = [float('inf')] * NUM_BINS

# This makes sure only 1 thread accesses latest_ranges at a time.
lock = threading.Lock()

def lidar_thread():
    """
    
    """
    bin_angles = np.linspace(-90, 90, NUM_BINS)
    
    # Reset before scanning
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


try:
    thread = threading.Thread(target=lidar_thread, daemon=True)
    thread.start()
    time.sleep(5)
    for num in range(300):
        time.sleep(.2)
        print(read_lidar_ranges())
except KeyboardInterrupt:
    pass

finally:
    lidar.stop()
    time.sleep(.2)
    lidar.stop_motor()
    time.sleep(.2)
    lidar.disconnect()


