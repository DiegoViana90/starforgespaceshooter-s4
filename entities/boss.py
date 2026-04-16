import math
import random
import pygame
from settings import WIDTH, HEIGHT, RED
from entities.bullet import Bullet
from entities.bomb import Bomb
from utils import clamp

class Boss:
    def __init__(self):
        self.x = WIDTH + 180
        self.y = HEIGHT // 2 - 90
        self.w = 180
        self.h = 160
        self.hp = 120
        self.max_hp = 120

        self.entry_done = False
        self.base_y = self.y
        self.move_angle = 0

        self.last_triple = 0
        self.last_bomb = 0
        self.triple_delay = 1200
        self.bomb_delay = 2200

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, enemy_bullets, bombs):
        now = pygame.time.get_ticks()

        if not self.entry_done:
            self.x -= 2
            if self.x <= WIDTH - self.w - 70:
                self.entry_done = True
        else:
            self.move_angle += 0.03
            self.y = self.base_y + math.sin(self.move_angle) * 120
            self.y = clamp(self.y, 40, HEIGHT - self.h - 40)

            if now - self.last_triple >= self.triple_delay:
                cy = self.y + self.h // 2
                enemy_bullets.append(Bullet(self.x - 12, cy - 28, -8, -2, "enemy", w=24, h=6, color=(255, 90, 90)))
                enemy_bullets.append(Bullet(self.x - 12, cy, -8, 0, "enemy", w=24, h=6, color=(255, 90, 90)))
                enemy_bullets.append(Bullet(self.x - 12, cy + 28, -8, 2, "enemy", w=24, h=6, color=(255, 90, 90)))
                self.last_triple = now

            if now - self.last_bomb >= self.bomb_delay:
                bombs.append(Bomb(self.x + 20, self.y + self.h // 2, vx=-4, vy=random.uniform(-1.5, 1.5)))
                self.last_bomb = now

    def draw(self, screen):
        pygame.draw.rect(screen, (120, 90, 90), (self.x, self.y, self.w, self.h), border_radius=14)
        pygame.draw.rect(screen, (170, 130, 130), (self.x + 20, self.y + 18, self.w - 40, self.h - 36), border_radius=10)

        pygame.draw.circle(screen, RED, (int(self.x + 55), int(self.y + 50)), 14)
        pygame.draw.circle(screen, RED, (int(self.x + 55), int(self.y + self.h - 50)), 14)
        pygame.draw.rect(screen, (80, 60, 60), (self.x - 16, self.y + 35, 20, 30))
        pygame.draw.rect(screen, (80, 60, 60), (self.x - 16, self.y + self.h - 65, 20, 30))
        pygame.draw.rect(screen, (220, 180, 180), (self.x + self.w - 34, self.y + self.h // 2 - 18, 26, 36), border_radius=5)
