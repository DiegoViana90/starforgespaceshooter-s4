import pygame


class LaserBeam:
    def __init__(self, x, y, screen_w):
        self.x = x
        self.y = y
        self.w = max(220, screen_w - int(x) - 20)
        self.h = 16
        self.kind = "laser_beam"
        self.alive = True
        self.ttl = 2
        self.damage = 3

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y - self.h // 2), int(self.w), int(self.h))

    def update(self):
        self.ttl -= 1
        if self.ttl <= 0:
            self.alive = False

    def draw(self, screen):
        outer = self.rect()
        mid = pygame.Rect(outer.x, outer.y + 3, outer.w, max(4, outer.h - 6))
        inner = pygame.Rect(outer.x, outer.y + 6, outer.w, max(2, outer.h - 12))

        pygame.draw.rect(screen, (80, 180, 255), outer, border_radius=8)
        pygame.draw.rect(screen, (140, 220, 255), mid, border_radius=6)
        pygame.draw.rect(screen, (220, 245, 255), inner, border_radius=4)
