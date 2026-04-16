import sys
import pygame

from settings import *
from entities.player import Player
from entities.health_pickup import HealthPickup
from entities.weapon_pickup import WeaponPickup
from systems.stars import StarField
from sound_manager import SoundManager
from ui.touch_controls import TouchControls
from ui.screens import draw_menu, draw_options
from ui.hud import draw_hud
from systems.spawn_manager import (
    update_spawns,
    update_player_bullets,
    update_enemy_bullets,
    update_bombs,
    update_enemies,
    update_boss,
    update_pickups,
    update_weapon_pickups,
    update_explosions,
)
from systems.collision_manager import handle_collisions


class Game:
    def __init__(self):
        self.sound = SoundManager()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.stars = StarField()
        self.touch_controls = TouchControls()
        self.finger_positions = {}

        self.HealthPickup = HealthPickup
        self.WeaponPickup = WeaponPickup

        self.menu_state = "main_menu"
        self.mobile_controls_enabled = self._detect_mobile_platform()
        self.reset()

    def _detect_mobile_platform(self):
        name = sys.platform.lower()
        return "android" in name or "ios" in name

    def reset(self):
        _, sh = self.screen.get_size()
        self.player = Player()
        self.player.y = sh // 2

        self.player_bullets = []
        self.enemy_bullets = []
        self.bombs = []
        self.enemies = []
        self.explosions = []
        self.pickups = []
        self.weapon_pickups = []

        self.spawn_timer = 0
        self.spawn_interval = 1500
        self.score = 0
        self.frame_count = 0

        self.game_over = False
        self.phase_clear = False

        self.boss_spawned = False
        self.boss = None

        self.kills = 0
        self.phase_target_kills = 18
        self.phase_spawning_done = False

    def draw_text(self, text, font_obj, color, x, y):
        img = font_obj.render(text, True, color)
        self.screen.blit(img, (x, y))

    def menu_buttons(self):
        from ui.layout import Layout
        return Layout(*self.screen.get_size()).menu_buttons()

    def options_buttons(self):
        from ui.layout import Layout
        return Layout(*self.screen.get_size()).options_buttons()

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            self.frame_count += 1

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def handle_events(self):
        sw, sh = self.screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(
                    (max(800, event.w), max(500, event.h)),
                    pygame.RESIZABLE
                )

            elif event.type == pygame.KEYDOWN:
                if self.menu_state == "playing":
                    if (self.game_over or self.phase_clear) and event.key == pygame.K_r:
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        self.menu_state = "main_menu"
                elif self.menu_state == "main_menu":
                    if event.key == pygame.K_RETURN:
                        self.reset()
                        self.menu_state = "playing"
                elif self.menu_state == "options":
                    if event.key == pygame.K_ESCAPE:
                        self.menu_state = "main_menu"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos

                if self.menu_state == "main_menu":
                    buttons = self.menu_buttons()
                    if buttons["start"].collidepoint(pos):
                        self.reset()
                        self.menu_state = "playing"
                    elif buttons["options"].collidepoint(pos):
                        self.menu_state = "options"
                    elif buttons["exit"].collidepoint(pos):
                        self.running = False

                elif self.menu_state == "options":
                    buttons = self.options_buttons()
                    if buttons["sound"].collidepoint(pos):
                        self.sound.enabled = not self.sound.enabled
                    elif buttons["touch"].collidepoint(pos):
                        self.mobile_controls_enabled = not self.mobile_controls_enabled
                    elif buttons["back"].collidepoint(pos):
                        self.menu_state = "main_menu"

                elif self.menu_state == "playing" and self.mobile_controls_enabled:
                    self.touch_controls.mouse_down(pos, sw, sh)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.touch_controls.mouse_up()

            elif event.type == pygame.MOUSEMOTION:
                self.touch_controls.mouse_motion(event.pos)

            elif event.type == pygame.FINGERDOWN:
                x = int(event.x * self.screen.get_width())
                y = int(event.y * self.screen.get_height())
                self.finger_positions[event.finger_id] = (x, y)
                if self.menu_state == "playing" and self.mobile_controls_enabled:
                    self.touch_controls.finger_down(event.finger_id, x, y, self.screen.get_width(), self.screen.get_height())

            elif event.type == pygame.FINGERMOTION:
                x = int(event.x * self.screen.get_width())
                y = int(event.y * self.screen.get_height())
                self.finger_positions[event.finger_id] = (x, y)

            elif event.type == pygame.FINGERUP:
                if event.finger_id in self.finger_positions:
                    del self.finger_positions[event.finger_id]
                self.touch_controls.finger_up(event.finger_id)

    def update(self, dt):
        self.stars.update()

        if self.menu_state != "playing":
            update_explosions(self)
            return

        keys = pygame.key.get_pressed()
        sw, sh = self.screen.get_size()

        show_touch = self.touch_controls.visible_for(self.mobile_controls_enabled)

        if show_touch:
            tx, ty, tfire = self.touch_controls.get_move_and_fire(self.finger_positions, sw, sh)
        else:
            tx, ty, tfire = 0, 0, False

        firing_input = keys[pygame.K_SPACE] or tfire

        if self.game_over or self.phase_clear:
            update_explosions(self)
            update_pickups(self)
            update_weapon_pickups(self)
            return

        self.player.update(keys, dt, firing_input, (tx, ty), sw, sh)

        if firing_input:
            fired = self.player.try_fire(self.player_bullets)
            if fired:
                self.sound.play("shoot")

        update_spawns(self, dt)
        update_player_bullets(self)
        update_enemy_bullets(self)
        update_bombs(self)
        update_enemies(self)
        update_boss(self)
        update_pickups(self)
        update_weapon_pickups(self)
        handle_collisions(self)
        update_explosions(self)

    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen)

        if self.menu_state == "main_menu":
            draw_menu(self)
            pygame.display.flip()
            return

        if self.menu_state == "options":
            draw_options(self)
            pygame.display.flip()
            return

        if not self.game_over:
            self.player.draw(self.screen)

        for bullet in self.player_bullets:
            bullet.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for bomb in self.bombs:
            bomb.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for pickup in self.pickups:
            pickup.draw(self.screen)

        for pickup in self.weapon_pickups:
            pickup.draw(self.screen)

        if self.boss is not None:
            self.boss.draw(self.screen)

        for exp in self.explosions:
            exp.draw(self.screen)

        draw_hud(self)

        sw, sh = self.screen.get_size()
        if self.touch_controls.visible_for(self.mobile_controls_enabled):
            tx, ty, tfire = self.touch_controls.get_move_and_fire(self.finger_positions, sw, sh)
            self.touch_controls.draw(self.screen, sw, sh, (tx, ty), tfire)

        pygame.display.flip()
