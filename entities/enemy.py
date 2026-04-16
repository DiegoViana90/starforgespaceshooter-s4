import math
import random
import pygame
from settings import WIDTH, HEIGHT, ENEMY_EASY, ENEMY_MEDIUM, ENEMY_HARD
from entities.bullet import Bullet
from utils import clamp


class Enemy:
    def __init__(self):
        self.kind = random.choice(["hover", "wave", "drifter"])

        self.w = random.randint(26, 40)
        self.h = random.randint(20, 30)
        self.x = WIDTH + random.randint(20, 120)
        self.y = random.randint(50, HEIGHT - 90)

        roll = random.random()
        if roll < 0.65:
            self.level = "easy"
            self.hp = 1
            self.color = ENEMY_EASY
            self.shoot_chance = 0.0022
            self.attack_speed = random.uniform(2.2, 3.0)
            self.hover_duration = random.randint(180, 320)
        elif roll < 0.9:
            self.level = "medium"
            self.hp = 2
            self.color = ENEMY_MEDIUM
            self.shoot_chance = 0.0032
            self.attack_speed = random.uniform(2.8, 3.8)
            self.hover_duration = random.randint(140, 240)
        else:
            self.level = "hard"
            self.hp = 3
            self.color = ENEMY_HARD
            self.shoot_chance = 0.0042
            self.attack_speed = random.uniform(3.4, 4.6)
            self.hover_duration = random.randint(110, 180)

        self.enter_speed = random.uniform(2.0, 2.8)
        self.hold_x = random.randint(700, 860)

        self.wave_offset = random.uniform(0, math.tau)
        self.wave_speed = random.uniform(0.02, 0.05)
        self.wave_amplitude = random.randint(18, 36)

        self.state = "entering"
        self.hover_timer = 0
        self.hover_center_y = self.y
        self.current_y = float(self.y)
        self.drift_velocity = random.uniform(-0.25, 0.25)

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, enemy_bullets, frame_count):
        if self.state == "entering":
            self.x -= self.enter_speed
            self._move_vertical(frame_count, entering=True)

            if self.x <= self.hold_x:
                self.x = self.hold_x
                self.state = "hovering"
                self.hover_timer = 0
                self.hover_center_y = self.current_y

        elif self.state == "hovering":
            self.hover_timer += 1
            self._move_vertical(frame_count, slow=True)

            if self.hover_timer >= self.hover_duration:
                self.state = "attacking"

        elif self.state == "attacking":
            self.x -= self.attack_speed
            self._move_vertical(frame_count, slow=False)

        can_shoot = self.state in ("hovering", "attacking") and self.x < WIDTH - 40
        if can_shoot and random.random() < self.shoot_chance:
            enemy_bullets.append(
                Bullet(self.x - 10, self.y + self.h // 2 - 2, -6, 0, "enemy", w=16, h=4)
            )

    def _move_vertical(self, frame_count, slow=False, entering=False):
        target_y = self.current_y

        if self.kind == "hover":
            speed_mul = 0.55 if slow or entering else 0.9
            target_y = self.hover_center_y + math.sin(
                frame_count * self.wave_speed * speed_mul + self.wave_offset
            ) * self.wave_amplitude

        elif self.kind == "wave":
            speed_mul = 0.75 if slow or entering else 1.15
            amp = self.wave_amplitude + (4 if slow or entering else 10)
            target_y = self.hover_center_y + math.sin(
                frame_count * self.wave_speed * speed_mul + self.wave_offset
            ) * amp

        elif self.kind == "drifter":
            drift_strength = 0.18 if slow or entering else 0.35
            self.drift_velocity += math.sin(frame_count * 0.03 + self.wave_offset) * 0.01
            self.drift_velocity = max(-0.6, min(0.6, self.drift_velocity))
            target_y = self.current_y + self.drift_velocity * (1.0 + drift_strength)

        # suavização pra nunca "teleportar"
        self.current_y += (target_y - self.current_y) * 0.12
        self.current_y = clamp(self.current_y, 30, HEIGHT - self.h - 30)
        self.y = int(self.current_y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.w, self.h), border_radius=6)
        pygame.draw.circle(screen, (255, 235, 235), (int(self.x + 10), int(self.y + self.h // 2)), 4)
        pygame.draw.rect(screen, (100, 50, 50), (self.x + self.w - 12, self.y + 5, 10, self.h - 10))
