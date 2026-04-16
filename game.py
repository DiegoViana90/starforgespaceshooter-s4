import sys
import random
import pygame

from settings import *
from entities.player import Player
from entities.enemy import Enemy
from entities.boss import Boss
from entities.explosion import Explosion
from entities.health_pickup import HealthPickup
from entities.weapon_pickup import WeaponPickup
from systems.stars import StarField
from sound_manager import SoundManager
from ui.touch_controls import TouchControls


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

        self.menu_state = "main_menu"
        self.mobile_controls_enabled = self._detect_mobile_platform()
        self.reset()

    def _detect_mobile_platform(self):
        name = sys.platform.lower()
        return "android" in name or "ios" in name

    def reset(self):
        sw, sh = self.screen.get_size()
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

    def run(self):
        while self.running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            self.frame_count += 1

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

    def menu_buttons(self):
        sw, sh = self.screen.get_size()
        bw, bh = 280, 54
        cx = sw // 2 - bw // 2
        start_y = sh // 2 - 30

        return {
            "start": pygame.Rect(cx, start_y, bw, bh),
            "options": pygame.Rect(cx, start_y + 70, bw, bh),
            "exit": pygame.Rect(cx, start_y + 140, bw, bh),
        }

    def options_buttons(self):
        sw, sh = self.screen.get_size()
        bw, bh = 360, 54
        cx = sw // 2 - bw // 2
        start_y = sh // 2 - 30

        return {
            "sound": pygame.Rect(cx, start_y, bw, bh),
            "touch": pygame.Rect(cx, start_y + 70, bw, bh),
            "back": pygame.Rect(cx, start_y + 160, bw, bh),
        }

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

                elif self.menu_state == "playing":
                    self.touch_controls.mouse_down(pos, sw, sh)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.touch_controls.mouse_up()

            elif event.type == pygame.MOUSEMOTION:
                self.touch_controls.mouse_motion(event.pos)

            elif event.type == pygame.FINGERDOWN:
                x = int(event.x * self.screen.get_width())
                y = int(event.y * self.screen.get_height())
                self.finger_positions[event.finger_id] = (x, y)
                if self.menu_state == "playing":
                    self.touch_controls.finger_down(
                        event.finger_id,
                        x,
                        y,
                        self.screen.get_width(),
                        self.screen.get_height()
                    )

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
            self.update_explosions()
            return

        keys = pygame.key.get_pressed()
        sw, sh = self.screen.get_size()

        show_touch = self.touch_controls.visible_for(sw, sh, self.mobile_controls_enabled)
        if show_touch:
            tx, ty, tfire = self.touch_controls.get_move_and_fire(
                self.finger_positions, sw, sh
            )
        else:
            tx, ty, tfire = 0, 0, False

        firing_input = keys[pygame.K_SPACE] or tfire

        if self.game_over or self.phase_clear:
            self.update_explosions()
            self.update_pickups()
            self.update_weapon_pickups()
            return

        self.player.update(keys, dt, firing_input, (tx, ty), sw, sh)

        if firing_input:
            fired = self.player.try_fire(self.player_bullets)
            if fired:
                self.sound.play("shoot")

        self.update_spawns(dt)
        self.update_player_bullets()
        self.update_enemy_bullets()
        self.update_bombs()
        self.update_enemies()
        self.update_boss()
        self.update_pickups()
        self.update_weapon_pickups()
        self.handle_collisions()
        self.update_explosions()

    def update_spawns(self, dt):
        if self.kills >= self.phase_target_kills:
            self.phase_spawning_done = True

        if not self.phase_spawning_done and not self.boss_spawned:
            self.spawn_timer += dt * 1000
            if self.spawn_timer >= self.spawn_interval:
                self.enemies.append(Enemy())
                self.spawn_timer = 0

                if self.spawn_interval > 950:
                    self.spawn_interval -= 12

        if self.phase_spawning_done and not self.boss_spawned and len(self.enemies) == 0:
            self.boss_spawned = True
            self.boss = Boss()

    def update_player_bullets(self):
        sw, _ = self.screen.get_size()
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.x > sw + 40:
                self.player_bullets.remove(bullet)

    def update_enemy_bullets(self):
        _, sh = self.screen.get_size()
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.x + bullet.w < -50 or bullet.y < -50 or bullet.y > sh + 50:
                self.enemy_bullets.remove(bullet)

    def update_bombs(self):
        _, sh = self.screen.get_size()
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.x < -60 or bomb.y > sh + 60:
                self.bombs.remove(bomb)

    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy.update(self.enemy_bullets, self.frame_count)
            if enemy.x + enemy.w < -60:
                self.enemies.remove(enemy)

    def update_boss(self):
        if self.boss is not None:
            self.boss.update(self.enemy_bullets, self.bombs)

    def update_pickups(self):
        for pickup in self.pickups[:]:
            pickup.update()
            if pickup.x + pickup.size < -40:
                self.pickups.remove(pickup)

    def update_weapon_pickups(self):
        for pickup in self.weapon_pickups[:]:
            pickup.update()
            if pickup.x + pickup.size < -40:
                self.weapon_pickups.remove(pickup)

    def update_explosions(self):
        for exp in self.explosions[:]:
            exp.update()
            if exp.timer <= 0:
                self.explosions.remove(exp)

    def maybe_spawn_health_pickup(self, enemy):
        if self.player.hp >= 100:
            return
        if random.random() < 0.18:
            px = enemy.x + enemy.w // 2 - 9
            py = enemy.y + enemy.h // 2 - 9
            self.pickups.append(HealthPickup(px, py))

    def maybe_spawn_weapon_pickup(self, enemy):
        chance = 0.0
        if getattr(enemy, "level", "") == "medium":
            chance = 0.75
        elif getattr(enemy, "level", "") == "hard":
            chance = 0.95

        if random.random() < chance:
            px = enemy.x + enemy.w // 2 - 10
            py = enemy.y + enemy.h // 2 - 10
            self.weapon_pickups.append(WeaponPickup(px, py))

    def handle_collisions(self):
        self.handle_player_bullet_hits()
        self.handle_enemy_bullet_hits()
        self.handle_bomb_hits()
        self.handle_enemy_contact()
        self.handle_boss_contact()
        self.handle_pickup_hits()
        self.handle_weapon_pickup_hits()

    def handle_player_bullet_hits(self):
        for bullet in self.player_bullets[:]:
            if bullet not in self.player_bullets:
                continue

            hit_something = False

            for enemy in self.enemies[:]:
                if bullet.rect().colliderect(enemy.rect()):
                    enemy.hp -= 1
                    hit_something = True

                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)

                    if enemy.hp <= 0:
                        self.explosions.append(
                            Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0)
                        )
                        self.sound.play("explosion")
                        self.maybe_spawn_health_pickup(enemy)
                        self.maybe_spawn_weapon_pickup(enemy)

                        if enemy in self.enemies:
                            self.enemies.remove(enemy)

                        self.score += 100
                        self.kills += 1
                    break

            if hit_something:
                continue

            if (
                self.boss is not None
                and bullet in self.player_bullets
                and bullet.rect().colliderect(self.boss.rect())
            ):
                self.boss.hp -= 1
                self.player_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.x, bullet.y, 0.5))

                if self.boss.hp <= 0:
                    self.sound.play("explosion")
                    self.explosions.append(
                        Explosion(self.boss.x + self.boss.w // 2, self.boss.y + self.boss.h // 2, 2.8)
                    )
                    self.score += 3000
                    self.boss = None
                    self.phase_clear = True

    def handle_enemy_bullet_hits(self):
        for bullet in self.enemy_bullets[:]:
            if bullet.rect().colliderect(self.player.rect()):
                self.explosions.append(
                    Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 0.8)
                )
                self.enemy_bullets.remove(bullet)
                self.sound.play("hit")
                self.player.hp -= 8
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_bomb_hits(self):
        for bomb in self.bombs[:]:
            if bomb.rect().colliderect(self.player.rect()):
                self.explosions.append(Explosion(bomb.x, bomb.y, 1.3))
                self.explosions.append(
                    Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.0)
                )
                self.bombs.remove(bomb)
                self.sound.play("hit")
                self.player.hp -= 18
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_enemy_contact(self):
        for enemy in self.enemies[:]:
            if enemy.rect().colliderect(self.player.rect()):
                self.explosions.append(
                    Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0)
                )
                self.explosions.append(
                    Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.0)
                )
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                self.sound.play("hit")
                self.player.hp -= 12
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_boss_contact(self):
        if self.boss is not None and self.boss.rect().colliderect(self.player.rect()):
            self.explosions.append(
                Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.4)
            )
            self.sound.play("hit")
            self.player.hp -= 30
            if self.player.hp <= 0:
                self.game_over = True

    def handle_pickup_hits(self):
        for pickup in self.pickups[:]:
            if pickup.rect().colliderect(self.player.rect()):
                self.player.hp = min(100, self.player.hp + 20)
                self.pickups.remove(pickup)
                self.sound.play("pickup")

    def handle_weapon_pickup_hits(self):
        for pickup in self.weapon_pickups[:]:
            if pickup.rect().colliderect(self.player.rect()):
                self.player.give_special_ammo(30)
                self.weapon_pickups.remove(pickup)
                self.sound.play("pickup")

    def draw_menu(self):
        sw, sh = self.screen.get_size()

        title_font = pygame.font.SysFont("arial", 56, bold=True)
        game_font = pygame.font.SysFont("arial", 44, bold=False)
        sub_font = pygame.font.SysFont("arial", 24)

        title1 = title_font.render("STARFORGE", True, CYAN)
        title2 = game_font.render("SPACE SHOOTER S4", True, WHITE)
        subtitle = sub_font.render("Retro arcade shooter", True, (180, 180, 200))

        title1_rect = title1.get_rect(center=(sw // 2, 140))
        title2_rect = title2.get_rect(center=(sw // 2, 195))
        subtitle_rect = subtitle.get_rect(center=(sw // 2, 250))

        self.screen.blit(title1, title1_rect)
        self.screen.blit(title2, title2_rect)
        self.screen.blit(subtitle, subtitle_rect)

        buttons = self.menu_buttons()
        for rect in buttons.values():
            pygame.draw.rect(self.screen, (45, 45, 70), rect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=12)

        def draw_button_label(text, rect):
            label = FONT.render(text, True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        draw_button_label("START GAME", buttons["start"])
        draw_button_label("OPTIONS", buttons["options"])
        draw_button_label("EXIT", buttons["exit"])

    def draw_options(self):
        sw, sh = self.screen.get_size()

        title = BIG_FONT.render("OPTIONS", True, CYAN)
        title_rect = title.get_rect(center=(sw // 2, 140))
        self.screen.blit(title, title_rect)

        buttons = self.options_buttons()
        for rect in buttons.values():
            pygame.draw.rect(self.screen, (45, 45, 70), rect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=12)

        sound_label = "SOUND: ON" if self.sound.enabled else "SOUND: OFF"
        touch_label = "TOUCH CONTROLS: ON" if self.mobile_controls_enabled else "TOUCH CONTROLS: OFF"

        def draw_button_label(text, rect):
            label = FONT.render(text, True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            self.screen.blit(label, label_rect)

        draw_button_label(sound_label, buttons["sound"])
        draw_button_label(touch_label, buttons["touch"])
        draw_button_label("BACK", buttons["back"])

    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen)

        if self.menu_state == "main_menu":
            self.draw_menu()
            pygame.display.flip()
            return

        if self.menu_state == "options":
            self.draw_options()
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

        self.draw_hud()

        sw, sh = self.screen.get_size()
        if self.touch_controls.visible_for(sw, sh, self.mobile_controls_enabled):
            tx, ty, tfire = self.touch_controls.get_move_and_fire(self.finger_positions, sw, sh)
            self.touch_controls.draw(self.screen, sw, sh, (tx, ty), tfire)

        pygame.display.flip()

    def draw_hud(self):
        sw, sh = self.screen.get_size()

        pygame.draw.rect(self.screen, (60, 60, 60), (20, 20, 220, 24), border_radius=8)
        pygame.draw.rect(
            self.screen,
            GREEN if self.player.hp > 30 else RED,
            (20, 20, max(0, self.player.hp * 2.2), 24),
            border_radius=8,
        )
        pygame.draw.rect(self.screen, WHITE, (20, 20, 220, 24), 2, border_radius=8)

        self.draw_text(f"Score: {self.score}", FONT, WHITE, 20, 55)

        if self.boss is None and not self.boss_spawned:
            self.draw_text("Fase 1", FONT, CYAN, sw - 110, 20)
        elif self.boss is not None:
            self.draw_text("CHEFÃO", FONT, RED, sw - 140, 20)

            boss_hp_w = 280
            pygame.draw.rect(self.screen, (60, 60, 60), (sw - 330, 55, boss_hp_w, 20), border_radius=8)
            current_boss_bar = int((self.boss.hp / self.boss.max_hp) * boss_hp_w)
            pygame.draw.rect(self.screen, RED, (sw - 330, 55, current_boss_bar, 20), border_radius=8)
            pygame.draw.rect(self.screen, WHITE, (sw - 330, 55, boss_hp_w, 20), 2, border_radius=8)

        weapon_bar_x = 20
        weapon_bar_y = sh - 40
        weapon_bar_w = min(320, sw - 40)
        weapon_bar_h = 18

        pygame.draw.rect(
            self.screen,
            (55, 55, 55),
            (weapon_bar_x, weapon_bar_y, weapon_bar_w, weapon_bar_h),
            border_radius=6,
        )

        weapon_text = ""

        if self.player.special_ammo > 0:
            ratio = self.player.special_ammo / self.player.max_special_ammo
            fill_w = int(weapon_bar_w * ratio)
            pygame.draw.rect(
                self.screen,
                (255, 220, 70),
                (weapon_bar_x, weapon_bar_y, fill_w, weapon_bar_h),
                border_radius=6,
            )
            weapon_text = "TIRO TRIPLO"

        elif self.player.overheated:
            ratio = max(0.0, min(1.0, self.player.weapon_heat / self.player.max_heat))
            fill_w = int(weapon_bar_w * ratio)
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen,
                    (220, 70, 70),
                    (weapon_bar_x, weapon_bar_y, fill_w, weapon_bar_h),
                    border_radius=6,
                )
            weapon_text = "AGUARDE..."

        else:
            ratio = self.player.weapon_heat / self.player.max_heat
            fill_w = int(weapon_bar_w * ratio)
            bar_color = (
                180 + int(75 * ratio),
                max(50, 220 - int(140 * ratio)),
                60,
            )
            if fill_w > 0:
                pygame.draw.rect(
                    self.screen,
                    bar_color,
                    (weapon_bar_x, weapon_bar_y, fill_w, weapon_bar_h),
                    border_radius=6,
                )
            weapon_text = "ARMA NORMAL"

        pygame.draw.rect(
            self.screen,
            WHITE,
            (weapon_bar_x, weapon_bar_y, weapon_bar_w, weapon_bar_h),
            2,
            border_radius=6,
        )

        text_surface = FONT.render(weapon_text, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(weapon_bar_x + weapon_bar_w // 2, weapon_bar_y + weapon_bar_h // 2)
        )
        self.screen.blit(text_surface, text_rect)

        if self.game_over:
            self.draw_text("GAME OVER", BIG_FONT, RED, sw // 2 - 140, sh // 2 - 40)
            self.draw_text("Pressione R para reiniciar", FONT, WHITE, sw // 2 - 130, sh // 2 + 20)

        if self.phase_clear:
            self.draw_text("FASE 1 COMPLETA!", BIG_FONT, GREEN, sw // 2 - 220, sh // 2 - 50)
            self.draw_text("Pressione R para jogar de novo", FONT, WHITE, sw // 2 - 150, sh // 2 + 20)

