import pygame
import math
import random
from settings import *
from src.algorithms import generate_full_patrol_path, get_next_step_chase

# --- LỚP HIỆU ỨNG MÁU ---
class Blood(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        # Vẽ máu loang lổ
        pygame.draw.circle(self.image, (180, 0, 0), (TILESIZE//2, TILESIZE//2), random.randint(10, 18))
        for _ in range(5):
            rx = random.randint(5, 35)
            ry = random.randint(5, 35)
            pygame.draw.circle(self.image, (200, 0, 0), (rx, ry), random.randint(3, 6))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)
        self.start_time = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.start_time > 5000:
            self.kill()

# --- LỚP GUARD ---
class Guard(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.guards
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.grid_x = x
        self.grid_y = y
        
        self.load_images()
        self.image = self.images['down']
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILESIZE, y * TILESIZE)
        
        # Logic AI
        self.patrol_path = generate_full_patrol_path((x, y), game.map.walls, GRID_WIDTH, GRID_HEIGHT)
        self.path_index = 0
        self.state = 'PATROL' 
        self.last_move = pygame.time.get_ticks()
        self.move_delay = 400 
        self.alert_start_time = 0
        self.alert_duration = 600
        
        # Sức khỏe (2 HP)
        self.max_hp = 2
        self.hp = 2 

    def load_images(self):
        try:
            self.images = {
                'down': pygame.transform.scale(pygame.image.load('assets/G_down.jpg'), (TILESIZE, TILESIZE)),
                'up': pygame.transform.scale(pygame.image.load('assets/G_up.jpg'), (TILESIZE, TILESIZE)),
                'left': pygame.transform.scale(pygame.image.load('assets/G_left.jpg'), (TILESIZE, TILESIZE)),
                'right': pygame.transform.scale(pygame.image.load('assets/G_right.jpg'), (TILESIZE, TILESIZE))
            }
        except FileNotFoundError:
            s = pygame.Surface((TILESIZE, TILESIZE))
            s.fill(RED)
            self.images = {'down': s, 'up': s, 'left': s, 'right': s}

    def has_line_of_sight(self):
        # Logic tầm nhìn chính xác (chống nhìn xuyên tường)
        x0, y0 = self.grid_x + 0.5, self.grid_y + 0.5
        x1, y1 = self.game.player.grid_x + 0.5, self.game.player.grid_y + 0.5
        dist = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        if dist > 7: return False
        steps = int(dist * 5) + 1
        if steps <= 1: return True
        dx = (x1 - x0) / steps
        dy = (y1 - y0) / steps
        current_x, current_y = x0, y0
        for i in range(1, steps): 
            current_x += dx
            current_y += dy
            if (int(current_x), int(current_y)) in self.game.map.walls:
                return False
        return True

    def get_facing_direction(self):
        if self.image == self.images['right']: return 'right'
        if self.image == self.images['left']: return 'left'
        if self.image == self.images['up']: return 'up'
        return 'down'

    def take_damage(self):
        self.hp -= 1
        if self.hp > 0:
            print(f"Lính trúng đạn! HP còn: {self.hp}")
            self.state = 'CHASE' # Bị bắn thì đuổi luôn
            self.move_delay = 200
        else:
            self.die()

    def die(self):
        Blood(self.game, self.grid_x, self.grid_y)
        self.game.map.spawn_key(self.grid_x, self.grid_y)
        self.kill()

    # --- HÀM VẼ THANH MÁU MỚI (FLOATING) ---
    def draw_health(self, surface):
        """Vẽ thanh máu bay lơ lửng trên đầu"""
        # Kích thước thanh máu
        bar_width = 32
        bar_height = 6
        
        # Vị trí: Canh giữa theo chiều ngang, nằm trên đầu lính 8px
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 10 
        
        # 1. Vẽ nền đỏ (đại diện cho phần máu đã mất)
        bg_rect = pygame.Rect(x, y, bar_width, bar_height)
        pygame.draw.rect(surface, (255, 0, 0), bg_rect)
        
        # 2. Vẽ máu hiện tại (xanh lá)
        if self.hp > 0:
            ratio = self.hp / self.max_hp
            current_width = int(bar_width * ratio)
            hp_rect = pygame.Rect(x, y, current_width, bar_height)
            pygame.draw.rect(surface, (0, 255, 0), hp_rect)
            
        # 3. Vẽ viền đen cho rõ
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)

    def update(self):
        now = pygame.time.get_ticks()
        can_see = self.has_line_of_sight()
        
        # Logic State
        if self.state == 'PATROL':
            if can_see: self.state = 'ALERT'; self.alert_start_time = now
        elif self.state == 'ALERT':
            if not can_see: self.state = 'PATROL'
            elif now - self.alert_start_time > self.alert_duration: self.state = 'CHASE'; self.move_delay = 300
        elif self.state == 'CHASE':
            if not can_see: self.state = 'PATROL'; self.move_delay = 400

        # Logic Di chuyển
        if self.state != 'ALERT' and now - self.last_move > self.move_delay:
            self.last_move = now
            next_x, next_y = self.grid_x, self.grid_y

            if self.state == 'PATROL' and self.patrol_path:
                next_x, next_y = self.patrol_path[self.path_index]
                self.path_index = (self.path_index + 1) % len(self.patrol_path)
            elif self.state == 'CHASE':
                target = (self.game.player.grid_x, self.game.player.grid_y)
                next_x, next_y = get_next_step_chase((self.grid_x, self.grid_y), target, self.game.map.walls, GRID_WIDTH, GRID_HEIGHT)

            # Xác định hướng
            if next_x > self.grid_x: self.current_dir = 'right'
            elif next_x < self.grid_x: self.current_dir = 'left'
            elif next_y > self.grid_y: self.current_dir = 'down'
            elif next_y < self.grid_y: self.current_dir = 'up'
            else: self.current_dir = 'down' # Đứng yên
            
            self.grid_x, self.grid_y = next_x, next_y
            self.rect.topleft = (self.grid_x * TILESIZE, self.grid_y * TILESIZE)
        
        # Nếu chưa di chuyển lần nào, gán mặc định
        if not hasattr(self, 'current_dir'): self.current_dir = 'down'

        # Update hình ảnh (Hiệu ứng)
        final_image = self.images[self.current_dir].copy()
        
        if self.state == 'ALERT':
            font = pygame.font.SysFont("arial", 30, bold=True)
            text_surf = font.render("!", True, (255, 0, 0))
            rect = text_surf.get_rect(center=(TILESIZE//2, TILESIZE//2 - 10))
            pygame.draw.circle(final_image, (255, 255, 0), rect.center, 12)
            final_image.blit(text_surf, rect)
        elif self.state == 'CHASE':
            final_image.fill((50, 20, 0), special_flags=pygame.BLEND_ADD)

        # Gán ảnh
        self.image = final_image
        # LƯU Ý: Không vẽ thanh máu ở đây nữa, mà vẽ ở Main Loop để không bị hình ảnh che mất