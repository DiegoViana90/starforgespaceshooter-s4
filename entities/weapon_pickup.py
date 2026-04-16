import math
import pygame
from settings import WHITE


class WeaponPickup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed_x = -2.4
        self.base_y = y
        self.wave = 0.0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def update(self):
        self.x += self.speed_x
        self.wave += 0.11
        self.y = self.base_y + math.sin(self.wave) * 7

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 210, 70), (self.x, self.y, self.size, self.size), border_radius=5)
        pygame.draw.rect(screen, (255, 150, 40), (self.x + 2, self.y + 2, self.size - 4, self.size - 4), border_radius=4)

        pygame.draw.rect(screen, WHITE, (self.x + 4, self.y + 4, 3, 12), border_radius=1)
        pygame.draw.rect(screen, WHITE, (self.x + 8, self.y + 2, 3, 16), border_radius=1)
        pygame.draw.rect(screen, WHITE, (self.x + 12, self.y + 4, 3, 12), border_radius=1)
