# NavSystem Repository Restructuring

This document outlines the changes made to restructure the NavSystem repository, including the addition of Bluetooth functionality, implementation of a cohesive testing framework, and creation of mock data for testing.

## Repository Structure

The repository has been restructured to follow a more organized and maintainable layout:

```
NavSystem/
├── data/               # Data files (CSV files, mock data)
│   ├── keyframe_data.csv
│   ├── landmark_data.csv
│   ├── dummy_pos_data.csv
│   └── mock/           # Mock data for testing
│       ├── frames/     # Mock video frames
│       └── audio/      # Mock audio samples
├── docs/               # Documentation
├── src/                # Source code
│   └── navsystem/      # Main package
│       ├── __init__.py
│       ├── audio_processor.py
│       ├── bluetooth_receiver.py
│       ├── data_setup.py
│       ├── distance_calculator.py
│       ├── navigation_system.py
│       ├── path_finding.py
│       ├── pointcloud_unpacker.py
│       ├── raspberry_pi_sender.py
│       ├── Recieve_pos_data.py
│       ├── tts_system.py
│       ├── turn_recognition.py
│       └── video_processor.py
├── tests/              # Test files
│   ├── __init__.py
│   ├── test_bluetooth_integration.py
│   ├── test_config.py
│   ├── test_navigation.py
│   ├── test_system_integration.py
│   └── test_utils.py
├── .gitignore          # Git ignore file
├── README.md           # Repository readme
├── CheckList           # Project checklist
└── run_tests.py        # Script to run all tests
```

## Key Changes

1. **Organized Directory Structure**: Created separate directories for source code, tests, data, and documentation.

2. **Python Package Structure**: Converted the source code into a proper Python package with `__init__.py` files.

3. **Relative Imports**: Updated all imports to use relative imports within the package.

4. **Added Missing Files**: Created missing files that were referenced but not present:
   - `audio_processor.py`: Implements audio-to-text conversion
   - `path_finding.py`: Implements path finding for navigation

5. **Mock Implementations**: Added mock implementations for external dependencies:
   - Mock Bluetooth module for testing without actual Bluetooth hardware
   - Mock Speech Recognition for testing without audio hardware

6. **Testing Framework**: Implemented a cohesive testing framework:
   - `test_config.py`: Base test configuration
   - `test_utils.py`: Test utilities and mock data generation
   - Updated test files to work with the new structure

7. **Mock Data Generation**: Added utilities to generate mock data for testing:
   - Mock video frames for testing video processing
   - Mock audio data for testing audio processing

8. **Validation Script**: Created `run_tests.py` to validate system functionality.

9. **Git Ignore**: Added a `.gitignore` file to exclude unnecessary files from version control.

## Bluetooth Integration

The Bluetooth integration allows the system to receive video and audio data from a Raspberry Pi:

1. **Bluetooth Receiver**: `bluetooth_receiver.py` handles Bluetooth connections and routes data to appropriate queues.

2. **Video Processor**: `video_processor.py` processes video frames for stella vslam and updates position data.

3. **Audio Processor**: `audio_processor.py` converts audio to text and interprets commands.

4. **Raspberry Pi Sender**: `raspberry_pi_sender.py` captures and sends video and audio data from a Raspberry Pi.

## Testing Framework

The testing framework consists of several components:

1. **Base Test Case**: `BaseTestCase` in `test_config.py` provides common setup and teardown methods.

2. **Test Utilities**: `test_utils.py` includes utilities for setting up test environments and generating mock data.

3. **Mock Classes**: Mock implementations of external dependencies for testing without hardware.

4. **Test Files**:
   - `test_bluetooth_integration.py`: Tests Bluetooth integration components
   - `test_system_integration.py`: Tests full system integration
   - `test_navigation.py`: Tests navigation system components

5. **Validation Script**: `run_tests.py` runs all tests and validates system functionality.

## How to Use

### Running Tests

To run all tests and validate system functionality:

```bash
python3 run_tests.py
```

To run specific test files:

```bash
python3 -m unittest tests/test_bluetooth_integration.py
python3 -m unittest tests/test_system_integration.py
python3 -m unittest tests/test_navigation.py
```

### Using the System

1. **Start the Bluetooth Receiver**:

```bash
python3 -m navsystem.bluetooth_receiver
```

2. **Start the Video Processor**:

```bash
python3 -m navsystem.video_processor
```

3. **Start the Audio Processor**:

```bash
python3 -m navsystem.audio_processor
```

4. **Start the Navigation System**:

```bash
python3 -m navsystem.navigation_system
```

5. **On the Raspberry Pi, run the sender script**:

```bash
python3 raspberry_pi_sender.py --server-mac XX:XX:XX:XX:XX:XX
```

## Future Improvements

1. **Configuration Files**: Add configuration files for different environments.

2. **Dependency Management**: Add requirements.txt or setup.py for dependency management.

3. **Continuous Integration**: Set up CI/CD pipeline for automated testing.

4. **Documentation**: Add more detailed documentation for each component.

5. **Error Handling**: Improve error handling and recovery mechanisms.

6. **Logging**: Enhance logging for better debugging and monitoring.

7. **Security**: Implement secure Bluetooth communication.
