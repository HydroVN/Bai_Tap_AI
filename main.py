import os
import glob
import msvcrt 
import time

def clear_screen():
    """Xóa màn hình console"""
    os.system('cls' if os.name == 'nt' else 'clear')

def read_map(filename):
    """Đọc file map"""
    try:
        with open(filename, 'r') as f:
            return [list(line.strip()) for line in f if line.strip()]
    except:
        return None

def find_player(grid):
    """Tìm vị trí P"""
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 'P':
                return r, c
    return None, None

def print_game(grid, level_name):
    """Vẽ bản đồ"""
    clear_screen()
    print(f"=== LEVEL: {level_name} ===")
    print("Di chuyển: W, A, S, D | Thoát: Q")
    print("=" * 30)
    for row in grid:
        # P: Mặt cười, 1: Tường, 0: Đường, E: Đích
        line = "".join(row)
        print(line.replace("P", "☻").replace("1", "█").replace("0", " ").replace("G", "+")) 
    print("=" * 30)

def play_level(map_path):
    """Chơi 1 màn"""
    grid = read_map(map_path)
    if not grid: return False
    
    level_name = os.path.basename(map_path)
    rows = len(grid)
    cols = len(grid[0])
    
    while True:
        print_game(grid, level_name)
        pr, pc = find_player(grid) # Tìm vị trí người chơi
        
        if pr is None:
            print("Lỗi: Mất nhân vật P!")
            return False

        # Nhận phím bấm
        key = msvcrt.getch().lower()
        
        nr, nc = pr, pc
        if key == b'w': nr -= 1
        elif key == b's': nr += 1
        elif key == b'a': nc -= 1
        elif key == b'd': nc += 1
        elif key == b'q': 
            print("Bye bye!"); exit()
        else: continue 

        # Xử lý di chuyển
        if 0 <= nr < rows and 0 <= nc < cols:
            target = grid[nr][nc]
            
            if target == '1': # Tường
                continue
            elif target == 'E': # Đích
                grid[pr][pc] = '0'
                grid[nr][nc] = 'P'
                print_game(grid, level_name)
                print("\n>>> CHIẾN THẮNG! <<<")
                # Dừng 1 chút hoặc bấm Enter để qua màn
                print("Nhấn phím bất kỳ để qua màn tiếp theo...")
                msvcrt.getch() 
                return True
            else: # Đường đi (0) hoặc Goal (G)
                grid[pr][pc] = '0'
                grid[nr][nc] = 'P'

# --- CHƯƠNG TRÌNH CHÍNH (Đã sửa đường dẫn) ---
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Tìm map ở cùng thư mục với main.py
    search_pattern = os.path.join(script_dir, "map*.txt")
    map_files = sorted(glob.glob(search_pattern))

    # 2. Nếu không thấy, tìm tiếp vào trong thư mục con tên là "map"
    if not map_files:
        search_pattern = os.path.join(script_dir, "map", "map*.txt")
        map_files = sorted(glob.glob(search_pattern))

    if not map_files:
        print("LỖI: Vẫn không tìm thấy file map nào cả!")
        print(f"Đang tìm tại: {script_dir}")
        print(f"Hoặc tại: {os.path.join(script_dir, 'map')}")
        print("Hãy chắc chắn bạn đã tạo file map1.txt, map2.txt...")
    else:
        print(f"Tìm thấy {len(map_files)} màn chơi. Bắt đầu nào!")
        time.sleep(1)
        
        for map_file in map_files:
            if not play_level(map_file):
                break
        
        print("\nCHÚC MỪNG! BẠN ĐÃ PHÁ ĐẢO TOÀN BỘ GAME!")