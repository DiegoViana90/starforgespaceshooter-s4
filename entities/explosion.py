import pygame
from settings import YELLOW, ORANGE, WHITE

class Explosion:
    def __init__(self, x, y, size=1.0):
        self.x = x
        self.y = y
        self.timer = int(20 * size)
        self.max_timer = int(20 * size)
        self.size = size

    def update(self):
        self.timer -= 1

    def draw(self, screen):
        progress = 1 - (self.timer / self.max_timer)
        radius = int((8 + progress * 24) * self.size)

        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), radius)
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), max(4, radius - int(8 * self.size)))
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), max(2, radius - int(16 * self.size)))
