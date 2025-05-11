import unittest
from turn_recognition import TurnRecognizer, TurnDirection, TurnType

class TestTurnRecognizer(unittest.TestCase):
    def setUp(self):
        self.recognizer = TurnRecognizer()

    def test_normalize_angle(self):
        test_cases = [
            (190, -170),
            (-190, 170),
            (360, 0),
            (-360, 0),
            (720, 0),
        ]

        print("\n--- test_normalize_angle ---")
        for input_angle, expected in test_cases:
            actual = self.recognizer.normalize_angle(input_angle)
            print(f"Input: {input_angle}, Expected: {expected}, Actual: {actual}")
            self.assertAlmostEqual(actual, expected)

    def test_detect_turn(self):
        test_cases = [
            (0, 0, (TurnDirection.STRAIGHT, TurnType.NONE, 0)),
            (0, 10, (TurnDirection.STRAIGHT, TurnType.NONE, 10)),
            (0, 20, (TurnDirection.RIGHT, TurnType.SLIGHT, 20)),
            (0, 50, (TurnDirection.RIGHT, TurnType.NORMAL, 50)),
            (0, 100, (TurnDirection.RIGHT, TurnType.SHARP, 100)),
            (0, 200, (TurnDirection.LEFT, TurnType.UTURN, 160)),
            (0, -20, (TurnDirection.LEFT, TurnType.SLIGHT, 20)),
        ]

        print("\n--- test_detect_turn ---")
        for prev, current, expected in test_cases:
            actual = self.recognizer.detect_turn(prev, current)
            print(f"Input: ({prev}, {current})")
            print(f"Expected: {expected}")
            print(f"Actual: {actual}")
            print("---------------------------")
            self.assertEqual(actual[0], expected[0])
            self.assertEqual(actual[1], expected[1])
            self.assertAlmostEqual(actual[2], expected[2])

    def test_analyze_path(self):
        # Path is linear, orientations suggest a right turn at node 1
        path_positions = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 2, 0)]
        orientations = [0, 45, 90, 90]
        expected = [
            (1, TurnDirection.RIGHT, TurnType.NORMAL, 45)
        ]

        actual = self.recognizer.analyze_path(path_positions, orientations)

        print("\n--- test_analyze_path ---")
        print(f"Path: {path_positions}")
        print(f"Orientations: {orientations}")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        print("---------------------------")

        self.assertEqual(len(actual), len(expected))
        for a, e in zip(actual, expected):
            self.assertEqual(a[0], e[0])
            self.assertEqual(a[1], e[1])
            self.assertEqual(a[2], e[2])
            self.assertAlmostEqual(a[3], e[3])

if __name__ == '__main__':
    unittest.main()
