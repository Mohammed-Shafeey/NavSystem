import numpy as np
import heapq

class PathFinder:
    def __init__(self, keyframe_positions, graph):
        """
        keyframe_positions: dict of {kf_id: (x, y, z)}
        graph: dict of {kf_id: [(neighbor_kf_id, distance)]}
        """
        self.keyframe_positions = keyframe_positions
        self.graph = graph

    def find_nearest_keyframe(self, position):
        min_dist = float('inf')
        nearest_kf = None
        for kf_id, kf_pos in self.keyframe_positions.items():
            dist = np.linalg.norm(np.array(kf_pos) - np.array(position))
            if dist < min_dist:
                min_dist = dist
                nearest_kf = kf_id
        return nearest_kf

    def heuristic(self, a_id, b_id):
        a = np.array(self.keyframe_positions[a_id])
        b = np.array(self.keyframe_positions[b_id])
        return np.linalg.norm(a - b)

    def astar(self, start_id, goal_id):
        open_set = [(0, start_id)]
        came_from = {}
        g_score = {start_id: 0}
        
        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_id:
                return self.reconstruct_path(came_from, current)

            for neighbor, weight in self.graph.get(current, []):
                tentative_g = g_score[current] + weight
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal_id)
                    heapq.heappush(open_set, (f_score, neighbor))

        return None  # path not found

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
