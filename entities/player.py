import pygame
from settings import CYAN, WHITE, ORANGE
from entities.bullet import Bullet
from entities.laser_beam import LaserBeam
from utils import clamp


class Player:
    def __init__(self):
        self.x = 120
        self.y = 300
        self.w = 48
        self.h = 28
        self.speed = 5
        self.hp = 100

        self.shoot_delay = 120
        self.last_shot = 0

        self.weapon_heat = 0.0
        self.max_heat = 100.0
        self.heat_per_shot = 9.0
        self.cool_rate = 26.0
        self.overheat_cool_rate = 42.0
        self.overheated = False

        self.special_ammo = 0
        self.max_special_ammo = 42
        self.special_weapon_type = None

        self.laser_tick_ms = 70
        self.last_laser_tick = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def apply_difficulty(self, difficulty):
        if difficulty == "easy":
            self.heat_per_shot = 7.0
            self.cool_rate = 30.0
            self.overheat_cool_rate = 52.0
            self.max_special_ammo = 72
        elif difficulty == "hard":
            self.heat_per_shot = 12.0
            self.cool_rate = 22.0
            self.overheat_cool_rate = 34.0
            self.max_special_ammo = 36
        else:
            self.heat_per_shot = 9.0
            self.cool_rate = 26.0
            self.overheat_cool_rate = 42.0
            self.max_special_ammo = 54

        if self.special_ammo > self.max_special_ammo:
            self.special_ammo = self.max_special_ammo

    def update(self, keys, dt, firing_input, move_input, screen_w, screen_h):
        mx, my = move_input

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            my -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            my += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            mx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            mx += 1

        if mx != 0 or my != 0:
            length = (mx * mx + my * my) ** 0.5
            if length != 0:
                mx /= length
                my /= length

        self.x += mx * self.speed
        self.y += my * self.speed

        self.x = clamp(self.x, 20, screen_w // 2)
        self.y = clamp(self.y, 20, screen_h - self.h - 20)

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

    def try_fire(self, bullets, screen_w=None):
        now = pygame.time.get_ticks()
        center_y = self.y + self.h // 2 - 2

        if self.special_ammo > 0 and self.special_weapon_type == "laser":
            if screen_w is None:
                return False

            if now - self.last_laser_tick < self.laser_tick_ms:
                return False

            bullets.append(LaserBeam(self.x + self.w - 4, center_y, screen_w))
            self.special_ammo -= 1
            self.last_laser_tick = now

            if self.special_ammo <= 0:
                self.special_weapon_type = None

            return True

        if now - self.last_shot < self.shoot_delay:
            return False

        if self.special_ammo > 0 and self.special_weapon_type == "triple":
            bullets.append(Bullet(self.x + self.w, center_y - 10, 12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            bullets.append(Bullet(self.x + self.w, center_y,      12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            bullets.append(Bullet(self.x + self.w, center_y + 10, 12, 0, "player", w=18, h=5, color=(255, 220, 80)))
            self.special_ammo -= 1
            if self.special_ammo <= 0:
                self.special_weapon_type = None
            self.last_shot = now
            return True

        if self.special_ammo > 0 and self.special_weapon_type == "spread":
            bullets.append(Bullet(self.x + self.w, center_y, 12, -2.2, "player", w=18, h=5, color=(120, 255, 180)))
            bullets.append(Bullet(self.x + self.w, center_y, 12,  0.0, "player", w=18, h=5, color=(120, 255, 180)))
            bullets.append(Bullet(self.x + self.w, center_y, 12,  2.2, "player", w=18, h=5, color=(120, 255, 180)))
            self.special_ammo -= 1
            if self.special_ammo <= 0:
                self.special_weapon_type = None
            self.last_shot = now
            return True

        if self.overheated:
            return False

        bullets.append(Bullet(self.x + self.w, center_y, 11, 0, "player"))
        self.weapon_heat += self.heat_per_shot

        if self.weapon_heat >= self.max_heat:
            self.weapon_heat = self.max_heat
            self.overheated = True

        self.last_shot = now
        return True

    def give_special_ammo(self, weapon_type, amount):
        self.special_weapon_type = weapon_type
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

        pygame.draw.circle(screen, WHITE, (int(self.x + 18), int(self.y + self.h // 2)), 6)

        pygame.draw.polygon(screen, ORANGE, [
            (self.x - 10, self.y + self.h // 2),
            (self.x, self.y + 8),
            (self.x, self.y + self.h - 8),
        ])
