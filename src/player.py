import pygame
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, game, x, y, direction):
        self.groups = game.all_sprites, game.bullets
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.speed = 10
        
        self.image = pygame.Surface((8, 8))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos = pygame.math.Vector2(x, y)
        
        self.vel = pygame.math.Vector2(0, 0)
        if direction == 'left': self.vel.x = -self.speed
        elif direction == 'right': self.vel.x = self.speed
        elif direction == 'up': self.vel.y = -self.speed
        elif direction == 'down': self.vel.y = self.speed

    def update(self):
        self.pos += self.vel
        self.rect.center = self.pos
        
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

        grid_x = int(self.pos.x // TILESIZE)
        grid_y = int(self.pos.y // TILESIZE)
        if (grid_x, grid_y) in self.game.map.walls:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        self.has_gun = False
        self.has_key = False
        self.facing = 'down'
        self.last_shot = 0
        self.shoot_delay = 500
        
        self.load_images()
        self.image = self.images['down']
        self.rect = self.image.get_rect()
        self.update_pixel_pos()

    def load_images(self):
        self.images = {}
        directions = ['down', 'up', 'left', 'right']
        for d in directions:
            filename = f"assets/P_{d}.jpg"
            try:
                img = pygame.image.load(filename)
                img = pygame.transform.scale(img, (TILESIZE, TILESIZE))
                img.set_colorkey((255, 255, 255)) 
                self.images[d] = img
            except FileNotFoundError:
                s = pygame.Surface((TILESIZE, TILESIZE))
                s.fill(BLUE)
                self.images[d] = s

    def update_pixel_pos(self):
        self.rect.topleft = (self.grid_x * TILESIZE, self.grid_y * TILESIZE)

    def move(self, dx, dy):
        if dx > 0: self.facing = 'right'; self.image = self.images['right']
        elif dx < 0: self.facing = 'left'; self.image = self.images['left']
        elif dy > 0: self.facing = 'down'; self.image = self.images['down']
        elif dy < 0: self.facing = 'up'; self.image = self.images['up']

        target_x = self.grid_x + dx
        target_y = self.grid_y + dy

        if (target_x, target_y) not in self.game.map.walls:
            self.grid_x = target_x
            self.grid_y = target_y
            self.update_pixel_pos()
            self.check_pick_item()

    def check_pick_item(self):
        pos = (self.grid_x, self.grid_y)
        if pos in self.game.map.items:
            item_type = self.game.map.items[pos]
            if item_type == 'GUN':
                self.has_gun = True
                del self.game.map.items[pos]
            elif item_type == 'KEY':
                self.has_key = True
                del self.game.map.items[pos]

    def shoot(self):
        now = pygame.time.get_ticks()
        if self.has_gun and now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            Bullet(self.game, self.rect.centerx, self.rect.centery, self.facing)