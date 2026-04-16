import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60
TITLE = "Shooter 2D estilo SNES"

BLACK = (5, 5, 12)
WHITE = (240, 240, 240)
RED = (220, 70, 70)
GREEN = (80, 220, 120)
YELLOW = (255, 220, 70)
BLUE = (100, 170, 255)
CYAN = (80, 240, 255)
ORANGE = (255, 150, 60)
PURPLE = (180, 100, 240)

ENEMY_EASY = (120, 230, 255)
ENEMY_MEDIUM = (255, 180, 90)
ENEMY_HARD = (235, 90, 90)

FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 48)
