from data_setup import *
from path_finding import PathFinder

data = load_keyframes("keyframe_data.csv")

graph = build_graph(data, 3)

path_finder = PathFinder(data, graph)



