import csv
import numpy as np
from collections import defaultdict

def load_keyframes(csv_path):
    keyframes = {}
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                kf_id = int(row[0].strip())
                x = float(row[2].strip())
                y = float(row[3].strip())
                z = float(row[4].strip())
                keyframes[kf_id] = (x, y, z)
            except Exception as e:
                print(f"Skipping row due to error: {e}")
    return keyframes

def build_graph(keyframes, distance_threshold=1.5):
    graph = defaultdict(list)
    kf_ids = list(keyframes.keys())

    for i in range(len(kf_ids)):
        id1 = kf_ids[i]
        pos1 = np.array(keyframes[id1])
        for j in range(i+1, len(kf_ids)):
            id2 = kf_ids[j]
            pos2 = np.array(keyframes[id2])
            dist = np.linalg.norm(pos1 - pos2)
            if dist < distance_threshold:
                graph[id1].append((id2, dist))
                graph[id2].append((id1, dist))  # Undirected edge
    return dict(graph)
