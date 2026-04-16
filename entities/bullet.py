import pygame
from settings import WHITE, YELLOW, RED

class Bullet:
    def __init__(self, x, y, vx, vy, owner, w=18, h=5, color=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.vx = vx
        self.vy = vy
        self.owner = owner
        self.color = color

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        color = self.color if self.color is not None else (YELLOW if self.owner == "player" else RED)
        pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h))
        inner_w = max(2, self.w - 6)
        inner_h = max(2, self.h - 2)
        pygame.draw.rect(screen, WHITE, (self.x + 3, self.y + 1, inner_w, inner_h))
