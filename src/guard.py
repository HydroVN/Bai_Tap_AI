import pygame
import os
from settings import *
from src.algorithms import generate_full_patrol_path

class Guard(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.guards
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        
        # --- LOAD ẢNH GUARD ---
        self.load_images()
        self.image = self.images['down'] # Mặc định
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)
        
        # Logic đường đi (giữ nguyên)
        self.path = generate_full_patrol_path((x, y), game.map.walls, GRID_WIDTH, GRID_HEIGHT)
        self.path_index = 0
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 300 

    def load_images(self):
        """Tải 4 hướng ảnh của Guard (dựa trên file bạn đã có)"""
        try:
            # Load ảnh và scale cho vừa ô
            self.images = {
                'down': pygame.transform.scale(pygame.image.load('assets/G_down.jpg'), (TILESIZE, TILESIZE)),
                'up': pygame.transform.scale(pygame.image.load('assets/G_up.jpg'), (TILESIZE, TILESIZE)),
                'left': pygame.transform.scale(pygame.image.load('assets/G_left.jpg'), (TILESIZE, TILESIZE)),
                'right': pygame.transform.scale(pygame.image.load('assets/G_right.jpg'), (TILESIZE, TILESIZE))
            }
            # Nếu ảnh jpg có nền trắng/đen muốn xóa, dùng lệnh:
            # self.images['down'].set_colorkey((255, 255, 255)) # Ví dụ xóa màu trắng
        except FileNotFoundError:
            print("LỖI: Không tìm thấy ảnh Guard. Đang dùng hình vuông đỏ.")
            s = pygame.Surface((TILESIZE, TILESIZE))
            s.fill(RED)
            self.images = {'down': s, 'up': s, 'left': s, 'right': s}

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_move > self.move_delay:
            self.last_move = now
            if self.path:
                target = self.path[self.path_index]
                target_x, target_y = target
                
                # --- TỰ ĐỘNG ĐỔI ẢNH THEO HƯỚNG ---
                if target_x > self.grid_x:
                    self.image = self.images['right']
                elif target_x < self.grid_x:
                    self.image = self.images['left']
                elif target_y > self.grid_y:
                    self.image = self.images['down']
                elif target_y < self.grid_y:
                    self.image = self.images['up']
                # ----------------------------------

                self.grid_x, self.grid_y = target_x, target_y
                self.rect.topleft = (self.grid_x * TILESIZE, self.grid_y * TILESIZE)
                
                self.path_index = (self.path_index + 1) % len(self.path)