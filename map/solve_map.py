import collections

def read_map(filename):
    """Đọc file map và chuyển thành lưới 2D"""
    try:
        with open(filename, 'r') as f:
            # Đọc từng dòng, loại bỏ khoảng trắng thừa
            grid = [list(line.strip()) for line in f if line.strip()]
        return grid
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file {filename}")
        return None

def find_positions(grid):
    """Tìm vị trí bắt đầu (P) và kết thúc (E)"""
    start = None
    end = None
    rows = len(grid)
    cols = len(grid[0])

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 'P':
                start = (r, c)
            elif grid[r][c] == 'E':
                end = (r, c)
    return start, end

def solve_maze_bfs(grid, start, end):
    """Tìm đường đi ngắn nhất từ P đến E bằng BFS"""
    rows = len(grid)
    cols = len(grid[0])
    
    # Queue lưu trữ: (tọa độ hiện tại, đường đi tính đến lúc này)
    queue = collections.deque([(start, [start])])
    visited = set()
    visited.add(start)

    # 4 hướng di chuyển: Lên, Xuống, Trái, Phải
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        (r, c), path = queue.popleft()

        # Nếu tìm thấy đích
        if (r, c) == end:
            return path

        # Duyệt các ô lân cận
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Kiểm tra biên và vật cản
            if 0 <= nr < rows and 0 <= nc < cols:
                cell = grid[nr][nc]
                # Đi được nếu không phải tường '1' và chưa đi qua
                # Coi 'G' và '0' là đường đi được
                if cell != '1' and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    new_path = path + [(nr, nc)]
                    queue.append(((nr, nc), new_path))
    
    return None # Không tìm thấy đường

def print_solution(grid, path):
    """In map ra màn hình với đường đi được vẽ"""
    # Copy grid để không làm hỏng dữ liệu gốc
    output_grid = [row[:] for row in grid]
    
    if path:
        # Đánh dấu đường đi, trừ điểm đầu P và điểm cuối E
        for r, c in path[1:-1]:
            output_grid[r][c] = '.' 
        
        print(f"-> Tìm thấy đường đi với {len(path)-1} bước:")
    else:
        print("-> Không tìm thấy đường đi!")

    # In ra màn hình
    for row in output_grid:
        print("".join(row))

# --- CHẠY CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    # Đổi tên file map ở đây để test (map1.txt, map2.txt...)
    map_file = "map1.txt" 
    
    print(f"Đang giải {map_file}...")
    grid = read_map(map_file)
    
    if grid:
        start_pos, end_pos = find_positions(grid)
        
        if start_pos and end_pos:
            path = solve_maze_bfs(grid, start_pos, end_pos)
            print_solution(grid, path)
        else:
            print("Lỗi: Map thiếu điểm P (Start) hoặc E (End).")