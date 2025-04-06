class Node:
    def __init__(self, x: float, y: float, z: float, orientation: float, next: Node, prev: Node):
        self.x = x
        self.y = y
        self.z = z
        self.next = next
        self.prev = prev
        self.orientation = orientation  #in degrees 
