import pygame
import sys
import os
import glob
import math # Cần import math để làm hiệu ứng nháy
from settings import *
from src.environment import Map
from src.player import Player
from src.guard import Guard
from src.algorithms import bfs_solve

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Prison Escape - Stealth Action")
        self.clock = pygame.time.Clock()
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(self.base_dir, 'assets', 'arial.ttf')
        try:
            self.font = pygame.font.Font(font_path, 24)
            self.title_font = pygame.font.Font(font_path, 48)
            self.alarm_font = pygame.font.Font(font_path, 36) # Font cho báo động
        except FileNotFoundError:
            self.font = pygame.font.SysFont("arial", 24)
            self.title_font = pygame.font.SysFont("arial", 48, bold=True)
            self.alarm_font = pygame.font.SysFont("arial", 36, bold=True)

        self.map_dir = os.path.join(self.base_dir, 'map')
        self.current_map_path = ""
        self.current_path_hint = []

    def draw_text(self, text, font, color, x, y, align="center"):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if align == "center": rect.center = (x, y)
        elif align == "left": rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def get_maps(self):
        pattern = os.path.join(self.map_dir, "map*.txt")
        return sorted(glob.glob(pattern))

    def menu_screen(self):
        map_files = self.get_maps()
        selected_index = 0
        while True:
            self.screen.fill(BLACK)
            self.draw_text("CHỌN MÀN CHƠI", self.title_font, WHITE, SCREEN_WIDTH // 2, 80)
            self.draw_text("Dùng mũi tên Lên/Xuống để chọn, Enter để chơi", self.font, LIGHTGREY, SCREEN_WIDTH // 2, 130)

            start_y = 180
            for i, filepath in enumerate(map_files):
                filename = os.path.basename(filepath)
                display_name = filename.replace(".txt", "").replace("map", "Map ")
                color = YELLOW if i == selected_index else WHITE
                prefix = "> " if i == selected_index else "  "
                self.draw_text(f"{prefix}{display_name}", self.font, color, SCREEN_WIDTH // 2, start_y + i * 40)

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: selected_index = (selected_index - 1) % len(map_files)
                    if event.key == pygame.K_DOWN: selected_index = (selected_index + 1) % len(map_files)
                    if event.key == pygame.K_RETURN: self.current_map_path = map_files[selected_index]; return "PLAY"
                    if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

    def play_level(self):
        self.map = Map(self.current_map_path)
        self.all_sprites = pygame.sprite.Group()
        self.guards = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        for row, tiles in enumerate(self.map.grid_data):
            for col, tile in enumerate(tiles):
                if tile == 'P': self.player = Player(self, col, row)
                if tile == 'G': Guard(self, col, row)

        # --- BIẾN CHO CHẾ ĐỘ BÁO ĐỘNG ---
        self.alarm_active = False
        self.alarm_timer = ALARM_TIME # 15 giây
        
        playing = True
        while playing:
            self.dt = self.clock.tick(FPS) / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "MENU"
                    if event.key in [pygame.K_LEFT, pygame.K_a]: self.player.move(-1, 0)
                    if event.key in [pygame.K_RIGHT, pygame.K_d]: self.player.move(1, 0)
                    if event.key in [pygame.K_UP, pygame.K_w]: self.player.move(0, -1)
                    if event.key in [pygame.K_DOWN, pygame.K_s]: self.player.move(0, 1)
                    if event.key == pygame.K_SPACE: self.player.shoot()

            # UPDATE
            self.all_sprites.update()
            
            # Xử lý đạn
            hits = pygame.sprite.groupcollide(self.bullets, self.guards, True, False)
            for bullet, hit_guards in hits.items():
                for guard in hit_guards:
                    guard.take_damage()

            # --- LOGIC BÁO ĐỘNG ---
            # 1. Kiểm tra xem có lính nào đang CHASE không
            if not self.alarm_active:
                for guard in self.guards:
                    if guard.state == 'CHASE':
                        self.alarm_active = True
                        break # Chỉ cần 1 lính phát hiện là kích hoạt
            
            # 2. Nếu báo động đang bật -> Đếm ngược
            if self.alarm_active:
                self.alarm_timer -= self.dt
                if self.alarm_timer <= 0:
                    return "LOSE" # Hết giờ mà chưa thoát -> Thua

            # --- AI Hint (Chỉ hiện khi có Key) ---
            self.current_path_hint = []
            if self.player.has_key:
                current_guards_pos = [(g.grid_x, g.grid_y) for g in self.guards]
                self.current_path_hint = bfs_solve(
                    (self.player.grid_x, self.player.grid_y),
                    self.map.end_point, self.map.walls, current_guards_pos, GRID_WIDTH, GRID_HEIGHT
                )

            # Check Win/Lose
            if pygame.sprite.spritecollide(self.player, self.guards, False): return "LOSE"
            if (self.player.grid_x, self.player.grid_y) == self.map.end_point:
                if self.player.has_key: return "WIN"

            # DRAW
            self.screen.fill(BLACK)
            self.map.draw(self.screen, show_exit=self.player.has_key)
            
            if self.current_path_hint:
                for (cx, cy) in self.current_path_hint[1:]:
                    center_pos = (cx * TILESIZE + TILESIZE // 2, cy * TILESIZE + TILESIZE // 2)
                    pygame.draw.circle(self.screen, GREEN, center_pos, 5)

            self.all_sprites.draw(self.screen)
            for guard in self.guards:
                guard.draw_health(self.screen)

            # --- VẼ HIỆU ỨNG BÁO ĐỘNG (NẾU KÍCH HOẠT) ---
            if self.alarm_active:
                # 1. Màn hình nháy đỏ (dùng hàm sin để tạo nhịp đập)
                # Alpha chạy từ 50 đến 150
                alpha = int(abs(math.sin(pygame.time.get_ticks() / 200)) * 100) + 50
                alarm_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                alarm_surface.fill((255, 0, 0)) # Màu đỏ
                alarm_surface.set_alpha(alpha)
                self.screen.blit(alarm_surface, (0, 0))
                
                # 2. Vẽ chữ đếm ngược
                time_str = f"{self.alarm_timer:.2f}"
                self.draw_text(f"BÁO ĐỘNG! CẦN THOÁT TRONG: {time_str}", self.alarm_font, WHITE, SCREEN_WIDTH // 2, 50)

            # UI Thường
            gun_status = "ĐÃ CÓ" if self.player.has_gun else "CHƯA CÓ"
            key_status = "ĐÃ CÓ" if self.player.has_key else "CHƯA CÓ"
            color_key = GREEN if self.player.has_key else RED
            self.draw_text(f"SÚNG: {gun_status}", self.font, WHITE, 100, SCREEN_HEIGHT - 20)
            self.draw_text(f"CHÌA KHÓA: {key_status}", self.font, color_key, SCREEN_WIDTH - 150, SCREEN_HEIGHT - 20)

            pygame.display.flip()

    def end_screen(self, result):
        while True:
            self.screen.fill(BLACK)
            if result == "WIN":
                self.draw_text("CHIẾN THẮNG!", self.title_font, GREEN, SCREEN_WIDTH // 2, 150)
                self.draw_text("Bạn đã trốn thoát thành công.", self.font, WHITE, SCREEN_WIDTH // 2, 220)
            else:
                self.draw_text("THẤT BẠI!", self.title_font, RED, SCREEN_WIDTH // 2, 150)
                # Kiểm tra xem thua do hết giờ hay bị bắt
                if hasattr(self, 'alarm_timer') and self.alarm_timer <= 0:
                     self.draw_text("Hết thời gian thoát thân!", self.font, WHITE, SCREEN_WIDTH // 2, 220)
                else:
                     self.draw_text("Cảnh sát đã tóm được bạn.", self.font, WHITE, SCREEN_WIDTH // 2, 220)

            self.draw_text("Nhấn [R] để Chơi lại", self.font, YELLOW, SCREEN_WIDTH // 2, 350)
            self.draw_text("Nhấn [M] để Về menu", self.font, (100, 200, 255), SCREEN_WIDTH // 2, 400)
            self.draw_text("Nhấn [Q] để Thoát", self.font, LIGHTGREY, SCREEN_WIDTH // 2, 450)
            
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r: return "REPLAY"
                    if event.key == pygame.K_m: return "MENU"
                    if event.key == pygame.K_q: pygame.quit(); sys.exit()

    def run(self):
        state = "MENU"
        while True:
            if state == "MENU":
                action = self.menu_screen()
                if action == "PLAY": state = "PLAYING"
            elif state == "PLAYING":
                result = self.play_level()
                state = "MENU" if result == "MENU" else result
            elif state == "WIN" or state == "LOSE":
                choice = self.end_screen(state)
                state = "PLAYING" if choice == "REPLAY" else "MENU"

if __name__ == "__main__":
    game = Game()
    game.run()