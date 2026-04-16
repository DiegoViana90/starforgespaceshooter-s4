import random
import math
import pygame
from settings import WIDTH, HEIGHT

class StarField:
    def __init__(self):
        self.stars_far = [self._make_far_star() for _ in range(130)]
        self.stars_near = [self._make_near_star() for _ in range(18)]

    def _make_far_star(self):
        return {
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT),
            "size": random.choice([1, 1, 1, 2]),
            "speed": random.uniform(0.15, 0.55),
            "base": random.randint(65, 180),
            "amp": random.randint(0, 45),
            "pulse": random.uniform(0.01, 0.05),
            "phase": random.uniform(0, math.tau),
        }

    def _make_near_star(self):
        return {
            "x": random.uniform(0, WIDTH),
            "y": random.uniform(0, HEIGHT),
            "size": random.choice([2, 2, 3]),
            "speed": random.uniform(1.2, 2.1),
            "brightness": random.randint(170, 235),
        }

    def _reset_far_star(self, star):
        star["x"] = WIDTH + random.uniform(0, 40)
        star["y"] = random.uniform(0, HEIGHT)
        star["size"] = random.choice([1, 1, 1, 2])
        star["speed"] = random.uniform(0.15, 0.55)
        star["base"] = random.randint(65, 180)
        star["amp"] = random.randint(0, 45)
        star["pulse"] = random.uniform(0.01, 0.05)
        star["phase"] = random.uniform(0, math.tau)

    def _reset_near_star(self, star):
        star["x"] = WIDTH + random.uniform(0, 80)
        star["y"] = random.uniform(0, HEIGHT)
        star["size"] = random.choice([2, 2, 3])
        star["speed"] = random.uniform(1.2, 2.1)
        star["brightness"] = random.randint(170, 235)

    def update(self):
        for star in self.stars_far:
            star["x"] -= star["speed"]
            star["phase"] += star["pulse"]

            if star["x"] < -5:
                self._reset_far_star(star)

        for star in self.stars_near:
            star["x"] -= star["speed"]

            if star["x"] < -8:
                self._reset_near_star(star)

    def draw(self, screen):
        for star in self.stars_far:
            brightness = int(star["base"] + math.sin(star["phase"]) * star["amp"])
            brightness = max(50, min(220, brightness))
            color = (brightness, brightness, min(255, brightness + 20))

            pygame.draw.circle(
                screen,
                color,
                (int(star["x"]), int(star["y"])),
                star["size"]
            )

        for star in self.stars_near:
            b = star["brightness"]
            color = (b, b, min(255, b + 15))

            pygame.draw.circle(
                screen,
                color,
                (int(star["x"]), int(star["y"])),
                star["size"]
            )
