# src/player.py
import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        self.image = pygame.Surface((TILESIZE - 4, TILESIZE - 4))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.update_pixel_pos()

    def update_pixel_pos(self):
        # Cập nhật vị trí vẽ dựa trên toạ độ lưới
        self.rect.topleft = (self.grid_x * TILESIZE + 2, self.grid_y * TILESIZE + 2)

    def move(self, dx, dy):
        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        # Kiểm tra va chạm với tường trong map
        if (target_x, target_y) not in self.game.map.walls:
            self.grid_x = target_x
            self.grid_y = target_y
            self.update_pixel_pos()