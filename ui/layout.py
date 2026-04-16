import pygame


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


class Layout:
    def __init__(self, screen_w, screen_h):
        self.w = screen_w
        self.h = screen_h

        self.scale = min(screen_w / 1000, screen_h / 600)
        self.scale = clamp(self.scale, 0.8, 1.8)

        self.safe_top = int(18 * self.scale)
        self.safe_bottom = int(18 * self.scale)
        self.safe_left = int(14 * self.scale)
        self.safe_right = int(14 * self.scale)

    def font(self, base, bold=False):
        size = max(14, int(base * self.scale))
        return pygame.font.SysFont("arial", size, bold=bold)

    def hud_rects(self):
        hp_x = self.safe_left + 8
        hp_y = self.safe_top + 8
        hp_w = int(220 * self.scale)
        hp_h = int(24 * self.scale)

        score_x = hp_x
        score_y = hp_y + hp_h + int(10 * self.scale)

        stage_x = self.w - self.safe_right - int(110 * self.scale)
        stage_y = hp_y

        boss_bar_w = int(280 * self.scale)
        boss_bar_h = int(20 * self.scale)
        boss_bar_x = self.w - self.safe_right - boss_bar_w - int(20 * self.scale)
        boss_bar_y = score_y

        weapon_bar_x = self.safe_left + 8
        weapon_bar_w = min(int(320 * self.scale), self.w - self.safe_left - self.safe_right - 30)
        weapon_bar_h = max(16, int(18 * self.scale))
        weapon_bar_y = self.h - self.safe_bottom - weapon_bar_h - 8

        return {
            "hp": pygame.Rect(hp_x, hp_y, hp_w, hp_h),
            "score_pos": (score_x, score_y),
            "stage_pos": (stage_x, stage_y),
            "boss_bar": pygame.Rect(boss_bar_x, boss_bar_y, boss_bar_w, boss_bar_h),
            "weapon_bar": pygame.Rect(weapon_bar_x, weapon_bar_y, weapon_bar_w, weapon_bar_h),
        }

    def menu_buttons(self):
        bw = int(clamp(self.w * 0.28, 240, 360))
        bh = int(clamp(self.h * 0.085, 48, 70))
        cx = self.w // 2 - bw // 2
        start_y = int(self.h * 0.47)
        gap = int(16 * self.scale)

        return {
            "start": pygame.Rect(cx, start_y, bw, bh),
            "options": pygame.Rect(cx, start_y + bh + gap, bw, bh),
            "exit": pygame.Rect(cx, start_y + (bh + gap) * 2, bw, bh),
        }

    def options_buttons(self):
        bw = int(clamp(self.w * 0.36, 280, 460))
        bh = int(clamp(self.h * 0.085, 48, 70))
        cx = self.w // 2 - bw // 2
        start_y = int(self.h * 0.47)
        gap = int(16 * self.scale)

        return {
            "sound": pygame.Rect(cx, start_y, bw, bh),
            "touch": pygame.Rect(cx, start_y + bh + gap, bw, bh),
            "back": pygame.Rect(cx, start_y + (bh + gap) * 2 + int(24 * self.scale), bw, bh),
        }

    def touch_rects(self):
        hud = self.hud_rects()
        weapon_bar = hud["weapon_bar"]

        controls_bottom = weapon_bar.y - int(14 * self.scale)

        pad_size = int(clamp(min(self.w, self.h) * 0.15, 86, 150))
        fire_size = int(clamp(min(self.w, self.h) * 0.13, 78, 132))

        dpad = pygame.Rect(
            self.safe_left + 10,
            controls_bottom - pad_size,
            pad_size,
            pad_size
        )

        fire = pygame.Rect(
            self.w - self.safe_right - fire_size - 10,
            controls_bottom - fire_size,
            fire_size,
            fire_size
        )

        return dpad, fire
