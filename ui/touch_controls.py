import pygame
from ui.layout import Layout


class TouchControls:
    def __init__(self):
        self.left_finger_id = None
        self.right_finger_id = None
        self.mouse_active = False
        self.mouse_pos = (0, 0)

    def layout(self, screen_w, screen_h):
        layout = Layout(screen_w, screen_h)
        return layout.touch_rects()

    def visible_for(self, enabled):
        return enabled

    def finger_down(self, finger_id, x, y, screen_w, screen_h):
        dpad_rect, fire_rect = self.layout(screen_w, screen_h)
        pos = (x, y)

        if dpad_rect.collidepoint(pos) and self.left_finger_id is None:
            self.left_finger_id = finger_id

        if fire_rect.collidepoint(pos) and self.right_finger_id is None:
            self.right_finger_id = finger_id

    def finger_up(self, finger_id):
        if self.left_finger_id == finger_id:
            self.left_finger_id = None
        if self.right_finger_id == finger_id:
            self.right_finger_id = None

    def mouse_down(self, pos, screen_w, screen_h):
        dpad_rect, fire_rect = self.layout(screen_w, screen_h)
        self.mouse_active = True
        self.mouse_pos = pos
        return dpad_rect.collidepoint(pos) or fire_rect.collidepoint(pos)

    def mouse_up(self):
        self.mouse_active = False

    def mouse_motion(self, pos):
        self.mouse_pos = pos

    def get_move_and_fire(self, finger_positions, screen_w, screen_h):
        move_x = 0
        move_y = 0
        firing = False

        dpad_rect, fire_rect = self.layout(screen_w, screen_h)

        if self.left_finger_id is not None and self.left_finger_id in finger_positions:
            pos = finger_positions[self.left_finger_id]
            move_x, move_y = self._calc_dpad_vector(pos, dpad_rect)

        if self.right_finger_id is not None and self.right_finger_id in finger_positions:
            pos = finger_positions[self.right_finger_id]
            if fire_rect.collidepoint(pos):
                firing = True

        if self.mouse_active:
            if dpad_rect.collidepoint(self.mouse_pos):
                move_x, move_y = self._calc_dpad_vector(self.mouse_pos, dpad_rect)
            if fire_rect.collidepoint(self.mouse_pos):
                firing = True

        return move_x, move_y, firing

    def _calc_dpad_vector(self, pos, rect):
        cx, cy = rect.center
        dx = pos[0] - cx
        dy = pos[1] - cy

        deadzone = rect.width * 0.16
        move_x = 0
        move_y = 0

        if abs(dx) > deadzone:
            move_x = 1 if dx > 0 else -1
        if abs(dy) > deadzone:
            move_y = 1 if dy > 0 else -1

        return move_x, move_y

    def draw(self, screen, screen_w, screen_h, move_vec, firing):
        dpad_rect, fire_rect = self.layout(screen_w, screen_h)

        active = (120, 220, 255)
        fire_color = (255, 120, 120) if firing else (255, 255, 255)

        pygame.draw.rect(screen, (60, 60, 70), dpad_rect, border_radius=12)
        pygame.draw.rect(screen, (230, 230, 230), dpad_rect, 2, border_radius=12)

        h_rect = pygame.Rect(
            dpad_rect.x,
            dpad_rect.centery - dpad_rect.height // 6,
            dpad_rect.width,
            dpad_rect.height // 3
        )
        v_rect = pygame.Rect(
            dpad_rect.centerx - dpad_rect.width // 6,
            dpad_rect.y,
            dpad_rect.width // 3,
            dpad_rect.height
        )

        pygame.draw.rect(screen, (180, 180, 180), h_rect, border_radius=6)
        pygame.draw.rect(screen, (180, 180, 180), v_rect, border_radius=6)

        mx, my = move_vec
        if mx == -1:
            pygame.draw.circle(screen, active, (dpad_rect.left + dpad_rect.width // 4, dpad_rect.centery), max(8, dpad_rect.width // 14))
        if mx == 1:
            pygame.draw.circle(screen, active, (dpad_rect.right - dpad_rect.width // 4, dpad_rect.centery), max(8, dpad_rect.width // 14))
        if my == -1:
            pygame.draw.circle(screen, active, (dpad_rect.centerx, dpad_rect.top + dpad_rect.height // 4), max(8, dpad_rect.width // 14))
        if my == 1:
            pygame.draw.circle(screen, active, (dpad_rect.centerx, dpad_rect.bottom - dpad_rect.height // 4), max(8, dpad_rect.width // 14))

        pygame.draw.circle(screen, (70, 70, 80), fire_rect.center, fire_rect.width // 2)
        pygame.draw.circle(screen, fire_color, fire_rect.center, fire_rect.width // 2, 3)

        font = pygame.font.SysFont("arial", max(16, fire_rect.width // 5))
        label = font.render("FIRE", True, fire_color)
        screen.blit(label, label.get_rect(center=fire_rect.center))
