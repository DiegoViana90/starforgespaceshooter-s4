import random
from entities.enemy import Enemy
from entities.boss import Boss


def update_spawns(game, dt):
    if game.kills >= game.phase_target_kills:
        game.phase_spawning_done = True

    if not game.phase_spawning_done and not game.boss_spawned:
        game.spawn_timer += dt * 1000
        if game.spawn_timer >= game.spawn_interval:
            game.enemies.append(Enemy())
            game.spawn_timer = 0

            if game.spawn_interval > 950:
                game.spawn_interval -= 12

    if game.phase_spawning_done and not game.boss_spawned and len(game.enemies) == 0:
        game.boss_spawned = True
        game.boss = Boss()


def update_player_bullets(game):
    sw, _ = game.screen.get_size()
    for bullet in game.player_bullets[:]:
        bullet.update()
        if bullet.x > sw + 40:
            game.player_bullets.remove(bullet)


def update_enemy_bullets(game):
    _, sh = game.screen.get_size()
    for bullet in game.enemy_bullets[:]:
        bullet.update()
        if bullet.x + bullet.w < -50 or bullet.y < -50 or bullet.y > sh + 50:
            game.enemy_bullets.remove(bullet)


def update_bombs(game):
    _, sh = game.screen.get_size()
    for bomb in game.bombs[:]:
        bomb.update()
        if bomb.x < -60 or bomb.y > sh + 60:
            game.bombs.remove(bomb)


def update_enemies(game):
    for enemy in game.enemies[:]:
        enemy.update(game.enemy_bullets, game.frame_count)
        if enemy.x + enemy.w < -60:
            game.enemies.remove(enemy)


def update_boss(game):
    if game.boss is not None:
        game.boss.update(game.enemy_bullets, game.bombs)


def update_pickups(game):
    for pickup in game.pickups[:]:
        pickup.update()
        if pickup.x + pickup.size < -40:
            game.pickups.remove(pickup)


def update_weapon_pickups(game):
    for pickup in game.weapon_pickups[:]:
        pickup.update()
        if pickup.x + pickup.size < -40:
            game.weapon_pickups.remove(pickup)


def update_explosions(game):
    for exp in game.explosions[:]:
        exp.update()
        if exp.timer <= 0:
            game.explosions.remove(exp)


def maybe_spawn_health_pickup(game, enemy):
    if game.player.hp >= 100:
        return

    if random.random() < 0.18:
        px = enemy.x + enemy.w // 2 - 9
        py = enemy.y + enemy.h // 2 - 9
        game.pickups.append(game.HealthPickup(px, py))


def maybe_spawn_weapon_pickup(game, enemy):
    chance = 0.0

    if getattr(enemy, "level", "") == "medium":
        chance = 0.35
    elif getattr(enemy, "level", "") == "hard":
        chance = 0.65

    if random.random() < chance:
        px = enemy.x + enemy.w // 2 - 10
        py = enemy.y + enemy.h // 2 - 10
        game.weapon_pickups.append(game.WeaponPickup(px, py))
