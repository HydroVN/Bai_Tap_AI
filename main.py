import pygame
import sys
import os
import glob
from settings import *
from src.environment import Map
from src.player import Player
from src.guard import Guard
# Import thuật toán BFS đã có sẵn trong source của bạn
from src.algorithms import bfs_solve

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Prison Escape - Advanced AI")
        self.clock = pygame.time.Clock()
        
        # --- SỬA PHẦN NÀY ---
        # Đường dẫn tới file font bạn vừa copy vào folder assets
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(self.base_dir, 'assets', 'arial.ttf') 
        
        try:
            # Load font từ file (hỗ trợ tiếng Việt tốt nhất)
            self.font = pygame.font.Font(font_path, 24)
            self.title_font = pygame.font.Font(font_path, 48) # Có thể bỏ bold=True nếu font không hỗ trợ
        except FileNotFoundError:
            # Nếu quên copy file font thì dùng tạm font hệ thống (có thể lỗi font)
            print("Cảnh báo: Không tìm thấy file font.ttf trong assets!")
            self.font = pygame.font.SysFont("arial", 24)
            self.title_font = pygame.font.SysFont("arial", 48, bold=True)
        # --------------------

        self.map_dir = os.path.join(self.base_dir, 'map')
        
        # Biến lưu trạng thái game
        self.current_map_path = ""
        self.current_path_hint = [] # Chứa đường đi BFS gợi ý

    def draw_text(self, text, font, color, x, y, align="center"):
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if align == "center":
            rect.center = (x, y)
        elif align == "left":
            rect.topleft = (x, y)
        self.screen.blit(surface, rect)

    def get_maps(self):
        """Lấy danh sách các file map trong folder map/"""
        pattern = os.path.join(self.map_dir, "map*.txt")
        files = sorted(glob.glob(pattern))
        return files

    def menu_screen(self):
        """Giao diện chọn Map"""
        map_files = self.get_maps()
        selected_index = 0
        
        waiting = True
        while waiting:
            self.screen.fill(BLACK)
            self.draw_text("CHỌN MÀN CHƠI", self.title_font, WHITE, SCREEN_WIDTH // 2, 80)
            self.draw_text("Dùng mũi tên Lên/Xuống để chọn, Enter để chơi", self.font, LIGHTGREY, SCREEN_WIDTH // 2, 130)

            # Vẽ danh sách map
            start_y = 180
            for i, filepath in enumerate(map_files):
                filename = os.path.basename(filepath)
                color = YELLOW if i == selected_index else WHITE
                prefix = "> " if i == selected_index else "  "
                self.draw_text(f"{prefix}{filename}", self.font, color, SCREEN_WIDTH // 2, start_y + i * 40)

            pygame.display.flip()

            # Xử lý sự kiện menu
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_index = (selected_index - 1) % len(map_files)
                    if event.key == pygame.K_DOWN:
                        selected_index = (selected_index + 1) % len(map_files)
                    if event.key == pygame.K_RETURN: # Enter
                        self.current_map_path = map_files[selected_index]
                        return "PLAY" # Chuyển sang trạng thái chơi
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

    def play_level(self):
        """Vòng lặp chơi game chính"""
        # 1. Load Map
        self.map = Map(self.current_map_path)
        self.all_sprites = pygame.sprite.Group()
        self.guards = pygame.sprite.Group()
        
        # Spawn nhân vật
        for row, tiles in enumerate(self.map.grid_data):
            for col, tile in enumerate(tiles):
                if tile == 'P':
                    self.player = Player(self, col, row)
                if tile == 'G':
                    Guard(self, col, row)

        playing = True
        while playing:
            self.dt = self.clock.tick(FPS) / 1000
            
            # --- EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "MENU" # Bấm ESC để quay lại menu
                    # Di chuyển Player
                    if event.key in [pygame.K_LEFT, pygame.K_a]: self.player.move(-1, 0)
                    if event.key in [pygame.K_RIGHT, pygame.K_d]: self.player.move(1, 0)
                    if event.key in [pygame.K_UP, pygame.K_w]: self.player.move(0, -1)
                    if event.key in [pygame.K_DOWN, pygame.K_s]: self.player.move(0, 1)

            # --- UPDATE ---
            self.all_sprites.update()
            
            # >>> LOGIC TÍNH ĐƯỜNG BFS ĐỘNG (REAL-TIME) <<<
            # Lấy vị trí lính hiện tại để làm vật cản
            current_guards_pos = [(g.grid_x, g.grid_y) for g in self.guards]
            
            # Gọi hàm BFS từ src/algorithms.py
            # Input: Vị trí P, Vị trí E, Tường cố định, Vị trí Lính (coi như tường tạm thời)
            self.current_path_hint = bfs_solve(
                (self.player.grid_x, self.player.grid_y),
                self.map.end_point,
                self.map.walls,
                current_guards_pos,  # Truyền lính vào đây để né
                GRID_WIDTH,
                GRID_HEIGHT
            )

            # --- CHECK WIN/LOSE ---
            # 1. Thua: Chạm lính
            if pygame.sprite.spritecollide(self.player, self.guards, False):
                return "LOSE"
            
            # 2. Thắng: Đến đích E
            if (self.player.grid_x, self.player.grid_y) == self.map.end_point:
                return "WIN"

            # --- DRAW ---
            self.screen.fill(BLACK)
            self.map.draw(self.screen) # Vẽ tường và đích
            
            # Vẽ đường gợi ý BFS (Màu xanh lá cây nhạt)
            if self.current_path_hint:
                # Bỏ qua điểm đầu (Player) để đỡ bị vẽ đè
                for (cx, cy) in self.current_path_hint[1:]:
                    center_pos = (cx * TILESIZE + TILESIZE // 2, cy * TILESIZE + TILESIZE // 2)
                    pygame.draw.circle(self.screen, GREEN, center_pos, 5)

            self.all_sprites.draw(self.screen) # Vẽ P và G
            pygame.display.flip()

    def end_screen(self, result):
        """Màn hình kết thúc (Thắng/Thua)"""
        waiting = True
        while waiting:
            self.screen.fill(BLACK)
            
            if result == "WIN":
                self.draw_text("CHIẾN THẮNG!", self.title_font, GREEN, SCREEN_WIDTH // 2, 150)
                self.draw_text("Bạn đã trốn thoát thành công.", self.font, WHITE, SCREEN_WIDTH // 2, 220)
            else:
                self.draw_text("BỊ BẮT!", self.title_font, RED, SCREEN_WIDTH // 2, 150)
                self.draw_text("Cảnh sát đã tóm được bạn.", self.font, WHITE, SCREEN_WIDTH // 2, 220)

            # Hướng dẫn nút bấm
            self.draw_text("Nhấn [R] để Chơi lại màn này", self.font, YELLOW, SCREEN_WIDTH // 2, 350)
            self.draw_text("Nhấn [M] để Về menu chọn map", self.font,  (100, 200, 255), SCREEN_WIDTH // 2, 400)
            self.draw_text("Nhấn [Q] để Thoát", self.font, LIGHTGREY, SCREEN_WIDTH // 2, 450)
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        return "REPLAY" # Chơi lại map cũ
                    if event.key == pygame.K_m:
                        return "MENU"   # Về menu
                    if event.key == pygame.K_q:
                        pygame.quit(); sys.exit()

    def run(self):
        """Hàm điều phối luồng chính (Main Loop)"""
        state = "MENU"
        
        while True:
            if state == "MENU":
                action = self.menu_screen()
                if action == "PLAY":
                    state = "PLAYING"
            
            elif state == "PLAYING":
                result = self.play_level() # Trả về WIN, LOSE hoặc MENU
                if result == "MENU":
                    state = "MENU"
                else:
                    state = result # Gán WIN hoặc LOSE để chuyển màn hình
            
            elif state == "WIN" or state == "LOSE":
                choice = self.end_screen(state)
                if choice == "REPLAY":
                    state = "PLAYING" # Chơi lại ngay map hiện tại
                elif choice == "MENU":
                    state = "MENU"

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    game = Game()
    game.run()