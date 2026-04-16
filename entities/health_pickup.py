import math
import pygame
from settings import GREEN, WHITE

class HealthPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 18
        self.speed_x = -2.2
        self.base_y = y
        self.wave = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def update(self):
        self.x += self.speed_x
        self.wave += 0.12
        self.y = self.base_y + math.sin(self.wave) * 6

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.size, self.size), border_radius=4)
        pygame.draw.rect(screen, WHITE, (self.x + 6, self.y + 3, 6, 12), border_radius=2)
        pygame.draw.rect(screen, WHITE, (self.x + 3, self.y + 6, 12, 6), border_radius=2)
