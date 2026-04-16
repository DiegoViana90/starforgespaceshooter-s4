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


class Game:
    def __init__(self):
        self.sound = SoundManager()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.stars = StarField()
        self.reset()

    def reset(self):
        self.player = Player()
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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if (self.game_over or self.phase_clear) and event.key == pygame.K_r:
                    self.reset()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        firing_input = keys[pygame.K_SPACE]

        self.stars.update()

        if self.game_over or self.phase_clear:
            self.update_explosions()
            self.update_pickups()
            self.update_weapon_pickups()
            return

        self.player.update(keys, dt, firing_input)

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
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.x > WIDTH + 40:
                self.player_bullets.remove(bullet)

    def update_enemy_bullets(self):
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.x + bullet.w < -50 or bullet.y < -50 or bullet.y > HEIGHT + 50:
                self.enemy_bullets.remove(bullet)

    def update_bombs(self):
        for bomb in self.bombs[:]:
            bomb.update()
            if bomb.x < -60 or bomb.y > HEIGHT + 60:
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
            chance = 0.35
        elif getattr(enemy, "level", "") == "hard":
            chance = 0.65

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
                        self.explosions.append(Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0))
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

            if self.boss is not None and bullet in self.player_bullets and bullet.rect().colliderect(self.boss.rect()):
                self.boss.hp -= 1
                self.player_bullets.remove(bullet)
                self.explosions.append(Explosion(bullet.x, bullet.y, 0.5))

                if self.boss.hp <= 0:
                    self.explosions.append(Explosion(self.boss.x + self.boss.w // 2, self.boss.y + self.boss.h // 2, 2.8))
                    self.score += 3000
                    self.boss = None
                    self.phase_clear = True

    def handle_enemy_bullet_hits(self):
        for bullet in self.enemy_bullets[:]:
            if bullet.rect().colliderect(self.player.rect()):
                self.explosions.append(Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 0.8))
                self.enemy_bullets.remove(bullet)
                self.player.hp -= 8
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_bomb_hits(self):
        for bomb in self.bombs[:]:
            if bomb.rect().colliderect(self.player.rect()):
                self.explosions.append(Explosion(bomb.x, bomb.y, 1.3))
                self.explosions.append(Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.0))
                self.bombs.remove(bomb)
                self.player.hp -= 18
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_enemy_contact(self):
        for enemy in self.enemies[:]:
            if enemy.rect().colliderect(self.player.rect()):
                self.explosions.append(Explosion(enemy.x + enemy.w // 2, enemy.y + enemy.h // 2, 1.0))
                self.explosions.append(Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.0))
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                self.player.hp -= 12
                if self.player.hp <= 0:
                    self.game_over = True

    def handle_boss_contact(self):
        if self.boss is not None and self.boss.rect().colliderect(self.player.rect()):
            self.explosions.append(Explosion(self.player.x + self.player.w // 2, self.player.y + self.player.h // 2, 1.4))
            self.player.hp -= 30
            if self.player.hp <= 0:
                self.game_over = True

    def handle_pickup_hits(self):
        for pickup in self.pickups[:]:
            if pickup.rect().colliderect(self.player.rect()):
                self.player.hp = min(100, self.player.hp + 20)
                self.pickups.remove(pickup)

    def handle_weapon_pickup_hits(self):
        for pickup in self.weapon_pickups[:]:
            if pickup.rect().colliderect(self.player.rect()):
                self.player.give_special_ammo(18)
                self.weapon_pickups.remove(pickup)

    def draw(self):
        self.screen.fill(BLACK)
        self.stars.draw(self.screen)

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
        pygame.display.flip()

    def draw_hud(self):
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
            self.draw_text("Fase 1", FONT, CYAN, WIDTH - 110, 20)
        elif self.boss is not None:
            self.draw_text("CHEFÃO", FONT, RED, WIDTH - 140, 20)

            boss_hp_w = 280
            pygame.draw.rect(
                self.screen,
                (60, 60, 60),
                (WIDTH - 330, 55, boss_hp_w, 20),
                border_radius=8,
            )
            current_boss_bar = int((self.boss.hp / self.boss.max_hp) * boss_hp_w)
            pygame.draw.rect(
                self.screen,
                RED,
                (WIDTH - 330, 55, current_boss_bar, 20),
                border_radius=8,
            )
            pygame.draw.rect(self.screen, WHITE, (WIDTH - 330, 55, boss_hp_w, 20), 2, border_radius=8)

        weapon_bar_x = 20
        weapon_bar_y = HEIGHT - 40
        weapon_bar_w = 320
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
            self.draw_text("GAME OVER", BIG_FONT, RED, WIDTH // 2 - 140, HEIGHT // 2 - 40)
            self.draw_text("Pressione R para reiniciar", FONT, WHITE, WIDTH // 2 - 130, HEIGHT // 2 + 20)

        if self.phase_clear:
            self.draw_text("FASE 1 COMPLETA!", BIG_FONT, GREEN, WIDTH // 2 - 220, HEIGHT // 2 - 50)
            self.draw_text("Pressione R para jogar de novo", FONT, WHITE, WIDTH // 2 - 150, HEIGHT // 2 + 20)