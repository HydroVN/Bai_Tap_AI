import pygame
import random
from settings import *

class Map:
    def __init__(self, filename):
        self.grid_data = []
        self.walls = set()      
        self.empty_tiles = []   
        self.items = {}         
        self.player_start = (1, 1)
        self.end_point = (1, 1) 
        
        self.load_map(filename)

    def load_map(self, filename):
        try:
            with open(filename, 'r') as f:
                for row_idx, line in enumerate(f):
                    row_data = []
                    for col_idx, char in enumerate(line.strip()):
                        if char == '1':
                            self.walls.add((col_idx, row_idx))
                        elif char == 'S': 
                            self.items[(col_idx, row_idx)] = 'GUN'
                            self.empty_tiles.append((col_idx, row_idx))
                        elif char != 'P' and char != 'E' and char != 'G':
                            self.empty_tiles.append((col_idx, row_idx))
                        
                        if char == 'P':
                            self.player_start = (col_idx, row_idx)
                        elif char == 'E':
                            self.end_point = (col_idx, row_idx)
                        
                        row_data.append(char)
                    self.grid_data.append(row_data)
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {filename}")

    def spawn_key(self, x, y):
        self.items[(x, y)] = 'KEY'

    def get_random_empty_tile(self):
        if self.empty_tiles:
            return random.choice(self.empty_tiles)
        return (1, 1)

    def draw(self, screen, show_exit=False):
        """Vẽ bản đồ. show_exit=True mới hiện cửa."""
        
        # 1. VẼ TƯỜNG (CONNECTED)
        wall_color = (60, 60, 60)
        border_color = (200, 200, 200)
        border_width = 2

        for x, y in self.walls:
            rect = pygame.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(screen, wall_color, rect)
            
            # Vẽ viền nếu không tiếp xúc tường khác
            if (x - 1, y) not in self.walls: pygame.draw.line(screen, border_color, rect.topleft, rect.bottomleft, border_width)
            if (x + 1, y) not in self.walls: pygame.draw.line(screen, border_color, rect.topright, rect.bottomright, border_width)
            if (x, y - 1) not in self.walls: pygame.draw.line(screen, border_color, rect.topleft, rect.topright, border_width)
            if (x, y + 1) not in self.walls: pygame.draw.line(screen, border_color, rect.bottomleft, rect.bottomright, border_width)

        # 2. VẼ VẬT PHẨM
        for (ix, iy), item_type in self.items.items():
            rect = pygame.Rect(ix * TILESIZE, iy * TILESIZE, TILESIZE, TILESIZE)
            if item_type == 'GUN':
                pygame.draw.circle(screen, WHITE, rect.center, 12)
                pygame.draw.circle(screen, PURPLE, rect.center, 10)
            elif item_type == 'KEY':
                pygame.draw.circle(screen, WHITE, rect.center, 10)
                pygame.draw.circle(screen, GOLD, rect.center, 8)
        
        # 3. VẼ CỬA (Nếu show_exit=True)
        if show_exit:
            ex, ey = self.end_point
            exit_rect = pygame.Rect(ex * TILESIZE, ey * TILESIZE, TILESIZE, TILESIZE)
            pygame.draw.rect(screen, CYAN, exit_rect, 4)
            font = pygame.font.SysFont("arial", 20, bold=True)
            text = font.render("EXIT", True, CYAN)
            text_rect = text.get_rect(center=exit_rect.center)
            screen.blit(text, text_rect)