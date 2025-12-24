# src/guard.py
import pygame
from settings import *
from src.algorithms import generate_full_patrol_path

class Guard(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.guards
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        self.image = pygame.Surface((TILESIZE - 4, TILESIZE - 4))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE + 2, y * TILESIZE + 2)
        
        # TẠO LỘ TRÌNH FULL MAP
        # Guard sẽ đi hết map rồi mới quay lại từ đầu
        self.path = generate_full_patrol_path((x, y), game.map.walls, GRID_WIDTH, GRID_HEIGHT)
        self.path_index = 0
        
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 300 # Giảm delay xuống 300 để lính đi nhanh hơn chút cho mượt

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.last_move = now
            if self.path:
                # Lấy vị trí tiếp theo
                target = self.path[self.path_index]
                self.grid_x, self.grid_y = target
                
                # Cập nhật hình ảnh
                self.rect.topleft = (self.grid_x * TILESIZE + 2, self.grid_y * TILESIZE + 2)
                
                # Đi tiếp, lặp lại vô tận
                self.path_index = (self.path_index + 1) % len(self.path)