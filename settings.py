import pygame

# Màn hình & Lưới
TILESIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = GRID_WIDTH * TILESIZE
SCREEN_HEIGHT = GRID_HEIGHT * TILESIZE
FPS = 60

# Màu sắc (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (160, 160, 160)
BLUE = (0, 0, 255)      # Player
RED = (200, 0, 0)       # Guard / Máu / Báo động
GREEN = (0, 255, 0)     # Hint Path / HP Bar
YELLOW = (255, 255, 0)  # Vision Cone / Bullet

PURPLE = (128, 0, 128)  # Súng
GOLD = (255, 215, 0)    # Chìa khóa
CYAN = (0, 255, 255)    # Cửa thoát hiểm
ORANGE = (255, 165, 0)  # Cảnh báo

# --- CẤU HÌNH BÁO ĐỘNG ---
ALARM_TIME = 15  # Thời gian đếm ngược (giây) khi bị phát hiện