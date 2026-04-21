import math
import random
import pygame
from settings import WIDTH, HEIGHT, RED
from entities.bullet import Bullet
from entities.bomb import Bomb
from utils import clamp


class Boss:
    def __init__(self, phase=1):
        self.phase = phase

        self.x = WIDTH + 180
        self.y = HEIGHT // 2 - 90
        self.w = 180
        self.h = 160

        if phase == 1:
            self.hp = 120
            self.max_hp = 120
            self.triple_delay = 1200
            self.bomb_delay = 2200
            self.move_speed = 0.03
            self.move_amp = 120
        else:
            self.hp = 180
            self.max_hp = 180
            self.triple_delay = 850
            self.bomb_delay = 1500
            self.move_speed = 0.05
            self.move_amp = 145

        self.entry_done = False
        self.base_y = self.y
        self.move_angle = 0

        self.last_triple = 0
        self.last_bomb = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, enemy_bullets, bombs):
        now = pygame.time.get_ticks()

        if not self.entry_done:
            self.x -= 2.4 if self.phase == 2 else 2
            if self.x <= WIDTH - self.w - 70:
                self.entry_done = True
        else:
            self.move_angle += self.move_speed
            self.y = self.base_y + math.sin(self.move_angle) * self.move_amp
            self.y = clamp(self.y, 40, HEIGHT - self.h - 40)

            if now - self.last_triple >= self.triple_delay:
                cy = self.y + self.h // 2

                if self.phase == 1:
                    enemy_bullets.append(Bullet(self.x - 12, cy - 28, -8, -2, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy,      -8,  0, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy + 28, -8,  2, "enemy", w=24, h=6, color=(255, 90, 90)))
                else:
                    enemy_bullets.append(Bullet(self.x - 12, cy - 42, -9, -3, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy - 18, -9, -1, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy,      -9,  0, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy + 18, -9,  1, "enemy", w=24, h=6, color=(255, 90, 90)))
                    enemy_bullets.append(Bullet(self.x - 12, cy + 42, -9,  3, "enemy", w=24, h=6, color=(255, 90, 90)))

                self.last_triple = now

            if now - self.last_bomb >= self.bomb_delay:
                bombs.append(
                    Bomb(
                        self.x + 20,
                        self.y + self.h // 2,
                        vx=-4.6 if self.phase == 2 else -4,
                        vy=random.uniform(-1.6, 1.6)
                    )
                )
                self.last_bomb = now

    def draw(self, screen):
        base_color = (120, 90, 90) if self.phase == 1 else (145, 70, 70)
        inner_color = (170, 130, 130) if self.phase == 1 else (200, 110, 110)

        pygame.draw.rect(screen, base_color, (self.x, self.y, self.w, self.h), border_radius=14)
        pygame.draw.rect(screen, inner_color, (self.x + 20, self.y + 18, self.w - 40, self.h - 36), border_radius=10)

        pygame.draw.circle(screen, RED, (int(self.x + 55), int(self.y + 50)), 14)
        pygame.draw.circle(screen, RED, (int(self.x + 55), int(self.y + self.h - 50)), 14)

        pygame.draw.rect(screen, (80, 60, 60), (self.x - 16, self.y + 35, 20, 30))
        pygame.draw.rect(screen, (80, 60, 60), (self.x - 16, self.y + self.h - 65, 20, 30))
        pygame.draw.rect(screen, (220, 180, 180), (self.x + self.w - 34, self.y + self.h // 2 - 18, 26, 36), border_radius=5)
