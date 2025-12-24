import pygame
import random
from settings import *

class Map:
    def __init__(self, filename):
        self.grid_data = []
        self.walls = set()      # Chứa tọa độ tường
        self.empty_tiles = []   # Chứa tọa độ ô trống (để spawn lính)
        self.player_start = (1, 1)
        self.end_point = (1, 1) # Điểm E
        
        self.load_map(filename)

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                for row_idx, line in enumerate(f):
                    row_data = []
                    for col_idx, char in enumerate(line.strip()):
                        # 1. Xử lý tường
                        if char == '1':
                            self.walls.add((col_idx, row_idx))
                        else:
                            # Nếu không phải tường thì là ô trống, thêm vào danh sách
                            # (Trừ vị trí Player và Exit ra để tránh spawn đè lên)
                            if char != 'P' and char != 'E':
                                self.empty_tiles.append((col_idx, row_idx))
                        
                        # 2. Xử lý điểm đặc biệt
                        if char == 'P':
                            self.player_start = (col_idx, row_idx)
                        elif char == 'E':
                            self.end_point = (col_idx, row_idx)
                        
                        row_data.append(char)
                    self.grid_data.append(row_data)
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {filename}")

    def get_random_empty_tile(self):
        """Lấy một tọa độ ngẫu nhiên không phải tường"""
        if self.empty_tiles:
            return random.choice(self.empty_tiles)
        return (1, 1) # Fallback nếu không tìm thấy

    def draw(self, screen):
        """Vẽ bản đồ lên màn hình"""
        # Vẽ tường
        for x, y in self.walls:
            rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(screen, LIGHTGREY, rect)
            pygame.draw.rect(screen, DARKGREY, rect, 1) # Viền cho đẹp
        
        # Vẽ điểm kết thúc (Exit)
        ex, ey = self.end_point
        exit_rect = pygame.Rect(ex * TILESIZE, ey * TILESIZE, TILESIZE, TILESIZE)
        pygame.draw.rect(screen, (0, 255, 255), exit_rect) # Màu Cyan nổi bật