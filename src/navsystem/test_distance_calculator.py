import unittest
import numpy as np
from distance_calculator import DistanceCalculator

class TestDistanceCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = DistanceCalculator()
        self.calc.last_reported_distance = 0
        self.calc.distance_update_threshold = 5

    def test_calculate_distance(self):
        p1 = (0, 0, 0)
        p2 = (3, 4, 0)
        expected = 5.0
        actual = self.calc.calculate_distance(p1, p2)

        print("\n--- test_calculate_distance ---")
        print(f"Input: {p1}, {p2}")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        print("-------------------------------")

        self.assertAlmostEqual(actual, expected)

    def test_calculate_path_distance(self):
        positions = [(0, 0, 0), (3, 0, 0), (3, 4, 0)]
        expected = 7.0
        actual = self.calc.calculate_path_distance(positions)

        print("\n--- test_calculate_path_distance ---")
        print(f"Input positions: {positions}")
        print(f"Expected: {expected}")
        print(f"Actual: {actual}")
        print("------------------------------------")

        self.assertAlmostEqual(actual, expected)

    def test_calculate_distance_to_turn(self):
        current = (0, 0, 0)
        path = [(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 4, 0)]
        turns = [2, 3]
        expected_distance = 2.0
        expected_turn_index = 2

        actual_distance, actual_index = self.calc.calculate_distance_to_turn(current, path, turns)

        print("\n--- test_calculate_distance_to_turn ---")
        print(f"Input current_position: {current}")
        print(f"Input path_positions: {path}")
        print(f"Input turn_indices: {turns}")
        print(f"Expected distance: {expected_distance}")
        print(f"Actual distance: {actual_distance}")
        print(f"Expected turn index: {expected_turn_index}")
        print(f"Actual turn index: {actual_index}")
        print("----------------------------------------")

        self.assertAlmostEqual(actual_distance, expected_distance)
        self.assertEqual(actual_index, expected_turn_index)

    def test_should_update_distance(self):
        distances = [6, 7]
        expected_results = [True, False]
        results = []

        print("\n--- test_should_update_distance ---")
        for new_distance, expected in zip(distances, expected_results):
            result = self.calc.should_update_distance(new_distance)
            results.append(result)
            print(f"Input new_distance: {new_distance}")
            print(f"Expected: {expected}")
            print(f"Actual: {result}")
            print("---------------------------")
            self.assertEqual(result, expected)

    def test_get_distance_description(self):
        test_cases = [
            (6.2, "6 meters"),
            (43, "45 meters"),
            (853, "850 meters"),
            (1200, "1.2 kilometers"),
        ]

        print("\n--- test_get_distance_description ---")
        for dist, expected in test_cases:
            result = self.calc.get_distance_description(dist)
            print(f"Input distance: {dist}")
            print(f"Expected: {expected}")
            print(f"Actual: {result}")
            print("---------------------------")
            self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()