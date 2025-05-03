import os
import heapq
from distance_calculator import DistanceCalculator


class PathFinder:
    """
    Simple path finder implementation for the navigation system.
    """
    def __init__(self, graph, positions):
        # Fix the graph: convert list of (neighbor, cost) to {neighbor: cost}
        self.graph = {}
        for node, neighbors in graph.items():
            if isinstance(neighbors, list):
                self.graph[node] = {neighbor: cost for neighbor, cost in neighbors}
            else:
                self.graph[node] = neighbors  # If already a dict, keep it
        self.positions = positions

    def find_path(self, start, end):
        """
        Find the shortest path from start to end using A* search with Euclidean heuristic.

        Args:
            start: Starting node
            end: Destination node

        Returns:
            list: Path from start to end, or empty list if no path exists
        """
        if start == end:
            return [start]

        calculator = DistanceCalculator()
        open_set = []
        heapq.heappush(open_set, (0, start, [start]))  # (priority, node, path)

        g_scores = {start: 0}

        while open_set:
            _, current, path = heapq.heappop(open_set)

            if current == end:
                return path

            for neighbor, cost in self.graph.get(current, {}).items():
                tentative_g_score = g_scores[current] + cost

                if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g_score

                    # Heuristic: estimated cost from neighbor to end
                    heuristic = calculator.calculate_distance(self.positions[neighbor], self.positions[end])

                    priority = tentative_g_score + heuristic
                    heapq.heappush(open_set, (priority, neighbor, path + [neighbor]))

        return []  # No path found