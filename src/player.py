import pygame
import os
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        
        # --- LOAD ẢNH PLAYER ---
        self.load_images()
        # Mặc định nhìn xuống, nếu chưa bấm gì
        self.image = self.images.get('down', self.images.get('right')) 
        self.rect = self.image.get_rect()
        
        # Đặt vị trí ban đầu
        self.update_pixel_pos()

    def load_images(self):
        """Tải 4 hướng ảnh của Player (Hỗ trợ file .jpg)"""
        self.images = {}
        directions = ['down', 'up', 'left', 'right']
        
        for d in directions:
            # Tên file sẽ là P_down.jpg, P_up.jpg, v.v...
            filename = f"assets/P_{d}.jpg"
            
            try:
                # Load ảnh
                img = pygame.image.load(filename)
                
                # Scale ảnh cho vừa ô (TILESIZE)
                img = pygame.transform.scale(img, (TILESIZE, TILESIZE))
                
                # --- XÓA NỀN (QUAN TRỌNG VỚI FILE JPG) ---
                # Nếu ảnh có nền trắng, dùng (255, 255, 255)
                # Nếu ảnh có nền đen, dùng (0, 0, 0)
                # Bạn hãy thử đổi số này nếu thấy viền lạ quanh nhân vật
                img.set_colorkey((255, 255, 255)) 
                
                self.images[d] = img
                
            except FileNotFoundError:
                # Nếu thiếu file nào thì báo lỗi file đó
                print(f"Cảnh báo: Không tìm thấy file {filename}")
                # Tạo hình vuông xanh tạm thời
                s = pygame.Surface((TILESIZE, TILESIZE))
                s.fill(BLUE)
                self.images[d] = s

    def update_pixel_pos(self):
        self.rect.topleft = (self.grid_x * TILESIZE, self.grid_y * TILESIZE)

    def move(self, dx, dy):
        # 1. Đổi ảnh theo hướng bấm phím
        if dx > 0:
            self.image = self.images['right']
        elif dx < 0:
            self.image = self.images['left']
        elif dy > 0:
            self.image = self.images['down']
        elif dy < 0:
            self.image = self.images['up']

        # 2. Xử lý di chuyển logic
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        # Kiểm tra va chạm tường
        if (target_x, target_y) not in self.game.map.walls:
            self.grid_x = target_x
            self.grid_y = target_y
            self.update_pixel_pos()