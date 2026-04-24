import subprocess
import math

def read_lidar_ranges():
    """
    Returns a list of ranges from a single lidar scan.
    inf = no obstacle detected in that ray.
    """
    proc = subprocess.Popen(
        ["gz", "topic", "-e", "-t", "/lidar/scan", "-n", "1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    output, _ = proc.communicate()

    ranges = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("ranges:"):
            try:
                val = float(line.split(":", 1)[1].strip())
                ranges.append(val)
            except ValueError:
                pass

    ranges = ranges[::-1]
    return ranges

# Test it
if __name__ == "__main__":
    ranges = read_lidar_ranges()
    print(f"Got {len(ranges)} rays")
    print(ranges)