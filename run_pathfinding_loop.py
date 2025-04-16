from data_setup import *
from path_finding import PathFinder
from Recieve_pos_data import get_latest_position
import time

data = load_keyframes("keyframe_data.csv")

graph = build_graph(data, 1)

path_finder = PathFinder(data, graph)

while True:
    # current_pos = get_latest_position() # use this in production
    
    current_pos = (-13, .2, -4) # dummy data
    
    kf_id, kf_pos = find_nearest_keyframe(current_pos, data)
    
    print("nearest keyframe is ", kf_id, " at ", kf_pos)
    
    path = path_finder.astar(kf_id, 66)

    print(path)
    
    time.sleep(1)


    
