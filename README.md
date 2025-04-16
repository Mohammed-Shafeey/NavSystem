# NavSystem - Indoor Navigation System

## Project Overview
NavSystem is an indoor navigation system that uses SLAM (Simultaneous Localization and Mapping) technology to guide users through complex environments where GPS may not be available. The system calculates optimal paths using the A* algorithm, recognizes turns, calculates distances, and provides voice guidance to users.

## Key Components

### Core Navigation
- **Path Finding**: Implements A* algorithm to find optimal paths between locations
- **Graph Building**: Creates a navigation graph from keyframe data
- **Position Tracking**: Receives position updates from SLAM system

### Enhanced Features
- **Turn Recognition**: Detects and classifies turns (slight, normal, sharp, U-turn)
- **Distance Calculation**: Provides accurate distance measurements to destinations and turns
- **Text-to-Speech**: Delivers clear voice instructions to guide users

## Setup and Installation

### Prerequisites
- Python 3.6 or higher
- Required packages: numpy, pyttsx3

### Installation
1. Clone the repository
2. Install required packages:
   ```
   pip install numpy pyttsx3
   ```

## Usage

### Basic Navigation
```python
from navigation_system import NavigationSystem

# Initialize the navigation system
nav_system = NavigationSystem(keyframe_file="keyframe_data.csv")

# Set current position (x, y, z, orientation)
nav_system.set_current_position((-13, 0.2, -4), 175)

# Set destination keyframe ID
nav_system.set_destination(66)

# Calculate path
nav_system.calculate_path()

# Start navigation
nav_system.start_navigation()

# When finished
nav_system.stop_navigation()
```

## File Structure
- `path_finding.py`: A* pathfinding implementation
- `data_setup.py`: Data loading and graph building
- `turn_recognition.py`: Turn detection and classification
- `distance_calculator.py`: Distance calculation utilities
- `tts_system.py`: Text-to-speech integration
- `navigation_system.py`: Main navigation system that integrates all components
- `Recieve_pos_data.py`: Position data reception from SLAM system

## Development Status
- [x] Path finding algorithm (A*)
- [x] Data structure and graph building
- [x] Turn recognition
- [x] Distance calculation
- [x] Text-to-speech integration
- [x] Complete navigation system

## Future Improvements
- User interface for destination selection
- Integration with building maps and landmarks
- Performance optimization for larger environments
- Mobile application integration
