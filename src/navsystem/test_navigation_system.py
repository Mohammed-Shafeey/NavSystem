from navigation_system import NavigationSystem
from tts_system import TTSSystem
from distance_calculator import DistanceCalculator
from turn_recognition import TurnRecognizer
from path_finding import PathFinder
from data_setup import build_graph
from data_setup import load_keyframes


import time

# ----------------------------
# MOCK DATA
# ----------------------------

mock_keyframes_raw = [
    {"id": 0, "x": 0, "y": 0, "z": 0, "orientation": 0},
    {"id": 1, "x": 1, "y": 0, "z": 0, "orientation": 0},
    {"id": 2, "x": 2, "y": 0, "z": 0, "orientation": 45},
    {"id": 3, "x": 2, "y": 1, "z": 0, "orientation": 90},
]

mock_landmarks = {
    0: (0, 0, 0),
    1: (1, 0, 0),
    2: (2, 0, 0),
    3: (2, 1, 0),
}

mock_user_positions = [
    (0.1, 0.1, 0),
    (0.9, 0.0, 0),
    (2.0, 0.1, 0),
    (2.0, 0.9, 0),
]

# ----------------------------
# WRAPPER TEST CLASS
# ----------------------------

class TestNavigationSystem(NavigationSystem):
    def __init__(self):
        super().__init__(keyframe_file="data/keyframe_data.csv")
        self.tts = TTSSystem()
        self.distance_calculator = DistanceCalculator()
        self.turn_recognizer = TurnRecognizer()
        self.pathfinder = None  # will init later
        self.test_path = []
        self.test_turns = []

    def load_mock_data(self):
        # Create keyframe dict in expected format 
        self.keyframes = {
            kf["id"]: [(kf["x"], kf["y"], kf["z"]), kf["orientation"]]
            for kf in mock_keyframes_raw
        }
        
        graph_input = {k: v[0] for k, v in self.keyframes.items()}
        self.graph = build_graph(graph_input)
        # Graph from positions only

        # Create full keyframe dict with orientation for turn detection
        self.full_keyframes = {kf["id"]: kf for kf in mock_keyframes_raw}
        self.landmarks = mock_landmarks
        self.path = [0, 1, 2, 3]
        self.test_path = [mock_landmarks[idx] for idx in self.path]
        self.orientations = [self.full_keyframes[i]["orientation"] for i in self.path]

        # Initialize pathfinder now that graph and landmarks are set
        self.pathfinder = PathFinder(self.graph, self.landmarks)

        # Detect turns
        self.test_turns = [
            idx for idx, _, _, _ in self.turn_recognizer.analyze_path(self.test_path, self.orientations)
        ]

    def run_test(self):
        print("\n--- Running Navigation System Test with Mock Data ---")
        self.load_mock_data()
        self.tts.start()

        for i, pos in enumerate(mock_user_positions):
            print(f"\n[Step {i}] Simulated user position: {pos}")
            dist, turn_idx = self.distance_calculator.calculate_distance_to_turn(
                pos, self.test_path, self.test_turns
            )

            if dist is not None:
                desc = self.distance_calculator.get_distance_description(dist)

                # Get full turn data for this index
                direction, turn_type = None, None
                for idx, d, t, _ in self.turn_recognizer.analyze_path(self.test_path, self.orientations):
                    if idx == turn_idx:
                        direction = d
                        turn_type = t
                        break

                if direction and turn_type:
                    direction_str = direction.value
                    type_str = turn_type.value
                    self.tts.speak(f"In {desc}, turn {direction_str}.")
                else:
                    self.tts.speak(f"Next turn in {desc}")
            else:
                self.tts.speak("No more turns ahead")

            time.sleep(4)


if __name__ == "__main__":
    tester = TestNavigationSystem()
    tester.run_test()