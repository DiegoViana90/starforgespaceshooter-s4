import pygame
from settings import HEIGHT, CYAN, WHITE, ORANGE, WIDTH
from entities.bullet import Bullet
from utils import clamp


class Player:
    def __init__(self):
        self.x = 120
        self.y = HEIGHT // 2
        self.w = 48
        self.h = 28
        self.speed = 5
        self.hp = 100

        self.shoot_delay = 120
        self.last_shot = 0

        # calor da arma normal
        self.weapon_heat = 0.0
        self.max_heat = 100.0
        self.heat_per_shot = 9.0
        self.cool_rate = 26.0
        self.overheat_cool_rate = 42.0
        self.overheated = False

        # munição especial
        self.special_ammo = 0
        self.max_special_ammo = 42

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, keys, dt, firing_input):
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed

        self.x = clamp(self.x, 20, WIDTH // 2)
        self.y = clamp(self.y, 20, HEIGHT - self.h - 20)

        self._update_weapon_state(dt, firing_input)

    def _update_weapon_state(self, dt, firing_input):
        if self.special_ammo > 0:
            self.weapon_heat = 0
            self.overheated = False
            return

        if self.overheated:
            self.weapon_heat -= self.overheat_cool_rate * dt
            if self.weapon_heat <= 0:
                self.weapon_heat = 0
                self.overheated = False
            return

        if not firing_input:
            self.weapon_heat -= self.cool_rate * dt
            if self.weapon_heat < 0:
                self.weapon_heat = 0

    def try_fire(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_delay:
            return False

        if self.special_ammo > 0:
            center_y = self.y + self.h // 2 - 2
            bullets.append(Bullet(self.x + self.w, center_y - 10, 12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            bullets.append(Bullet(self.x + self.w, center_y,      12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            bullets.append(Bullet(self.x + self.w, center_y + 10, 12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            self.special_ammo -= 1
            self.last_shot = now
            return True

        if self.overheated:
            return False

        bullets.append(Bullet(self.x + self.w, self.y + self.h // 2 - 2, 11, 0, "player"))
        self.weapon_heat += self.heat_per_shot

        if self.weapon_heat >= self.max_heat:
            self.weapon_heat = self.max_heat
            self.overheated = True

        self.last_shot = now
        return True

    def give_special_ammo(self, amount=18):
        self.special_ammo = min(self.max_special_ammo, self.special_ammo + amount)
        self.weapon_heat = 0
        self.overheated = False

    def draw(self, screen):
        pygame.draw.polygon(screen, CYAN, [
            (self.x, self.y + self.h // 2),
            (self.x + 18, self.y),
            (self.x + self.w, self.y + self.h // 2),
            (self.x + 18, self.y + self.h),
        ])

        pygame.draw.circle(screen, WHITE, (self.x + 18, self.y + self.h // 2), 6)

        pygame.draw.polygon(screen, ORANGE, [
            (self.x - 10, self.y + self.h // 2),
            (self.x, self.y + 8),
            (self.x, self.y + self.h - 8),
        ])
