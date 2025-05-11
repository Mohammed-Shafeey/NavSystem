import unittest
from path_finding import PathFinder

class TestPathFinder(unittest.TestCase):

    def setUp(self):
        # Define a simple graph where nodes are connected with explicit costs
        self.graph = {
            'A': [('B', 1), ('C', 4)],
            'B': [('A', 1), ('C', 2), ('D', 5)],
            'C': [('A', 4), ('B', 2), ('D', 1)],
            'D': [('B', 5), ('C', 1)]
        }

        # Define 2D positions for nodes used by the distance heuristic
        self.positions = {
            'A': (0, 0, 0),
            'B': (1, 0, 0),
            'C': (1, 1, 0),
            'D': (2, 1, 0)
        }

        self.pathfinder = PathFinder(self.graph, self.positions)

    def test_shortest_path(self):
        start, end = 'A', 'D'
        expected_path = ['A', 'B', 'C', 'D']
        path = self.pathfinder.find_path(start, end)

        print("\n=== test_shortest_path ===")
        print(f"Input: start={start}, end={end}")
        print(f"Expected Path: {expected_path}")
        print(f"Actual Path:   {path}")

        self.assertEqual(path, expected_path)

    def test_same_start_end(self):
        start, end = 'B', 'B'
        path = self.pathfinder.find_path('B', 'B')
        
        print("\n=== test_same_start_end ===")
        print(f"Input: start={start}, end={end}")
        print(f"Expected Path: {['B']}")
        print(f"Actual Path:   {path}")
        self.assertEqual(path, ['B'])

    def test_unreachable_node(self):
        graph = {
            'A': [('B', 1)],
            'B': [('A', 1)],
            'C': [],
            'D': []
        }
        positions = {
            'A': (0, 0, 0),
            'B': (1, 0, 0),
            'C': (2, 2, 0),
            'D': (3, 3, 0)
        }
        pathfinder = PathFinder(graph, positions)
        start, end = 'A', 'D'
        expected_path = []

        path = pathfinder.find_path(start, end)
        
        print("\n=== test_unreachable_node ===")
        print(f"Input: start={start}, end={end}")
        print(f"Expected Path: {expected_path}")
        print(f"Actual Path:   {path}")
            
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()
