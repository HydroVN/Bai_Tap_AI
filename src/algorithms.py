import random
from collections import deque

# --- HÀM TÌM HÀNG XÓM (CỐ ĐỊNH - PURE DFS) ---
def get_neighbors_fixed(node, grid_width, grid_height, walls, dynamic_obstacles=None):
    """
    Tìm các ô xung quanh theo thứ tự ưu tiên CỐ ĐỊNH.
    Thứ tự này (Lên -> Phải -> Xuống -> Trái) quyết định hình dáng đường đi DFS.
    """
    x, y = node
    neighbors = []
    
    # Thứ tự ưu tiên: 
    # 1. (0, -1): Lên
    # 2. (1, 0):  Phải
    # 3. (0, 1):  Xuống
    # 4. (-1, 0): Trái
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)] 
    
    if dynamic_obstacles is None:
        dynamic_obstacles = set()

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_width and 0 <= ny < grid_height:
            # Kiểm tra tường và vật cản động
            if (nx, ny) not in walls and (nx, ny) not in dynamic_obstacles:
                neighbors.append((nx, ny))
    return neighbors

# --- THUẬT TOÁN BFS (TÌM ĐƯỜNG THOÁT) ---
def bfs_solve(start, end, walls, guards_positions, grid_width, grid_height):
    # Chuyển list lính sang set để tra cứu nhanh
    unsafe_tiles = set(guards_positions)
    
    queue = deque([start])
    came_from = {start: None}
    
    found = False
    
    while queue:
        current = queue.popleft()
        if current == end:
            found = True
            break
        
        # Dùng get_neighbors_fixed để đường gợi ý không bị nhảy lung tung
        for next_node in get_neighbors_fixed(current, grid_width, grid_height, walls, unsafe_tiles):
            if next_node not in came_from:
                queue.append(next_node)
                came_from[next_node] = current
                
    if not found:
        return []
    
    path = []
    current = end
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# --- THUẬT TOÁN DFS (TUẦN TRA - PURE DFS) ---
def generate_full_patrol_path(start, walls, grid_width, grid_height):
    """
    Tạo lộ trình tuần tra bằng DFS thuần túy (Không Random).
    Lính sẽ đi thẳng một mạch đến khi đụng tường mới rẽ.
    """
    path = [start]
    visited = {start}
    stack = [start]
    current = start
    
    while stack:
        # --- THAY ĐỔI QUAN TRỌNG Ở ĐÂY ---
        # Trước đây ta dùng get_neighbors_random, giờ ta dùng get_neighbors_fixed
        # để đảm bảo DFS hoạt động theo đúng quy tắc ưu tiên hướng.
        neighbors = get_neighbors_fixed(current, grid_width, grid_height, walls)
        
        # Lọc những ô chưa đi qua
        unvisited_neighbors = [n for n in neighbors if n not in visited]
        
        if unvisited_neighbors:
            # PURE DFS: Luôn chọn phần tử đầu tiên trong danh sách ưu tiên
            # (Ví dụ: Nếu có đường Lên, nó sẽ luôn chọn Lên thay vì Phải)
            next_node = unvisited_neighbors[0]
            
            visited.add(next_node)
            stack.append(current)
            path.append(next_node)
            current = next_node
        else:
            # Backtracking (Quay lui) khi hết đường
            if not stack:
                break
            parent = stack.pop()
            path.append(parent)
            current = parent
            
    return path