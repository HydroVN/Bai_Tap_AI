import random
from collections import deque

def get_neighbors_fixed(node, grid_width, grid_height, walls, dynamic_obstacles=None):
    x, y = node
    neighbors = []
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] 
    
    if dynamic_obstacles is None:
        dynamic_obstacles = set()

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height:
            if (nx, ny) not in walls and (nx, ny) not in dynamic_obstacles:
                neighbors.append((nx, ny))
    return neighbors

def bfs_solve(start, end, walls, guards_positions, grid_width, grid_height):
    unsafe_tiles = set(guards_positions)
    queue = deque([start])
    came_from = {start: None}
    found = False
    
    while queue:
        current = queue.popleft()
        if current == end:
            found = True
            break
        
        for next_node in get_neighbors_fixed(current, grid_width, grid_height, walls, unsafe_tiles):
            if next_node not in came_from:
                queue.append(next_node)
                came_from[next_node] = current
                
    if not found: return []
    
    path = []
    current = end
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def generate_full_patrol_path(start, walls, grid_width, grid_height):
    path = [start]
    visited = {start}
    stack = [start]
    current = start
    
    while stack:
        neighbors = get_neighbors_fixed(current, grid_width, grid_height, walls)
        unvisited_neighbors = [n for n in neighbors if n not in visited]
        
        if unvisited_neighbors:
            next_node = unvisited_neighbors[0]
            visited.add(next_node)
            stack.append(current)
            path.append(next_node)
            current = next_node
        else:
            if not stack: break
            parent = stack.pop()
            path.append(parent)
            current = parent
    return path

def get_next_step_chase(start, target, walls, grid_width, grid_height):
    """Tìm bước đi tiếp theo để tiến về phía target ngắn nhất (BFS)"""
    queue = deque([start])
    came_from = {start: None}
    found = False
    
    while queue:
        current = queue.popleft()
        if current == target:
            found = True
            break
            
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions) 
        
        for dx, dy in directions:
            nx, ny = current[0] + dx, current[1] + dy
            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if (nx, ny) not in walls and (nx, ny) not in came_from:
                    queue.append((nx, ny))
                    came_from[(nx, ny)] = current
    
    if not found: return start
        
    path = []
    curr = target
    while curr != start:
        path.append(curr)
        curr = came_from[curr]
    
    if len(path) > 0: return path[-1]
    return start