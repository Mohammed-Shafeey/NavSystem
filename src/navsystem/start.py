from navigation_system import NavigationSystem
import time

# Initialize
nav_system = NavigationSystem(keyframe_file="data/keyframe_data.csv")

# Set the current position (x, y, z) and orientation (yaw in degrees)
nav_system.set_current_position((-13, 0.2, -4), 175)

# Set the destination keyframe ID
nav_system.set_destination(130)

# Calculate the path
nav_system.calculate_path()

# Start navigation (will give voice/direction updates)
nav_system.start_navigation()

time.sleep(100)
