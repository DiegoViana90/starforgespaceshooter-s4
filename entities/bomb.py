import pygame
from settings import PURPLE, WHITE

class Bomb:
    def __init__(self, x, y, vx=-4, vy=2):
        self.x = x
        self.y = y
        self.radius = 9
        self.vx = vx
        self.vy = vy
        self.gravity = 0.18

    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity

    def draw(self, screen):
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x - 2), int(self.y - 2)), 2)
