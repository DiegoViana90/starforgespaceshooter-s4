import math
import pygame
from settings import WHITE


class WeaponPickup:
    def __init__(self, x, y, weapon_type="triple"):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
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
        color = (255, 210, 70)
        if self.weapon_type == "spread":
            color = (120, 255, 180)
        elif self.weapon_type == "laser":
            color = (120, 220, 255)

        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size), border_radius=5)
        pygame.draw.rect(screen, (40, 40, 40), (self.x + 2, self.y + 2, self.size - 4, self.size - 4), border_radius=4)

        font = pygame.font.SysFont("arial", 12, bold=True)
        label = "T"
        if self.weapon_type == "spread":
            label = "S"
        elif self.weapon_type == "laser":
            label = "L"

        text = font.render(label, True, WHITE)
        screen.blit(text, text.get_rect(center=(self.x + self.size / 2, self.y + self.size / 2)))
